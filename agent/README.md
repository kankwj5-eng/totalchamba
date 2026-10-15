# Agente de publicación de TotalChanba

Este proceso se ejecuta en **GitHub Actions**, no en el navegador ni en Vercel.
Lee información pública y estructurada de fuentes autorizadas, conserva el
enlace de cada anuncio y escribe `public/data/jobs.json`.

## Origen y estado

Cada fuente se muestra con un estado verificable:

- `actualizada`: respondió y aportó al menos una oferta válida.
- `sin_resultados`: respondió, pero no produjo ofertas válidas.
- `no_disponible`: no pudo revisarse; las ofertas anteriores pueden permanecer hasta siete días, sin falsificar la fecha de revisión.
- `requiere_configuracion`: falta una credencial aprobada o configuración.
- `directorio`: enlace externo para explorar; **no** integra sus ofertas al índice.

Las estrellas son una medida explicable de **información publicada en la
oferta**, no una calificación de reputación de la empresa.

## Conectores estructurados

`ats_boards.json` es una lista permitida de tableros empresariales previamente
identificados por su página pública. Proveedores soportados:

- **Lever**: `api.lever.co/v0/postings/{board}`
- **Greenhouse**: `boards-api.greenhouse.io/v1/boards/{board}/jobs`
- **Ashby**: `api.ashbyhq.com/posting-api/job-board/{board}`
- **SmartRecruiters**: `api.smartrecruiters.com/v1/companies/{board}/postings`

La inclusión en el archivo de configuración no verifica la identidad legal de
la empresa. Las tarjetas solamente obtienen la insignia de empresa revisada
cuando existe evidencia válida y específica en `verified_employers.json`.

El filtro de ubicación debe contener Nicaragua o una región elegible explícita.
Cuando las sedes aparecen junto a otros países se conserva la mención a
Nicaragua; no se asume que la sede física coincida con la sede del empleador.

## Frecuencia, validación y seguridad

`.github/workflows/actualizar-empleos.yml` consulta las fuentes cada seis
horas y al modificar código o configuración del agente. El archivo
`agent/consistency.py` evita publicar un índice vacío si fallaron **todas**
las integraciones, así como registros sin URL individual, IDs repetidos o
verificaciones empresariales sin evidencia.

Para validar localmente:

```sh
python -m pip install -r requirements.txt pytest
python -m pytest -q
python -m agent.consistency public/data/jobs.json
```

Las páginas protegidas o que prohiban el rastreo no se fuerzan ni se
esquivan. Nunca se inventan anuncios, ubicaciones exactas, salarios ni
reseñas. Los portales de directorio conservan un enlace de salida.

## Publicación

Vercel sirve únicamente `public/` como sitio estático. La actualización de
datos la hace GitHub, por lo que Vercel debe estar **conectado al repositorio**
para desplegar los nuevos índices tras cada commit del robot.
