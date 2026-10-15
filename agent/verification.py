"""Identidad empresarial: nunca se infiere a partir del nombre o una valoración.

Una verificación exige revisión editorial manual verificable y caduca a los 180
 días. La lista arranca vacía para evitar insignias falsas.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse
from .quality import comparable, valid_date


def load_registry(file: Path):
    try:
        entries = json.loads(file.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return entries if isinstance(entries, list) else []


def evidence_for(job, registry, current_date):
    company = comparable(job.get('company'))
    if not company or company in ('empresa no especificada', 'confidencial'):
        return None
    for row in registry:
        if not isinstance(row, dict) or comparable(row.get('company')) != company:
            continue
        reviewed = valid_date(row.get('reviewed_on'))
        if not reviewed or not 0 <= (current_date - reviewed).days <= 180:
            continue
        official = urlparse(str(row.get('official_careers_url', '')))
        proof = urlparse(str(row.get('proof_url', '')))
        if not official.hostname or official.scheme != 'https' or not proof.hostname or proof.scheme != 'https':
            continue
        # Requiere un tablero oficial identificado y la URL original coincide
        # con el mismo host verificado, o se revisa el subdominio exacto ATS.
        # Emparejar el identificador del tablero, nunca el dominio compartido
        # `jobs.lever.co` o `job-boards.greenhouse.io` por sí solo.
        prefix = str(row.get('listing_url_prefix', ''))
        original = str(job.get('url', ''))
        parsed_prefix = urlparse(prefix)
        parsed_original = urlparse(original)
        if (parsed_prefix.scheme != 'https' or not parsed_prefix.hostname or
            parsed_original.hostname != parsed_prefix.hostname or not
            parsed_prefix.path.endswith('/') or not original.startswith(prefix)):
            continue
        if not proof.hostname == official.hostname:
            continue
        if not row.get('reviewed_by') or not row.get('evidence_type'):
            continue
        return {'official_careers_url': row['official_careers_url'], 'proof_url': row['proof_url'],
                'reviewed_on': row['reviewed_on'], 'evidence_type': row['evidence_type']}
    return None


def apply_verification(jobs, registry, today):
    for job in jobs:
        proof = evidence_for(job, registry, today)
        clarity = job.get('clarity')
        if isinstance(clarity, dict):
            clarity['employer_verified'] = bool(proof)
            clarity['employer_evidence'] = proof
    return jobs
