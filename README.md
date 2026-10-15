# TotalChanba 5.0 🇳🇮 — Portal nacional de oportunidades

Portal web en español (HTML/CSS/JS estático), recolector Python y actualización mediante GitHub Actions. Despliegue preparado para Vercel. **No está desplegado**. Es un proyecto independiente de los portales que enlaza y no almacena CVs ni datos de candidatos.

> **Cobertura real y verificabilidad.** El paquete incluye **nueve publicaciones de muestra** consultadas originalmente el **14/10/2026**, y **16 fuentes en el directorio**, no nueve ofertas nuevamente comprobadas hoy. Al activar el recolector, las ofertas se reemplazan por lo efectivamente recopilado. El directorio NO significa recolección de todas sus fuentes. No hay actualmente empresas registradas como verificadas. Hay **dos tableros Lever identificados** para el próximo run (Bluelight Consulting y FreeBalance), pero todavía **no se ha comprobado en vivo el extractor del API** ni se han añadido ofertas de ellos al índice inicial.

## Nuevas mejoras visuales (5.0)

- Tarjetas grandes tipo expediente, con empresa anunciada, fotografía ilustrativa, datos principales, sección desplegable de condiciones, claridad y mapa.
- **12 fotografías originales generadas con IA**, almacenadas localmente en WebP (aprox. 23–67 KB) y seleccionadas automáticamente según puesto y sector. No son fotos del anunciante ni de sus instalaciones.
- Avatar de animalitos determinista por empresa, sin simular logo o identidad real. Preparado para incorporar recursos de marcas con permisos y procedencia verificada.
- Campos extra `requirements`, `benefits`, `experience` y `education` conservados solamente cuando son proporcionados por la fuente (por ejemplo, JobPosting/JSON-LD).
- Preguntas útiles y contextualizadas para candidatos según los datos que faltan: horario, salario, dirección o requisitos. Son sugerencias, no respuestas reales.
- Aviso visible cuando el índice es histórico/de muestra o está desactualizado. Nunca se presentan revisiones antiguas como nuevas.
- Reparado el diseño en pantallas pequeñas: las tarjetas ya no compiten con una barra lateral fija de 248 píxeles.
- **26 pruebas automatizadas de Python aprobadas**; verificación offline en Chromium para escritorio y móvil de búsqueda, imágenes, mapas, favoritos, filtros, estrellas y comparador. Esto no sustituye una auditoría de accesibilidad externa.

## Funciones heredadas

- Filtros por puesto, empresa, departamento, categoría, modalidad, fecha, origen, salario publicado, nivel de claridad (3/4/5 estrellas) y tipo de ubicación.
- **Estrellas transparentes**: 1–5 estrellas calculadas por información **publicada en el anuncio**, no por reputación del empleador. Cada anuncio explica sus siete criterios; pueden faltar salarios. No se inventan opiniones ni clasificaciones de empresas.
- **Comprobación empresarial**: código listo para registrar evidencia editorial con fecha y enlace oficial; ninguna ficha se autoverifica. Las revisiones caducan a los 180 días y requieren coincidencia del tablero autorizado y una prueba en el sitio oficial. Registro vacío por seguridad (`agent/verified_employers.json`).
- **Google Maps sin clave**: enlace de búsqueda por región si solo se conoce ciudad, por dirección si la vacante declara calle; sin mapa en remoto o cuando falta ubicación. Nunca se presenta una búsqueda como pin confirmado del trabajo.
- **Places API (New) opcional y de pago**: puede buscar `place_id` únicamente para direcciones declaradas, sin guardar resultados completos. Se desactiva por defecto, limitada a 8 consultas por corrida y 30 máximo, con secreto y revisión de costos. No garantiza sede laboral.
- **Greenhouse + Lever**: conectores Python a APIs públicas de tableros de empresas; se habilitan tras declarar tokens reales revisados en `agent/ats_boards.json`. Esta edición incluye **2 tableros reales hallados en portales públicos**: `bluelightconsulting` y `freebalance.com`, ambos con filtro de ciudades de Nicaragua. La captura de API todavía necesita su primer run conectado. Ofertas fuera de Nicaragua y enlaces con dominios no autorizados se filtran conservadoramente.
- **Radar por departamento**, comparación local de hasta tres vacantes con salario tal como aparece, favoritos en este navegador, búsqueda compartible por URL, modo lectura clara, navegación con teclado y preferencia `prefers-reduced-motion`.
- Mantenimiento anterior: deduplicación, frescura, metadata de fuentes, sanitización, directorio sin confusión con ofertas, recordatorio antifraudes y encabezados de seguridad en Vercel.

## Estructura

```text
agent/
  collector.py          # Índice y extracción HTML/ReliefWeb
  sources.py            # Portales y directorio
  ats.py                # Greenhouse/Lever; config ats_boards.json
  geo.py                # Clasificación regional/dirección/remoto; URLs Google Maps
  google_places.py      # Opt-in clave Places API
  signals.py            # 7 criterios reproducibles de claridad
  verification.py       # Evidencias de empleadores aprobadas manualmente
  verified_employers.json   # [] hasta que existan pruebas
  quality.py            # Caducidad, deduplicación, facetas
public/
  index.html
  assets/{app.js,styles.css,favicon.svg}
  assets/occupations/*.webp   # Doce escenas laborales IA; no son empresas
  data/jobs.json        # Muestra inicial fechada
.github/workflows/actualizar-empleos.yml
tests/
  test_*.py, browser_check.py, browser_v3.py
vercel.json
```

