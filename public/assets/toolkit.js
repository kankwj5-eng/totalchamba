/* TotalChanba · Estudio de Candidatura (local y sin cuentas). */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const STORAGE_CV = 'totalchanba-cv-local-v1';
  const params = new URLSearchParams(location.search);
  const selectedId = /^[a-f0-9]{16}$/i.test(params.get('vacante')||'') ? params.get('vacante') : '';
  let job = null, questionIndex = 0, interviewQuestions = [];
  let timerId = null, timerRemaining = 90, timerStartedAt = 0;
  let moodIndex = 0;
  const guideDefault = {
    focus:'Elegí una vacante para adaptar la preparación a su área. Destacá experiencias que realmente puedas demostrar.',
    cv:['Presentá tu trayectoria desde la más reciente.', 'Incluí herramientas o habilidades que conozcas de verdad.', 'Revisá la descripción original antes de adaptar tu CV.'],
    interview:['¿Por qué te interesa este puesto?', 'Contá una situación difícil y cómo la resolviste.', '¿Qué preguntas harías sobre la jornada y el contrato?'],
    ask_employer:['¿Cuáles son las funciones principales?', '¿Qué modalidad y jornada tiene el puesto?', '¿Cuál es el salario y las condiciones de contratación?'],
    published_fields:[]
  };
  const areaGuides = {
    'Administración': {focus:'Demostrá precisión, organización y confidencialidad.', cv:['Contá ejemplos reales de control de documentos, atención u hojas de cálculo.', 'Indicá herramientas de oficina que dominás realmente.', 'Explicá cómo evitaste errores o mejoraste un proceso.'], interview:['¿Cómo organizás tareas con distintas fechas?', '¿Qué harías al detectar una cifra incorrecta?', '¿Cómo cuidás información confidencial?']},
    'Ventas': {focus:'Prepará ejemplos de servicio al cliente y buena comunicación.', cv:['Indicá tareas auténticas de atención, caja o ventas.', 'Resaltá resultados demostrables, sin cifras inventadas.', 'Describí cómo resolviste inquietudes de clientes.'], interview:['¿Cómo atendés a un cliente insatisfecho?', '¿Qué harías si no conocés un producto?', '¿Cómo organizás tu trabajo en horas de demanda?']},
    'Tecnología': {focus:'Mostrá proyectos, diagnóstico de problemas y capacidad de aprendizaje.', cv:['Mencioná herramientas concretas que realmente usás.', 'Incluí portafolio propio si existe.', 'Explicá un resultado técnico que puedas demostrar.'], interview:['¿Cómo investigás un problema desconocido?', 'Contá un error técnico que solucionaste.', '¿Cómo protegés la información?']},
    'Industria': {focus:'Destacá trabajo técnico verificable y seguridad.', cv:['Señalá equipos que efectivamente conocés.', 'Indicá procedimientos de seguridad que aplicaste.', 'Explicá resultados prácticos de tu oficio.'], interview:['¿Qué verificás antes de operar maquinaria?', '¿Cómo actuarías ante una falla peligrosa?', 'Explicá un trabajo de precisión que realizaste.']},
    'Logística': {focus:'Resaltá puntualidad, registro de inventarios y seguridad.', cv:['Describí inventarios o despachos que realmente manejaste.', 'Indicá licencias vigentes si aplican.', 'Incluí ejemplos de entrega y organización.'], interview:['¿Qué harías ante inventario faltante?', '¿Cómo organizás rutas o entregas?', '¿Qué prácticas de seguridad aplicás?']},
    'Salud': {focus:'Priorizá formación acreditada y seguridad de pacientes.', cv:['Indicá títulos y acreditaciones reales.', 'Describí prácticas sin compartir información de pacientes.', 'Nombrá protocolos que conozcas de verdad.'], interview:['¿Cómo manejás información privada?', '¿Cuándo pedirías apoyo a un superior?', '¿Cómo colaborás ante una urgencia?']},
    'Educación': {focus:'Mostrá estrategias pedagógicas y comunicación.', cv:['Indicá niveles y asignaturas impartidas.', 'Explicá una estrategia que haya ayudado a aprender.', 'Incluí formación docente real.'], interview:['¿Cómo adaptás una clase a distintos ritmos?', '¿Qué harías con un conflicto en el aula?', '¿Cómo evaluás el aprendizaje?']},
    'Servicios': {focus:'Mostrá trato respetuoso y confiabilidad.', cv:['Describí turnos, tareas y normas de servicio que conozcas.', 'Indicá formación o experiencia comprobable.', 'Contá una situación de atención o trabajo en equipo.'], interview:['¿Qué hacés cuando llega un reclamo?', '¿Cómo organizás un turno con mucha demanda?', '¿Qué medidas de higiene o seguridad aplicás?']}
  };
  const PLAN = [
    'Leí el anuncio original y comprobé la fecha y el enlace',
    'Confirmé que la ubicación y modalidad me convienen',
    'Revisé requisitos y anoté cualquier información faltante',
    'Preparé mi CV con experiencias y datos reales',
    'Preparé una presentación y respuestas para la entrevista',
    'Verifiqué el canal oficial antes de enviar la postulación'
  ];
  const moodPrompts = [
    'Elegí una sola vacante que te interese y anotá tres motivos.',
    'Revisá un párrafo de tu CV y quitá frases que no podás demostrar.',
    'Practicá una respuesta de entrevista de 90 segundos.',
    'Consultá una formación que refuerce tu perfil.',
    'Anotá dos preguntas que quisieras hacerle al empleador.',
    'Tomá un descanso breve y retomá cuando tengas energía.'
  ];
  function notice(msg){
    const el=$('notification');el.textContent=msg;el.hidden=false;
    clearTimeout(notice.timeout);notice.timeout=setTimeout(()=>{el.hidden=true;},3100);
  }
  function validUrl(value){
    try{const p=new URL(value);return p.protocol==='https:' && !!p.hostname && !p.username && !p.password;}
    catch{return false;}
  }
  function putText(id,value){$(id).textContent=String(value??'');}
  function el(tag,text,cls){
    const a=document.createElement(tag);if(cls)a.className=cls;if(text!==undefined)a.textContent=String(text);return a;
  }
  function listInto(id,items){
    const parent=$(id);parent.replaceChildren(...items.map(t=>el('li',t)));
  }
  function activeTab(tab){
    const key=['guia','cv','entrevista','carta','plan','animo'].includes(tab)?tab:'guia';
    document.querySelectorAll('[data-tab]').forEach(button=>{
      const on=button.dataset.tab===key;button.classList.toggle('active',on);
      if(on){button.setAttribute('aria-current','page');}else{button.removeAttribute('aria-current');}
    });
    document.querySelectorAll('.panel').forEach(panel=>{panel.hidden=panel.id!=='panel-'+key;});
    const u=new URL(location.href);u.searchParams.set('tab',key);history.replaceState(null,'',u);
  }
  function currentGuide(){
    const g=job?.career_guide;
    if(g&&g.basis==='recomendaciones_generales_por_oficio'&&Array.isArray(g.cv)&&Array.isArray(g.interview))return g;
    const category=job?.category||'';
    return {...guideDefault,...(areaGuides[category]||{})};
  }
  function guideSetup(){
    const g=currentGuide();
    putText('guide-focus',g.focus||guideDefault.focus);
    listInto('guide-cv',(g.cv||guideDefault.cv).slice(0,4));
    listInto('guide-ask',(g.ask_employer||guideDefault.ask_employer).slice(0,4));
    const facts=$('source-facts');facts.replaceChildren();
    if(!job){facts.append(el('p','No hay una vacante seleccionada. Podés usar el CV y las demás herramientas igualmente.','empty-fact'));return;}
    const mapping=[['Requisitos',job.requirements],['Experiencia',job.experience],['Formación',job.education],['Salario',job.salary],['Tipo de contrato',job.type],['Modalidad',job.modality]];
    const real=mapping.filter(([key,value])=>typeof value==='string'&&value.trim()&&!/^No especificad|^Default$/.test(value));
    if(!real.length){facts.append(el('p','La fuente no incluyó datos estructurados adicionales. Consultá la oferta original.','empty-fact'));return;}
    for(const [label,value] of real){
      const item=el('div',undefined,'source-fact');item.append(el('strong',label),el('p',value.slice(0,680)));facts.append(item);
    }
  }
  async function loadJob(){
    if(!selectedId){guideSetup();setupQuestions();setupPlan();return;}
    try{
      const response=await fetch('/data/jobs.json',{cache:'no-cache'});
      if(!response.ok)throw new Error('Índice inaccesible');
      const json=await response.json();
      job=Array.isArray(json.jobs)?json.jobs.find(item=>item?.id===selectedId&&validUrl(item.url)):null;
      if(!job){notice('No se encontró esa vacante en el índice actual. Las herramientas siguen disponibles.');}
    }catch{notice('No se pudo cargar la vacante. Podés usar las herramientas generales.');}
    if(job){
      putText('selected-title',job.title);
      putText('selected-company',job.company||'Empresa no especificada');
      const meta=$('job-context');
      meta.replaceChildren(el('span',job.location||'Nicaragua'),el('span',job.category||'Empleo'));
      for(const id of ['source-original','plan-original']){
        $(id).href=job.url;$(id).target='_blank';$(id).rel='noopener noreferrer';
      }
      const originalDate=job.published_at ? 'Publicado: '+job.published_at : 'Fecha de publicación no disponible';
      meta.append(el('span',originalDate));
    }
    guideSetup();setupQuestions();setupPlan();renderLetter();
  }
  function cvSnapshot(){
    const ids=['cv-name','cv-city','cv-email','cv-phone','cv-profile','cv-experience','cv-education','cv-skills'];
    return Object.fromEntries(ids.map(id=>[id,$(id).value.slice(0,2000)]));
  }
  function cvPreview(){
    const fields=cvSnapshot();
    putText('paper-name',fields['cv-name']||'Tu nombre completo');
    const contacts=[fields['cv-city'],fields['cv-email'],fields['cv-phone']].filter(Boolean);
    putText('paper-contact',contacts.join('  •  ')||'Ciudad · Correo · Teléfono');
    putText('paper-profile',fields['cv-profile']||'Escribí aquí un resumen auténtico de tu experiencia.');
    putText('paper-experience',fields['cv-experience']||'Tus actividades, responsabilidades y resultados demostrables.');
    putText('paper-education',fields['cv-education']||'Tu formación, cursos y certificaciones.');
    putText('paper-skills',fields['cv-skills']||'Herramientas y habilidades que realmente dominás.');
    // En pantalla hay ayudas de escritura. Al imprimir, se omiten las secciones vacías.
    for(const [field,id] of [['cv-profile','paper-profile'],['cv-experience','paper-experience'],
                             ['cv-education','paper-education'],['cv-skills','paper-skills']]){
      $(id).closest('section').classList.toggle('is-empty',!fields[field].trim());
    }
    if(!($('letter-name').value.trim()))$('letter-name').placeholder=fields['cv-name']||'Tu nombre';
  }
  function cvAudit(){
    const d=cvSnapshot();
    const criteria=[
      ['Nombre identificable',d['cv-name'].trim().length>=5],
      ['Un medio de contacto',d['cv-email'].includes('@')||d['cv-phone'].replace(/\\D/g,'').length>=7],
      ['Perfil escrito por vos',d['cv-profile'].trim().length>=25],
      ['Experiencia o formación auténtica',d['cv-experience'].trim().length>=15||d['cv-education'].trim().length>=15],
      ['Habilidades concretas',d['cv-skills'].trim().length>=6]
    ];
    const complete=criteria.filter(([,yes])=>yes).length;
    putText('cv-audit-count',complete+' de '+criteria.length);
    $('cv-audit-list').replaceChildren(...criteria.map(([label,yes])=>{
      const line=el('li',undefined,yes?'complete':'pending');
      line.append(el('span',yes?'✓':'○'),el('span',label));
      return line;
    }));
  }
  function cvRestore(){
    try{
      const data=JSON.parse(localStorage.getItem(STORAGE_CV)||'null');
      if(!data||typeof data!=='object')return;
      for(const [id,value] of Object.entries(data)){
        if($(id)&&id.startsWith('cv-')&&typeof value==='string')$(id).value=value;
      }
      notice('CV recuperado de este dispositivo');
    }catch{}
  }
  function setupCV(){
    cvRestore();cvPreview();cvAudit();
    $('cv-form').addEventListener('input',()=>{cvPreview();cvAudit();});
    $('cv-save').addEventListener('click',()=>{
      try{localStorage.setItem(STORAGE_CV,JSON.stringify(cvSnapshot()));notice('CV guardado solo en este dispositivo');}
      catch{notice('No se pudo guardar; revisá los permisos del navegador');}
    });
    $('cv-clear').addEventListener('click',()=>{
      if(!confirm('¿Borrar los datos del CV en pantalla y la copia guardada en este dispositivo?'))return;
      try{localStorage.removeItem(STORAGE_CV);}catch{}
      $('cv-form').reset();cvPreview();cvAudit();notice('Datos del CV borrados');
    });
    $('cv-print').addEventListener('click',()=>{
      if(!$('cv-name').value.trim()){notice('Escribí tu nombre para identificar tu CV.');$('cv-name').focus();return;}
      document.body.classList.add('print-cv');window.print();
    });
    window.addEventListener('afterprint',()=>document.body.classList.remove('print-cv'));
  }
  function setupQuestions(){
    interviewQuestions=(currentGuide().interview||guideDefault.interview).slice(0,6);
    if(!interviewQuestions.length)interviewQuestions=guideDefault.interview;
    questionIndex=0;renderQuestion();
  }
  function renderQuestion(){
    putText('question-count',`PREGUNTA ${questionIndex+1} / ${interviewQuestions.length}`);
    putText('question-text',interviewQuestions[questionIndex]);
  }
  function timerShow(){
    const min=String(Math.floor(timerRemaining/60)).padStart(2,'0');
    const sec=String(timerRemaining%60).padStart(2,'0');
    putText('timer-value',`${min}:${sec}`);
  }
  function timerPause(){
    if(timerId!==null){clearInterval(timerId);timerId=null;}
    $('timer-start').textContent='▶ Continuar práctica';
  }
  function timerReset(){timerPause();timerRemaining=90;timerShow();$('timer-start').textContent='▶ Comenzar práctica';}
  function setupInterview(){
    $('question-next').addEventListener('click',()=>{
      questionIndex=(questionIndex+1)%interviewQuestions.length;renderQuestion();timerReset();
    });
    $('timer-reset').addEventListener('click',timerReset);
    $('timer-start').addEventListener('click',()=>{
      if(timerId!==null){timerPause();return;}
      if(timerRemaining<=0)timerRemaining=90;
      timerStartedAt=Date.now() - (90-timerRemaining)*1000;
      timerId=setInterval(()=>{
        timerRemaining=Math.max(0,90-Math.floor((Date.now()-timerStartedAt)/1000));
        timerShow();
        if(timerRemaining<=0){timerPause();notice('Tiempo de práctica completado. Podés seguir hablando sin límite.');}
      },250);
      $('timer-start').textContent='Ⅱ Pausar';
    });
    $('star-copy').addEventListener('click',()=>{
      const fields=[['Situación','star-situation'],['Tarea','star-task'],['Acción','star-action'],['Resultado','star-result']];
      const content=fields.map(([label,id])=>label+': '+($(id).value.trim()||'[pendiente]')).join('\n\n');
      copyText(content);
    });
    document.addEventListener('visibilitychange',()=>{if(document.hidden&&timerId!==null)timerPause();});
  }
  async function copyText(content){
    try{await navigator.clipboard.writeText(content);notice('Copiado al portapapeles');}
    catch{
      const input=el('textarea');input.value=content;document.body.append(input);input.select();
      try{document.execCommand('copy');notice('Texto copiado');}
      catch{notice('Seleccioná y copiá el texto manualmente');}
      input.remove();
    }
  }
  function renderLetter(){
    const title=job?.title||'el puesto anunciado';
    const company=job?.company&&!/^Empresa no especificada/i.test(job.company)?job.company:'su organización';
    const name=$('letter-name').value.trim()||$('cv-name').value.trim();
    const interest=$('letter-interest').value.trim();
    const proof=$('letter-proof').value.trim();
    const data=[
      'Asunto: Candidatura a '+title,
      'Estimado equipo de selección de '+company+':',
      '',
      'Me gustaría presentar mi candidatura para '+title+'.',
      interest ? interest : '[Explicá con tus palabras por qué te interesa el puesto.]',
      '',
      proof ? 'Sobre mi experiencia: '+proof : '[Agregá un logro, aprendizaje o habilidad real que sea pertinente.]',
      '',
      'Quedo a disposición para conversar sobre mi experiencia y conocer mejor las responsabilidades de la plaza.',
      '',
      'Atentamente,',
      name||'[Tu nombre completo]'
    ];
    $('letter-output').value=data.join('\n');
  }
  function setupLetter(){
    $('letter-create').addEventListener('click',()=>{renderLetter();notice('Borrador actualizado. Revisalo antes de enviarlo.');});
    $('letter-copy').addEventListener('click',()=>copyText($('letter-output').value));
  }
  function planKey(){return 'totalchanba-plan-v1-'+(selectedId||'general');}
  function planRead(){
    try{
      const state=JSON.parse(localStorage.getItem(planKey())||'null');
      return state&&typeof state==='object'?state:{done:[],status:'explorando',notes:''};
    }catch{return {done:[],status:'explorando',notes:''};}
  }
  function savePlan(){
    const state={
      done:[...document.querySelectorAll('#plan-list input[type=checkbox]')].map((x,i)=>x.checked?i:null).filter(x=>x!==null),
      status:$('application-status').value,
      notes:$('application-notes').value.slice(0,1000)
    };
    try{localStorage.setItem(planKey(),JSON.stringify(state));notice('Seguimiento guardado en este dispositivo');}
    catch{notice('No se pudo guardar el seguimiento');}
  }
  function planProgress(){
    const checks=[...document.querySelectorAll('#plan-list input')];
    const completed=checks.filter(x=>x.checked).length;
    putText('plan-completed',completed+' de '+checks.length+' pasos');
    putText('plan-percent',Math.round(completed/checks.length*100)+'%');
    $('plan-bar').style.width=Math.round(completed/checks.length*100)+'%';
  }
  function setupPlan(){
    const state=planRead();
    const area=$('plan-list');area.replaceChildren();
    PLAN.forEach((step,i)=>{
      const label=el('label',undefined,'plan-step');
      const box=document.createElement('input');box.type='checkbox';box.checked=Array.isArray(state.done)&&state.done.includes(i);
      box.addEventListener('change',planProgress);
      label.append(box,el('span',step));area.append(label);
    });
    $('application-status').value=['explorando','preparando','enviada','entrevista','respuesta'].includes(state.status)?state.status:'explorando';
    $('application-notes').value=typeof state.notes==='string'?state.notes.slice(0,1000):'';
    planProgress();
  }
  function bindPlan(){
    $('application-save').addEventListener('click',savePlan);
    $('plan-clear').addEventListener('click',()=>{
      if(!confirm('¿Reiniciar el seguimiento de esta vacante en este dispositivo?'))return;
      try{localStorage.removeItem(planKey());}catch{}
      setupPlan();notice('Seguimiento reiniciado');
    });
  }
  function setupMood(){
    $('mood-next').addEventListener('click',()=>{
      putText('mood-prompt',moodPrompts[moodIndex%moodPrompts.length]);moodIndex++;
    });
  }
  function bindTabs(){
    document.querySelectorAll('[data-tab]').forEach(btn=>btn.addEventListener('click',()=>activeTab(btn.dataset.tab)));
    document.querySelectorAll('[data-jump]').forEach(btn=>btn.addEventListener('click',()=>{
      activeTab(btn.dataset.jump);document.querySelector('.tool-tabs').scrollIntoView({behavior:'smooth',block:'start'});
    }));
    activeTab(params.get('tab')||'guia');
  }
  function start(){
    bindTabs();setupCV();setupInterview();setupLetter();bindPlan();setupMood();
    loadJob();
  }
  start();
})();