/* TotalChanba 5.1 · interfaz estática, sin seguimiento de personas ni cuentas. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const FALLBACK_SOURCES = [
    {id:'encuentra24',name:'Encuentra24',url:'https://www.encuentra24.com/nicaragua-es/empleos-ofertas-de-trabajos',focus:'Oficios y empleo local',kind:'portal',collection:'directorio'},
    {id:'tecoloco',name:'Tecoloco',url:'https://www.tecoloco.com.ni/',focus:'Empresas y profesionales',kind:'portal',collection:'directorio'},
    {id:'computrabajo',name:'Computrabajo',url:'https://ni.computrabajo.com/',focus:'Empleo formal',kind:'portal',collection:'directorio'}
  ];
  const savedKey = 'totalchanba-favorites-v1';
  const searchKeys = ['q','departamento','area','modalidad','fuente','dias','salario','orden','claridad','mapa','revision'];
  const state = {search:'',department:'',category:'',modality:'',source:'',days:'',salaryOnly:false,favoritesOnly:false,minStars:'',mapPrecision:'',review:'',sort:'recent'};
  let allJobs=[], allSources=FALLBACK_SOURCES, favorites=new Set(), shown=8;
  let sourceTerm='', sourceKind='', loadFailed=false, messageTimer=0, generatedAt=null;
  const comparison=new Set();
  const sourceById = new Map();

  const html = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fold = v => String(v ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es').replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
  const tokens = v => fold(v).split(' ').filter(Boolean).slice(0,10);
  const safeLink = v => {try {const u=new URL(v);return u.protocol==='https:' && !!u.hostname && !u.username && !u.password;} catch{return false;}};
  const dateUTC = v => {if(!v)return null;const d=new Date(String(v).length===10?v+'T12:00:00Z':v);return Number.isNaN(+d)?null:d;};
  const when = v => {const d=dateUTC(v);return d?d.toLocaleDateString('es-NI',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}):'Fecha no publicada';};
  const initials = v => {const words=String(v||'').replace(/[^\p{L}\d ]/gu,'').split(/\s+/).filter(Boolean);return (words.length>1?words[0][0]+words[1][0]:(words[0]||'NI').slice(0,2)).toUpperCase();};
  const countFmt = n => new Intl.NumberFormat('es-NI').format(n);
  // La fecha de publicación puede faltar. La última consulta no demuestra que la plaza siga abierta.
  function inLastCollection(job){
    const checked=dateUTC(job.verified_at),run=dateUTC(generatedAt);
    return Boolean(checked&&run&&Math.abs(checked.getTime()-run.getTime())<=30*60000);
  }
  const clipText=(v,length=125)=>String(v||'').trim().slice(0,length);
  function toast(message){const el=$('toast');el.textContent=message;el.classList.add('visible');clearTimeout(messageTimer);messageTimer=setTimeout(()=>el.classList.remove('visible'),2900);}
  function loadFavorites(){try{const data=JSON.parse(localStorage.getItem(savedKey)||'[]');favorites=new Set(Array.isArray(data)?data.filter(x=>typeof x==='string').slice(0,1000):[]);}catch{favorites=new Set();}}
  function persistFavorites(){try{localStorage.setItem(savedKey,JSON.stringify([...favorites]));}catch{toast('No se pudieron guardar favoritos en este navegador');}}
  function readQuery(){
    const p=new URLSearchParams(location.search);
    state.search=(p.get('q')||'').slice(0,150);
    for(const [field,key] of [['department','departamento'],['category','area'],['modality','modalidad'],['source','fuente'],['days','dias']])state[field]=(p.get(key)||'').slice(0,80);
    state.salaryOnly=p.get('salario')==='1';
    state.minStars=/^[345]$/.test(p.get('claridad')||'')?p.get('claridad'):'';
    state.mapPrecision=['region','address'].includes(p.get('mapa'))?p.get('mapa'):'';
    state.review=['latest','earlier'].includes(p.get('revision'))?p.get('revision'):'';
    if(['recent','relevance','title','source','clarity'].includes(p.get('orden')))state.sort=p.get('orden');
  }
  function queryUrl(){
    const p=new URLSearchParams(location.search);for(const k of searchKeys)p.delete(k);
    for(const [key,value] of [['q',state.search],['departamento',state.department],['area',state.category],['modalidad',state.modality],['fuente',state.source],['dias',state.days],['salario',state.salaryOnly?'1':''],['claridad',state.minStars],['mapa',state.mapPrecision],['revision',state.review],['orden',state.sort==='recent'?'':state.sort]]){if(value)p.set(key,value);}
    return `${location.origin}${location.pathname}${p.toString()?'?'+p.toString():''}${location.hash||''}`;
  }
  function syncUrl(){history.replaceState(null,'',queryUrl());}
  function syncFilters(){
    for(const [id,val] of [['search',state.search],['quick-dept',state.department],['filter-dept',state.department],['filter-cat',state.category],['filter-mode',state.modality],['filter-source',state.source],['filter-date',state.days],['filter-clarity',state.minStars],['filter-map',state.mapPrecision],['filter-review',state.review],['sort',state.sort]])$(id).value=val;
    $('salary-only').checked=state.salaryOnly;
    $('favorites-only').checked=state.favoritesOnly;
  }
  function populate(id,field,exclude=[]){
    const el=$(id);const keep=el.querySelector('option')?.cloneNode(true);el.replaceChildren(keep);
    const values=new Map();
    for(const job of allJobs){const v=job[field];if(!v||exclude.includes(v))continue;values.set(v,(values.get(v)||0)+1);}
    const sorted=[...values].sort((a,b)=>a[0].localeCompare(b[0],'es'));
    for(const [label,n] of sorted){const opt=document.createElement('option');opt.value=label;opt.textContent=`${label} · ${n}`;el.append(opt);}
  }
  function populateSources(){
    const el=$('filter-source'),first=el.querySelector('option')?.cloneNode(true);
    el.replaceChildren(first);
    const values=new Map();
    for(const job of allJobs){values.set(job.source,(values.get(job.source)||0)+1);}
    for(const s of allSources.filter(s=>values.has(s.id)).sort((a,b)=>a.name.localeCompare(b.name,'es'))){
      const opt=document.createElement('option');opt.value=s.id;opt.textContent=`${s.name} · ${values.get(s.id)}`;el.append(opt);
    }
  }
  function initData(data){
    allJobs=Array.isArray(data.jobs)?data.jobs.filter(j=>j&&typeof j.id==='string'&&j.title&&safeLink(j.url)):[];
    generatedAt=data.generated_at||null;
    allSources=Array.isArray(data.sources)&&data.sources.length?data.sources.filter(s=>s&&s.id&&s.name&&safeLink(s.url)):FALLBACK_SOURCES;
    sourceById.clear();for(const source of allSources)sourceById.set(source.id,source);
    $('stat-jobs').textContent=countFmt(allJobs.length);
    $('stat-sources').textContent=countFmt(allSources.length);
    $('stat-date').textContent=data.generated_at?when(data.generated_at):'Sin actualizar';
    const reviewed=allJobs.filter(inLastCollection).length;
    $('stat-reviewed').textContent=countFmt(reviewed);
    $('stat-carried').textContent=countFmt(allJobs.length-reviewed);
    $('stat-collectors').textContent=countFmt(allSources.filter(s=>s.status==='actualizada'||s.status==='sin_resultados').length);
    $('health-note').textContent='La última consulta incorpora publicaciones de fuentes externas; una recopilación reciente no garantiza que el puesto continúe abierto.';
    const dataNotice=$('data-notice');
    if(dataNotice){
      const last=dateUTC(data.generated_at);
      const old=last && (Date.now()-last.getTime())>7*86400000;
      const sample=Object.values(data.metadata?.collection_status||{}).includes('muestra_inicial');
      dataNotice.hidden=!(old||sample);
      dataNotice.textContent=sample
        ?`Aviso de transparencia: este índice contiene ofertas de muestra observadas el ${last?when(data.generated_at):'día indicado en las fuentes'}. No significa que sigan abiertas. Confirmá siempre la vacante en el portal original.`
        :`Los datos fueron generados el ${last?when(data.generated_at):'día indicado'} y pueden estar desactualizados. Consultá los portales de origen.`;
    }
    populate('quick-dept','department',['Nicaragua']);populate('filter-dept','department',['Nicaragua']);populate('filter-cat','category');populateSources();
    if(![...$('filter-dept').options].some(x=>x.value===state.department))state.department='';
    if(![...$('filter-cat').options].some(x=>x.value===state.category))state.category='';
    if(![...$('filter-source').options].some(x=>x.value===state.source))state.source='';
    syncFilters();renderSources();renderRadar();renderJobs();
  }
  function rank(job,words){
    const title=fold(job.title),company=fold(job.company),cat=fold(job.category),place=fold(job.location);
    return words.reduce((score,word)=>score+(title.includes(word)?12:0)+(company.includes(word)?7:0)+(cat.includes(word)?4:0)+(place.includes(word)?3:0),0);
  }
  function filteredJobs(){
    const words=tokens(state.search);
    const now=new Date();
    const filtered=allJobs.filter(j=>{
      if(state.favoritesOnly&&!favorites.has(j.id))return false;
      if(state.review==='latest'&&!inLastCollection(j))return false;
      if(state.review==='earlier'&&inLastCollection(j))return false;
      if(state.department&&j.department!==state.department)return false;
      if(state.category&&j.category!==state.category)return false;
      if(state.modality&&!fold(j.modality).includes(fold(state.modality)))return false;
      if(state.source&&j.source!==state.source&&!j.also_on?.some(x=>x.source===state.source))return false;
      if(state.salaryOnly&&!j.salary)return false;
      if(state.minStars&&(j.clarity?.stars||1)<Number(state.minStars))return false;
      if(state.mapPrecision==='region'&&!['region','address'].includes(j.maps?.precision))return false;
      if(state.mapPrecision==='address'&&j.maps?.precision!=='address')return false;
      if(state.days){const date=dateUTC(j.published_at);if(!date||+date>+now+86400000||(+now-(+date))/86400000>Number(state.days))return false;}
      if(words.length){const corpus=fold([j.title,j.company,j.location,j.department,j.summary,j.category,j.source].join(' '));if(!words.every(w=>corpus.includes(w)))return false;}
      return true;
    });
    filtered.sort((a,b)=>{
      if(state.sort==='clarity'){const d=(b.clarity?.score||0)-(a.clarity?.score||0);if(d)return d;}
      if(state.sort==='title')return a.title.localeCompare(b.title,'es');
      if(state.sort==='source')return a.source.localeCompare(b.source,'es');
      if(state.sort==='relevance'&&words.length){const d=rank(b,words)-rank(a,words);if(d)return d;}
      const latest=(j)=>j.published_at||j.verified_at||'';
      return latest(b).localeCompare(latest(a));
    });
    return filtered;
  }
  function mapUrl(info){
    if(!info||!['region','address'].includes(info.precision)||!info.query)return null;
    const q=new URLSearchParams({api:'1',query:String(info.query).slice(0,240)});
    if(/^[A-Za-z0-9_-]{8,200}$/.test(info.place_id||''))q.set('query_place_id',info.place_id);
    return `https://www.google.com/maps/search/?${q}`;
  }
  function clarityUi(j){
    const c=j.clarity||{}, stars=Math.max(1,Math.min(5,Number(c.stars)||1));
    const found=(c.present||[]).map(x=>`<li>✓ ${html(x.label)}</li>`).join('');
    const missing=(c.missing||[]).map(x=>`<li>— Falta: ${html(x.label)}</li>`).join('');
    return `<div class="clarity-row"><span class="clarity-stars" aria-label="${stars} de 5 estrellas en claridad del anuncio">${'★'.repeat(stars)}<i>${'☆'.repeat(5-stars)}</i></span><b>${stars}/5</b><span>claridad del anuncio</span></div>
      <details class="clarity-details"><summary>¿Por qué ${stars} estrellas?</summary><div class="detail-content"><p><b>${Number(c.score)||0}/100 puntos de información.</b> No es una calificación de la empresa ni de su salario.</p><ul>${found}${missing}</ul><p class="identity-note">◎ Identidad del empleador: ${c.employer_verified?'revisión documental disponible':'no verificada por TotalChanba'}.</p></div></details>`;
  }
  /* La imagen es ilustrativa del oficio y nunca se presenta como una foto del empleador. */
  // Selección determinista de fotografía por función. Nunca se usan retratos reales de empleadores.
  const pictures = [
    ['industry',/torn|f[aá]brica|m[aá]quin|operari|soldad|industr|producc|mec[aá]nic|metal|electric/i],
    ['construction',/construc|obra|albañil|arquitect|ingenier[íi]a civil|fontaner/i],
    ['health',/enfermer|m[eé]dic|cl[ií]nic|farmacia|odontolog|laboratorio cl[ií]nico|salud/i],
    ['agriculture',/agric|cultiv|campo|granja|ganader|cosecha|agronom/i],
    ['logistics',/chofer|conductor|cami[oó]n|bodega|almac[eé]n|log[ií]st|transport|repart|mensajer|inventario/i],
    ['kitchen',/cocin|pizz|chef|restauran|alimento|panader|meser/i],
    ['cleaning',/limpiez|conserj|aseo|higiene/i],
    ['security',/guardia|seguridad|vigil|custod/i],
    ['finance',/contab|digitaci[oó]n|finanz|factur|auditor|tesorer|planilla/i],
    ['support',/call.?center|cobro|atenci[oó]n|cliente|telefon|soporte|telemercadeo/i],
    ['sales',/venta|comerc|asesor|tienda|caja|dependient|promotor/i],
    ['office',/.*/]
  ];
  const animalAvatars=['🦊','🐼','🐻','🐨','🐰','🦉','🐯','🐸','🦝','🐧','🐱','🐶'];
  function jobPicture(j){
    const str=[j.title,j.category].join(' ');
    return pictures.find(([k,regex])=>regex.test(str))?.[0]||'office';
  }
  function animalFor(company){
    let sum=0;for(const c of String(company||'Empresa'))sum=(sum*31+c.codePointAt(0))>>>0;
    return animalAvatars[sum%animalAvatars.length];
  }
  function jobCard(j){
    const source=sourceById.get(j.source);
    const saved=favorites.has(j.id),compared=comparison.has(j.id);
    const info=j.maps||{}, map=mapUrl(info);
    const company=j.company||'Empleador no indicado';
    const image=jobPicture(j);
    const verified=Boolean(j.clarity?.employer_verified&&safeLink(j.clarity.employer_evidence?.proof_url));
    const date=j.published_at?when(j.published_at):'Fecha no publicada';
    const recentlyChecked=inLastCollection(j);
    const freshnessText=recentlyChecked?'Recopilada en la última consulta':j.verified_at?'Conservada de otra consulta · última lectura '+when(j.verified_at):'Sin comprobación documentada';
    const detailChips=[['Experiencia',j.experience],['Formación',j.education],['Beneficios',j.benefits],['Requisitos',j.requirements]]
      .filter(([,value])=>typeof value==='string'&&value.trim()).slice(0,3);
    const highlights=detailChips.length?'<div class="tc-highlights" aria-label="Datos disponibles del anuncio">'+detailChips.map(([label,value])=>`<div><b>${html(label)}</b><span>${html(clipText(value,105))}</span></div>`).join('')+'</div>':'';
    const salary=j.salary||'No publicado';
    const modality=j.modality&&j.modality!=='No especificada'?j.modality:'No indicada';
    const type=j.type&&j.type!=='No especificado'?j.type:'No indicado';
    const place=j.location||j.department||'Sin ubicación publicada';
    const precision=info.precision==='address'?'Dirección declarada · pendiente de confirmar sede':info.precision==='region'?'Zona aproximada · no es sede exacta':'Ubicación no verificable';
    const mapMarkup=map?`<a class="tc-maps-link" href="${html(map)}" target="_blank" rel="noopener noreferrer">⌖ Buscar zona en Google Maps ↗</a>`:'<span class="tc-map-missing">Sin mapa disponible</span>';
    const alternatives=Array.isArray(j.also_on)?j.also_on.filter(a=>safeLink(a.url)):[];
    const also=alternatives.length?`<div class="tc-also"><b>También publicada en</b>${alternatives.map(a=>`<a href="${html(a.url)}" target="_blank" rel="noopener noreferrer">${html(sourceById.get(a.source)?.name||a.source)} ↗</a>`).join('')}</div>`:'';
    const thumb=`/assets/occupations/${image}.webp`;
    const label=j.category||'Empleo';
    const questions=[];
    if(!j.salary)questions.push('¿Cuál es el salario base, la moneda y cada cuánto se paga?');
    if(!j.type||/^No especificad/i.test(j.type))questions.push('¿Cuál es la jornada y el tipo de contrato?');
    if(info.precision!=='address'&&j.modality!=='Remoto')questions.push('¿Cuál es la sede exacta de trabajo?');
    if(!j.requirements)questions.push('¿Qué experiencia y habilidades son indispensables?');
    const questionsHtml=questions.length?`<div class="tc-interview-prep"><strong>Preguntas útiles antes de postular</strong><ul>${questions.slice(0,3).map(q=>`<li>${html(q)}</li>`).join('')}</ul><small>Son sugerencias para vos; no respuestas del anunciante.</small></div>`:'';
    const details=[['Requisitos publicados',j.requirements],['Experiencia solicitada',j.experience],['Formación indicada',j.education],['Beneficios publicados',j.benefits]]
      .filter(([name,value])=>typeof value==='string'&&value.trim())
      .map(([name,value])=>`<div class="tc-expanded-fact"><strong>${html(name)}</strong><p>${html(value)}</p></div>`).join('');
    return `<article class="job-card tc-job" aria-labelledby="title-${html(j.id)}">
      <div class="tc-card-head">
        <div class="tc-company-avatar" role="img" aria-label="Avatar ilustrativo de animalito, no es el logo de la empresa">${animalFor(company)}</div>
        <div class="tc-company-info"><strong>${html(company)}</strong><div class="tc-company-sub"><span>${html(label)}</span><span class="tc-separator">•</span><span>Publicado: ${html(date)}</span></div>
        <span class="tc-company-trust ${verified?'is-verified':''}">${verified?'✓ Empresa con identidad revisada':'◌ Identidad empresarial no verificada'}</span>
        <span class="tc-review-status ${recentlyChecked?'is-recent':'is-older'}">${recentlyChecked?'●':'◷'} ${html(freshnessText)}</span></div>
        <button class="save-job tc-save ${saved?'active':''}" data-save="${html(j.id)}" type="button" aria-label="${saved?'Quitar de guardados':'Guardar vacante'}: ${html(j.title)}" aria-pressed="${saved}">${saved?'♥':'♡'}</button>
      </div>
      <div class="tc-job-lead"><div class="tc-job-title"><div class="tc-eyebrow">OFERTA DE TRABAJO <span>·</span> ${html(source?.name||j.source)}</div><h3 id="title-${html(j.id)}">${html(j.title)}</h3><p>${html(j.summary||'La fuente no publicó una descripción resumida. Revisá los detalles en el anuncio original.')}</p><a class="tc-quick-link" href="${html(j.url)}" target="_blank" rel="noopener noreferrer">Leer publicación original ↗</a></div>
        <div class="tc-photo"><img src="${thumb}" loading="lazy" alt="Imagen generada con IA de un entorno de ${html(image)}; no representa a esta empresa ni su sede"/><span>IMAGEN ILUSTRATIVA · GENERADA CON IA</span></div>
      </div>
      <div class="tc-facts" aria-label="Datos principales del empleo">
        <div class="tc-fact tc-location"><span class="tc-fact-icon">⌖</span><div><small>Ubicación</small><strong>${html(place)}</strong></div></div>
        <div class="tc-fact tc-mode"><span class="tc-fact-icon">▣</span><div><small>Modalidad</small><strong>${html(modality)}</strong></div></div>
        <div class="tc-fact tc-type"><span class="tc-fact-icon">◷</span><div><small>Jornada o contrato</small><strong>${html(type)}</strong></div></div>
        <div class="tc-fact tc-salary"><span class="tc-fact-icon">◈</span><div><small>Salario publicado</small><strong>${html(salary)}</strong></div></div>
      </div>
      <div class="tc-middle"><div class="tc-about"><div class="tc-subheading"><span>◈</span> Qué sabemos de esta vacante</div>
        ${highlights}<dl class="tc-specs"><div><dt>Área de trabajo</dt><dd>${html(label)}</dd></div><div><dt>Empresa anunciada</dt><dd>${html(company)}</dd></div><div><dt>Salario</dt><dd>${html(j.salary||'No informado; consultar al empleador')}</dd></div><div><dt>Fecha de publicación</dt><dd>${html(date)}</dd></div></dl>
        <details class="tc-requirements"><summary>Ver requisitos, beneficios y datos no publicados <span>⌄</span></summary><div class="tc-requirement-body"><p>La descripción disponible es: ${html(j.summary||'No hay descripción resumida.')}</p>${details||'<p>Esta fuente no facilitó requisitos, experiencia, formación ni beneficios estructurados. Revisá el anuncio original para conocerlos.</p>'}<p>Para información no publicada aquí y para postular, consultá siempre la fuente original.</p>${questionsHtml}</div></details>
      </div><div class="tc-trust-panel"><div class="tc-subheading"><span>✳</span> Transparencia del anuncio</div>${clarityUi(j)}<div class="tc-trust-explain">Las estrellas califican los <b>datos publicados</b>, no la reputación ni la seguridad de la empresa.</div><div class="tc-map-block"><strong>⌖ Ubicación para orientarte</strong><small>${html(precision)}</small>${mapMarkup}</div></div></div>
      ${also}
      <div class="tc-card-footer"><div class="tc-provenance"><span class="tc-source-dot"></span><span>Vía <b>${html(source?.name||j.source)}</b>${j.verified_at?` · Datos revisados ${html(when(j.verified_at))}`:''}</span></div><div class="tc-card-actions"><button class="compare-button ${compared?'selected':''}" type="button" data-compare="${html(j.id)}" aria-pressed="${compared}">${compared?'✓ Comparando':'⇄ Comparar'}</button><button type="button" class="tc-share-job" data-share="${html(j.id)}" aria-label="Compartir enlace original de ${html(j.title)}">↗ Compartir</button><a class="tc-apply" href="${html(j.url)}" target="_blank" rel="noopener noreferrer" aria-label="Postular en anuncio original de ${html(j.title)}">Ver oferta original <span aria-hidden="true">↗</span></a></div></div>
    </article>`;
  }
  function renderRadar(){
    const el=$('radar-departments');if(!el)return;
    const counts=new Map();for(const j of allJobs){if(j.department&&j.department!=='Nicaragua')counts.set(j.department,(counts.get(j.department)||0)+1);}
    const total=Math.max(1,...counts.values());
    el.innerHTML=[...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'es')).map(([name,n])=>`<button type="button" class="radar-item ${state.department===name?'chosen':''}" data-radar="${html(name)}" aria-pressed="${state.department===name}"><span class="radar-place">${html(name)}</span><span class="radar-track"><span style="width:${Math.round(n/total*100)}%"></span></span><b>${n}</b></button>`).join('')||'<p>Sin ubicaciones territoriales documentadas.</p>';
  }
  function renderCompare(){
    const tray=$('compare-tray'),grid=$('compare-grid');if(!tray)return;
    for(const id of [...comparison])if(!allJobs.find(j=>j.id===id))comparison.delete(id);
    tray.hidden=comparison.size===0;
    grid.innerHTML=[...comparison].map(id=>{
      const j=allJobs.find(x=>x.id===id);if(!j)return '';
      return `<section class="compare-item"><span>${html(j.category||'Empleo')}</span><h4>${html(j.title)}</h4><p>${html(j.company||'Empleador no indicado')}</p><dl><div><dt>Zona</dt><dd>${html(j.location)}</dd></div><div><dt>Salario publicado</dt><dd>${html(j.salary||'No informado')}</dd></div><div><dt>Claridad</dt><dd>${j.clarity?.stars||1}/5 ★</dd></div><div><dt>Identidad verificada</dt><dd>${j.clarity?.employer_verified?'Identidad revisada':'No'}</dd></div></dl><a href="${html(j.url)}" target="_blank" rel="noopener noreferrer">Anuncio original ↗</a><button type="button" data-compare="${html(j.id)}" aria-label="Quitar ${html(j.title)} de la comparación">Quitar ✕</button></section>`;
    }).join('');
  }
  function renderJobs(){
    const jobs=filteredJobs(),grid=$('job-grid');
    $('matching-counter').textContent=countFmt(jobs.length);
    $('visible-count').textContent=jobs.length?`${countFmt(Math.min(shown,jobs.length))} de ${countFmt(jobs.length)}`:'';
    $('saved-count').textContent=countFmt(favorites.size);
    $('results-heading').textContent=state.favoritesOnly?'Empleos guardados':state.search?'Resultados de tu búsqueda':'Oportunidades en el índice';
    $('toggle-saved').setAttribute('aria-pressed',String(state.favoritesOnly));
    $('favorites-only').checked=state.favoritesOnly;
    const filters=[state.review==='latest'&&'recopiladas en la última consulta',state.review==='earlier'&&'conservadas de otras consultas',state.search&&`“${state.search}”`,state.department,state.category,state.modality,state.days&&`últimos ${state.days} días`,state.salaryOnly&&'con salario',state.minStars&&`${state.minStars}+ estrellas de claridad`,state.mapPrecision==='address'&&'dirección declarada',state.source&&sourceById.get(state.source)?.name].filter(Boolean);
    $('search-feedback').textContent=filters.length?`Filtros activos: ${filters.join(' · ')}`:'Mostrando las ofertas indexadas; las fuentes del directorio se encuentran más abajo.';
    if(!jobs.length){
      const title=loadFailed?'No se pudo cargar el índice':state.favoritesOnly?'No hay ofertas guardadas con estos filtros':'No hay ofertas que coincidan';
      const detail=loadFailed?'Podés consultar directamente nuestro directorio de portales.':'Cambiá los filtros o buscá también en las plataformas del directorio.';
      grid.innerHTML=`<div class="empty-state"><span class="empty-icon" aria-hidden="true">◎</span><h3>${html(title)}</h3><p>${html(detail)}</p><button type="button" id="empty-reset">${loadFailed?'Ir al directorio':'Limpiar filtros'}</button></div>`;
      $('empty-reset').addEventListener('click',()=>loadFailed?document.querySelector('#fuentes').scrollIntoView({behavior:'smooth'}):reset());
    } else grid.innerHTML=jobs.slice(0,shown).map(jobCard).join('');
    $('load-more').hidden=shown>=jobs.length;
    renderRadar();renderCompare();
  }
  function sourceGroup(kind){
    if(['portal','local','agregador','remoto'].includes(kind))return 'portal';
    return kind;
  }
  function renderSources(){
    const list=allSources.filter(s=>safeLink(s.url) && (!sourceKind||sourceGroup(s.kind)===sourceKind) && (!sourceTerm||fold([s.name,s.focus,s.kind].join(' ')).includes(fold(sourceTerm))));
    $('source-count').textContent=`${countFmt(list.length)} fuentes para explorar · las ofertas indexadas se muestran arriba por separado.`;
    $('sources-grid').innerHTML=list.length?list.map(s=>{
      const online=s.status==='actualizada';
      const status=online?`${s.jobs_count||0} ofertas en el índice`:s.status==='muestra_inicial'?`${s.jobs_count||0} ofertas de muestra · sin revisión en vivo`:s.status==='sin_resultados'?'Revisada · sin ofertas':s.status==='no_disponible'?'Actualización pendiente':s.status==='requiere_configuracion'?'Integración pendiente':'Abrir portal original';
      return `<a class="source-card" href="${html(s.url)}" target="_blank" rel="noopener noreferrer" aria-label="Explorar ${html(s.name)} en nueva pestaña"><div class="source-card-top"><span class="source-mark" aria-hidden="true">${html(initials(s.name))}</span><span class="source-external" aria-hidden="true">↗</span></div><h3>${html(s.name)}</h3><p>${html(s.focus||'Explorar oportunidades')}</p><div class="source-kind ${online?'':'direct'}"><i></i>${html(status)}</div></a>`;
    }).join(''):`<div class="sources-empty">No hay fuentes en esta sección. Probá con otra búsqueda.</div>`;
    document.querySelectorAll('[data-source-kind]').forEach(btn=>{const selected=btn.dataset.sourceKind===sourceKind;btn.classList.toggle('selected',selected);btn.setAttribute('aria-pressed',String(selected));});
  }
  function changed(){shown=8;syncFilters();syncUrl();renderJobs();}
  function reset(){Object.assign(state,{search:'',department:'',category:'',modality:'',source:'',days:'',salaryOnly:false,favoritesOnly:false,minStars:'',mapPrecision:'',review:'',sort:'recent'});changed();}
  function bind(){
    $('search').addEventListener('input',e=>{state.search=e.target.value.slice(0,150);changed();});
    $('search-button').addEventListener('click',()=>{document.querySelector('.results-area').scrollIntoView({behavior:'smooth',block:'start'});$('search').blur();});
    for(const [id,key] of [['quick-dept','department'],['filter-dept','department'],['filter-cat','category'],['filter-mode','modality'],['filter-source','source'],['filter-date','days'],['filter-clarity','minStars'],['filter-map','mapPrecision'],['filter-review','review'],['sort','sort']])$(id).addEventListener('change',e=>{state[key]=e.target.value;changed();});
    $('salary-only').addEventListener('change',e=>{state.salaryOnly=e.target.checked;changed();});
    $('reset-filters').addEventListener('click',reset);
    $('favorites-only').addEventListener('change',e=>{state.favoritesOnly=e.target.checked;changed();});
    $('toggle-saved').addEventListener('click',()=>{state.favoritesOnly=!state.favoritesOnly;changed();});
    $('load-more').addEventListener('click',()=>{shown+=8;renderJobs();});
    $('export-saved').addEventListener('click',()=>{
      const selected=allJobs.filter(j=>favorites.has(j.id));
      if(!selected.length){toast('Guardá una vacante antes de exportarla');return;}
      const columns=[['Puesto','title'],['Empresa','company'],['Departamento','department'],['Ubicación','location'],['Modalidad','modality'],['Contrato','type'],['Salario como publicado','salary'],['Última consulta','verified_at'],['Publicada','published_at'],['Origen','source'],['Enlace original','url']];
      const cell=value=>{
        let v=String(value??'').replace(/[\r\n]+/g,' ').trim();
        if(/^[=+\-@\t]/.test(v))v="'"+v; // Evita fórmulas ejecutables al abrir en una hoja de cálculo.
        return '"'+v.replace(/"/g,'""')+'"';
      };
      const csv='\uFEFF'+[columns.map(x=>cell(x[0])).join(','),...selected.map(j=>columns.map(([,key])=>cell(j[key])).join(','))].join('\r\n');
      const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
      const link=document.createElement('a');link.href=url;link.download='TotalChanba_mis_guardados.csv';
      document.body.append(link);link.click();link.remove();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
      toast('Descargadas '+countFmt(selected.length)+' vacantes guardadas');
    });
    $('share-search').addEventListener('click',async()=>{
      const url=queryUrl();
      try {await navigator.clipboard.writeText(url);toast('Enlace a esta búsqueda copiado');}
      catch {const temp=document.createElement('textarea');temp.value=url;document.body.append(temp);temp.select();const copied=document.execCommand('copy');temp.remove();toast(copied?'Enlace copiado':'Copiá la dirección desde tu navegador');}
    });
    document.querySelectorAll('[data-quick]').forEach(el=>el.addEventListener('click',()=>{
      const val=el.dataset.quick;reset();if(val==='Remoto')state.modality='Remoto';else state.category=val;
      changed();document.querySelector('#empleos').scrollIntoView({behavior:'smooth'});
    }));
    $('job-grid').addEventListener('click',e=>{
      const cb=e.target.closest('[data-compare]');
      if(cb){const id=cb.dataset.compare;if(comparison.has(id))comparison.delete(id);else if(comparison.size>=3){toast('Podés comparar hasta tres ofertas');return;}else comparison.add(id);renderJobs();return;}
      const share=e.target.closest('[data-share]');
      if(share){const job=allJobs.find(j=>j.id===share.dataset.share);if(job){
        const copy=async()=>{try{await navigator.clipboard.writeText(job.url);toast('Enlace del anuncio original copiado');}catch{toast('Usá el botón Ver oferta original para abrir la publicación');}};
        if(navigator.share){navigator.share({title:job.title,text:`${job.title} · ${job.company}`,url:job.url}).catch(()=>{});}else copy();
      }return;}
      const btn=e.target.closest('[data-save]');if(!btn)return;
      const id=btn.dataset.save;
      if(favorites.has(id)){favorites.delete(id);toast('Eliminada de tus guardados');}
      else{favorites.add(id);toast('Guardada en este dispositivo ♥');}
      persistFavorites();renderJobs();
    });
    $('radar-departments').addEventListener('click',e=>{const btn=e.target.closest('[data-radar]');if(!btn)return;state.department=state.department===btn.dataset.radar?'':btn.dataset.radar;changed();document.querySelector('#empleos').scrollIntoView({behavior:'smooth'});});
    $('clear-radar').addEventListener('click',()=>{state.department='';changed();});
    $('compare-clear').addEventListener('click',()=>{comparison.clear();renderJobs();});
    $('compare-tray').addEventListener('click',e=>{const btn=e.target.closest('[data-compare]');if(!btn)return;comparison.delete(btn.dataset.compare);renderJobs();});
    $('readable-mode').addEventListener('click',()=>{const enabled=document.body.classList.toggle('reading-mode');$('readable-mode').setAttribute('aria-pressed',String(enabled));toast(enabled?'Lectura clara activada':'Vista original restaurada');});
    $('source-search').addEventListener('input',e=>{sourceTerm=e.target.value.slice(0,100);renderSources();});
    document.querySelectorAll('[data-source-kind]').forEach(btn=>btn.addEventListener('click',()=>{sourceKind=btn.dataset.sourceKind;renderSources();}));
    document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName)){e.preventDefault();$('search').focus();$('empleos').scrollIntoView({behavior:'smooth'});}});
    window.addEventListener('popstate',()=>{readQuery();syncFilters();renderJobs();});
  }
  async function start(){
    loadFavorites();readQuery();bind();renderSources();
    try{
      const response=await fetch('/data/jobs.json',{cache:'no-cache'});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      initData(await response.json());
    }catch(e){console.warn('No se pudo leer el índice:',e);loadFailed=true;initData({jobs:[],sources:FALLBACK_SOURCES});}
  }
  start();
})();
