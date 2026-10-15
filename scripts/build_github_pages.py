"""Empaqueta TotalChanba para GitHub Pages bajo /totalchamba/.

No modifica public/: transforma exclusivamente los archivos copiados a _site.
El recolector de empleos permanece en GitHub Actions.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public"
DEST = ROOT / "_site"

def create_site():
    if not (SOURCE / "index.html").exists():
        raise FileNotFoundError("No existe public/index.html")
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SOURCE, DEST)
    (DEST / ".nojekyll").touch()

    for name in ("index.html", "herramientas.html"):
        path = DEST / name
        text = path.read_text(encoding="utf-8")
        # Las rutas internas de / corresponden al prefijo de Pages /totalchamba/.
        text = re.sub(r'(\b(?:href|src)=(["\']))/(?!/)', r'\1./', text)
        path.write_text(text, encoding="utf-8")

    for name in ("app.js", "toolkit.js", "bulletin.js"):
        path = DEST / "assets" / name
        js = path.read_text(encoding="utf-8")
        js = js.replace("fetch('/data/jobs.json'", "fetch('./data/jobs.json'")
        js = js.replace("fetch('/data/bulletin.json'", "fetch('./data/bulletin.json'")
        if name == "app.js":
            js = js.replace("/assets/occupations/", "./assets/occupations/")
            js = js.replace('href="/herramientas.html?', 'href="./herramientas.html?')
        path.write_text(js, encoding="utf-8")

    homepage = (DEST / "index.html").read_text(encoding="utf-8")
    jobs = (DEST / "assets" / "app.js").read_text(encoding="utf-8")
    assert 'href="./assets/styles.css"' in homepage
    assert "fetch('./data/jobs.json'" in jobs
    assert 'href="./herramientas.html?vacante=' in jobs
    assert (DEST / "data" / "jobs.json").exists()
    assert (DEST / "herramientas.html").exists()
    assert len(list((DEST / "assets" / "occupations").glob("*.webp"))) >= 10
    print("Vista pública GitHub Pages preparada:", DEST)

if __name__ == "__main__":
    create_site()
