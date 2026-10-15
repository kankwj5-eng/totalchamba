"""Verificador editorial de eventos y recursos: nunca convierte una nota en una vacante."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_KINDS = {'evento', 'formacion', 'convocatorias'}
ALLOWED_STATUSES = {'actividad_anunciada', 'directorio_oficial'}
OFFICIAL_DOMAINS = {'tecnacional.edu.ni', 'www.tecnacional.edu.ni',
                    'empleos.uno-ca.com', 'www.unicef.org', 'unicef.org'}

def check_bulletin(path: Path):
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict) or payload.get('schema_version') != 1:
        raise ValueError('Tablón: versión de esquema incorrecta')
    rows = payload.get('items')
    if not isinstance(rows, list) or len(rows) > 30:
        raise ValueError('Tablón: lista inválida o demasiado grande')
    ids=set()
    for entry in rows:
        if not isinstance(entry, dict):
            raise ValueError('Tablón: una entrada no es objeto')
        ident=entry.get('id')
        if not isinstance(ident,str) or not ident.strip() or ident in ids:
            raise ValueError('Tablón: identificador ausente o repetido')
        ids.add(ident)
        if entry.get('kind') not in ALLOWED_KINDS or entry.get('status') not in ALLOWED_STATUSES:
            raise ValueError('Tablón: tipo o estado desconocido')
        if not all(isinstance(entry.get(k),str) and entry[k].strip() for k in
                   ('title','summary','publisher','reviewed_on','url')):
            raise ValueError('Tablón: datos editoriales incompletos')
        link=urlsplit(entry['url'])
        if link.scheme!='https' or link.hostname not in OFFICIAL_DOMAINS or link.username or link.password:
            raise ValueError('Tablón: enlace no oficial')
        try:
            reviewed=date.fromisoformat(entry['reviewed_on'])
            if entry['kind']=='evento':
                start=date.fromisoformat(entry['starts_at'])
                expiry=date.fromisoformat(entry['expires_at'])
                if expiry < start:
                    raise ValueError('Tablón: evento expira antes de comenzar')
            else:
                if entry.get('starts_at') or entry.get('expires_at'):
                    raise ValueError('Tablón: recursos permanentes no tienen calendario')
        except (TypeError, KeyError, ValueError) as exc:
            raise ValueError('Tablón: fecha inválida') from exc
        if entry['kind']=='evento' and entry['status']!='actividad_anunciada':
            raise ValueError('Tablón: eventos deben estar identificados como anuncio')
        if entry['kind']!='evento' and entry['status']!='directorio_oficial':
            raise ValueError('Tablón: recursos no deben representarse como evento')
    return {'entries':len(rows),'events':sum(x['kind']=='evento' for x in rows)}


if __name__ == '__main__':
    print(check_bulletin(Path('public/data/bulletin.json')))
