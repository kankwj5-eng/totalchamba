# Historial de cambios

## 5.3 — 15/10/2026 · Asistencia verificable y accesibilidad
- Competencias documentadas con procedencia desde requisitos y formación, y autochequeo voluntario por vacante sin predicciones laborales.
- Respaldo de CV en JSON, importación validada y consentimiento antes de reemplazar datos.
- Parser salarial JSON-LD que conserva moneda y período explícitos; limpieza de tipos de contrato internos.
- Mapas normalizados y regenerados, sin duplicados geográficos ni sedes falsas para remoto.
- Auditorías WCAG 2.1 A/AA con axe-core y mejoras de contraste, además de Chromium.
- Ampliación de pruebas para competencias, salarios, importación y ubicación.

## 5.2 — 15/10/2026 · Estudio de Candidatura
- Se incorporaron seis herramientas de candidatura accesibles desde **cada vacante**: guía por oficio, CV profesional imprimible, entrevista STAR, carta de presentación, plan de postulación y acompañamiento motivacional general.
- Agente Python `career_advisor` integrado al recolector: 172 fichas enriquecidas con consejos **generales por profesión**, diferenciados de los requisitos oficiales.
- CV inspirado en estructura de Harvard (no oficial), con vista previa, impresión A4, almacenamiento local opcional y auditoría de cinco campos sin predicciones de contratación.
- Agenda editorial de recursos, formación y eventos anunciados con fuente oficial; eventos vencidos se ocultan y `agent.bulletin` valida fechas y dominios.
- Filtros de última consulta, diferenciación de vacantes conservadas y exportación local de favoritas a CSV.
- GitHub Actions ahora valida los tres JavaScript, 47 pruebas Python y recorridos automatizados con Chromium en Android simulado y escritorio.
- Se corrigió una condición de carrera entre el robot de actualización y otros cambios en `main` usando reintentos con rebase, nunca force-push.
- No se ha afirmado que las herramientas equivalgan a orientación laboral profesional ni que una fuente externa garantice contratación.

## 5.0 — 14/10/2026 (hora de Nicaragua)
- Cambio de marca visible a **TotalChanba** manteniendo URL del repositorio `totalchamba`.
- 12 fotografías temáticas originales de distintos oficios, comprimidas como WebP local; aviso de generación con IA.
- Fichas extendidas con animalitos, cuatro datos clave, enlace de Maps con precisión indicada, señales de claridad y fuente rastreable.
- Soporte de requisitos, beneficios, experiencia y formación cuando el origen lo proporciona; preguntas sugeridas si la información falta.
- Aviso visible para fuentes históricas/de muestra sin confundirse con vacantes vigentes.
- Solucionada la cuadrícula móvil y comprobada la ausencia de desbordamiento.
- 26 pruebas Python y verificaciones de navegador en dos tamaños superadas.


## 3.0 — 14/10/2026
- Estrellas reproducibles sobre transparencia de los anuncios con siete señales y su explicación. **No son calificaciones empresariales**.
- Registro curado de verificación de identidad de empresas con evidencias y revisión que caduca (sin empresas aprobadas en esta entrega).
- Búsqueda territorial por departamento en radar interactivo, etiquetado de ubicación, enlace a Google Maps sin clave, Google Places opt-in limitado.
- Conectores Python configurables para Greenhouse y Lever, incluye dos tableros públicos identificados (Bluelight y FreeBalance), pendientes de primera ejecución API.
- Comparación hasta tres empleos, filtros extra de claridad/ubicación, orden por claridad y modo lectura clara.
- Pruebas de nuevas capas y automatización visual de los principales flujos móviles/escritorio.
- Las nueve ofertas de demostración de octubre 14 se mantienen como **muestra histórica**, no como nuevos hallazgos.

## 2.0 — 14/10/2026
- Búsqueda multitémino, favoritos, fuentes, fechas, calidad de recolección, deduplicación y protección antifraudes.
