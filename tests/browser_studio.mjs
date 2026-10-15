// Browser smoke tests de TotalChanba Studio; se ejecutan contra el sitio estático local.
import { chromium } from 'playwright';

const origin=process.env.SITE_URL || 'http://127.0.0.1:4173';
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const errors=[];
function assert(ok,message){if(!ok)throw new Error(message);}
async function check(viewport){
  const page=await browser.newPage({viewport});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(origin+'/herramientas.html',{waitUntil:'domcontentloaded'});
  await page.locator('[data-tab="cv"]').click();
  assert(await page.locator('#panel-cv').isVisible(),'CV no aparece al pulsar pestaña');
  await page.locator('#cv-name').fill('Persona de Prueba');
  await page.locator('#cv-city').fill('Estelí, Nicaragua');
  await page.locator('#cv-experience').fill('Atención al cliente y organización');
  const preview=await page.locator('#paper-name').innerText();
  assert(preview.includes('Persona de Prueba'),'La vista previa del CV no se actualiza: preview='+JSON.stringify(preview)+', input='+JSON.stringify(await page.locator('#cv-name').inputValue())+', errores='+JSON.stringify(errors));
  await page.locator('#cv-save').click();
  await page.reload({waitUntil:'domcontentloaded'});
  await page.locator('[data-tab="cv"]').click();
  assert(await page.locator('#cv-name').inputValue()==='Persona de Prueba','No recuperó CV guardado');
  await page.locator('[data-tab="entrevista"]').click();
  const before=await page.locator('#question-text').innerText();
  await page.locator('#question-next').click();
  assert((await page.locator('#question-text').innerText())!==before,'Otra pregunta no funciona');
  await page.locator('[data-tab="carta"]').click();
  await page.locator('#letter-interest').fill('Me interesa aportar con experiencias reales');
  await page.locator('#letter-proof').fill('Organicé documentos con precisión');
  await page.locator('#letter-create').click();
  const letter=await page.locator('#letter-output').inputValue();
  assert(letter.includes('Organicé documentos con precisión'),'No crea la carta');
  await page.locator('[data-tab="plan"]').click();
  await page.locator('#plan-list input').first().check();
  await page.locator('#application-save').click();
  await page.reload({waitUntil:'domcontentloaded'});
  await page.locator('[data-tab="plan"]').click();
  assert(await page.locator('#plan-list input').first().isChecked(),'Plan de postulación no se conservó');
  await page.locator('[data-tab="animo"]').click();
  await page.locator('#mood-next').click();
  assert((await page.locator('#mood-prompt').innerText()).length>15,'Guía de ánimo no funciona');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+2),'El estudio excede el ancho del teléfono');
  await page.close();
}
try{
  await check({width:390,height:844});
  await check({width:1440,height:900});
  const page=await browser.newPage({viewport:{width:390,height:844}});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(origin+'/',{waitUntil:'domcontentloaded'});
  await page.locator('#bulletin-grid .tc-agenda-card').first().waitFor({timeout:15000});
  await page.locator('#job-grid .tc-kit-bridge a').first().waitFor({timeout:15000});
  assert(await page.locator('[data-bulletin-filter="formacion"]').count()===1,'Falta agenda editorial');
  const href=await page.locator('.tc-kit-bridge a').first().getAttribute('href');
  assert(href.startsWith('/herramientas.html?vacante='),'Enlace de kit sin vacante');
  await page.locator('.tc-kit-bridge a').first().click();
  await page.waitForURL(/herramientas.html\?vacante=/,{timeout:10000});
  await page.locator('#selected-title').waitFor({state:'visible'});
  assert((await page.locator('#selected-title').innerText()).length>4,'El kit no recibió contexto de vacante');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+2),'El portal excede el ancho del teléfono');
  await page.close();
  assert(errors.length===0,'Errores JS: '+errors.join('; '));
  console.log('TotalChanba Studio: pruebas funcionales en móvil y escritorio aprobadas.');
}finally{await browser.close();}
