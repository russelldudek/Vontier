from pathlib import Path
from playwright.sync_api import sync_playwright
import base64
import re
import shutil

base = Path(__file__).resolve().parents[1]
css_files = ['brand-tokens.css', 'styles-base.css', 'styles-doc.css', 'styles-responsive.css', 'styles-refinements.css']
css = '\n'.join((base / name).read_text(encoding='utf-8') for name in css_files)
logo_path = base / 'assets/brand/vontier-logo-4x.png'
logo_uri = 'data:image/png;base64,' + base64.b64encode(logo_path.read_bytes()).decode('ascii')
pairs = [
    ('resume.html', 'docs/Russell-Dudek-Vontier-Resume.pdf'),
    ('cover-letter.html', 'docs/Russell-Dudek-Vontier-Cover-Letter.pdf'),
    ('executive-brief.html', 'docs/Russell-Dudek-Vontier-Executive-Brief.pdf'),
    ('interview-brief.html', 'docs/Russell-Dudek-Vontier-Interview-Brief.pdf'),
    ('120-day-plan.html', 'docs/Russell-Dudek-Vontier-120-Day-Plan.pdf'),
    ('leadership-advantage.html', 'docs/Russell-Dudek-Vontier-Leadership-Advantage.pdf'),
]

chrome = next((p for p in [
    shutil.which('google-chrome'),
    shutil.which('google-chrome-stable'),
    shutil.which('chromium'),
    shutil.which('chromium-browser'),
] if p), None)
if not chrome:
    raise SystemExit('No system Chrome/Chromium executable found')

(base / 'docs').mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=chrome, headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    for src, out in pairs:
        html = (base / src).read_text(encoding='utf-8')
        html = re.sub(r'<link rel="stylesheet" href="[^"]+">', '', html)
        html = html.replace('</head>', '<style>' + css + '</style></head>')
        html = html.replace('assets/brand/vontier-logo-4x.png', logo_uri)
        page.set_content(html, wait_until='domcontentloaded', timeout=30000)
        page.emulate_media(media='print')
        page.pdf(
            path=str(base / out),
            format='Letter',
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=False,
        )
        print(out)
    browser.close()
