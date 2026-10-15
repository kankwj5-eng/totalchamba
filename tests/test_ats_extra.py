"""Integraciones ATS: sólo ofertas públicas listadas y sedes aceptadas."""
from datetime import datetime,timezone
from agent.ats import source_for_board, likely_ni
from agent.ats_extra import nicaragua_location,parse_ashby,parse_smart,collect_extra
from agent.collector import normalise

NOW=datetime(2026,10,14,22,tzinfo=timezone.utc)
ASH=source_for_board({'provider':'ashby','board':'hirehangar','company':'Hire Hangar',
                      'id':'ats-ashby-hirehangar','name':'Hire Hangar','locations':[]})
SMART=source_for_board({'provider':'smartrecruiters','board':'DeliveryHero','company':'Delivery Hero',
                        'id':'ats-smartrecruiters-deliveryhero','name':'Delivery Hero','locations':[]})

def test_multicountry_ni_allowed_and_foreign_only_rejected():
    assert likely_ni('México; Costa Rica; Nicaragua - Managua')
    assert not likely_ni('Costa Rica; Mexico City')
    assert nicaragua_location({'country':'ni','city':'Managua'})=='Managua, Nicaragua'

def test_ashby_must_be_listed_and_explicitly_eligible():
    fake={'jobs':[{'title':'Analista','location':'Costa Rica - San José',
          'secondaryLocations':[{'location':'Nicaragua - Managua'}],
          'isListed':True,'jobUrl':'https://jobs.ashbyhq.com/hirehangar/abc-123',
          'descriptionPlain':'Trabajo de oficina','publishedAt':'2026-10-13',
          'compensation':{'compensationTierSummary':'USD $500-700 / mes'},'workplaceType':'Remote'},
         {'title':'Privada','location':'Nicaragua - Managua','isListed':False,
          'jobUrl':'https://jobs.ashbyhq.com/hirehangar/oculta'},
         {'title':'Otro país','location':'México',
          'jobUrl':'https://jobs.ashbyhq.com/hirehangar/mexico'}]}
    rows=parse_ashby(fake,ASH)
    assert len(rows)==1 and rows[0]['modality']=='Remoto'
    assert '500' in rows[0]['salary']
    assert normalise(rows[0],ASH,NOW)
    assert normalise({**rows[0],'url':'https://jobs.ashbyhq.com/otra/abc'},ASH,NOW) is None

def test_smart_requires_company_host_original_url_and_ni_location():
    item={'id':'744000124016918','name':'Auxiliar','location':{'country':'ni','city':'Managua'}}
    detail={'postingUrl':'https://jobs.smartrecruiters.com/DeliveryHero/744000124016918',
            'name':'Auxiliar','location':{'country':'NI','city':'Managua'},
            'jobAd':{'sections':{'qualifications':{'text':'Saber organizar inventario'}}}}
    row=parse_smart(item,detail,SMART)
    assert row['requirements']=='Saber organizar inventario'
    assert normalise(row,SMART,NOW)
    assert parse_smart(item,{'name':'Auxiliar'},SMART) is None
    assert normalise({**row,'url':'https://jobs.smartrecruiters.com/OtraEmpresa/744000124016918'},SMART,NOW) is None

def test_new_ats_collectors_with_mocked_public_apis():
    ash={'jobs':[{'title':'Recruitment Assistant','location':'Nicaragua - Managua',
          'isListed':True,'jobUrl':'https://jobs.ashbyhq.com/hirehangar/1234'}]}
    def ash_fetch(url):
        assert 'posting-api/job-board/hirehangar' in url
        return ash
    assert len(collect_extra(ASH,NOW,normalise,fetcher=ash_fetch))==1
    def smart_fetch(url):
        if '/postings?' in url:
            assert 'country=ni' in url
            return {'content':[{'id':'744000124016918','name':'Auxiliar',
                                'location':{'country':'NI','city':'Managua'}}]}
        return {'name':'Auxiliar','postingUrl':'https://jobs.smartrecruiters.com/DeliveryHero/744000124016918',
                'location':{'country':'NI','city':'Managua'}}
    assert len(collect_extra(SMART,NOW,normalise,fetcher=smart_fetch))==1
