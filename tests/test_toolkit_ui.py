"""Contrato del DOM entre la web estática y sus herramientas de candidatura."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def test_main_site_tools_entry_points_exist():
    html=(ROOT/'public/index.html').read_text(encoding='utf-8')
    js=(ROOT/'public/assets/app.js').read_text(encoding='utf-8')
    assert '/herramientas.html' in html
    assert '/herramientas.html?vacante=' in js
    assert 'data-bulletin-filter="evento"' in html
    assert 'id="bulletin-grid"' in html
    assert 'id="export-saved"' in html


def test_toolkit_document_has_all_bound_ids():
    page=(ROOT/'public/herramientas.html').read_text(encoding='utf-8')
    code=(ROOT/'public/assets/toolkit.js').read_text(encoding='utf-8')
    ids=set(re.findall(r'\bid="([^"]+)"',page))
    references=set(re.findall(r"\$\(['\"]([a-z0-9-]+)['\"]\)",code))
    assert not references-ids, 'Faltan controles HTML: '+str(references-ids)
    for section in ('guia','cv','entrevista','carta','plan','animo'):
        assert 'id="panel-'+section+'"' in page
        assert 'data-tab="'+section+'"' in page


def test_forms_are_local_and_printable():
    html=(ROOT/'public/herramientas.html').read_text(encoding='utf-8')
    js=(ROOT/'public/assets/toolkit.js').read_text(encoding='utf-8')
    css=(ROOT/'public/assets/toolkit.css').read_text(encoding='utf-8')
    assert 'action="http' not in html
    assert 'localStorage' in js and 'window.print()' in js
    assert 'print-cv' in css and '@media print' in css
    assert '<script src="/assets/toolkit.js" defer></script>' in html
    assert 'textContent' in js
    assert not re.search(r'\beval\s*\(',js)


def test_bulletin_has_no_live_event_fabrication():
    html=(ROOT/'public/index.html').read_text(encoding='utf-8')
    code=(ROOT/'public/assets/bulletin.js').read_text(encoding='utf-8')
    assert 'no se publican ferias' in html.lower()
    assert "item.expires_at<localDate()" in code
    assert "official.has(u.hostname)" in code
