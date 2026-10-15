import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from agent.collector import discover, normalise, jsonld_jobs, from_jsonld, department, category, PoliteClient
from agent.sources import SOURCES

DATE = datetime(2026,10,14,tzinfo=timezone.utc)
E = next(s for s in SOURCES if s['id']=='encuentra24')
T = next(s for s in SOURCES if s['id']=='tecoloco')

def test_encuentra_links_only_real_job_detail():
    soup = BeautifulSoup('''<a href="/nicaragua-es/empleos-ofertas-de-trabajos/tornero/33120722">Tornero</a>
    <a href="/nicaragua-es/empleos-ofertas-de-trabajos">Listado</a>
    <a href="/nicaragua-es/empleos-ofertas-de-trabajos/tornero/33120722?tracking=hi">Duplicado</a>''','html.parser')
    assert discover(soup,E)==['https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/tornero/33120722']

def test_tecoloco_links():
    soup=BeautifulSoup('<a href="/1100920/agente-de-ventas.aspx">Ver oferta</a><a href="/login.aspx">login</a>','html.parser')
    assert len(discover(soup,T))==1

def test_schema_jobposting():
    payload={'@context':'https://schema.org','@type':'JobPosting','title':'Analista de datos',
       'hiringOrganization':{'@type':'Organization','name':'Empresa X'},
       'jobLocation':{'address':{'addressLocality':'Estelí','addressCountry':'NI'}},
       'datePosted':'2026-10-10','validThrough':'2026-11-10'}
    soup=BeautifulSoup('<script type="application/ld+json">'+json.dumps(payload)+'</script>','html.parser')
    found=jsonld_jobs(soup)
    obj=normalise(from_jsonld(found[0],'https://www.tecoloco.com.ni/12345/analista.aspx'),T,DATE)
    assert obj['title']=='Analista de datos'
    assert obj['company']=='Empresa X'
    assert obj['department']=='Estelí'
    assert obj['category']=='Otros'

def test_reject_expired_job():
    assert normalise({'title':'Auxiliar de bodega','url':'https://www.encuentra24.com/a','expires':'2026-10-01'},E,DATE) is None

def test_reject_unsafe_url():
    assert normalise({'title':'Trabajo falso','url':'javascript:alert(1)'},E,DATE) is None
    assert normalise({'title':'Trabajo falso','url':'https://malo.invalid/job'},E,DATE) is None

def test_category_and_department():
    assert category('Conductor de transporte')=='Logística'
    assert department('Matagalpa, Nicaragua')=='Matagalpa'
    assert category('Técnico de mantenimiento')=='Industria'

def test_robots_fail_closed():
    client=PoliteClient()
    client.robots['https://example.com']=None
    assert not client.allowed('https://example.com/jobs')

def test_reliefweb_api_data_parsing(monkeypatch):
    monkeypatch.setenv('RELIEFWEB_APPNAME', 'test-approved-name')
    from agent import collector
    import io
    source=next(x for x in SOURCES if x['id']=='reliefweb')
    doc={'data':[{'fields':{
      'title':'Especialista de proyectos','url':'https://reliefweb.int/job/1234567',
      'source':[{'name':'Organización A'}], 'city':[{'name':'Managua'}],
      'date':{'created':'2026-10-12T00:00:00Z','closing':'2026-10-25T23:59:59Z'},
      'body':'Trabajar en seguimiento de proyectos.'
    }}]}
    class Response:
      status=200
      def __enter__(self): return self
      def __exit__(self,*a): pass
      def read(self,n): return json.dumps(doc).encode()
    monkeypatch.setattr(collector,'urlopen',lambda *args,**kwargs:Response())
    found=collector.collect_reliefweb(source,DATE)
    assert len(found)==1
    assert found[0]['company']=='Organización A'
    assert found[0]['department']=='Managua'
