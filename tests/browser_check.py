"""Pruebas visuales opcionales (Playwright + Chromium), sin requerir red externa.

En entornos que bloquean HTTP se sirven HTML/CSS/JS y datos en memoria.
No es una dependencia de producción.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def setup_page(browser, width, height):
    """Offline browser: HTML/CSS/JS/JSON served from memory, photos as data URLs."""
    import base64
    page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
    page.set_content((ROOT/'public/index.html').read_text(encoding='utf-8'),wait_until='domcontentloaded',timeout=10000)
    page.add_style_tag(content=(ROOT/'public/assets/styles.css').read_text(encoding='utf-8'))
    payload=(ROOT/'public/data/jobs.json').read_text(encoding='utf-8')
    page.evaluate("""(payload) => {
      history.replaceState = () => {};
      window.fetch = async () => ({ok:true, json:async()=>JSON.parse(payload)});
    }""", payload)
    page.add_script_tag(content=(ROOT/'public/assets/app.js').read_text(encoding='utf-8'))
    page.wait_for_function("document.querySelector('#stat-jobs').textContent === '9'",timeout=5000)
    photos={p.name:'data:image/webp;base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
            for p in (ROOT/'public/assets/occupations').glob('*.webp')}
    page.evaluate("""(photos) => {
       const swap=()=>{
         for(const img of document.querySelectorAll('img[src*="/assets/occupations/"]')){
           const filename=img.src.split('/').pop(); if(photos[filename]){img.loading="eager";img.src=photos[filename];}
         }
       };
       swap();
       new MutationObserver(swap).observe(document.getElementById('job-grid'),{childList:true,subtree:true});
    }""",photos)
    page.wait_for_function("[...document.querySelectorAll('.tc-photo img')].every(img=>img.complete && img.naturalWidth>100)",timeout=5000)
    return page


def run():
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        try:
            for name, width, height in [('desktop', 1400, 900), ('mobile', 390, 844)]:
                page=setup_page(browser,width,height)
                errors=[]
                page.on('pageerror',lambda error: errors.append(str(error)))
                assert page.locator('#stat-jobs').inner_text()=='9', f'{name}: índice'
                assert page.locator('#stat-sources').inner_text()=='16', f'{name}: fuentes'
                assert page.locator('.job-card').count()==8, f'{name}: tarjetas'
                page.locator('#search').fill('remoto')
                assert page.locator('.job-card').count()>=1, f'{name}: búsqueda'
                page.locator('#reset-filters').click()
                page.locator('#filter-cat').select_option('Servicios')
                assert page.locator('.job-card').count()>0, f'{name}: categoría'
                page.locator('#filter-cat').select_option('')
                page.locator('#salary-only').check()
                assert page.locator('.job-card').count()==2, f'{name}: salarios'
                page.locator('#salary-only').uncheck()
                page.locator('[data-source-kind="publico"]').click()
                assert page.locator('.source-card').count()==3, f'{name}: sector público'
                page.locator('[data-source-kind=""]').click()
                page.locator('#source-search').fill('UNICEF')
                assert page.locator('.source-card').count()==1, f'{name}: buscar portal'
                page.locator('#source-search').fill('')
                page.locator('#reset-filters').click()
                page.locator('.job-card [data-save]').first.click()
                page.locator('#toggle-saved').click()
                assert page.locator('.job-card').count()==1, f'{name}: favoritos'
                page.locator('#toggle-saved').click()
                assert not errors, f'{name}: JS {errors}'
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 2'), f'{name}: desbordamiento horizontal'
                page.screenshot(path=str(ROOT/f'chambani_v2_{name}.png'),full_page=True)
                page.close()
                print('OK:',name,'búsquedas, filtros, favoritos y diseño adaptable')
        finally:
            browser.close()


if __name__=='__main__':
    run()
