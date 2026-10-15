"""Pruebas de los agentes de orientación y curación editorial."""
import copy
import json
from datetime import date
from pathlib import Path
import pytest
from agent.career_advisor import advise, enrich
from agent.bulletin import check_bulletin

ROOT=Path(__file__).resolve().parents[1]


def test_career_advisor_never_invents_requirements():
    original={
      'title':'Auxiliar contable de digitación',
      'category':'Administración','salary':None,
      'modality':'No especificada','address':None,
      'requirements':None
    }
    saved=copy.deepcopy(original)
    result=advise(original)
    assert original==saved
    assert result['basis']=='recomendaciones_generales_por_oficio'
    assert result['occupation_area']=='Administración'
    assert len(result['cv'])>=2
    assert any('salario' in q for q in result['ask_employer'])
    assert 'Requisitos publicados' not in result['published_fields']
    assert all('no son requisitos' not in line.lower() for line in result['cv'])


def test_career_advisor_per_role_and_actual_source_fields():
    job={'title':'Tornero', 'category':'Industria','requirements':'Lectura de planos',
         'salary':'C$ 12 000', 'modality':'Presencial','address':'Zona industrial'}
    enrich([job])
    guide=job['career_guide']
    assert guide['occupation_area']=='Industria'
    assert 'Requisitos publicados' in guide['published_fields']
    assert 'Salario publicado' in guide['published_fields']
    assert not any('salario' in question for question in guide['ask_employer'])
    assert job['requirements']=='Lectura de planos'


def test_unknown_profession_uses_general_safe_guide():
    a=advise({'title':'Otra plaza', 'category':'Otro'})
    assert a['focus'] and a['interview']
    assert a['basis']=='recomendaciones_generales_por_oficio'


def test_bulletin_real_entries_have_valid_links_and_dates():
    summary=check_bulletin(ROOT/'public/data/bulletin.json')
    assert summary['entries']>=3 and summary['events']>=1


def test_bulletin_rejects_fake_links(tmp_path):
    feed=json.loads((ROOT/'public/data/bulletin.json').read_text())
    feed['items'][0]['url']='https://empleos-falsos.example/'
    path=tmp_path/'bulletin.json'
    path.write_text(json.dumps(feed))
    with pytest.raises(ValueError,match='enlace no oficial'):
        check_bulletin(path)


def test_bulletin_rejects_invalid_event_dates(tmp_path):
    feed=json.loads((ROOT/'public/data/bulletin.json').read_text())
    event=next(x for x in feed['items'] if x['kind']=='evento')
    event['expires_at']='2026-10-01'
    file=tmp_path/'bulletin.json'
    file.write_text(json.dumps(feed))
    with pytest.raises(ValueError,match='fecha inválida'):
        check_bulletin(file)


def test_bulletin_rejects_unverified_status(tmp_path):
    feed=json.loads((ROOT/'public/data/bulletin.json').read_text())
    feed['items'][0]['status']='oferta_confirmada'
    file=tmp_path/'bulletin.json'
    file.write_text(json.dumps(feed))
    with pytest.raises(ValueError,match='estado desconocido'):
        check_bulletin(file)


def test_documented_skills_are_literal_and_provenanced():
    from agent.career_advisor import documented_terms
    original={'title':'Desarrollador Python', 'category':'Tecnología',
              'requirements':'Experiencia con Excel, SQL e inglés para reportes. Deseable Power BI.',
              'education':'Bachillerato aprobado', 'summary':'Se capacita en SAP.'}
    found=documented_terms(original)
    pairs={(x['label'],x['source']) for x in found}
    assert ('Excel','requisitos') in pairs
    assert ('SQL','requisitos') in pairs
    assert ('Inglés','requisitos') in pairs
    assert ('Power BI','requisitos') in pairs
    assert ('Bachillerato','formación') in pairs
    assert ('SAP','requisitos') not in pairs
    assert ('Python','requisitos') not in pairs
    assert all(x['source'] in ('requisitos','formación') for x in found)

def test_documented_skills_skip_substring_false_positive():
    from agent.career_advisor import documented_terms
    row={'requirements':'Estamos buscando un consultor de NoSQL para un equipo JavaScript.',
         'title':'JavaScript', 'summary':'Experiencia Excel'}
    found=documented_terms(row)
    names=[x['label'] for x in found]
    assert 'SQL' not in names
    assert 'Excel' not in names
    assert names==['JavaScript']

def test_documented_skills_omit_missing_requirements():
    from agent.career_advisor import documented_terms
    found=documented_terms({'requirements':None,'education':None,'title':'Excel Analyst'})
    assert found==[]

def test_advisor_exposes_documented_terms_separate_from_suggestions():
    job={'title':'Analista','category':'Administración','requirements':'Dominio de Excel y manejo de inventarios'}
    guide=advise(job)
    assert guide['documented_terms']
    assert guide['basis']=='recomendaciones_generales_por_oficio'
    assert job['requirements']=='Dominio de Excel y manejo de inventarios'
