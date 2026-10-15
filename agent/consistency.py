"""Validación de publicación del índice. Nunca reemplazar el último índice usable por un fallo total."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit


def validate_index(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    jobs = data.get("jobs")
    sources = data.get("sources")
    meta = data.get("metadata")
    if not isinstance(jobs, list) or not isinstance(sources, list) or not isinstance(meta, dict):
        raise ValueError("Índice inválido: jobs, sources y metadata son obligatorios")
    ids = set()
    for n, item in enumerate(jobs):
        if not isinstance(item, dict):
            errors.append(f"Entrada {n}: no es objeto")
            continue
        ident, url = item.get("id"), item.get("url")
        p = urlsplit(str(url or ""))
        if not ident or ident in ids:
            errors.append(f"Entrada {n}: ID ausente o repetido")
        ids.add(ident)
        if p.scheme != "https" or not p.hostname or p.username or p.password:
            errors.append(f"Entrada {n}: enlace original inseguro o ausente")
        if not item.get("title") or not item.get("source"):
            errors.append(f"Entrada {n}: faltan título o fuente")
        if item.get("employer_verified") and not item.get("employer_evidence"):
            errors.append(f"Entrada {n}: identidad verificada sin evidencia")
    status = meta.get("collection_status", {})
    if not isinstance(status, dict):
        errors.append("Estado de fuentes ausente")
        status = {}
    # Si todas las integraciones fallaron/no están configuradas, no perder el índice anterior.
    attempted = {"actualizada", "sin_resultados"}
    if not jobs and not (attempted & set(status.values())):
        errors.append("Ninguna integración respondió correctamente; no publicar índice vacío")
    if errors:
        raise ValueError("; ".join(errors))
    return {"indexed": len(jobs), "sources": len(sources),
            "updated": sum(s in attempted for s in status.values())}


if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "public/data/jobs.json")
    print(json.dumps(validate_index(target), ensure_ascii=False))
