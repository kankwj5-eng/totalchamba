import json
from datetime import date, datetime, timezone
from pathlib import Path
from agent.signals import assess,decorate
from agent.geo import map_metadata, maps_url
from agent.verification import evidence_for,apply_verification
from agent.ats import boards, source_for_board, parse_greenhouse, parse_lever, collect_ats
from agent.collector import normalise,from_jsonld

NOW=datetime(2026,10,14,22,0,tzinfo=timezone.utc)
SOURCE={'id':'ats-lever-ejemplo','url':'https://jobs.lever.co/ejemplo','collection':'ats', 'allowed_hosts':['jobs.lever.co'],'provider':'lever','board':'ejemplo','company':'Ejemplo','name':'Ejemplo'}


def test_clarity_is_reproducible_and_not_company_rating():
    j={'title':'Auxiliar de bodega','company':'Empresa XYZ','department':'Estelí', 'location':'Estelí', 'modality':'Presencial','published_at':'2026-10-14','type':'Tiempo completo','salary':'C$ 12000'}
    result=assess(j)
    assert result['score']==100 and result['stars']==5
    assert result['employer_verified'] is False
    j['salary']=None
    r=assess(j)
    assert r['score']==85 and r['stars']==5
    assert any(x['key']=='salario' for x in r['missing'])
    j['company']='Empresa no especificada'
    assert assess(j)['score']==65


def test_map_uses_only_declared_location_and_never_invents_employer_address():
    info=map_metadata('Banco Nacional','Estelí','Presencial')
    assert info['precision']=='region' and 'Banco' not in info['query']
    assert 'query=' in maps_url(info)
    address=map_metadata('Empresa X','Estelí','Presencial','Calle 2 norte')
    assert address['precision']=='address' and 'Calle+2+norte' in maps_url(address)
    assert map_metadata('Empresa X','Managua','Remoto')['precision']=='none'
    assert maps_url({'precision':'none'}) is None


def test_ats_opt_in_empty_and_strict(tmp_path):
    config=tmp_path/'boards.json'
    config.write_text(json.dumps([{'provider':'lever','board':'ejemplo','company':'Ejemplo','enabled':True},
                                  {'provider':'greenhouse','board':'otro','company':'X','enabled':False},
                                  {'provider':'lever','board':'https://site.invalid','company':'E','enabled':True}]))
    result=boards(config)
    assert len(result)==1 and result[0]['board']=='ejemplo'
    source=source_for_board(result[0])
    assert source['collection']=='ats'


def test_real_board_config_is_explicit_and_bounded():
    rows=boards(Path(__file__).resolve().parents[1]/'agent/ats_boards.json')
    assert sorted(x['board'] for x in rows)==sorted(['bluelightconsulting','freebalance.com','powerdigitalmarketing','hirehangar','DeliveryHero'])
    assert all(x['locations'] for x in rows)

def test_parse_ats_location_and_normalization():
    greenhouse={'jobs':[{'title':'Soporte Técnico','location':{'name':'Estelí, Nicaragua'},'absolute_url':'https://job-boards.greenhouse.io/ejemplo/jobs/123', 'updated_at':'2026-10-13'},
                        {'title':'Otras vacantes','location':{'name':'Madrid, España'},'absolute_url':'https://job-boards.greenhouse.io/ejemplo/jobs/124'}]}
    green={'id':'ats-greenhouse-ejemplo','company':'Ejemplo','collection':'ats','provider':'greenhouse','board':'ejemplo','url':'https://job-boards.greenhouse.io/ejemplo','allowed_hosts':['job-boards.greenhouse.io']}
    items=parse_greenhouse(greenhouse,green)
    assert len(items)==1
    result=normalise(items[0],green,NOW)
    assert result and result['department']=='Estelí'
    lever=[{'text':'Auxiliar administrativo','categories':{'location':'Managua, Nicaragua'},'workplaceType':'remote','salaryRange':{'currency':'USD','min':1000,'max':1600,'interval':'month'},'hostedUrl':'https://jobs.lever.co/ejemplo/abc'},
           {'text':'Auxiliar de ventas','categories':{'location':'New York'},'hostedUrl':'https://jobs.lever.co/ejemplo/def'}]
    parsed=parse_lever(lever,SOURCE)
    assert len(parsed)==1
    assert parsed[0]['modality']=='Remoto' and parsed[0]['salary'].startswith('USD 1000')
    assert normalise(parsed[0],SOURCE,NOW)
    assert normalise({**parsed[0],'url':'https://jobs.lever.co/otra/abc'},SOURCE,NOW) is None


def test_issuer_verification_expiring_and_only_with_evidence():
    job={'company':'Ejemplo','url':'https://jobs.lever.co/ejemplo/123','clarity':assess({})}
    record={'company':'Ejemplo','official_careers_url':'https://example.com/carreras',
            'proof_url':'https://example.com/carreras','listing_url_prefix':'https://jobs.lever.co/ejemplo/',
            'reviewed_on':'2026-10-11','reviewed_by':'Revisión editorial','evidence_type':'Sitio oficial'}
    apply_verification([job],[record],date(2026,10,14))
    assert job['clarity']['employer_verified'] is True
    assert evidence_for(job,[record],date(2027,8,1)) is None
    assert evidence_for({**job,'url':'https://otro.example/trabajo'},[record],date(2026,10,14)) is None


def test_jsonld_street_address_extracted_only_when_present():
    entry={'title':'Plaza','jobLocation':{'address':{'streetAddress':'De la iglesia 1 c al norte','addressLocality':'Estelí','addressCountry':'NI'}}}
    extracted=from_jsonld(entry,'https://example.com/job/1')
    assert extracted['address']=='De la iglesia 1 c al norte'
    assert 'Estelí' in extracted['location']

def test_regional_ats_is_not_mistaken_for_ni_job():
    from agent.ats import likely_ni
    assert not likely_ni("Remote, Latin America")
    assert not likely_ni("Worldwide")
    assert not likely_ni("LATAM")
    assert not likely_ni("Madrid, España")
    assert likely_ni("Remote, Nicaragua")
    assert likely_ni("Costa Rica, México, Nicaragua")
    assert likely_ni("Managua, Nicaragua")


def test_geocoding_does_not_invent_regional_nicaraguan_office():
    assert map_metadata("Empresa", "LATAM", "No especificada")['precision'] == 'none'
    assert map_metadata("Empresa", "Worldwide", "")['precision'] == 'none'
    assert map_metadata("Empresa", "Managua, Nicaragua", "Presencial")['precision'] == 'region'


def test_maps_do_not_duplicate_country_or_pin_remote_locations():
    assert map_metadata('Empresa','Managua, Nicaragua','Presencial')['query']=='Managua, Nicaragua'
    exact=map_metadata('Empresa','Estelí, Nicaragua','Presencial','Calle central')
    assert exact['query']=='Calle central, Estelí, Nicaragua'
    assert map_metadata('Empresa','Remote - Nicaragua','','')['precision']=='none'
