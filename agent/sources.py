"""Catálogo de fuentes verificadas. 'directorio' no implica acceso a sus vacantes."""
SOURCES = [
    {"id":"encuentra24", "name":"Encuentra24", "url":"https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos", "kind":"portal", "collection":"crawler", "focus":"Oficios y empleo local", "color":"#fbbf7a"},
    {"id":"tecoloco", "name":"Tecoloco", "url":"https://www.tecoloco.com.ni/empleos?Keywords=+&PerPage=100", "kind":"portal", "collection":"crawler", "focus":"Empresas y profesionales", "color":"#b8b5ff"},
    {"id":"computrabajo", "name":"Computrabajo", "url":"https://ni.computrabajo.com/offersgrid/search", "kind":"portal", "collection":"directorio", "focus":"Empleo formal", "color":"#8fd9f5"},
    {"id":"linkedin", "name":"LinkedIn Jobs", "url":"https://ni.linkedin.com/jobs/empleos-en-nicaragua", "kind":"portal", "collection":"directorio", "focus":"Profesionales y remoto", "color":"#83b9ff"},
    {"id":"opcionempleo", "name":"Opcionempleo", "url":"https://www.opcionempleo.com.ni/", "kind":"agregador", "collection":"directorio", "focus":"Varias industrias", "color":"#fbcb7a"},
    {"id":"vacantes", "name":"Vacantes.com", "url":"https://vacantes.com/es/", "kind":"remoto", "collection":"directorio", "focus":"Trabajo remoto", "color":"#d2aaff"},
    {"id":"empleosnicaragua", "name":"Empleos Nicaragua", "url":"https://empleosnicaragua.net/", "kind":"local", "collection":"directorio", "focus":"Talento nicaragüense", "color":"#98efc2"},
    {"id":"trabajosnica", "name":"Trabajosnica", "url":"https://trabajosnica.com/", "kind":"local", "collection":"directorio", "focus":"Ofertas locales y empresas verificadas", "color":"#c1e89f"},
    {"id":"uno", "name":"UNO Nicaragua", "url":"https://empleos.uno-ca.com/ni/", "kind":"empresa", "collection":"directorio", "focus":"Vacantes directas de empresa", "color":"#f3bc9e"},
    {"id":"unicef", "name":"UNICEF Nicaragua", "url":"https://www.unicef.org/nicaragua/trabaja-con-unicef", "kind":"ong", "collection":"directorio", "focus":"Convocatorias y consultorías", "color":"#a7daf8"},
    {"id":"undp", "name":"PNUD", "url":"https://www.undp.org/es/careers", "kind":"ong", "collection":"directorio", "focus":"Empleo y cooperación internacional", "color":"#9dbaff"},
    {"id":"inide", "name":"INIDE", "url":"https://sarh.inide.gob.ni/convocatoria/", "kind":"publico", "collection":"directorio", "focus":"Convocatorias de institución pública", "color":"#c3d5ea"},
    {"id":"mined", "name":"MINED", "url":"https://www.mined.gob.ni/vacantes-2026/", "kind":"publico", "collection":"directorio", "focus":"Vacantes del sector educativo", "color":"#afccec"},
    {"id":"conami", "name":"CONAMI", "url":"https://www.conami.gob.ni/oportunidades-de-empleo/", "kind":"publico", "collection":"directorio", "focus":"Oportunidades de empleo y pasantías", "color":"#c5d6aa"},
    {"id":"reliefweb", "name":"ReliefWeb", "url":"https://reliefweb.int/jobs", "kind":"ong", "collection":"api", "focus":"ONG y cooperación humanitaria", "color":"#f3a7a7"},
    {"id":"unjobs", "name":"UNjobs", "url":"https://unjobs.org/duty_stations/nicaragua", "kind":"ong", "collection":"directorio", "focus":"Organismos y proyectos", "color":"#83c2ff"},
]
