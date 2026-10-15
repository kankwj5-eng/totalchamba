"""Etiquetas de ubicación sin geocodificación especulativa.

Solo la dirección declarada por la vacante justifica una búsqueda por dirección.
Un Place ID no demuestra que allí se desempeñe el trabajo; únicamente
identifica un establecimiento potencialmente coincidente.
"""
from __future__ import annotations
import re
import unicodedata
from urllib.parse import urlencode

UNKNOWN = {'', 'empresa no especificada', 'confidencial', 'empresa confidencial', 'anónimo', 'anonimo'}


def fold(value):
    result = unicodedata.normalize('NFKD', str(value or '').lower())
    return ''.join(c for c in result if not unicodedata.combining(c))


def map_metadata(company, location, modality='', street_address=''):
    """Devuelve metadatos rastreables: region, búsqueda, dirección, o no disponible."""
    company, location, street_address = (str(v or '').strip()[:160] for v in (company, location, street_address))
    if 'remot' in fold(modality) or 'telecommut' in fold(modality) or 'remot' in fold(location):
        return {'precision': 'none', 'reason': 'Trabajo remoto: no se publica sede presencial'}
    if (not location or fold(location) in {'nicaragua', 'no especificada', 'por definir', 'sin especificar'}
            or any(v in fold(location) for v in ('latin america', 'latam', 'worldwide', 'global remote'))
            and 'nicaragua' not in fold(location)):
        return {'precision': 'none', 'reason': 'El anuncio no indica ciudad o dirección suficiente'}
    # Evitar cadenas como «Managua, Nicaragua, Nicaragua». La sede exacta
    # nunca se deduce de nombre comercial ni de una zona general.
    regional_query = location if fold(location).rstrip(' ,').endswith('nicaragua') else location + ', Nicaragua'
    if street_address:
        # Este texto viene exclusivamente de la ficha, no de un buscador.
        query = ', '.join((street_address, regional_query))
        return {'precision': 'address', 'query': query[:240], 'label': 'Dirección declarada en el anuncio', 'evidence': 'anuncio_original'}
    # No se consulta una sede física basándose solo en el nombre de una empresa:
    # muchas empresas tienen varias sucursales y otras son intermediarias.
    return {'precision': 'region', 'query': regional_query[:200], 'label': 'Zona aproximada, no sede de trabajo', 'evidence': 'anuncio_original'}


def maps_url(metadata):
    """Enlace gratuito a búsqueda de Google Maps; no requiere API key."""
    if not isinstance(metadata, dict) or metadata.get('precision') == 'none':
        return None
    query = metadata.get('query')
    if not isinstance(query, str) or not query.strip():
        return None
    params = {'api': '1', 'query': query[:240]}
    place_id = metadata.get('place_id')
    if isinstance(place_id, str) and re.fullmatch(r'[A-Za-z0-9_-]{8,200}', place_id):
        params['query_place_id'] = place_id
    return 'https://www.google.com/maps/search/?' + urlencode(params)
