"""Orientación de candidaturas por profesión; reglas auditables sin IA generativa.

Nunca presume habilidades, estudios, experiencia, salario ni acceso a la empresa.
Los consejos son orientativos y se distinguen de requisitos publicados.
"""
from __future__ import annotations
import re
import unicodedata

def norm(text):
    v = unicodedata.normalize('NFKD', str(text or '').casefold())
    return ''.join(c for c in v if not unicodedata.combining(c))

GENERAL = {
    'focus': 'Mostrá logros comprobables y tu disponibilidad real.',
    'cv': ['Ordená experiencia y formación desde lo más reciente.', 'Describí tareas y resultados que realmente puedas demostrar.', 'Ajustá las palabras clave al anuncio sin copiar afirmaciones falsas.'],
    'interview': ['¿Qué te interesa de este puesto y por qué?', 'Contame una situación difícil y cómo la resolviste.', '¿Qué necesitás saber de la jornada, el contrato y la sede?'],
}
PLAYBOOKS = {
    'Tecnología': {
        'focus': 'Prepará evidencia técnica breve y comprensible de proyectos auténticos.',
        'cv': ['Indicá herramientas que manejás realmente y tu nivel.', 'Enlazá portafolio o repositorios propios, si existen.', 'Explicá resultados verificables: rendimiento, automatización o incidencias resueltas.'],
        'interview': ['¿Cómo diagnosticarías un problema que nunca viste?', '¿Qué medidas tomás para proteger datos?', 'Contá una mejora técnica que hayas implementado.'],
    },
    'Administración': {
        'focus': 'Orden, confidencialidad y precisión son habilidades clave que podés demostrar con ejemplos.',
        'cv': ['Mencioná herramientas ofimáticas que realmente utilizás.', 'Describí procesos que organizaste o errores que ayudaste a evitar.', 'Resaltá manejo responsable de registros y atención.'],
        'interview': ['¿Cómo priorizarías documentos urgentes?', '¿Qué harías si encontrás una cifra incorrecta?', '¿Cómo protegés información confidencial?'],
    },
    'Ventas': {
        'focus': 'Destacá atención al público, comunicación y resultados de servicio.',
        'cv': ['Describí tu experiencia real atendiendo clientes.', 'Indicá resultados medibles si contás con registros.', 'Señalá el manejo de caja o inventario solo cuando aplique.'],
        'interview': ['¿Qué hacés ante un cliente molesto?', '¿Cómo explicás un producto que no conocés?', '¿Cómo mantenés una atención respetuosa bajo presión?'],
    },
    'Logística': {
        'focus': 'Puntualidad, seguridad y control de existencias importan en operaciones.',
        'cv': ['Detallá tipos de inventario o despacho que manejaste.', 'Indicá licencias vigentes solo si el puesto las exige y las tenés.', 'Describí prácticas reales de seguridad y orden.'],
        'interview': ['¿Qué harías ante una diferencia de inventario?', '¿Cómo priorizás entregas con plazos distintos?', '¿Cómo prevenís accidentes durante la jornada?'],
    },
    'Industria': {
        'focus': 'Presentá experiencia práctica y respeto a protocolos de seguridad.',
        'cv': ['Enumerá máquinas o herramientas que conocés de verdad.', 'Mostrá tareas técnicas y resultados demostrables.', 'Incluí certificaciones reales de seguridad o mantenimiento si tenés.'],
        'interview': ['¿Qué comprobás antes de usar una máquina?', '¿Qué hacés si detectás una falla peligrosa?', 'Contá un trabajo técnico que resolviste con precisión.'],
    },
    'Servicios': {
        'focus': 'Un trato respetuoso y la confiabilidad cuentan mucho en servicios.',
        'cv': ['Describí tareas y turnos en los que tenés experiencia.', 'Incluí procesos de higiene o servicio que conozcas.', 'Mencioná referencias laborales solo con autorización.'],
        'interview': ['¿Cómo atenderías un reclamo?', '¿Qué harías si falta un insumo indispensable?', '¿Cómo organizás tus tareas en horas de mayor demanda?'],
    },
    'Salud': {
        'focus': 'Priorizá formación acreditada, ética y seguridad de las personas.',
        'cv': ['Escribí el nombre real de tus acreditaciones vigentes.', 'Indicá prácticas o servicios realizados sin revelar datos de pacientes.', 'Mencioná protocolos que conocés, no competencias sin respaldo.'],
        'interview': ['¿Cómo protegés la confidencialidad de un paciente?', '¿Qué hacés cuando una situación supera tus competencias?', '¿Cómo coordinás con colegas en un momento urgente?'],
    },
    'Educación': {
        'focus': 'Experiencia pedagógica y comunicación clara con estudiantes y familias.',
        'cv': ['Describí asignaturas, niveles y grupos que atendiste realmente.', 'Destacá estrategias de enseñanza que hayas empleado.', 'Incluí formación pedagógica acreditada si corresponde.'],
        'interview': ['¿Cómo adaptás una explicación para estudiantes distintos?', '¿Cómo medís el aprendizaje?', '¿Cómo actuarías ante un conflicto en el aula?'],
    },
}
SPECIFIC = (
    (r'contab|auditor|digitac|tesorer|factur', 'Administración'),
    (r'operari|soldad|torner|mecan|electric|construc|albanil', 'Industria'),
    (r'chofer|conductor|almacen|bodega|mensajer|repart|inventario', 'Logística'),
    (r'programador|software|developer|desarrollador|sistema|ingenieria de datos', 'Tecnología'),
    (r'cocin|meser|restauran|limpiez|seguridad|guardia', 'Servicios'),
    (r'enfermer|medic|odontolog|farmac', 'Salud'),
    (r'docent|maestr|profesor|tutor', 'Educación'),
    (r'venta|comercial|cajer|promotor|cliente', 'Ventas'),
)


