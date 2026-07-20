from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
required = [
    'index.html', 'resume.html', 'cover-letter.html', 'executive-brief.html',
    'interview-brief.html', '120-day-plan.html', 'leadership-advantage.html',
    'source-notes.html', 'styles.css', 'app.js', 'brand-intelligence.md',
    'brand-tokens.css', 'role-intelligence.md', 'README.md',
    'assets/brand/vontier-logo-original.png',
    'assets/brand/vontier-logo-4x.png',
    'docs/Russell-Dudek-Vontier-Resume.pdf',
    'docs/Russell-Dudek-Vontier-Cover-Letter.pdf',
    'docs/Russell-Dudek-Vontier-Executive-Brief.pdf',
    'docs/Russell-Dudek-Vontier-Interview-Brief.pdf',
    'docs/Russell-Dudek-Vontier-120-Day-Plan.pdf',
    'docs/Russell-Dudek-Vontier-Leadership-Advantage.pdf',
]
for relative in required:
    assert (root / relative).exists(), f'Missing required artifact: {relative}'

expected_pages = {
    'Russell-Dudek-Vontier-Resume.pdf': 2,
    'Russell-Dudek-Vontier-Cover-Letter.pdf': 1,
    'Russell-Dudek-Vontier-Executive-Brief.pdf': 2,
    'Russell-Dudek-Vontier-Interview-Brief.pdf': 6,
    'Russell-Dudek-Vontier-120-Day-Plan.pdf': 3,
    'Russell-Dudek-Vontier-Leadership-Advantage.pdf': 2,
}
for name, expected_count in expected_pages.items():
    reader = PdfReader(root / 'docs' / name)
    assert len(reader.pages) == expected_count, (name, len(reader.pages))
    text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    lowered = text.lower()
    assert 'russelldudek.github.io/vontier/' in lowered, name
    assert 'roleforge' not in lowered, name
    assert 'github.com/russelldudek/vontier' not in lowered, name
    if name == 'Russell-Dudek-Vontier-Leadership-Advantage.pdf':
        assert 'interview proof move' not in lowered, name
        assert 'ask russell to map' not in lowered, name

for name in ('Russell-Dudek-Vontier-Resume.pdf', 'Russell-Dudek-Vontier-Cover-Letter.pdf'):
    reader = PdfReader(root / 'docs' / name)
    text = '\n'.join(page.extract_text() or '' for page in reader.pages).lower()
    for required_text in (
        '412.287.8640',
        'russelldudek@gmail.com',
        'linkedin.com/in/russelldudek',
        'russelldudek.github.io/vontier/',
    ):
        assert required_text in text, (name, required_text)

html_files = list(root.glob('*.html'))
for path in html_files:
    soup = BeautifulSoup(path.read_text(), 'html.parser')
    ids = [tag.get('id') for tag in soup.find_all(attrs={'id': True})]
    assert len(ids) == len(set(ids)), f'Duplicate IDs in {path.name}'
    for link in soup.find_all('a', href=True):
        href = link['href'].strip()
        parsed = urlparse(href)
        if not href or href.startswith(('#', 'mailto:', 'tel:')) or parsed.scheme in {'http', 'https'}:
            continue
        target = href.split('#', 1)[0]
        if target:
            assert (root / target).exists(), f'Broken local link in {path.name}: {href}'

document_pages = {
    'resume.html': 'Resume',
    'cover-letter.html': 'Cover Letter',
    'executive-brief.html': 'Executive Brief',
    'interview-brief.html': 'Interview Brief',
    '120-day-plan.html': '120-Day Plan',
    'leadership-advantage.html': 'Leadership Advantage',
}
for page_name, current_label in document_pages.items():
    soup = BeautifulSoup((root / page_name).read_text(), 'html.parser')
    toolbar = soup.select_one('.doc-toolbar')
    assert toolbar is not None, page_name
    for href, label in document_pages.items():
        assert toolbar.find('a', href=href, string=label), (page_name, label)
    current = toolbar.select_one('a[aria-current="page"]')
    assert current and current.get_text(strip=True) == current_label, page_name
    download = toolbar.select_one('a[data-download-current]')
    assert download and download.has_attr('download'), page_name
    assert not download.has_attr('target'), page_name

for path in root.rglob('*'):
    if path.is_file() and path.suffix.lower() in {'.html', '.css', '.js', '.md', '.yml', '.yaml'}:
        lowered = path.read_text(errors='ignore').lower()
        assert 'roleforge' not in lowered, path
        assert 'github.com/russelldudek/vontier' not in lowered, path

print('QA passed')
