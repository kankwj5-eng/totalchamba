"""Pruebas del índice como producto: trazabilidad, limpieza y caducidad."""
from datetime import datetime, timedelta, timezone
import json
from agent.quality import valid_and_recent, merge_exact_reposts, expand_reposts, build_facets
from agent.collector import normalise, jsonld_jobs, update_data
from agent.sources import SOURCES
from bs4 import BeautifulSoup

NOW = datetime(2026, 10, 14, 22, 30, tzinfo=timezone.utc)
E = next(x for x in SOURCES if x['id'] == 'encuentra24')
T = next(x for x in SOURCES if x['id'] == 'tecoloco')


def make_job(source, job_url, title='Gerente de almacén', company='Empresa Real', location='Estelí'):
    return normalise({'url':job_url, 'title':title, 'company': company,
                      'location':location,'published_at':'2026-10-12'},source,NOW)


def test_automatic_category_and_explicit_date():
    assert make_job(E,'https://www.encuentra24.com/111')['category'] == 'Logística'
    j = make_job(E,'https://www.encuentra24.com/222')
    assert valid_and_recent(j,NOW)
    assert not valid_and_recent(j,NOW+timedelta(days=70))
    j['expires']='2026-10-13'
    assert not valid_and_recent(j,NOW)


def test_exact_duplicate_merges_but_preserves_other_urls():
    a = make_job(E,'https://www.encuentra24.com/111')
    b = make_job(T,'https://www.tecoloco.com.ni/111')
    merged=merge_exact_reposts([a,b])
    assert len(merged)==1
    assert len(merged[0]['also_on'])==1
    assert {merged[0]['url'],merged[0]['also_on'][0]['url']}=={a['url'],b['url']}
    rebuilt=expand_reposts(merged)
    assert {j['url'] for j in rebuilt}=={a['url'],b['url']}
    assert len(merge_exact_reposts(rebuilt))==1


def test_unknown_company_never_collapses_and_different_cities():
    a = make_job(E,'https://www.encuentra24.com/a',company='Confidencial')
    b = make_job(T,'https://www.tecoloco.com.ni/b',company='Confidencial')
    c = make_job(T,'https://www.tecoloco.com.ni/c',location='Managua')
    assert len(merge_exact_reposts([a,b,c]))==3


def test_jobposting_accepts_schema_org_type_uri():
    soup=BeautifulSoup('<script type="application/ld+json">'+json.dumps({'@type':'https://schema.org/JobPosting','title':'Técnico'})+'</script>','html.parser')
    assert len(jsonld_jobs(soup))==1


def test_contact_removed_from_summary():
    j = normalise({'url':'https://www.encuentra24.com/oferta', 'title':'Auxiliar general',
                   'summary':'Enviar hoja a correo@empresa.com o llamar +505 8888 1111'},E,NOW)
    assert 'correo@empresa.com' not in j['summary']
    assert '8888 1111' not in j['summary']


def test_facets_count_index_not_external_platforms():
    a=make_job(E,'https://www.encuentra24.com/a');b=make_job(T,'https://www.tecoloco.com.ni/b',location='Managua')
    f=build_facets([a,b])
    assert f['department']=={'Estelí':1,'Managua':1}


def test_missing_reliefweb_credentials_marked_not_connected(tmp_path,monkeypatch):
    monkeypatch.delenv('RELIEFWEB_APPNAME',raising=False)
    from agent import collector
    monkeypatch.setattr(collector,'collect_source',lambda *a,**k:None)
    result=update_data(today=NOW, destination=tmp_path/'jobs.json')
    assert next(s for s in result['sources'] if s['id']=='reliefweb')['status']=='requiere_configuracion'
    assert result['schema_version']==3
    assert result['jobs']==[]


def test_on_failure_preserve_at_most_7_days_not_reverify(tmp_path,monkeypatch):
    from agent import collector
    monkeypatch.setattr(collector,'collect_source',lambda *a,**k:None)
    old=make_job(E,'https://www.encuentra24.com/oferta')
    path=tmp_path/'jobs.json'
    path.write_text(json.dumps({'jobs':[old]}),encoding='utf-8')
    result=update_data(today=NOW+timedelta(days=2),destination=path)
    assert len(result['jobs'])==1
    assert result['jobs'][0]['verified_at']==old['verified_at']
    result=update_data(today=NOW+timedelta(days=8),destination=path)
    assert not result['jobs']
