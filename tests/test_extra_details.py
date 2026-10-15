from datetime import datetime, timezone
from agent.collector import normalise, from_jsonld
from agent.sources import SOURCES

SOURCE=next(x for x in SOURCES if x['id']=='encuentra24')
NOW=datetime(2026,10,14,tzinfo=timezone.utc)
URL='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/trabajo/123456'

def test_structured_details_preserved_without_invention():
    job=normalise({'url':URL,'title':'Operador de almacén','requirements':'Manejo de inventario', 'benefits':'Seguro de vida', 'experience':'2 años'},SOURCE,NOW)
    assert job['requirements']=='Manejo de inventario'
    assert job['benefits']=='Seguro de vida'
    assert job['experience']=='2 años'
    assert 'education' not in job


def test_optional_details_cleaned():
    job=normalise({'url':URL,'title':'Analista contable', 'requirements':'<b>Excel</b><script>ignorar()</script>'},SOURCE,NOW)
    assert 'Excel' in job['requirements']
    assert '<b>' not in job['requirements']


def test_jsonld_detail_fields():
    parsed=from_jsonld({'title':'Auxiliar de compras','jobBenefits':'Seguro médico', 'qualifications':'Excel', 'educationRequirements':'Secundaria', 'experienceRequirements':'1 año'},URL)
    assert parsed['requirements']=='Excel'
    assert parsed['benefits']=='Seguro médico'
    assert parsed['education']=='Secundaria'


def test_jsonld_salary_never_guesses_currency_or_period():
    from agent.collector import salary_from_jsonld
    value={'@type':'MonetaryAmount','currency':'USD','value':{'@type':'QuantitativeValue',
           'minValue':650,'maxValue':1000,'unitText':'MONTH'}}
    assert salary_from_jsonld(value)=='USD 650–1000 / mes'
    assert salary_from_jsonld({'currency':'NIO','value':12500})=='NIO 12500'
    assert salary_from_jsonld({'value':{'value':14000,'unitText':'MONTH'}})==''
    assert salary_from_jsonld({'currency':'USD','value':'contactar'})==''
    assert salary_from_jsonld(None)==''
    assert salary_from_jsonld({'currency':'USD','value':{'value':True}})==''


def test_jsonld_retains_salary_source_details():
    entry={'title':'Cajero','baseSalary':{'currency':'NIO','value':{'value':12000,'unitText':'MONTH'}}}
    parsed=from_jsonld(entry,URL)
    assert parsed['salary']=='NIO 12000 / mes'
    assert normalise(parsed,SOURCE,NOW)['salary']=='NIO 12000 / mes'


def test_employment_type_placeholder_not_published_as_real_contract():
    row=normalise({'url':URL,'title':'Vendedor de tienda','type':'Default'},SOURCE,NOW)
    assert row['type']=='No especificado'
    assert normalise({'url':URL,'title':'Vendedor','type':'Tiempo completo'},SOURCE,NOW)['type']=='Tiempo completo'
