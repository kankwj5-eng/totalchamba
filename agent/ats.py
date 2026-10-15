"""Conectores opt-in Greenhouse y Lever, únicamente APIs de vacantes públicas.

No se rastrean empresas ni se adivinan board tokens. Cada board se declara
manualmente en `agent/ats_boards.json`, tras comprobar entidad y condiciones.
"""
from __future__ import annotations
import json
import logging
import re
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from .geo import fold

log = logging.getLogger('chambani.ats')
TOKEN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{1,79}$')


def boards(path):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    result = []
    seen = set()
    for x in data:
        if not isinstance(x, dict) or x.get('provider') not in ('greenhouse', 'lever', 'ashby', 'smartrecruiters'):
            continue
        token = x.get('board', '')
        if not isinstance(token, str) or not TOKEN.fullmatch(token) or '..' in token:
            continue
        name = str(x.get('company') or '').strip()[:95]
        if len(name) < 2 or (x['provider'], token) in seen or x.get('enabled') is not True:
            continue
        seen.add((x['provider'], token))
        places = x.get('locations', [])
        if not isinstance(places,list): places=[]
        places=[v.strip()[:90] for v in places[:6] if isinstance(v,str) and 'nicaragua' in fold(v) and len(v.strip())>=8]
        result.append({'provider': x['provider'], 'board': token, 'company': name, 'locations': places,
                       'id': 'ats-' + x['provider'] + '-' + token.lower(),
                       'name': name + ' · ' + x['provider'].title()})
    return result[:35]


def source_for_board(board):
    provider, token = board['provider'], board['board']
    homes = {'greenhouse':'https://job-boards.greenhouse.io/','lever':'https://jobs.lever.co/',
             'ashby':'https://jobs.ashbyhq.com/','smartrecruiters':'https://jobs.smartrecruiters.com/'}
    hostnames = {'greenhouse':['boards.greenhouse.io','job-boards.greenhouse.io'],
                 'lever':['jobs.lever.co'],'ashby':['jobs.ashbyhq.com'],
                 'smartrecruiters':['jobs.smartrecruiters.com']}
    home = homes[provider] + token
    hosts = hostnames[provider]
    return {'id': board['id'], 'name': board['name'], 'url': home, 'kind': 'empresa',
            'collection': 'ats', 'focus': 'Ofertas publicadas en la web de la empresa',
            'color': '#a8dfd2', 'allowed_hosts': hosts, 'company': board['company'],
            'board': token, 'provider': provider, 'locations': board.get('locations', [])}


def likely_ni(text):
    """Filtro conservador: solo ubicación NI explícita, no países homónimos.

    Un puesto remoto que dice simplemente `Remote` NO es elegible por defecto.
    """
    t = fold(text)
    if not t: return False
    # Los anuncios multinacionales pueden incluir Nicaragua y otros países.
    if 'nicaragua' in t: return True
    if any(x in t for x in ('spain', 'espana', 'guatemala', 'costa rica', 'mexico', 'colombia')):
        return False
    return any(x in t for x in ('nicaragua', 'managua', 'esteli', 'matagalpa', 'jinotega',
                                'chinandega', 'masaya', 'nueva segovia', 'chontales',
                                'rivas, ni', 'leon, ni', 'granada, ni', 'latin america', 'latam', 'worldwide'))


def fetch_json(url, opener=urlopen):
    if not url.startswith(('https://boards-api.greenhouse.io/v1/boards/',
                          'https://api.lever.co/v0/postings/')):
        raise ValueError('Host de API no permitido')
    req = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'ChambaNI/3.0 (indexador ATS público)'})
    with opener(req, timeout=18) as response:
        if response.status != 200 or 'json' not in response.headers.get('Content-Type', '').lower():
            raise ValueError('Respuesta no JSON')
        return json.loads(response.read(3_000_000))


def parse_greenhouse(payload, source):
    rows = []
    for obj in payload.get('jobs', []) if isinstance(payload, dict) else []:
        if not isinstance(obj, dict) or not likely_ni(str((obj.get('location') or {}).get('name', ''))):
            continue
        url = obj.get('absolute_url', '')
        rows.append({'title': obj.get('title'), 'url': url, 'company': source['company'],
                     'location': (obj.get('location') or {}).get('name', ''),
                     'last_modified_at': obj.get('updated_at'),  # Fecha de edición ≠ publicación
                     'summary': obj.get('content') or '',
                     'modality': 'Remoto' if 'remote' in fold((obj.get('location') or {}).get('name')) else ''})
    return rows


def parse_lever(payload, source):
    rows = []
    for obj in payload if isinstance(payload, list) else []:
        if not isinstance(obj, dict):
            continue
        cats = obj.get('categories') or {}
        location = str(cats.get('location') or '')
        if not likely_ni(location):
            continue
        workplace = {'remote':'Remoto', 'hybrid':'Híbrido', 'on-site':'Presencial'}.get(str(obj.get('workplaceType') or '').lower(), '')
        salary = obj.get('salaryRange') or {}
        salary_text = obj.get('salaryDescriptionPlain') or ''
        if not salary_text and isinstance(salary,dict) and salary.get('currency') and salary.get('min') is not None and salary.get('max') is not None:
            salary_text = f"{salary['currency']} {salary['min']}-{salary['max']} / {salary.get('interval','periodo no indicado')}"
        rows.append({'title': obj.get('text'), 'url': obj.get('hostedUrl'),
                     'company': source['company'], 'location': location,
                     'summary': obj.get('descriptionPlain') or obj.get('openingPlain') or '', 'salary': salary_text,
                     'type': cats.get('commitment') or '',
                     'modality': workplace or ('Remoto' if 'remote' in fold(location) else '')})
    return rows


def collect_ats(source, now, normalise, fetcher=fetch_json):
    from .quality import valid_and_recent
    if source['provider'] in ('ashby','smartrecruiters'):
        from .ats_extra import collect_extra
        return collect_extra(source, now, normalise)
    if source['provider'] == 'greenhouse':
        url = f"https://boards-api.greenhouse.io/v1/boards/{source['board']}/jobs?" + urlencode({'content':'true'})
        parsed = parse_greenhouse(fetcher(url), source)
    else:
        parameters={'mode':'json', 'limit':'100'}
        if source.get('locations'):
            parameters['location']=source['locations']
        url = f"https://api.lever.co/v0/postings/{source['board']}?" + urlencode(parameters, doseq=True)
        parsed = parse_lever(fetcher(url), source)
    jobs = [normalise(item, source, now) for item in parsed[:100]]
    return [item for item in jobs if item and valid_and_recent(item, now)]
