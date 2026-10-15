"""Señales explicables, reproducibles. Nunca califica honestidad empresarial.

Las estrellas reflejan solo cuánta información aporta la ficha laboral; no
miden reputación, seguridad, salario justo ni verificación de una empresa.
"""
from __future__ import annotations
from .quality import comparable, UNKNOWN_COMPANIES, valid_date

SIGNALS = (
    ('puesto', 'Puesto definido', 25, lambda j: len(comparable(j.get('title', ''))) >= 8),
    ('empresa', 'Nombre del empleador', 20, lambda j: comparable(j.get('company', '')) not in UNKNOWN_COMPANIES),
    ('zona', 'Departamento identificado', 15, lambda j: comparable(j.get('department', '')) not in {'', 'nicaragua', 'no especificado'}),
    ('salario', 'Remuneración publicada', 15, lambda j: bool(str(j.get('salary') or '').strip())),
    ('modalidad', 'Modalidad publicada', 10, lambda j: comparable(j.get('modality','')) not in {'', 'no especificada', 'no especificado'}),
    ('fecha', 'Fecha de publicación', 10, lambda j: valid_date(j.get('published_at')) is not None),
    ('contrato', 'Tipo de contrato', 5, lambda j: comparable(j.get('type', '')) not in {'', 'no especificado', 'no especificada'}),
)


def assess(job):
    """Puntos 0..100, estrellas 1..5, evidencia completa para explicarlo."""
    passed, missing, points = [], [], 0
    for key, label, weight, test in SIGNALS:
        if test(job):
            points += weight
            passed.append({'key': key, 'label': label, 'points': weight})
        else:
            missing.append({'key': key, 'label': label, 'points': weight})
    return {'score': points, 'stars': max(1, min(5, (points + 19) // 20)),
            'basis': 'claridad_del_anuncio', 'present': passed, 'missing': missing,
            'employer_verified': False, 'employer_evidence': None,
            'warning': 'No representa opiniones, seguridad ni reputación de la empresa'}


def decorate(jobs):
    for job in jobs:
        job['clarity'] = assess(job)
    return jobs
