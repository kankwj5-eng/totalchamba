# Directorio inicial de fuentes (14/10/2026)

El enlace a una fuente NO significa que podamos incorporar automáticamente sus anuncios. Modo `crawler` = adaptador experimental, pendiente de validar acceso y selectores en infraestructura real. Modo `directorio` = enlace sin extracción. Modo `api` = integración condicionada a autorización.

| Fuente | Clase | Modo | URL |
|---|---|---|---|
| Encuentra24 | Portal | crawler | https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos |
| Tecoloco | Portal | crawler | https://www.tecoloco.com.ni/empleos?Keywords=+&PerPage=100 |
| Computrabajo | Portal | directorio | https://ni.computrabajo.com/offersgrid/search |
| LinkedIn Jobs | Portal | directorio | https://ni.linkedin.com/jobs/empleos-en-nicaragua |
| Opcionempleo | Agregador | directorio | https://www.opcionempleo.com.ni/ |
| Vacantes.com | Remoto | directorio | https://vacantes.com/es/ |
| Empleos Nicaragua | Local | directorio | https://empleosnicaragua.net/ |
| Trabajosnica | Local | directorio | https://trabajosnica.com/ |
| UNO Nicaragua | Empresa | directorio | https://empleos.uno-ca.com/ni/ |
| UNICEF Nicaragua | ONG | directorio | https://www.unicef.org/nicaragua/trabaja-con-unicef |
| PNUD | ONG | directorio | https://www.undp.org/es/careers |
| INIDE | Público | directorio | https://sarh.inide.gob.ni/convocatoria/ |
| MINED | Público | directorio | https://www.mined.gob.ni/vacantes-2026/ |
| CONAMI | Público | directorio | https://www.conami.gob.ni/oportunidades-de-empleo/ |
| ReliefWeb | ONG | api (requiere aprobación) | https://reliefweb.int/jobs |
| UNjobs | ONG | directorio | https://unjobs.org/duty_stations/nicaragua |

**Incorporar más fuentes:** acreditar URL y jurisdicción, revisar términos/robots y permisos, preferir API pública autorizada o feed oficial, desarrollar extractor con fixtures y tests, confirmar que las fichas son puestos laborales (no licitaciones u otros contratos), registrar fechas de cierre y medir tasas de éxito. No extraer páginas privadas ni eludir bloqueos.

**ReliefWeb:** desde el 1 de noviembre de 2025 los `appname` requieren aprobación previa. Documentación oficial: https://apidoc.reliefweb.int/parameters

## Actualización 3.0 (14/10/2026)

También se admiten tableros explícitamente autorizados/configurados de [Greenhouse](https://docs.greenhouse.io/job-board.html) y [Lever](https://github.com/lever/postings-api), pero `agent/ats_boards.json` contiene dos tableros públicos reales, **Bluelight Consulting** y **FreeBalance**, pendientes de comprobación de acceso a la API desde GitHub Actions. El dataset incluido contiene solo las 16 fuentes del directorio y nueve vacantes históricas de muestra, no anuncios nuevos de estas empresas.

El enlace a Google Maps es una **búsqueda** por zona o dirección provista, no una sede validada. Los servicios Google Places se activan únicamente con facturación, clave de servidor y revisión de costos.
