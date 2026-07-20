from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text and new not in text:
        raise SystemExit(f"Expected source text missing in {path}")
    target.write_text(text.replace(old, new), encoding="utf-8")


replace(
    "index.html",
    '<div class="torque-core"><div><strong>AI</strong>transmitted value</div></div>',
    '<div class="torque-core"><strong>AI</strong><span>transmitted</span><span>value</span></div>',
)
replace("resume.html", '<li>Food Safety Management Certification</li>', "")

for name in (
    "resume.html",
    "cover-letter.html",
    "executive-brief.html",
    "interview-brief.html",
    "120-day-plan.html",
    "leadership-advantage.html",
    "source-notes.html",
):
    target = ROOT / name
    text = target.read_text(encoding="utf-8")
    text = text.replace('href="#model"', 'href="index.html#model"')
    text = text.replace('href="#evidence"', 'href="index.html#evidence"')
    text = text.replace('href="#entry"', 'href="index.html#entry"')
    text = text.replace(
        ' download>Download PDF</a>',
        ' target="_blank" rel="noopener">Download PDF</a>',
    )
    target.write_text(text, encoding="utf-8")

replace(
    "styles-base.css",
    ".nav .nav-cta { background:var(--vontier-ink); color:white; }",
    ".nav .nav-cta { background:var(--vontier-ink); color:white; }\n"
    ".nav .nav-cta:hover,\n"
    ".nav .nav-cta:focus-visible { background:var(--vontier-teal-dark); color:white; }",
)
replace(
    "styles-base.css",
    ".torque-core { position:absolute; inset:41%; border-radius:50%; background:var(--vontier-ink); color:white; display:grid; place-items:center; text-align:center; padding:1rem; z-index:4; font-family:var(--display); text-transform:uppercase; letter-spacing:.08em; font-size:.76rem; box-shadow:0 0 0 10px rgba(255,255,255,.6); }\n"
    ".torque-core strong { display:block; font-size:1.8rem; letter-spacing:-.03em; text-transform:none; }",
    ".torque-core { position:absolute; inset:37%; border-radius:50%; background:var(--vontier-ink); color:white; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:.65rem; z-index:4; font-family:var(--display); text-transform:uppercase; line-height:1.02; letter-spacing:0; font-size:clamp(.58rem,1vw,.74rem); overflow:hidden; box-shadow:0 0 0 10px rgba(255,255,255,.6); }\n"
    ".torque-core strong { display:block; font-size:clamp(1.65rem,3vw,2.1rem); line-height:.9; margin-bottom:.32rem; letter-spacing:-.03em; text-transform:none; }\n"
    ".torque-core span { display:block; white-space:nowrap; letter-spacing:.12em; }",
)

regression = r'''from pathlib import Path
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
'''
(ROOT / "tests/user_feedback_regression.py").write_text(regression, encoding="utf-8")
print("Applied user-review patch")
