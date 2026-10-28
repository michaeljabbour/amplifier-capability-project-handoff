#!/usr/bin/env python3
"""Check static links, accessibility hooks, portable bytes and honest evidence state."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/project-handoff'


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = set(); self.references = []; self.assets = []; self.labels = set(); self.controls = []
        self.h1 = 0; self.examples = []; self.lang = None; self.source = ''; self.in_source = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'h1': self.h1 += 1
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate ID {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'label' and a.get('for'): self.labels.add(a['for'])
        if tag in {'input', 'select', 'textarea'}: self.controls.append((tag, a))
        if tag in {'a', 'link'} and 'href' in a: self.references.append(a['href'])
        if tag in {'img', 'script', 'iframe'} and 'src' in a:
            self.references.append(a['src']); self.assets.append(a['src'])
        if tag == 'link': self.assets.append(a.get('href', ''))
        if 'data-example' in a: self.examples.append((a['data-example'], 'hidden' in a))
        if tag == 'textarea' and a.get('id') == 'skill-source': self.in_source = True
    def handle_endtag(self, tag):
        if tag == 'textarea': self.in_source = False
    def handle_data(self, data):
        if self.in_source: self.source += data


def check(output):
    output = output.resolve()
    raw = (output / 'index.html').read_text(encoding='utf-8')
    page = Page(); page.feed(raw)
    assert page.lang == 'en' and page.h1 == 1, 'Use one English page title'
    assert not re.search(r'@@[A-Z_]+@@', raw), 'Unresolved site placeholder'
    checked = 0
    for reference in page.references:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme == 'https', f'Unsafe link protocol: {reference}'
            continue
        assert not parsed.path.startswith('/'), f'Root-relative static link: {reference}'
        target = (output / unquote(parsed.path)).resolve() if parsed.path else output / 'index.html'
        assert target.is_relative_to(output) and target.exists(), f'Missing/escaping local link: {reference}'
        if parsed.fragment and target.name == 'index.html':
            assert parsed.fragment in page.ids, f'Missing page fragment: {reference}'
        checked += 1
    for reference in page.assets:
        assert not urlsplit(reference).scheme and not reference.startswith('//'), 'Runtime asset must stay local'
    markdown_links = 0
    for path in output.rglob('*.md'):
        if path.is_relative_to(output / 'docs/evaluations') and path.name not in {
            'REPORT.md', 'ASSESSMENT.md', 'STUDY-QUALITY-REVIEW.md', 'SEMANTIC-SPOT-REVIEW.md'}:
            continue  # Frozen prompts/snapshots are immutable data, not navigation docs.
        for reference in re.findall(r'(?<!!)\[[^\]]*\]\(([^)\s]+)\)', path.read_text(encoding='utf-8')):
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            assert target.is_relative_to(output) and target.exists(), f'Broken Markdown link: {path.relative_to(output)}: {reference}'
            markdown_links += 1
    sources = sorted(p for p in ROOT.rglob('SKILL.md') if '_site' not in p.relative_to(ROOT).parts and '.git' not in p.relative_to(ROOT).parts)
    assert sources == [SKILL / 'SKILL.md'], 'Keep one canonical SKILL.md in source'
    skill_files = sorted(p for p in SKILL.rglob('*') if p.is_file())
    assert page.source == (SKILL / 'SKILL.md').read_text(encoding='utf-8'), 'Site source differs from installed skill'
    assert (output / 'downloads/project-handoff-skill.md').read_bytes() == (SKILL / 'SKILL.md').read_bytes()
    with ZipFile(output / 'downloads/project-handoff-skill.zip') as bundle:
        expected = ['project-handoff/' + p.relative_to(SKILL).as_posix() for p in skill_files]
        assert bundle.namelist() == expected and bundle.testzip() is None, 'ZIP is not exactly the portable folder'
        for path, name in zip(skill_files, expected):
            assert bundle.read(name) == path.read_bytes(), f'ZIP source drift: {name}'
    for path in (SKILL / 'references').rglob('*'):
        if path.is_file(): assert path.read_bytes() == (output / 'downloads' / path.relative_to(SKILL)).read_bytes()
    config = json.loads((ROOT / 'site/site.json').read_text())
    ids = [e['id'] for e in config['examples']]
    assert [i for i, _ in page.examples] == ids and [i for i, hidden in page.examples if not hidden] == ids[:1]
    for tag, attrs in page.controls:
        if attrs.get('type') == 'radio':
            continue  # These controls have a wrapping visible label and a fieldset legend.
        assert attrs.get('id') in page.labels, f'Visible label missing: {tag} {attrs}'
    assert 'fictional' in raw.lower() and 'Real people resuming real work: not measured.' in raw
    assert "connect-src 'none'" in raw and "object-src 'none'" in raw
    assert 'prefers-reduced-motion' in (output / 'assets/style.css').read_text()
    assert 'Memory install' in raw and 'No Memory' in raw
    for path in output.rglob('*.css'):
        css = path.read_text()
        assert not re.search(r'@import|url\(\s*[\'"]?(?:https?:|//)', css), f'External CSS asset: {path}'
    assert 'Copyright (c) Microsoft Corporation.' in (output / 'theme/LICENSE').read_text()
    if config.get('evidence_record'):
        source = ROOT / config['evidence_record']
        assert source.read_bytes() == (output / config['evidence_record']).read_bytes(), 'Summary export drift'
        summary = json.loads(source.read_text())
        exported_record = output / source.parent.relative_to(ROOT)
        for retained in source.parent.rglob('*'):
            if retained.is_file():
                assert retained.read_bytes() == (exported_record / retained.relative_to(source.parent)).read_bytes(), 'Retained evaluation export drift: ' + str(retained)
        if summary.get('status') == 'live-study':
            assert 'provisional automated judge labels' in raw and 'No credible effectiveness conclusion' in raw
            if source.with_name('STUDY-QUALITY-REVIEW.md').exists():
                assert 'both disputed' in raw and 'Study quality review' in raw
    digest = hashlib.sha256((output / 'downloads/project-handoff-skill.zip').read_bytes()).hexdigest()
    print(f'PASS: {checked} local page links/assets/fragments; {markdown_links} shipped Markdown links')
    print(f'PASS: {len(skill_files)} portable files and raw downloads match canonical sources byte for byte; one SKILL.md source')
    print(f'PASS: {len(ids)} explicitly fictional examples, visible labels, local assets, reduced motion and honest outcome label')
    print('Skill ZIP SHA-256: ' + digest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    check(parser.parse_args().output)
