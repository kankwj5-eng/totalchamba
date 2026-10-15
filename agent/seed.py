"""Muestra inicial de publicaciones reales comprobadas en páginas públicas el 14/10/2026.
No volver a ejecutar para 'simular' actualizaciones: el crawler reemplaza este fichero.
"""
import json
from datetime import datetime, timezone
from .collector import normalise, DATA_FILE
from .quality import merge_exact_reposts, build_facets
from .signals import decorate
from .sources import SOURCES
source=next(x for x in SOURCES if x['id']=='encuentra24')
now=datetime(2026,10,14,22,47,tzinfo=timezone.utc)
observed=[
  dict(title='Guardia de seguridad Altamira',company='Centro Médico Altamira',location='Managua',type='Tiempo completo',modality='Presencial',published_at='2026-10-14',summary='Seguridad de pacientes, personal e instalaciones en centro médico. Solicitan disponibilidad inmediata.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/guardia-de-seguridad-altamira/33126835'),
  dict(title='Conserje / limpieza para restaurante',company='A. Cifuentes',location='Managua, Carretera a Masaya',type='Tiempo completo',modality='Presencial',salary='C$11,350 + propinas',published_at='2026-10-13',summary='Limpieza y apoyo en restaurante de hamburguesas. Solicitan experiencia en restaurantes.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/conserje-limpieza-para-restaurante/33089570'),
  dict(title='Asesor de ventas',company='Sierras de Paz',location='Managua, Bolonia',type='Tiempo completo',modality='Presencial',published_at='2026-10-13',summary='Asesoría comercial con comisiones y capacitación; buscan personas con buena comunicación.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/asesor-de-ventas/24649745'),
  dict(title='Oficial de atención al cliente',company='Ultra de Nicaragua S.A.',location='Managua',type='Tiempo completo',modality='Presencial',published_at='2026-10-08',summary='Coordinar servicios técnicos y dar seguimiento a solicitudes y consultas de clientes.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/oficial-de-atencion-al-cliente/33017090'),
  dict(title='Cocinero/a de línea caliente y pizzero/a',company='Enmanuel Paramo',location='Managua',type='Tiempo completo',modality='Presencial',published_at='2026-10-06',summary='Preparación de pastas, pizzas y platos de cocina italiana; experiencia previa requerida.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/cocinero-a-de-linea-caliente-y-pizzero-a/33094128'),
  dict(title='Tornero',company='Douglas Hanon',location='Masaya, Tisma',type='Tiempo completo',modality='Presencial',published_at='2026-10-13',summary='Fabricación y rectificación de piezas mediante torno.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/tornero/33120722'),
  dict(title='Agentes de cobro / call center',company='CCG Comunicaciones',location='Managua',type='Tiempo completo',modality='Presencial',salary='US$285 base + comisiones',published_at='2026-10-10',summary='Gestión de cobranza telefónica y por redes sociales con capacitación inicial.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/agentes-de-cobro-call-center/33040989'),
  dict(title='Asesor comercial remoto / call center',company='Svitlana Kriv',location='León / Remoto',type='Tiempo completo',modality='Remoto',published_at='2026-10-12',summary='Atención y asesoramiento comercial por teléfono. Solicitan computadora propia e internet estable.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/asesor-comercial-remoto-call-center-remoto/33117703'),
  dict(title='Auxiliar contable de digitación',company='Empleos Nicaragua',location='Managua',type='Tiempo completo',modality='Presencial',published_at='2026-10-13',summary='Digitación y revisión de documentos contables y de comercio exterior. Solicitan formación en Contabilidad.',url='https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos/auxiliar-contable-de-digitacion/33053908'),
]
rows=[normalise(job,source,now) for job in observed]
rows=decorate(merge_exact_reposts([x for x in rows if x]))
DATA_FILE.write_text(json.dumps({
    'schema_version':3,
    'generated_at':now.isoformat(timespec='seconds').replace('+00:00','Z'),
    'jobs':rows,
    'sources':[{**s,'status':'muestra_inicial' if s['id']=='encuentra24' else ('requiere_configuracion' if s['id']=='reliefweb' else 'directorio'), 'jobs_count':sum(j['source']==s['id'] for j in rows), 'last_success':None} for s in SOURCES],
    'facets':build_facets(rows),
    'metadata':{'disclaimer':'Datos de vacantes externas consultados el 14/10/2026; confirmá su vigencia en el portal original.','collection_status':{'encuentra24':'muestra_inicial'},'indexed_count':len(rows)}
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Semilla verificada:',len(rows),'vacantes')
