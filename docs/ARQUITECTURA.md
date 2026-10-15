# Arquitectura y contratos de datos — versión 3

## Flujo

1. `agent/sources.py` mantiene el directorio (16 plataformas). Fuente con `collection=directorio` **solo da enlace**. `crawler` es experimental sujeto a robots y términos, `api` utiliza autorizaciones y `ats` significa un tablero Greenhouse/Lever configurado de forma explícita.
2. `agent/collector.py` limita el rastreo, valida URLs HTTPS, filtra anuncios no vigentes, oculta contactos en resumen y deduplica republicaciones evidentes.
3. `agent/ats.py` usa GET público a APIs de empleos, valida token y URL corporativa, y filtra puestos que podrían ser de Nicaragua. Nunca se activa por adivinar tokens.
4. `agent/geo.py` deriva `precision=region|address|none`; no transforma empresas en calles. `agent/google_places.py` opcional intenta un `place_id` bajo cuota, pero ello NO confirma ubicación laboral.
5. `agent/signals.py` calcula 1–5 estrellas por siete dimensiones de información de la oferta, nunca honestidad o satisfacción laboral. `agent/verification.py` etiqueta identidad revisada solo cuando se encuentra un registro editorial con prueba y caducidad válida.
6. `jobs.json` se publica como archivo estático; GitHub Actions actualiza cada 6 horas con desvíos de horario posibles. Vercel sirve la web. En el navegador se filtra y se conserva una lista local de favoritos. No cuentas ni candidatos almacenados.

## Contrato `public/data/jobs.json`

- `schema_version=3`.
- `generated_at`: cuándo se compiló el índice, **no** cuándo se publicó cada empleo.
- `jobs[]`: `id`, `title`, `company`, `location`, `department`, `address?`, `category`, `modality`, `type`, `salary?`, `summary`, `published_at?`, `last_modified_at?`, `expires?`, `source`, `url`, `verified_at`, `also_on?`, `maps`, `clarity`.
- `maps`: `precision=none` (remoto/sin datos), `region` (solo zona de publicación), `address` (dirección declarada). `query` construye el enlace de Google Maps; `place_id?` únicamente cuando existe una coincidencia opcional y no prueba que sea el sitio de trabajo.
- `clarity.score`: 0–100. Pesos: título 25, nombre de empresa 20, departamento 15, salario 15, modalidad 10, fecha 10, tipo de contrato 5. `clarity.stars`: 1–5 calculadas por bandas de veinte puntos. `present` y `missing` detallan las razones. `employer_verified` es **otra propiedad completamente distinta**, no una estrella. `employer_evidence` indica URL/fecha de la revisión, cuando existe.
- `sources[]`: fuente, estado, contador indexado y fechas de consulta; los 16 directorios no deben contar como 16 extractores activos.

## Estados de fuentes

`directorio`, `muestra_inicial`, `actualizada`, `sin_resultados`, `no_disponible`, `requiere_configuracion`. Ante fallos se retiene hasta 7 días el resultado anterior (sin cambiar su marca `verified_at`), con límites adicionales de antigüedad. Existen URLs de muestra con fechas explícitas y no se deben reactivar artificialmente.

## Límites y privacidad

- Sin scraping privado, bypass de CAPTCHA ni peticiones que el sitio prohíba. Cuando la fuente cambia de estructura, se deja el enlace directo en el directorio.
- Nunca incorporar la API Key de Google a `public/` ni a JavaScript.
- Google Places tiene restricciones de almacenamiento de contenido y atribución; se almacena solo `place_id`, con procedimiento presupuestario opcional. El frontend usa enlaces Maps URLs sin clave.
- Sin geolocalización del usuario ni uso de GPS. El proyecto declara `geolocation=()` en `Permissions-Policy`.
- Registro de verificación de empresas sujeto a control editorial y protección de ramas: el software no es una certificación empresarial ni un sistema antifraude infalible.
- Las pruebas automatizadas de flujos básicos no garantizan WCAG 2.2, revisión legal ni calidad de todos los anuncios reales.
