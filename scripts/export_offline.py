"""Empaquetar la web REAL de TotalChanba para abrirla sin servidor en Android.

Genera dos HTML autónomos con CSS, JS, imágenes y datos del índice de
la versión actual. NO actualiza vacantes: congela un corte de datos.
"""
from __future__ import annotations
import base64
import json
import re
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public'
OUTPUT=ROOT/'offline-export'
SRC={
    'index.html': ('assets/styles.css',['assets/app.js','assets/bulletin.js']),
    'herramientas.html': ('assets/toolkit.css',['assets/toolkit.js'])
}
DATA={
    '/data/jobs.json':json.loads((PUBLIC/'data/jobs.json').read_text(encoding='utf-8')),
    '/data/bulletin.json':json.loads((PUBLIC/'data/bulletin.json').read_text(encoding='utf-8'))
}


def json_js(value):
    """Incrustación segura de JSON dentro de elementos script."""
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')


def prepare(name,css_file,js_files,images):
    page=(PUBLIC/name).read_text(encoding='utf-8')
    css=(PUBLIC/css_file).read_text(encoding='utf-8')
    page=re.sub(r'<link\s+[^>]*href="https://fonts\.googleapis\.com[^"]*"[^>]*>', '', page)
    page=re.sub(r'<link\s+[^>]*href="https://fonts\.gstatic\.com[^"]*"[^>]*>', '', page)
    page=re.sub(r'<link\s+[^>]*rel="preconnect"[^>]*>', '', page)
    page=re.sub(r'<link\s+[^>]*href="/assets/favicon\.svg"[^>]*>', '', page)
    # Original HTML has stylesheet tag, replace rather than add a competing copy.
    stylesheet=re.compile(r'<link\s+[^>]*href="/'+re.escape(css_file)+r'"[^>]*>')
    page,count=stylesheet.subn('<style>\n'+css+'\n</style>',page)
    if count!=1: raise ValueError('No se encontró la hoja de estilos de '+name)
    script_list=[]
    for js_file in js_files:
        pattern=re.compile(r'<script\s+[^>]*src="/'+re.escape(js_file)+r'"[^>]*></script>')
        page,count=pattern.subn('',page)
        if count!=1: raise ValueError('No se encontró script '+js_file)
        js=(PUBLIC/js_file).read_text(encoding='utf-8')
        if js_file.endswith('/app.js'):
            marker='const thumb='+chr(96)+'/assets/occupations/function () { [native code] }.webp'+chr(96)+';'
            if marker not in js: raise ValueError('No se encontró la miniatura para incrustar')
            js=js.replace(marker,"const thumb=window.__TC_IMAGES__[image]||'';")
            js=js.replace('href="/herramientas.html?vacante=', 'href="./herramientas.html?vacante=')
        # El HTML se usa en rutas file://, no hay rutas absolutas al servidor.
        js=js.replace("fetch('/data/jobs.json'", "fetch('./data/jobs.json'")
        js=js.replace("fetch('/data/bulletin.json'", "fetch('./data/bulletin.json'")
        script_list.append(js)
    page=page.replace('href="/herramientas.html','href="./herramientas.html')
    page=page.replace('href="/#','href="./index.html#')
    page=page.replace('href="/"','href="./index.html"')
    page=page.replace('src="/assets/','src="./assets/')
    subtitle='VERSIÓN LOCAL ACTUAL · solo para revisar. Datos guardados en el momento de exportar; no acredita vacantes activas.'
    banner='<div role="status" style="position:relative;z-index:50;padding:10px 15px;background:#fff4cd;color:#584419;font:700 12px/1.5 system-ui;text-align:center;">'+subtitle+'</div>'
    page=page.replace('<body>','<body>\n'+banner,1)
    # Paquetes de datos legibles como fetch Response sin conectar a internet.
    boot=(
      '<script>\nwindow.__TC_IMAGES__='+json_js(images if name=='index.html' else {})+';\n'
      'window.__TC_PREVIEW_DATA__='+json_js(DATA)+';\n'
      "window.fetch=async function(input){const path=String(input);"
      "const name=path.includes('jobs.json')?'/data/jobs.json':path.includes('bulletin.json')?'/data/bulletin.json':null;"
      "if(!name)throw new Error('Sin red en esta copia local');"
      "return new Response(JSON.stringify(window.__TC_PREVIEW_DATA__[name]),{status:200,headers:{'Content-Type':'application/json'}});};\n"
      '</script>\n'
    )
    for js in script_list:
        if '</script' in js.lower(): raise ValueError('Script con cierre HTML inesperado')
        boot+='<script>\n'+js+'\n</script>\n'
    if '</body>' not in page: raise ValueError('HTML sin cierre de body')
    return page.replace('</body>',boot+'</body>')


def run():
    OUTPUT.mkdir(exist_ok=True)
    images={}
    for path in sorted((PUBLIC/'assets/occupations').glob('*.webp')):
        images[path.stem]='data:image/webp;base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
    if len(images)<10: raise ValueError('Faltan fotografías temáticas')
    for page_name,(css,js) in SRC.items():
        (OUTPUT/page_name).write_text(prepare(page_name,css,js,images),encoding='utf-8')
    docs=(
      'TOTALCHANBA · EDICIÓN LOCAL, ANDROID\n\n'
      '1. Descomprimí el archivo ZIP completo.\n'
      '2. Abrí index.html con Chrome, Firefox, Edge o el editor Acode (Preview).\n'
      '3. Tocá «Consejos para conseguir este trabajo» para abrir herramientas.html.\n'
      '4. El CV se procesa en tu navegador. Guardá respaldos en una carpeta segura.\n\n'
      'Las ofertas y eventos corresponden a la fecha de generación del paquete;\n'
      'NO se actualizan sin crear otro paquete. Las postulaciones siempre se\n'
      'realizan en las plataformas originales. No se incluye un servidor web.\n'
      'Repositorio: https://github.com/kankwj5-eng/totalchamba\n'
    )
    (OUTPUT/'LEEME.txt').write_text(docs,encoding='utf-8')
    with zipfile.ZipFile(OUTPUT/'TotalChanba_actual_offline_Android.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for filename in ('index.html','herramientas.html','LEEME.txt'):
            z.write(OUTPUT/filename,arcname=filename)
    print('Exportación local:', [(x.name,x.stat().st_size) for x in OUTPUT.iterdir()])


if __name__=='__main__':
    run()
