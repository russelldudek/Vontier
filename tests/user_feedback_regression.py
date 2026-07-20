from pathlib import Path
import re
import shutil
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOC_PAGES = ["resume.html", "cover-letter.html", "executive-brief.html", "interview-brief.html", "120-day-plan.html", "leadership-advantage.html", "source-notes.html"]

resume_text = (ROOT / "resume.html").read_text(encoding="utf-8")
assert "Food Safety Management Certification" not in resume_text

expected = {"Operating model": "index.html#model", "Evidence": "index.html#evidence", "120 days": "index.html#entry"}
for page_name in DOC_PAGES:
    soup = BeautifulSoup((ROOT / page_name).read_text(encoding="utf-8"), "html.parser")
    links = {a.get_text(" ", strip=True): a.get("href") for a in soup.select(".site-header .nav a")}
    for label, href in expected.items():
        assert links.get(label) == href, (page_name, label, links.get(label))
    pdf_link = soup.select_one('.doc-toolbar a[href$=".pdf"]')
    if pdf_link:
        assert pdf_link.get("target") == "_blank", page_name
        assert "noopener" in (pdf_link.get("rel") or []), page_name
        assert (ROOT / pdf_link["href"].removeprefix("./")).exists(), page_name

html = (ROOT / "index.html").read_text(encoding="utf-8")
css = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("brand-tokens.css", "styles-base.css", "styles-doc.css", "styles-responsive.css", "styles-refinements.css"))
html = re.sub(r'<link rel="stylesheet" href="[^"]+">', "", html)
html = html.replace("</head>", f"<style>{css}</style></head>")
chrome = shutil.which("chromium") or shutil.which("google-chrome")
assert chrome
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=chrome, headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1144, "height": 1345})
    page.set_content(html, wait_until="domcontentloaded")
    metrics = page.locator(".torque-core").evaluate("element => ({clientWidth: element.clientWidth, scrollWidth: element.scrollWidth, clientHeight: element.clientHeight, scrollHeight: element.scrollHeight})")
    assert metrics["scrollWidth"] <= metrics["clientWidth"], metrics
    assert metrics["scrollHeight"] <= metrics["clientHeight"], metrics
    button = page.locator(".nav .nav-cta")
    button.hover()
    colors = button.evaluate("element => ({background: getComputedStyle(element).backgroundColor, color: getComputedStyle(element).color})")
    assert colors["background"] != "rgb(237, 247, 245)", colors
    assert colors["color"] == "rgb(255, 255, 255)", colors
    browser.close()
print("User-feedback regressions passed")
