#!/usr/bin/env python3
"""Headless Chromium capture; read-only navigation and optional explicit scroll; no GUI."""
import argparse,json,pathlib,shutil
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('target');p.add_argument('output',type=pathlib.Path);p.add_argument('--width',type=int,default=720);p.add_argument('--height',type=int,default=1280);p.add_argument('--selector');p.add_argument('--scroll',type=int,default=0);p.add_argument('--chromium',default=shutil.which('chromium') or shutil.which('chromium-browser'));a=p.parse_args()
url=pathlib.Path(a.target).resolve().as_uri() if pathlib.Path(a.target).is_file() else a.target
if not url.startswith(('https://','http://','file://')):p.error('provide URL or local HTML file')
a.output.parent.mkdir(parents=True,exist_ok=True)
errors=[];failed=[];page_errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=a.chromium);page=browser.new_page(viewport={'width':a.width,'height':a.height},device_scale_factor=1,reduced_motion='reduce');page.on('pageerror',lambda e:page_errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('requestfailed',lambda r:failed.append({'url':r.url,'error':r.failure}))
    # Standalone HTML is rendered directly; for projects with relative assets use an authorized local dev server.
    resp=None
    if pathlib.Path(a.target).is_file():page.set_content(pathlib.Path(a.target).read_text(encoding='utf-8'),wait_until='load',timeout=30000)
    else:resp=page.goto(url,wait_until='load',timeout=30000)
    if resp and resp.status>=400:raise RuntimeError(f'HTTP {resp.status}')
    page.evaluate('document.fonts.ready');page.evaluate('(y)=>window.scrollTo(0,y)',a.scroll);page.wait_for_timeout(400)
    loc=page.locator(a.selector) if a.selector else None
    if loc:
        if loc.count()!=1:raise RuntimeError('selector must identify exactly one visible element')
        loc.screenshot(path=str(a.output),animations='disabled',timeout=10000)
    else:page.screenshot(path=str(a.output),animations='disabled')
    meta={'url':url,'status':resp.status if resp else None,'viewport':[a.width,a.height],'selector':a.selector,'console_errors':errors,'page_errors':page_errors,'failed_requests':failed,'note':'Inspect image and errors; successful capture does not prove correct UI.'};browser.close()
a.output.with_suffix('.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