# Sólo se muestran términos hallados literalmente en texto proporcionado por la fuente.
# No se usan como una evaluación automática de aptitud ni se recomiendan inventar.
SKILL_TERMS = (
    ('Excel', (r'excel', r'microsoft excel')),
    ('Word', (r'word', r'microsoft word')),
    ('Power BI', (r'power\s*bi',)),
    ('SAP', (r'sap',)),
    ('SQL', (r'sql',)),
    ('Python', (r'python',)),
    ('JavaScript', (r'javascript',)),
    ('Inglés', (r'ingles', r'english')),
    ('Atención al cliente', (r'atencion al cliente', r'servicio al cliente')),
    ('Inventarios', (r'inventario', r'inventarios')),
    ('Licencia de conducir', (r'licencia de conducir', r'licencia de conducir vigente')),
    ('Primeros auxilios', (r'primeros auxilios',)),
    ('Bachillerato', (r'bachillerato', r'bachiller',)),
    ('Trabajo en equipo', (r'trabajo en equipo',)),
    ('Contabilidad', (r'contabilidad', r'contable')),
    ('Soldadura', (r'soldadura',)),
    ('Manejo de caja', (r'manejo de caja',)),
    ('Seguridad industrial', (r'seguridad industrial',)),
)

def documented_terms(job):
    """Señales de preparación basadas únicamente en requisitos/estudios literales.
    
    No afirma que un término sea obligatorio: podría figurar como deseable.
    El candidato debe leer el texto original y demostrar sólo experiencia real.
    """
    found = []
    for field, source_label in (('requirements', 'requisitos'), ('education', 'formación')):
        raw = job.get(field)
        if not isinstance(raw, str) or not raw.strip():
            continue
        folded = norm(raw)
        for label, alternatives in SKILL_TERMS:
            if any(re.search(r'(?<!\\w)(?:' + pattern + r')(?!\\w)', folded)
                   for pattern in alternatives):
                if label not in [x['label'] for x in found]:
                    found.append({'label': label, 'source': source_label})
                if len(found) >= 8:
                    return found
    return found

def advise(job):
    title = norm(job.get('title'))
    category = str(job.get('category') or '')
    for pattern, suggested in SPECIFIC:
        if re.search(pattern, title):
            category = suggested
            break
    tips = PLAYBOOKS.get(category, GENERAL)
    published_fields = [label for key, label in (
        ('requirements', 'Requisitos publicados'), ('experience', 'Experiencia indicada'),
        ('education', 'Formación indicada'), ('salary', 'Salario publicado'),
        ('benefits', 'Beneficios publicados')
    ) if isinstance(job.get(key), str) and job[key].strip()]
    questions = []
    if not job.get('salary'):
        questions.append('¿Cuál es el salario, moneda y frecuencia de pago?')
    if job.get('modality') in ('', 'No especificada', None):
        questions.append('¿La modalidad es presencial, híbrida o remota?')
    if not job.get('address') and norm(job.get('modality')) != 'remoto':
        questions.append('¿Cuál es la dirección exacta donde se realizaría el trabajo?')
    if not job.get('requirements'):
        questions.append('¿Cuáles son las habilidades indispensables para postular?')
    return {
        'version': 1, 'basis': 'recomendaciones_generales_por_oficio',
        'occupation_area': category or 'General',
        'focus': tips['focus'],
        'cv': tips['cv'][:3],
        'interview': tips['interview'][:3],
        'ask_employer': questions[:4],
        'published_fields': published_fields,
        'documented_terms': documented_terms(job),
        'notice': 'Consejos orientativos. No son requisitos oficiales; solo el anuncio original puede confirmarlos.',
    }

def enrich(jobs):
    for job in jobs:
        if isinstance(job, dict):
            job['career_guide'] = advise(job)
    return jobs
