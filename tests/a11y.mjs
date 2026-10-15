/* Auditoría automatizada WCAG 2.1 A/AA con axe-core para páginas clave. */
import { chromium } from 'playwright';
import axe from 'axe-core';

const origin=process.env.SITE_URL||'http://127.0.0.1:4173';
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const screens=[
  {route:'/',name:'Buscador y directorio'},
  {route:'/herramientas.html',name:'Estudio: guía'},
  {route:'/herramientas.html?tab=cv',name:'Estudio: CV'},
  {route:'/herramientas.html?tab=entrevista',name:'Estudio: entrevista'},
  {route:'/herramientas.html?tab=plan',name:'Estudio: seguimiento'},
];
let blockers=[];
try{
 for(const screen of screens){
   const page=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
   await page.goto(origin+screen.route,{waitUntil:'domcontentloaded'});
   await page.addScriptTag({content:axe.source});
   const audit=await page.evaluate(async()=>{
     return window.axe.run(document,{
       runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}
     });
   });
   const serious=audit.violations.filter(x=>['critical','serious'].includes(x.impact));
   console.log(screen.name+': '+audit.violations.length+' reglas con observaciones, '+serious.length+' bloqueantes');
   for(const issue of serious){
     console.error('A11Y '+screen.name+' ['+issue.impact+'] '+issue.id+': '+issue.help);
     for(const item of issue.nodes.slice(0,4))console.error('   '+item.target.join(' ')+': '+item.failureSummary);
   }
   if(serious.length)blockers.push(screen.name+': '+serious.map(x=>x.id).join(', '));
   await page.close();
 }
 if(blockers.length)throw new Error('Hallazgos importantes de accesibilidad: '+blockers.join(' | '));
 console.log('Accesibilidad: sin hallazgos críticos o graves en las rutas evaluadas.');
}finally{await browser.close();}
