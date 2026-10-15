# Estudio de Candidatura de TotalChanba

> Edición 5.2 · Orientación para postulaciones de Nicaragua · Sin cuenta obligatoria

El objetivo no es prometer contrataciones ni simular ser el empleador: **ayudar a
transformar una vacante encontrada en pasos concretos de preparación**.

## Flujo de usuario

1. Una tarjeta de trabajo ofrece **Consejos para conseguir este trabajo**.
2. El enlace lleva a `/herramientas.html?vacante=ID`. El ID se busca en el
   índice publicado para recuperar exclusivamente título, empresa, zona, datos
   de la fuente y recomendaciones de orientación, no datos privados del usuario.
3. El espacio muestra seis pestañas:
   - **Guía**: consejos por oficio, campos realmente publicados y preguntas
     recomendadas para el empleador.
   - **CV profesional**: diseño sobrio inspirado en modelos de CV universitarios
     y comúnmente llamados «estilo Harvard», más un revisor local de cinco campos
   básicos de claridad del CV. Esa lista no predice empleabilidad ni aprobación
   por sistemas de selección. **No es una plantilla oficial
     de Harvard ni está avalada por esa universidad**. Vista previa, impresión
     A4 y la opción «Guardar como PDF» del navegador.
   - **Entrevista**: preguntas orientativas por profesión, cronómetro local de
     90 segundos y método STAR para organizar una respuesta auténtica.
   - **Carta**: un borrador estructurado enlazado con el título y la empresa,
     que requiere aportaciones del usuario y deja marcadores si faltan datos.
   - **Mi plan**: seis pasos de preparación, estado y notas, guardables
     exclusivamente en el dispositivo del usuario.
   - **Ánimo**: ideas breves y herramientas de autocuidado no clínicas; no
     pretende ofrecer psicoterapia, diagnóstico ni evaluación emocional.

## Agentes y responsabilidades

| Módulo | Responsabilidad |
|---|---|
| `agent.collector` | Integración con fuentes y conservación de enlaces y datos |
| `agent.ats` / `agent.ats_extra` | Lectura de tableros ATS públicos autorizados |
| `agent.quality` / `agent.consistency` | Duplicados, caducidad, validación previa a publicar |
| `agent.signals` / `agent.verification` | Claridad de anuncios e identidad con evidencias |
| `agent.geo` | Información territorial con grados de precisión |
| `agent.career_advisor` | Consejos profesionales generales por puesto, *sin inventar requisitos* |
| `agent.bulletin` | Validación editorial de recursos y eventos anunciados |

Estos son módulos especializados en Python, con reglas revisables. No son
agentes autónomos con conexión a servicios de IA generativa ni sustituyen a
un orientador laboral profesional.

## Reglas de confianza

- No completar antecedentes, salario, contratos, acreditaciones ni logros
  que el anuncio no aporta.
- El campo `career_guide` contiene explícitamente
  `basis=recomendaciones_generales_por_oficio`. **No representa exigencias
  de la empresa**.
- El currículum se forma con datos escritos por la persona. El botón
  **Guardar** lo almacena en el `localStorage` de *ese navegador* y se
  puede borrar. También existe guardado local explícito para el seguimiento
  de cada vacante.
- En esta edición **no existe servidor de CV**, ni cuentas de candidatos,
  ni envío automático de postulaciones, ni analítica de datos del currículum.
  El navegador puede gestionar sus propios permisos/autorrelleno.
- Las opciones imprimir/guardar PDF usan el diálogo del navegador; no generan
  una copia en la plataforma.
- Los consejos de bienestar son recordatorios generales, no terapia,
  diagnóstico ni un servicio de crisis.

## Tablón de anuncios, ferias y formación

`public/data/bulletin.json` contiene recursos y actividades curadas
editorialmente, con URL oficial, organización, estado y fecha de revisión.

- Eventos deben declarar `starts_at` y `expires_at`. La interfaz oculta
  automáticamente eventos vencidos.
- Una página de **directorio oficial** se muestra como recurso, no como
  evento próximo ni como matrícula abierta.
- Las ferias laborales sólo deben aparecer cuando se confirme fecha y
  enlace. **No inventar eventos por llenar la sección**.
- `python -m agent.bulletin` valida formato y dominios permitidos,
  pero no sustituye comprobar manualmente que el anuncio sigue vigente.
- La fuente de educación técnica usada como referencia inicial es
  [INATEC](https://www.tecnacional.edu.ni/); para convocatorias se citan
  [UNO Nicaragua](https://empleos.uno-ca.com/ni/) y
  [UNICEF Nicaragua](https://www.unicef.org/nicaragua/trabaja-con-unicef).

## Ejecución y pruebas

```bash
python -m pip install -r requirements.txt pytest
python -m pytest -q
python -m agent.bulletin
node --check public/assets/app.js
node --check public/assets/toolkit.js
node --check public/assets/bulletin.js
python -m http.server 4173 --directory public
```

La nueva acción `pruebas-visuales.yml` instala Chromium y recorre los
formularios y el portal en móvil y escritorio. El resultado debe consultarse
en GitHub Actions; un éxito en las pruebas automáticas no equivale a una
auditoría profesional completa de accesibilidad o UX.

## Próximas posibilidades

- Más formas de CV y ejemplos de logros reales por profesión,
  sin copiar datos falsos del empleador.
- Lectura de textos en voz alta **con permisos explícitos** y soporte
  para navegación por teclado y lectores de pantalla.
- Filtros adicionales de salario y contrato cuando los proveedores entreguen
  datos estructurados suficientes.
- Agenda editorial actualizada periódicamente, únicamente con fuentes
  confiables y condiciones de uso respetadas.
