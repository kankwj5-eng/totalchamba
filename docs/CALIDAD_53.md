# TotalChanba 5.3 — Calidad editorial, preparación y accesibilidad

## Principios del producto
1. **Postulaciones auténticas**: ningún asistente rellena títulos, certificados, idiomas o experiencia que la persona no haya declarado.
2. **Datos trazables**: cada oferta enlaza al anunciante; la fecha de recopilación no certifica que continúe abierta.
3. **Información incompleta ≠ riesgo empresarial**: las estrellas describen claridad del anuncio, nunca reputación, seguridad o legitimidad.
4. **Privacidad por defecto**: el CV se edita en el navegador. No se envía a un servidor de TotalChanba ni se pide registro.
5. **Acceso desde teléfonos**: los flujos principales se prueban a 390px y 1440px; la revisión WCAG no equivale a una certificación de accesibilidad.

## Agente orientador (`agent/career_advisor.py`)
El campo `career_guide.documented_terms` contiene un vocabulario acotado de términos
**encontrados literalmente** en `requirements` o `education`. No los extrae
del título, descripción general ni de sugerencias inventadas. Cada término tiene
`label` y `source` (requisitos o formación).

Ejemplo:
```json
{"label":"Excel","source":"requisitos"}
```

Esto **no indica que Excel sea obligatorio**: el anuncio podría decir que es
deseable. El usuario revisa el origen y marca voluntariamente cuáles puede
demostrar. Estas marcas solo se guardan localmente por vacante, bajo una clave
con identificador del anuncio. No se calcula puntuación de idoneidad ni se
rechaza ninguna candidatura.

## Creador de CV
- Botón **Copia de respaldo**: descarga `TotalChanba_CV_respaldo.json`.
- **Importar mi respaldo**: valida tipo, versión, tamaño máximo de 30 KB y
  campos de texto con límites antes de pedir permiso para sustituir los datos
  en pantalla.
- **Guardar en este dispositivo** es una acción independiente. Importar nunca
  obliga a persistir los datos y un archivo inválido no debe modificarlos.
- **Borrar mis datos** elimina el CV almacenado mediante TotalChanba en el
  navegador, pero **no** elimina archivos de respaldo descargados por la
  persona. El archivo de respaldo **no está cifrado**.
- Para compartir un CV, usar la impresión a PDF local. El diseño se inspira
  en prácticas de CV universitario, **sin afiliación ni certificado Harvard**.

## Calidad de campos y mapas
- `agent.collector.salary_from_jsonld` conserva valores de salario únicamente
  si la ficha declara **moneda de tres letras y cantidad válida**. El período
  se incluye solo cuando aparece en la fuente (`MONTH/YEAR/HOUR/WEEK/DAY`).
  No convertir automáticamente USD a C$ ni asumir salario mensual.
- El tipo de contrato `Default` o `Unknown` se convierte a
  `No especificado` en lugar de hacerse pasar por un tipo real.
- `agent.geo.map_metadata` evita repetir «Nicaragua», y no ubica anuncios
  remotos en una oficina aproximada. Una dirección declarada **no verifica
  físicamente la sede**.
- El recolector recalcula el mapa de cada anuncio tras fusionar duplicados o
  conservar datos previos. Un `place_id` identificado anteriormente solo
  se preserva cuando sigue siendo un caso basado en una dirección declarada
  y existe evidencia guardada de coincidencia con Google Places.
- Los cambios de fuente pueden dejar temporalmente anuncios con información
  parcial. Nunca se crean datos para rellenar esos huecos.

## Control de calidad automatizado
- Python: pruebas de términos literales (evitando falsos positivos SQL/NoSQL),
  salarios, privacidad conceptual del orientador y precisión territorial.
- Chromium con Playwright: entrada desde la tarjeta, CV, respaldo e importación
  con confirmación, archivo mal formado, autochequeo por vacante, carta,
  entrevista, plan, estado local y visualización móvil/escritorio.
- axe-core: auditoría automática de WCAG 2.1 A/AA en el portal y las secciones
  clave del Estudio de Candidatura. Se bloquea el flujo ante hallazgos
  *serious* o *critical*. Debe complementarse con pruebas manuales de
  teclado, zoom, lector de pantalla y contraste en dispositivos reales.

## Por desarrollar
- Modelos de CV alternativos que respeten la misma política de privacidad.
- Pruebas de accesibilidad con lectores de pantalla y navegación por teclado
  con participación de personas usuarias.
- Un protocolo editorial para incorporar nuevas bolsas, ferias y formación
  con fecha de revisión, evidencia y estados de error separados.
- Comprobaciones de vigencia individuales cuando los términos y APIs de las
  plataformas lo permitan, sin evadir controles ni declarar empleo abierto
  solamente por haberlo indexado.
