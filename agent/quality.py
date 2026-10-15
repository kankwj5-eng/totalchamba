"""Calidad editorial del índice: límites, vigencia, duplicados y procedencia.

No combina anuncios de empresas desconocidas ni deduce salarios o condiciones.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

UNKNOWN_COMPANIES = {'', 'empresa no especificada', 'confidencial', 'empresa confidencial', 'anónimo', 'anonimo'}


def comparable(value):
    txt = unicodedata.normalize('NFKD', str(value or '').lower())
    txt = ''.join(ch for ch in txt if not unicodedata.combining(ch))
    return ' '.join(re.findall(r'[a-z0-9]+', txt))


def valid_date(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
    except ValueError:
        return None


def valid_and_recent(job, now, max_age_days=45):
    """No ofrecer como actual una plaza publicada hace varios meses.

    Se admiten ofertas sin fecha si su verificación fue reciente. Fecha de
    publicación futura o fecha de cierre anterior a hoy: descartadas.
    """
    today = now.date()
    published = valid_date(job.get('published_at'))
    checked = valid_date(job.get('verified_at'))
    closing = valid_date(job.get('expires'))
    if closing and closing < today:
        return False
    if published and published > today + timedelta(days=1):
        return False
    if published and published < today - timedelta(days=max_age_days):
        return False
    if not published and (not checked or checked < today - timedelta(days=7)):
        return False
    return True


def merge_exact_reposts(jobs):
    """Agrupa republicaciones evidentes sin perder la URL de cada fuente.

    Sólo si coinciden título, *empresa identificada* y departamento concreto;
    títulos genéricos sin empresa permanecen separados. Una misma empresa puede
    tener varias plazas idénticas dentro de un portal: no se agrupan entre sí.
    """
    by_id = {}
    for item in jobs:
        if not isinstance(item, dict) or not item.get('id'):
            continue
        by_id[item['id']] = dict(item)
    groups = {}
    for item in by_id.values():
        company = comparable(item.get('company'))
        title = comparable(item.get('title'))
        dep = comparable(item.get('department'))
        if company in UNKNOWN_COMPANIES or dep in ('', 'nicaragua') or len(title) < 8:
            continue
        key = (company, title, dep)
        groups.setdefault(key, []).append(item)

    excluded = set()
    for group in groups.values():
        if len({j['source'] for j in group}) < 2:
            continue
        # Conservar todas las plazas del portal principal si hay varias iguales.
        members = sorted(group, key=lambda j: (j.get('verified_at') or '', j.get('published_at') or ''), reverse=True)
        source_seen = set()
        selected = []
        for item in members:
            if item['source'] not in source_seen:
                selected.append(item)
                source_seen.add(item['source'])
        if len(selected) < 2:
            continue
        main = selected[0]
        alternates = [{'source': j['source'], 'url': j['url'], 'verified_at': j.get('verified_at'), 'published_at': j.get('published_at')} for j in selected[1:]]
        main['also_on'] = alternates
        # Discard selected secondary records, but never silently discard multiple
        # distinct postings on the same platform.
        excluded.update(j['id'] for j in selected[1:])
    return [item for item in by_id.values() if item['id'] not in excluded]


def expand_reposts(jobs):
    """Restaurar enlaces alternativos desde el JSON previo antes de fusionar.

    Cada enlace mantiene su propia marca de tiempo para no ocultar caducidades.
    """
    expanded = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        primary = dict(job)
        primary.pop('also_on', None)
        expanded.append(primary)
        for alternate in job.get('also_on', []):
            if not isinstance(alternate, dict) or not alternate.get('source') or not alternate.get('url'):
                continue
            child = dict(primary)
            child['source'] = alternate['source']
            child['url'] = alternate['url']
            child['id'] = job_id(alternate['url'])
            child['verified_at'] = alternate.get('verified_at') or primary.get('verified_at')
            child['published_at'] = alternate.get('published_at') or primary.get('published_at')
            expanded.append(child)
    return expanded


def build_facets(jobs):
    facets = {}
    for key in ('department', 'category', 'modality', 'source'):
        values = {}
        for item in jobs:
            value = item.get(key) or 'No especificado'
            values[value] = values.get(value, 0) + 1
        facets[key] = dict(sorted(values.items(), key=lambda kv: (-kv[1], comparable(kv[0]))))
    return facets


def job_id(link):
    return hashlib.sha256(link.encode('utf-8')).hexdigest()[:16]
