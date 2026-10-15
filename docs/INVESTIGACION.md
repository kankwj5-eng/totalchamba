# Investigación técnica y priorización — ChambaNI 3.0 (14 de octubre de 2026)

## Repositorios estudiados

| Herramienta | Fuente | Estado y motivo |
|---|---|---|
| Scrapy | https://github.com/scrapy/scrapy | **Evaluada, no instalada.** Útil para crawling complejo cuando permisos legales/robots lo permitan. Hoy el extractor existente es suficiente para un índice pequeño. |
| RapidFuzz | https://github.com/rapidfuzz/RapidFuzz | **Evaluada, no instalada.** Detección de republicaciones fuzzy futura, solo con control para no combinar puestos distintos. |
| Leaflet | https://github.com/Leaflet/Leaflet | **Evaluada, no instalada.** Para mapa geográfico interactivo cuando existan coordenadas con origen verificable y proveedor de tiles compatible. No dibujar pines falsos. |
| MapLibre GL JS | https://github.com/maplibre/maplibre-gl-js | **Evaluada, no instalada.** Mapas vectoriales futuros, mayor complejidad que enlaces Google Maps iniciales. |
| geopy | https://github.com/geopy/geopy | **Evaluada, no instalada.** Interfaz a múltiples servicios, su librería no autoriza abusar APIs ajenas. |
| axe-core | https://github.com/dequelabs/axe-core | **Evaluada, no instalada.** Auditoría automática WCAG 2.2 en CI cuando se configure. También hará falta revisión manual. |
| Pa11y | https://github.com/pa11y/pa11y | **Evaluada, no instalada.** Pruebas periódicas de accesibilidad. |

**Repositorios usados indirectamente a nivel de diseño:** APIs documentadas de [Greenhouse Job Board](https://docs.greenhouse.io/job-board.html) y [Lever Postings](https://github.com/lever/postings-api), implementadas con cliente estándar Python sin dependencia Python nueva. Hay dos tokens obtenidos de tableros públicos: [Bluelight Consulting](https://jobs.lever.co/bluelightconsulting?location=Managua%2C+Nicaragua) y [FreeBalance](https://jobs.lever.co/freebalance.com?location=Managua%2C+Nicaragua), configurados para consulta futura. La ejecución de las APIs no se ha verificado en este entorno.

## APIs, políticas y elección

- [Google Maps URLs](https://developers.google.com/maps/documentation/urls/get-started): permiten abrir búsquedas y direcciones desde Android y la web **sin clave**. Implementado: búsquedas de zona o dirección declarada; no se finge pin exacto.
- [Google Places API (New)](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing/): requiere clave y facturación. Implementado como conector opcional detrás de variables de entorno y máximo de llamadas. Se deben consultar los [precios](https://developers.google.com/maps/billing-and-pricing/pricing?hl=es-419), máscaras de campo y [políticas de almacenamiento/atribución](https://developers.google.com/maps/documentation/places/web-service/policies).
- [Nominatim OSM público](https://operations.osmfoundation.org/policies/nominatim/): **no integrado**; su servicio comunitario prohíbe aplicaciones masivas periódicas bajo condiciones que no caben en el agente actual. Se necesita proveedor comercial o instancia dedicada con políticas y licencias adecuadas antes de geocodificar a escala.
- [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html) y [Lever Postings API](https://github.com/lever/postings-api/blob/master/README.md): API de anuncios públicos estructurados. Implementadas para tableros registrados con revisión, sin publicaciones automáticas hasta habilitar fuentes válidas.
- [FTC: evitar estafas de empleo](https://consumer.ftc.gov/consumer-alerts/2026/04/job-offer-text-probably-scam): refuerza la prohibición de pagar para obtener un puesto; ninguna clasificación automática suplanta la validación humana.

## Diseño diferencial y priorización

**Incorporado v3:** mapa condicionado a evidencia; semántica de ubicación; tres lentes (claridad, procedencia, precisión territorial); estrellas auditables con justificaciones; registro editorial de identidad; radar territorial de ofertas realmente indexadas; comparar hasta tres anuncios; modo de lectura con menos efectos; navegación móvil simple.

**Siguiente nivel viable, todavía NO construido:** revisar ATS de empresas con operaciones reales en Nicaragua; completar una base autorizada de direcciones laborales con coordenadas y política de uso de mapas; historial de vacantes y cierres con métricas de cambios; alertas opt-in de búsquedas mediante notificaciones; criterios sobre beneficios y contrato; filtros de accesibilidad laboral, transporte y adaptaciones cuando las vacantes lo declaren; reportes de anuncios sospechosos revisados por personas; accesibilidad verificada con axe-core+Pa11y y usuarios reales.

**Evitar:** crear estrellas falsas de confianza/reputación empresarial, deducir salarios no publicados, estimar direcciones exactas por nombre de compañía, importar reseñas de Google como si fueran evaluaciones laborales, presentar directorios como anuncios, llamar "tiempo real" a jobs verificados cada seis horas.
