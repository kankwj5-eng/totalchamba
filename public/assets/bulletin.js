/* Tablón editorial TotalChanba: recursos oficiales, sin fechas ni eventos inventados. */
(() => {
  'use strict';
  const grid=document.getElementById('bulletin-grid');
  if(!grid)return;
  const status=document.getElementById('bulletin-status');
  const buttons=[...document.querySelectorAll('[data-bulletin-filter]')];
  const official=new Set(['www.tecnacional.edu.ni','tecnacional.edu.ni','empleos.uno-ca.com','www.unicef.org','unicef.org']);
  const categories={evento:{icon:'◷',label:'Actividad anunciada'},formacion:{icon:'✳',label:'Formación técnica'},convocatorias:{icon:'↗',label:'Canal de convocatorias'}};
  let items=[],filter='';
  const localDate=()=>{
    const now=new Date();
    return now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0');
  };
  function validLink(href){
    try{const u=new URL(href);return u.protocol==='https:'&&official.has(u.hostname)&&!u.username&&!u.password;}catch{return false;}
  }
  const node=(tag,text,cls)=>{
    const elem=document.createElement(tag);if(cls)elem.className=cls;
    if(text!==undefined)elem.textContent=String(text);
    return elem;
  };
  function visible(item){
    if(item.kind==='evento'&&item.expires_at&&item.expires_at<localDate())return false;
    return true;
  }
  function paint(){
    grid.replaceChildren();
    const filtered=items.filter(x=>visible(x)&&(!filter||x.kind===filter));
    buttons.forEach(b=>{const on=b.dataset.bulletinFilter===filter;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    for(const item of filtered){
      const card=node('article',undefined,'tc-agenda-card type-'+item.kind);
      const ornament=node('div',undefined,'tc-agenda-card-icon');ornament.setAttribute('aria-hidden','true');ornament.textContent=categories[item.kind].icon;
      const head=node('div',undefined,'tc-agenda-card-head');head.append(node('span',categories[item.kind].label,'tc-agenda-card-tag'),node('span','↗','tc-agenda-card-arrow'));card.append(ornament,head);
      card.append(node('h3',item.title),node('p',item.summary));
      const meta=node('div',undefined,'tc-agenda-meta');
      meta.append(node('strong',item.publisher));
      if(item.starts_at){
        const d=new Date(item.starts_at+'T12:00:00Z');
        const when=Number.isNaN(+d)?item.starts_at:d.toLocaleDateString('es-NI',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'});
        meta.append(node('span','Fecha anunciada: '+when));
      }else{
        meta.append(node('span','Directorio oficial · consultá disponibilidad'));
      }
      card.append(meta);
      const url=node('a','Consultar fuente oficial ↗','tc-agenda-open');url.href=item.url;url.target='_blank';url.rel='noopener noreferrer';
      card.append(url);grid.append(card);
    }
    if(!filtered.length){
      const empty=node('div',undefined,'tc-agenda-empty');
      empty.append(node('strong',filter==='evento'?'Todavía no tenemos eventos próximos confirmados.':'No hay novedades verificadas en esta sección.'));
      empty.append(node('p','Volvé a consultar el tablón. No publicamos actividades sin fecha y enlace comprobables.'));
      grid.append(empty);
    }
    status.textContent=filtered.length+' recursos con fuente identificada. Revisá horarios, cupos y vigencia en el portal original.';
  }
  async function load(){
    try{
      const r=await fetch('/data/bulletin.json',{cache:'no-cache'});
      if(!r.ok)throw new Error('Tablón sin respuesta');
      const data=await r.json();
      if(data.schema_version!==1||!Array.isArray(data.items))throw new Error('Formato inválido');
      items=data.items.filter(x=>x&&categories[x.kind]&&validLink(x.url)&&typeof x.title==='string'&&typeof x.summary==='string'&&typeof x.publisher==='string').slice(0,30);
      paint();
    }catch{
      grid.replaceChildren(node('p','No se pudieron cargar los avisos. Podés seguir buscando vacantes en el índice.','tc-agenda-empty'));
      status.textContent='Tablón temporalmente no disponible.';
    }
  }
  buttons.forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.bulletinFilter;paint();}));
  load();
})();