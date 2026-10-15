# TotalChanba 5.0 🇳🇮 — Portal nacional de oportunidades

Portal web en español (HTML/CSS/JS estático), recolector Python y actualización mediante GitHub Actions. Despliegue preparado para Vercel. **No está desplegado**. Es un proyecto independiente de los portales que enlaza y no almacena CVs ni datos de candidatos.

> **Cobertura y verificabilidad (15/10/2026).** GitHub Actions generó un índice con **172 anuncios**, de los cuales **163 se obtuvieron en la última ejecución** (18 Tecoloco, 46 Bluelight Consulting, 3 FreeBalance, 59 Power Digital, 34 Hire Hangar y 3 Delivery Hero/PedidosYa); **9 anuncios anteriores fueron conservados temporalmente** y no se consideran revalidados. El directorio de 16 fuentes no implica extracción de todos esos portales. Hay 5 tableros ATS empresariales configurados; los cinco tableros empresariales ya devolvieron ofertas durante una ejecución conectada. Ninguna empresa recibe automáticamente insignia de verificación.

## Nuevas mejoras visuales (5.0)

- Tarjetas grandes tipo expediente, con empresa anunciada, fotografía ilustrativa, datos principales, sección desplegable de condiciones, claridad y mapa.
- **12 fotografías originales generadas con IA**, almacenadas localmente en WebP (aprox. 23–67 KB) y seleccionadas automáticamente según puesto y sector. No son fotos del anunciante ni de sus instalaciones.
- Avatar de animalitos determinista por empresa, sin simular logo o identidad real. Preparado para incorporar recursos de marcas con permisos y procedencia verificada.
- Campos extra `requirements`, `benefits`, `experience` y `education` conservados solamente cuando son proporcionados por la fuente (por ejemplo, JobPosting/JSON-LD).
- Preguntas útiles y contextualizadas para candidatos según los datos que faltan: horario, salario, dirección o requisitos. Son sugerencias, no respuestas reales.
- Aviso visible cuando el índice es histórico/de muestra o está desactualizado. Nunca se presentan revisiones antiguas como nuevas.
- Reparado el diseño en pantallas pequeñas: las tarjetas ya no compiten con una barra lateral fija de 248 píxeles.
- **34 pruebas automatizadas de Python aprobadas**; verificación offline en Chromium para escritorio y móvil de búsqueda, imágenes, mapas, favoritos, filtros, estrellas y comparador. Esto no sustituye una auditoría de accesibilidad externa.

## Funciones heredadas

- Filtros por puesto, empresa, departamento, categoría, modalidad, fecha, origen, salario publicado, nivel de claridad (3/4/5 estrellas) y tipo de ubicación.
- **Estrellas transparentes**: 1–5 estrellas calculadas por información **publicada en el anuncio**, no por reputación del empleador. Cada anuncio explica sus siete criterios; pueden faltar salarios. No se inventan opiniones ni clasificaciones de empresas.
- **Comprobación empresarial**: código listo para registrar evidencia editorial con fecha y enlace oficial; ninguna ficha se autoverifica. Las revisiones caducan a los 180 días y requieren coincidencia del tablero autorizado y una prueba en el sitio oficial. Registro vacío por seguridad (`agent/verified_employers.json`).
- **Google Maps sin clave**: enlace de búsqueda por región si solo se conoce ciudad, por dirección si la vacante declara calle; sin mapa en remoto o cuando falta ubicación. Nunca se presenta una búsqueda como pin confirmado del trabajo.
- **Places API (New) opcional y de pago**: puede buscar `place_id` únicamente para direcciones declaradas, sin guardar resultados completos. Se desactiva por defecto, limitada a 8 consultas por corrida y 30 máximo, con secreto y revisión de costos. No garantiza sede laboral.
- **APIs empresariales (Lever, Greenhouse, Ashby y SmartRecruiters)**: cinco tableros explícitos en `agent/ats_boards.json`: Bluelight Consulting, FreeBalance, Power Digital, Hire Hangar y Delivery Hero/PedidosYa. Los cinco tableros han aportado ofertas durante una ejecución de GitHub Actions, pero cada ejecución futura puede presentar restricciones o cero resultados y su estado se publica por separado. Se restringen host, tablero y territorio. No se inventan enlaces, salarios ni ubicación exacta.
- **Radar por departamento**, comparación local de hasta tres vacantes con salario tal como aparece, favoritos en este navegador, búsqueda compartible por URL, modo lectura clara, navegación con teclado y preferencia `prefers-reduced-motion`.
- Mantenimiento anterior: deduplicación, frescura, metadata de fuentes, sanitización, directorio sin confusión con ofertas, recordatorio antifraudes y encabezados de seguridad en Vercel.

## Estructura

```text
agent/
  collector.py          # Índice y extracción HTML/ReliefWeb
  sources.py            # Portales y directorio
  ats.py                # Greenhouse/Lever; config ats_boards.json
  ats_extra.py          # Conectores Ashby y SmartRecruiters
  consistency.py        # Puerta de publicación del índice
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
  data/jobs.json        # Índice generado con fuentes y estados
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

## Integraciones de portales empresariales

Para nuevas empresas, añadir a `agent/ats_boards.json` elementos como este **solo después de comprobar que el token corresponde a un tablero público real que publica vacantes aptas para Nicaragua**:

```json
[
  {"provider":"greenhouse", "board":"TOKEN_REAL", "company":"NOMBRE_REAL", "enabled":true},
  {"provider":"lever", "board":"TOKEN_REAL_2", "company":"EMPRESA_2", "enabled":true}
]
```

Estos son **ejemplos de configuración**, no nuevas empresas añadidas. La lista actual de cinco tableros autorizados se encuentra en `agent/ats_boards.json`. Los nuevos proveedores también aceptan `ashby` y `smartrecruiters`. No se adivinan tokens ni se sortean restricciones. Una oferta multinacional solo se clasifica como elegible cuando declara Nicaragua; algunas ofertas remotas regionales requieren comprobar los países admitidos. Ver `agent/README.md`.

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

1. El código **ya está publicado** en `https://github.com/kankwj5-eng/totalchamba` (rama `main`). El nombre visible es TotalChanba.
2. Autorizar en Vercel la cuenta y el alcance de GitHub que pueden acceder a `kankwj5-eng/totalchamba` y vincular el repositorio en el proyecto **TotalChanba** (Framework Other; Output Directory `public`). Los intentos desde ChatGPT recibieron **403 por alcance Vercel**, por lo que todavía no se ha publicado en Vercel. No introducir claves en el frontend.
3. El workflow de GitHub Actions ya se ejecutó con éxito e indexó 172 enlaces tras superar las pruebas. Sigue programado aproximadamente cada seis horas. Revisar permisos `contents: write` y los resultados de ejecución.
4. Verificar en los registros que cada nuevo tablero responde con ofertas antes de presentarlo como conectado, y revisar robots/términos de los portales de directorio.

Pruebas offline de esta entrega: **34 casos de Python aprobados, JavaScript con sintaxis validada, e interacciones en móvil/escritorio comprobadas**. No equivalen a cobertura legal de las fuentes, geocodificación exacta general ni auditoría de accesibilidad WCAG completa.

Documentación adicional: `docs/INVESTIGACION.md`, `docs/ARQUITECTURA.md`, `docs/FUENTES.md`, `CHANGELOG.md`, `docs/DISEÑO_TOTALCHANBA.md`.