## Ejecutar y probar

```bash
python -m pip install -r requirements.txt pytest
python -m pytest -q
node --check public/assets/app.js
python -m http.server 4173 --directory public
```

Abrir `http://localhost:4173`. Para actualizar ofertas desde los conectores que funcionen:

```bash
python -m agent.collector
```

**Aviso:** Esto ejecuta consultas externas sujetas a robots/condiciones, y puede retirar las vacantes de muestra si ya no hay coincidencias indexadas. Para regenerar expresamente la muestra inicial, `python -m agent.seed`, **solo para demostración**; no reetiqueta nada como recién verificado. Para pruebas visuales opcionales: instalar Playwright y Chromium y ejecutar `python tests/browser_v3.py`; el script utiliza `/usr/bin/chromium` y carga HTML/CSS/JS/JSON en memoria. Las fotografías se cargan como URLs de datos solo en la prueba.

## Greenhouse/Lever opt-in

Para nuevas empresas, añadir a `agent/ats_boards.json` elementos como este **solo después de comprobar que el token corresponde a un tablero público real que publica vacantes aptas para Nicaragua**:

```json
[
  {"provider":"greenhouse", "board":"TOKEN_REAL", "company":"NOMBRE_REAL", "enabled":true},
  {"provider":"lever", "board":"TOKEN_REAL_2", "company":"EMPRESA_2", "enabled":true}
]
```

Son **ejemplos de configuración adicionales**, no empresas incorporadas. Los dos tableros reales ya se encuentran en el archivo de configuración; eso no equivale a haber recolectado empleos. No adivinar tokens ni sortear restricciones. Las ofertas remotas para LATAM pueden ser geográficamente elegibles, pero hay que comprobar si admiten Nicaragua.

## Google Places: únicamente opt-in presupuestado

- Sin claves ni pago: ya funciona **Buscar en Google Maps** (URL de búsqueda), con etiquetado de ubicación.
- Para coincidencias de establecimientos: crear proyecto Google Maps Platform con facturación, habilitar **Places API (New)**, revisar precios/cuotas y registrar `GOOGLE_PLACES_API_KEY` como secreto **solo en GitHub Actions**.
- Activar la variable del repositorio `CHAMBANI_GOOGLE_PLACES_ENABLED=1`, y `CHAMBANI_PLACES_MAX_CALLS=8` u otro límite (≤30). Mantener 0 hasta realizar la evaluación presupuestaria.
- Se solicita `places.id`, `places.displayName`, `places.formattedAddress` para encontrar coincidencias; el sistema únicamente conserva el Place ID, pero el precio depende del campo de mayor nivel solicitado. **No afirmar que los servicios de Places son gratis**.
- No se utiliza Nominatim público en lotes periódicos por sus límites y política de uso. No se añaden reseñas o calificaciones de Google: requerirían otro régimen de atribución, términos y permisos y no miden confiabilidad como empleador.

## Insignias de identidad empresarial

Archivo `agent/verified_employers.json` = `[]` inicialmente. Una revisión individual podría tener las claves `company`, `official_careers_url`, `proof_url`, `listing_url_prefix`, `reviewed_on` (`YYYY-MM-DD`), `reviewed_by`, `evidence_type`. Revisar manualmente que el dominio pertenece a la empresa, que referencia el mismo tablero de contrataciones y que el token del tablero es correcto; proteger la rama de GitHub para que no lo modifiquen terceros sin aprobación. La comprobación técnica de estos campos no reemplaza la revisión humana.

**Importante:** ni una identidad revisada ni 5 estrellas aseguran contratación, autenticidad de todas las vacantes o buenas condiciones. Para verificar el anuncio, ir al enlace original.

## Publicar

1. Importar todos los archivos de este paquete en el repositorio `https://github.com/kankwj5-eng/totalchamba` (actualmente vacío) **manteniendo la estructura de carpetas**. El nombre visible de la página es TotalChanba.
2. Importar a Vercel (framework Other; `outputDirectory=public` según `vercel.json`). El sitio será estático; no introducir claves secretas en el frontend.
3. Activar el workflow de GitHub Actions y revisar permisos `contents: write` o cambiar el mecanismo a un PR si existe protección de rama. Se ejecuta aproximadamente cada seis horas, sin garantía de puntualidad.
4. Revisar las condiciones y permisos de cada fuente y comprobar el primer run real antes de promocionar el portal como actualizado.

Pruebas offline de esta entrega: **26 casos de Python aprobados, JavaScript con sintaxis validada, e interacciones en móvil/escritorio comprobadas**. No equivalen a cobertura legal de las fuentes, geocodificación exacta general ni auditoría de accesibilidad WCAG completa.

Documentación adicional: `docs/INVESTIGACION.md`, `docs/ARQUITECTURA.md`, `docs/FUENTES.md`, `CHANGELOG.md`, `docs/DISEÑO_TOTALCHANBA.md`.
