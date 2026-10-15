"""Agente de recopilación respetuoso: robots.txt, límites, duplicados y caducidad.

Ejecutar: python -m agent.collector
Opcional: COLLECT_MAX_PER_SOURCE=25 COLLECT_DELAY=2 python -m agent.collector
Sin claves, sin eludir captchas, sesiones privadas ni limitaciones anti-bot.
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
import re
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from .sources import SOURCES
from .quality import valid_and_recent, merge_exact_reposts, expand_reposts, build_facets
from .geo import map_metadata
from .signals import decorate
from .verification import load_registry, apply_verification
from .ats import boards, source_for_board, collect_ats

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "public/data/jobs.json"
USER_AGENT = os.getenv('TOTALCHANBA_USER_AGENT', os.getenv('CHAMBANI_USER_AGENT', 'TotalChanbaIndexer/1.0 (public job metadata; polite crawler)'))
MAX_PER_SOURCE = max(1, min(int(os.getenv('COLLECT_MAX_PER_SOURCE','18')),80))
DELAY = max(float(os.getenv('COLLECT_DELAY','2')),1.0)
TIMEOUT = 14
log = logging.getLogger('chambani')

DEPARTMENTS = ['Managua','Estelí','León','Chinandega','Masaya','Granada','Matagalpa','Jinotega','Nueva Segovia','Madriz','Boaco','Chontales','Carazo','Rivas','Río San Juan','Costa Caribe Norte','Costa Caribe Sur','RAAN','RAAS']
CATS = {
  'Ventas': ['venta','asesor comercial','vendedor','ventas','mercadeo','marketing','promotor','cobranza','credito','crédito'],
  'Administración': ['administrat','oficina','recepcion','secretari','recursos humanos','reclutad','contab','finanza','cajer'],
  'Tecnología': ['software','programador','developer','desarrollador','soporte técnico','informatic','tecnolog','frontend','backend','sistemas'],
  'Logística': ['bodega','almacen','transporte','conductor','chofer','repartidor','motorizad','logíst','logistic','flota'],
  'Servicios': ['limpieza','conserje','seguridad','cocin','meser','restaurante','panader','hotel','atención al cliente','call center','callcenter','belleza','masaje'],
  'Salud': ['enfermer','médic','farmacia','laboratorio clínico','odontolog'],
  'Educación': ['docente','profesor','maestr','tutor','educador'],
  'Industria': ['operario','mecánic','electric','soldad','torner','mantenimiento','producción','ingenier','construcción'],
}

def plain(value):
    if value is None: return ''
    if isinstance(value, list): return ' '.join(plain(v) for v in value)
    if isinstance(value,dict): return plain(value.get('name') or value.get('value') or '')
    return re.sub(r'\s+', ' ', BeautifulSoup(str(value), 'html.parser').get_text(' ',strip=True)).strip()

def fold(value):
    return ''.join(x for x in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(x))

def category(title):
    t = fold(title)
    for cat, keys in CATS.items():
        if any(fold(k) in t for k in keys): return cat
    return 'Otros'

def department(location):
    f = fold(location)
    for dep in DEPARTMENTS:
        if fold(dep) in f: return dep
    return 'Nicaragua'

def url_clean(value):
    p = urlparse(value)
    if p.scheme != 'https' or not p.hostname: return None
    if p.username or p.password: return None
    if p.hostname in ('localhost','127.0.0.1') or p.hostname.endswith('.local'): return None
    return urlunparse((p.scheme,p.netloc,p.path,'','',''))

def date_clean(value):
    if not value: return None
    s = str(value).strip()
    try:
        dt = datetime.fromisoformat(s.replace('Z','+00:00'))
        return dt.date().isoformat()
    except ValueError:
        pass
    for format in ['%d/%m/%Y','%Y-%m-%d']:
        try: return datetime.strptime(s, format).date().isoformat()
        except ValueError: pass
    return None

def normalise(job, source, now=None):
    """Una oferta debe tener URL individual y título real; nunca se fabrica una vacante."""
    now = now or datetime.now(timezone.utc)
    link = url_clean(str(job.get('url','')))
    title = plain(job.get('title'))[:130]
    if not link or len(title) < 4: return None
    parsed = urlparse(link)
    if source.get('collection') == 'ats':
        if parsed.hostname not in source.get('allowed_hosts', []): return None
        if parsed.hostname == 'jobs.lever.co' and not parsed.path.startswith('/' + source['board'] + '/'): return None
        if parsed.hostname in ('boards.greenhouse.io', 'job-boards.greenhouse.io') and not parsed.path.startswith('/' + source['board'] + '/'): return None
        if parsed.hostname in ('jobs.ashbyhq.com','jobs.smartrecruiters.com') and not parsed.path.startswith('/' + source['board'] + '/'): return None
    elif parsed.hostname != urlparse(source['url']).hostname: return None
    location = plain(job.get('location'))[:110] or 'Nicaragua'
    expires = date_clean(job.get('expires'))
    if expires and expires < now.date().isoformat(): return None
    company = plain(job.get('company'))[:95] or 'Empresa no especificada'
    summary = plain(job.get('summary'))
    summary = re.sub(r'(?i)\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b', '[contacto en origen]', summary)
    summary = re.sub(r'(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)', '[teléfono en origen]', summary)[:280]
    salary = plain(job.get('salary'))[:70]
    published = date_clean(job.get('published_at'))
    if published and published > (now.date()+timedelta(days=1)).isoformat(): return None
    address = plain(job.get('address'))[:160]
    optional = {}
    for key, maximum in [('requirements',640),('benefits',480),('experience',240),('education',240)]:
        value = plain(job.get(key))
        if value: optional[key] = value[:maximum]
    return {
        'id': hashlib.sha256(link.encode()).hexdigest()[:16],
        'title': title, 'company': company,
        'location': location, 'department': department(location),
        'address': address or None,
        'maps': map_metadata(company, location, job.get('modality'), address),
        'category': category(title), 'modality': plain(job.get('modality')) or 'No especificada',
        'type': (lambda v: v if fold(v) not in ('default', 'not specified', 'unknown', 'n/a', 'na') else 'No especificado')(plain(job.get('type')) or 'No especificado'),
        'salary': salary or None, 'summary': summary or 'Consultá los detalles y requisitos en la publicación original.',
        'published_at': published,
        'last_modified_at': date_clean(job.get('last_modified_at')),
        'expires': expires,
        'source': source['id'], 'url': link,
        'verified_at': now.isoformat(timespec='seconds').replace('+00:00','Z'),
        **optional,
    }

class PoliteClient:
    def __init__(self):
        self.robots = {}
        self.last_host = {}

    def allowed(self, url):
        parsed = urlparse(url)
        if parsed.scheme != 'https' or not parsed.hostname: return False
        key = f'{parsed.scheme}://{parsed.netloc}'
        if key not in self.robots:
            robots = RobotFileParser()
            robots_url = f'{key}/robots.txt'
            try:
                req = Request(robots_url, headers={'User-Agent': USER_AGENT,'Accept':'text/plain'})
                with urlopen(req, timeout=TIMEOUT) as r:
                    status = r.status
                    body = r.read(500_000).decode('utf-8','replace')
                if status != 200: raise ValueError('robots sin status 200')
                robots.parse(body.splitlines())
                self.robots[key] = robots
            except (URLError, HTTPError, TimeoutError, ValueError, OSError) as exc:
                log.warning('Robots inaccesible en %s: %s (omitido por seguridad)', key, exc)
                self.robots[key] = None
        robot = self.robots[key]
        return bool(robot is not None and robot.can_fetch(USER_AGENT,url))

    def get(self, url):
        if not self.allowed(url): return None
        host = urlparse(url).hostname
        elapsed = time.monotonic() - self.last_host.get(host,0)
        if elapsed < DELAY: time.sleep(DELAY-elapsed)
        self.last_host[host] = time.monotonic()
        try:
            req = Request(url, headers={'User-Agent':USER_AGENT,'Accept':'text/html,application/xhtml+xml', 'Accept-Language':'es-NI,es;q=0.9'})
            with urlopen(req,timeout=TIMEOUT) as resp:
                if resp.status != 200: return None
                if 'html' not in resp.headers.get('Content-Type','').lower(): return None
                html = resp.read(2_000_000).decode('utf-8','replace')
            return BeautifulSoup(html,'html.parser')
        except (URLError,HTTPError,TimeoutError,ValueError,OSError) as exc:
            log.warning('%s: %s',url,exc)
            return None

def discover(soup,source):
    links = []
    site = source['id']
    for a in soup.select('a[href]'):
        url = url_clean(urljoin(source['url'],a.get('href','')))
        if not url: continue
        path = urlparse(url).path
        if site == 'encuentra24':
            valid = bool(re.search(r'/nicaragua-es/empleos-ofertas-de-trabajos/[^/?]+/\d+',path))
        elif site == 'tecoloco':
            valid = bool(re.match(r'^/\d+/[^/]+\.aspx$',path))
        else: valid = False
        if valid and url not in links: links.append(url)
        if len(links) >= MAX_PER_SOURCE: break
    return links

def jsonld_jobs(soup):
    found = []
    def traverse(obj):
        if isinstance(obj,list):
            for v in obj: traverse(v)
        elif isinstance(obj,dict):
            kinds = obj.get('@type',[])
            if isinstance(kinds,str): kinds=[kinds]
            if any(str(kind).rsplit('/', 1)[-1] == 'JobPosting' for kind in kinds): found.append(obj)
            for x in obj.get('@graph',[]): traverse(x)
    for node in soup.select('script[type="application/ld+json"]'):
        try: traverse(json.loads(node.string or node.get_text()))
        except (json.JSONDecodeError,ValueError,TypeError): continue
    return found

def salary_from_jsonld(value):
    """Moneda y valor del anuncio; jamás deducir moneda o frecuencia."""
    if not isinstance(value, dict):
        return ''
    currency = str(value.get('currency') or '').strip().upper()
    if not re.fullmatch(r'[A-Z]{3}', currency):
        return ''
    amount = value.get('value')
    if not isinstance(amount, dict):
        amount = {'value': amount}
    def clean_number(n):
        if isinstance(n, bool) or n is None: return ''
        raw = str(n).strip()
        return raw if re.fullmatch(r'\d{1,9}(?:[.,]\d{1,2})?', raw) else ''
    lower = clean_number(amount.get('minValue'))
    upper = clean_number(amount.get('maxValue'))
    exact = clean_number(amount.get('value'))
    if lower and upper:
        shown = lower + '–' + upper
    else:
        shown = exact or lower or upper
    if not shown:
        return ''
    unit = str(amount.get('unitText') or value.get('unitText') or '').strip().upper()
    period = {'MONTH':'mes', 'YEAR':'año', 'WEEK':'semana',
              'DAY':'día', 'HOUR':'hora'}.get(unit, '')
    return f'{currency} {shown}' + (f' / {period}' if period else '')

def from_jsonld(item, url):
    loc = item.get('jobLocation',{})
    if isinstance(loc,list): loc=loc[0] if loc else {}
    street = ''
    if isinstance(loc,dict):
        addr=loc.get('address',{})
        if isinstance(addr,dict):
            street = plain(addr.get('streetAddress'))
            loc=', '.join(filter(None,[plain(addr.get('addressLocality')),plain(addr.get('addressRegion')),plain(addr.get('addressCountry'))]))
        else: loc=plain(addr)
    else: loc=plain(loc)
    return {
        'url':url, 'title': item.get('title'), 'company':item.get('hiringOrganization'),
        'location':loc, 'address': street, 'type':item.get('employmentType'),
        'summary':item.get('description'),
        'requirements': item.get('qualifications') or item.get('skills'),
        'benefits':item.get('jobBenefits'),
        'experience':item.get('experienceRequirements'),
        'education':item.get('educationRequirements'),
        'published_at':item.get('datePosted'),
        'expires':item.get('validThrough'),
        'salary': salary_from_jsonld(item.get('baseSalary')),
        'modality': 'Remoto' if item.get('jobLocationType')=='TELECOMMUTE' else 'No especificada',
    }

def labeled(text, label):
    match = re.search(rf'{label}\s*:?\s*(.+?)(?=\n|$)',text, re.I)
    return match.group(1).strip() if match else ''

def from_html(soup,url,source_id):
    """Adaptadores para las páginas de detalle de dos fuentes; datos ausentes se dejan vacíos."""
    for node in soup(['script','style','nav','footer']): node.decompose()
    h1 = soup.select_one('h1')
    title = plain(h1.get_text(' ',strip=True)) if h1 else ''
    text = soup.get_text('\n',strip=True)
    if source_id == 'tecoloco':
        # Título y metadatos localizables en la ficha pública.
        company = ''
        for header in soup.select('h2,h3'):
            v=plain(header.get_text(' ',strip=True))
            if v and v.upper()==v and len(v)<75:
                company=v; break
        return {'url':url,'title':title,'company':company,
           'location':labeled(text,'Ubicación'),
           'type':labeled(text,'Tipo de contratación'),
           'published_at':labeled(text,'Fecha de Publicación'),
           'expires':labeled(text,'Fecha de Expiración'),
           'summary': text.split('Descripción de la oferta',1)[-1][:240] if 'Descripción de la oferta' in text else ''}
    if source_id == 'encuentra24':
        company=''
        # De entrada, sólo admite la identidad si aparece en la ficha.
        user=soup.select_one('h1 + a')
        if user: company=plain(user.get_text(' ',strip=True))
        return {'url':url,'title':title,'company':company,
           'location':labeled(text,'dirección') or labeled(text,'ubicación'),
           'type':labeled(text,'tipo de jornada'),
           'modality':labeled(text,'tipo de trabajo'),
           'salary':labeled(text,'salario'),
           'summary':text.split('Descripción',1)[-1][:250] if 'Descripción' in text else ''}
    return {'url':url,'title':title}

def collect_reliefweb(source, now=None):
    """API pública documentada de ReliefWeb (sin rastreo HTML).

    Su endpoint es público con límites explícitos; solicitamos únicamente un resumen.
    No hay garantía de vacantes para Nicaragua en cada ejecución.
    """
    now = now or datetime.now(timezone.utc)
    # Desde nov-2025 ReliefWeb exige un appname previamente aprobado.
    # Nunca usar uno supuesto ni burlar la autorización.
    appname = os.getenv('RELIEFWEB_APPNAME', '').strip()
    if not appname: 
        log.info('ReliefWeb no configurado: registrar un appname aprobado primero')
        return None
    from urllib.parse import urlencode
    url = 'https://api.reliefweb.int/v2/jobs?' + urlencode({'appname': appname})
    body = json.dumps({
      'limit': 100,
      'filter': {'field': 'country', 'value': 'Nicaragua'},
      'sort': ['date.created:desc'],
      'fields': {'include': ['title','url','source.name','city.name','country.name','date.created','date.closing','body']}
    }).encode('utf-8')
    try:
      req = Request(url, data=body, headers={'User-Agent':USER_AGENT, 'Content-Type':'application/json','Accept':'application/json'},method='POST')
      with urlopen(req, timeout=TIMEOUT) as response:
        if response.status != 200: return None
        payload = json.loads(response.read(1_500_000))
    except (URLError, HTTPError, TimeoutError, ValueError, OSError) as exc:
      log.warning('API ReliefWeb inaccesible: %s', exc)
      return None
    results=[]
    for entry in payload.get('data', []):
      f=entry.get('fields', {})
      sources=f.get('source',[])
      cities=f.get('city',[])
      if isinstance(sources,dict): sources=[sources]
      if isinstance(cities,dict): cities=[cities]
      dates=f.get('date',{})
      url=f.get('url') or ''
      # Solo ficha original en dominio ReliefWeb; no atribuimos URL inventadas.
      if urlparse(url).hostname not in ('reliefweb.int','www.reliefweb.int'): continue
      parsed={
        'url': url,
        'title': f.get('title'),
        'company': plain(sources[0]) if sources else '',
        'location': plain(cities[0]) if cities else 'Nicaragua',
        'published_at':dates.get('created') if isinstance(dates,dict) else '',
        'expires':dates.get('closing') if isinstance(dates,dict) else '',
        'summary': f.get('body',''),
        'type':'No especificado',
      }
      normal=normalise(parsed,source,now)
      if normal: results.append(normal)
    return results


def collect_source(client,source):
    page = client.get(source['url'])
    if page is None: return None
    links=discover(page,source)
    results=[]
    for link in links:
        details=client.get(link)
        if details is None: continue
        entries=jsonld_jobs(details)
        parsed=from_jsonld(entries[0],link) if entries else from_html(details,link,source['id'])
        result=normalise(parsed,source)
        if result: results.append(result)
    return results

def update_data(today=None, client=None, destination=None):
    """Actualiza el índice sin aparentar que una fuente no disponible se revisó.

    `destination` permite pruebas aisladas. Fallos no borran anuncios recientes,
    pero se conservan con su fecha de verificación original.
    """
    now = today or datetime.now(timezone.utc)
    output = Path(destination) if destination else DATA_FILE
    previous = {}
    if output.exists():
        try: previous = json.loads(output.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError): pass
    prev_sources = {s.get('id'): s for s in previous.get('sources', []) if isinstance(s, dict)}
    client = client or PoliteClient()
    collected = []
    statuses = {}
    enriched = []
    configured_boards = boards(ROOT / 'agent/ats_boards.json')
    active_sources = SOURCES + [source_for_board(b) for b in configured_boards]
    for source in active_sources:
        sid = source['id']
        previous_source = prev_sources.get(sid, {})
        item = dict(source)
        item['last_success'] = previous_source.get('last_success')
        if source['collection'] not in ('crawler', 'api', 'ats'):
            item['status'] = 'directorio'
            enriched.append(item)
            statuses[sid] = item['status']
            continue
        item['last_attempt'] = now.isoformat(timespec='seconds').replace('+00:00', 'Z')
        if sid == 'reliefweb' and not os.getenv('RELIEFWEB_APPNAME', '').strip():
            current = None
            item['status'] = 'requiere_configuracion'
        else:
            log.info('Consultando %s', source['name'])
            try:
                current = (collect_reliefweb(source, now) if source['collection'] == 'api' else
                           collect_ats(source, now, normalise) if source['collection'] == 'ats' else
                           collect_source(client, source))
            except Exception as exc:
                log.exception('Error leyendo %s: %s', sid, exc)
                current = None
            item['status'] = 'no_disponible' if current is None else ('sin_resultados' if not current else 'actualizada')
        if current is None:
            # Recuperar sólo ofertas indexadas recientemente. Jamás cambiar verified_at.
            for job in expand_reposts(previous.get('jobs', [])):
                if not isinstance(job, dict) or job.get('source') != sid:
                    continue
                checked = job.get('verified_at')
                try:
                    age = now - datetime.fromisoformat(checked.replace('Z', '+00:00'))
                except (ValueError, TypeError, AttributeError):
                    continue
                if timedelta(0) <= age <= timedelta(days=7) and valid_and_recent(job, now):
                    collected.append(job)
        else:
            item['last_success'] = item['last_attempt']
            collected.extend(job for job in current if valid_and_recent(job, now))
        enriched.append(item)
        statuses[sid] = item['status']
    unique = {}
    for job in collected:
        if not isinstance(job, dict) or not job.get('id') or not url_clean(job.get('url', '')):
            continue
        if not valid_and_recent(job, now):
            continue
        unique[job['id']] = job
    rows = merge_exact_reposts(unique.values())
    for job in rows:
        if not isinstance(job.get('maps'), dict):
            job['maps'] = map_metadata(job.get('company'),job.get('location'),job.get('modality'),job.get('address'))
    try:
        from .google_places import enrich_jobs
        enrich_jobs(rows, previous.get('jobs', []))
    except (ValueError, TypeError, OSError) as exc:
        log.warning('Enriquecimiento de ubicaciones omitido: %s', exc)
    decorate(rows)
    apply_verification(rows, load_registry(ROOT / 'agent/verified_employers.json'), now.date())
    # Consejos personalizados y auditables; nunca reescribe requisitos de las fuentes.
    from .career_advisor import enrich as enrich_career
    enrich_career(rows)
    rows.sort(key=lambda j: (j.get('published_at') or '', j.get('verified_at') or ''), reverse=True)
    for source in enriched:
        source['jobs_count'] = sum(1 for j in rows if j.get('source') == source['id'] or any(a.get('source') == source['id'] for a in j.get('also_on', [])))
    payload = {
        'schema_version': 3,
        'generated_at': now.isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'jobs': rows,
        'sources': enriched,
        'facets': build_facets(rows),
        'metadata': {
            'disclaimer': 'Ofertas de terceros; comprobá la vigencia y postulá en la fuente original.',
            'collection_status': statuses,
            'indexed_count': len(rows),
            'methodology': 'Solo ofertas individuales. Estrellas = claridad del anuncio, no prestigio ni identidad confirmada del empleador. La ubicación puede ser aproximada.',
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    log.info('Indexadas %d ofertas; fuentes: %s', len(rows), statuses)
    return payload

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
    update_data()
