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
