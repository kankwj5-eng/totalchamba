"""Enriquecimiento opcional con Google Places (New).

Solo se conserva `place_id` (permitido por políticas de Google), no se guardan
coordenadas, dirección ni nombre devueltos por la API. Ante ambigüedad, se omite.
Las llamadas cuestan dinero y requieren proyecto con facturación habilitada.
"""
from __future__ import annotations
import json
import os
from urllib.request import urlopen, Request
from urllib.error import URLError
from .geo import fold

ENDPOINT = 'https://places.googleapis.com/v1/places:searchText'


def unique_match(places, job):
    """Requiere dirección declarada, nombre de empresa y UNA coincidencia clara."""
    if job.get('maps', {}).get('precision') != 'address':
        return None
    company = fold(job.get('company', ''))
    if company in ('', 'empresa no especificada', 'confidencial'):
        return None
    candidates = []
    for place in places:
        name = fold((place.get('displayName') or {}).get('text', ''))
        address = fold(place.get('formattedAddress', ''))
        place_id = place.get('id')
        if not place_id or not name or not address or 'nicaragua' not in address:
            continue
        # Previene coincidencias con un comercio de nombre parecido.
        meaningful = [w for w in company.split() if len(w) >= 4 and w not in {'nicaragua', 'empresa', 'sociedad', 'anonima'}]
        if meaningful and not all(w in name.split() for w in meaningful[:3]):
            continue
        candidates.append(place_id)
    return candidates[0] if len(candidates) == 1 else None


def resolve_place_id(job, api_key, transport=urlopen):
    if job.get('maps', {}).get('precision') != 'address' or not api_key:
        return None
    body = json.dumps({'textQuery': (job['company'] + ', ' + job['maps']['query'])[:220],
                       'languageCode': 'es', 'regionCode': 'NI', 'pageSize': 5}).encode()
    request = Request(ENDPOINT, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress',
        'User-Agent': 'ChambaNI/3.0'})
    try:
        with transport(request, timeout=16) as response:
            if response.status != 200: return None
            payload = json.loads(response.read(256_000))
        return unique_match(payload.get('places') or [], job)
    except (URLError, OSError, ValueError, KeyError, TypeError):
        return None


def enrich_jobs(jobs, previous_jobs=None, resolver=resolve_place_id):
    """Opt-in y presupuesto bajo; no asume que un establecimiento sea sede laboral."""
    if os.getenv('CHAMBANI_GOOGLE_PLACES_ENABLED') != '1':
        return 0
    key = os.getenv('GOOGLE_PLACES_API_KEY', '')
    if not key: return 0
    limit = min(max(int(os.getenv('CHAMBANI_PLACES_MAX_CALLS', '8')), 0), 30)
    old = {}
    for item in previous_jobs or []:
        info = item.get('maps') or {}
        if info.get('place_id') and info.get('precision') == 'address':
            old[(item.get('url'), item.get('company'), item.get('location'), item.get('address'))] = info['place_id']
    calls = 0
    for job in jobs:
        info = job.get('maps') or {}
        if info.get('precision') != 'address': continue
        k = (job.get('url'), job.get('company'), job.get('location'), job.get('address'))
        matched = old.get(k)
        if not matched:
            if calls >= limit: break
            calls += 1
            matched = resolver(job, key)
        if matched:
            info['place_id'] = matched
            info['label'] = 'Coincidencia de establecimiento; comprobar sede laboral'
            info['evidence'] = 'google_places_match'
    return calls
