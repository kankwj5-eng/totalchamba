"""Smoke test accesible, offline. Requiere Playwright y Chromium."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_check import setup_page

ROOT=Path(__file__).resolve().parents[1]


def run():
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for label, width, height in [('desktop',1380,860),('mobile',390,844)]:
                page=setup_page(browser,width,height)
                errors=[]
                page.on('pageerror', lambda error: errors.append(str(error)))
                assert page.locator('.clarity-row').count()==8
                assert 'claridad del anuncio' in page.locator('.clarity-row').first.inner_text()
                page.locator('.clarity-details').first.locator('summary').click()
                assert page.locator('.clarity-details[open]').count()==1
                assert page.locator('.tc-map-block .tc-maps-link').count()>=1
                # Enlace a búsqueda por zona, no coordenadas inventadas.
                href=page.locator('.tc-map-block .tc-maps-link').first.get_attribute('href')
                assert href.startswith('https://www.google.com/maps/search/?api=1&query=')
                assert 'Centro+M%C3%A9dico' not in href
                page.locator('#filter-clarity').select_option('5')
                assert 0<page.locator('.job-card').count()<=8
                page.locator('#filter-clarity').select_option('')
                page.locator('#filter-map').select_option('address')
                assert page.locator('.job-card').count()==0 # Muestra sin direcciones concretas.
                page.locator('#filter-map').select_option('')
                page.locator('[data-radar="Masaya"]').click()
                assert page.locator('.job-card').count()==1
                page.locator('#clear-radar').click()
                page.locator('.job-card [data-compare]').first.click()
                assert page.locator('.compare-item').count()==1
                page.locator('.job-card [data-compare]').nth(1).click()
                assert page.locator('.compare-item').count()==2
                page.locator('.job-card [data-compare]').nth(2).click()
                assert page.locator('.compare-item').count()==3
                page.locator('.job-card [data-compare]').nth(3).click()
                assert page.locator('.compare-item').count()==3
                page.locator('#compare-clear').click()
                assert page.locator('#compare-tray').is_hidden()
                page.locator('#readable-mode').click()
                assert page.locator('body.reading-mode').count()==1
                assert page.locator('#readable-mode').get_attribute('aria-pressed')=='true'
                page.locator('#readable-mode').click()
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
                assert errors == [], f'{label}: {errors}'
                assert page.locator('.tc-photo img').count() == 8
                assert page.locator('.tc-photo img').first.evaluate('(img) => img.complete && img.naturalWidth>100')
                assert page.locator('#data-notice').is_visible()
                page.screenshot(path=str(ROOT/f'totalchanba_v5_{label}.png'),full_page=True)
                page.close()
                print('OK:',label,'estrellas, maps, radar, comparador, lectura clara, responsive')
        finally:
            browser.close()

if __name__=='__main__':
    run()
