#!/usr/bin/env python3
"""Build the static guide and portable download with the Python standard library."""
import argparse
import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit, unquote
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/project-handoff'
ARCHIVE_DATE = (2026, 10, 28, 0, 0, 0)


def esc(value):
    return html.escape(str(value), quote=True)


def skill_files():
    return sorted(p for p in SKILL.rglob('*') if p.is_file() and not p.is_symlink())


def output_path(source, output):
    source = source.resolve()
    if source == SKILL / 'SKILL.md':
        return output / 'downloads/project-handoff-skill.md'
    if source.is_relative_to(SKILL):
        return output / 'downloads' / source.relative_to(SKILL)
    if source == ROOT / 'site/theme/LICENSE':
        return output / 'theme/LICENSE'
    return output / source.relative_to(ROOT)


LINK = re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^)\s]+)\)')


def local_source(reference, source):
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    target = (source.parent / unquote(parsed.path)).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f'Document link escapes the repository: {source}: {reference}')
    return target


def export_documents(output):
    """Ship the linked text sources; keep portable skill files byte-identical."""
    queue = [ROOT / 'README.md', ROOT / 'LICENSE', ROOT / 'docs/EXAMPLES.md',
             ROOT / 'docs/PROVENANCE.md', ROOT / 'docs/BENCHMARK.md',
             ROOT / 'contracts/handoff.v1.md', ROOT / 'site/theme/LICENSE'] + skill_files()
    queue += [ROOT / path for path in ('CHANGELOG.md', 'docs/EVALUATION.md', 'docs/DESIGN.md',
                                     'docs/VALIDATION.md', 'docs/RIGHT-SHAPE-REVIEW.md') if (ROOT / path).is_file()]
    seen = set()
    while queue:
        source = queue.pop(0).resolve()
        if source in seen:
            continue
        seen.add(source)
        if not source.is_relative_to(ROOT) or not source.exists() or source.is_symlink():
            raise ValueError(f'Missing or unsafe source document: {source}')
        if source.is_dir():
            # A static directory link needs its contents as well as the directory.
            queue.extend(p for p in sorted(source.iterdir()) if p.name not in {'.git', '__pycache__', '_site'} and not p.name.startswith('.'))
            output_path(source, output).mkdir(parents=True, exist_ok=True)
            continue
        destination = output_path(source, output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        evaluation_data = source.is_relative_to(ROOT / 'docs/evaluations') and source.name not in {
            'REPORT.md', 'ASSESSMENT.md', 'STUDY-QUALITY-REVIEW.md', 'SEMANTIC-SPOT-REVIEW.md'}
        if source.suffix == '.md' and not evaluation_data:
            text = source.read_text(encoding='utf-8')
            def replace(match):
                label, reference = match.groups()
                target = local_source(reference, source)
                if target is None:
                    return match.group(0)
                if not target.exists():
                    raise ValueError(f'Missing Markdown source target: {source}: {reference}')
                queue.append(target)
                # The portable folder is deliberately self-contained and stays exact.
                if source.is_relative_to(SKILL):
                    return match.group(0)
                parsed = urlsplit(reference)
                relative = os.path.relpath(output_path(target, output), destination.parent).replace(os.sep, '/')
                return f'[{label}]({relative}' + (f'#{parsed.fragment}' if parsed.fragment else '') + ')'
            rewritten = LINK.sub(replace, text)
            destination.write_text(rewritten, encoding='utf-8')
        else:
            shutil.copyfile(source, destination)
    return seen


def inline(text, source, output):
    """Escape source text, then render only the Markdown constructs used here."""
    pieces, cursor = [], 0
    token = re.compile(r'(`[^`\n]+`)|\[([^\]\n]+)\]\(([^)\s]+)\)|(\*\*([^*]+)\*\*)')
    for match in token.finditer(text):
        pieces.append(esc(text[cursor:match.start()]))
        if match.group(1):
            pieces.append('<code>' + esc(match.group(1)[1:-1]) + '</code>')
        elif match.group(2):
            label, href = match.group(2), match.group(3)
            target = local_source(href, source)
            if target is not None:
                parsed = urlsplit(href)
                href = './' + output_path(target, output).relative_to(output).as_posix()
                if parsed.fragment:
                    href += '#' + parsed.fragment
            if urlsplit(href).scheme not in {'', 'https'}:
                raise ValueError(f'Unsupported source URL: {href}')
            pieces.append('<a href="' + esc(href) + '">' + esc(label) + '</a>')
        else:
            pieces.append('<strong>' + esc(match.group(5)) + '</strong>')
        cursor = match.end()
    pieces.append(esc(text[cursor:]))
    return ''.join(pieces)


def markdown(text, source, output):
    if text.startswith('---\n'):
        text = text.split('---\n', 2)[-1]
    lines, i, result = text.splitlines(), 0, []
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('```'):
            code, i = [], i + 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i += 1
            result.append('<pre><code>' + esc('\n'.join(code)) + '</code></pre>'); i += 1
            continue
        heading = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading:
            level = min(6, len(heading[1]) + 2)
            result.append(f'<h{level}>' + inline(heading[2], source, output) + f'</h{level}>'); i += 1
            continue
        if line.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s|:\-]+\|$', lines[i + 1]):
            cells = lambda row: [c.strip() for c in row.strip('|').split('|')]
            headers = cells(line); i += 2
            table = ['<div class="source-table-wrap"><table class="source-table"><thead><tr>']
            table.extend('<th scope="col">' + inline(c, source, output) + '</th>' for c in headers)
            table.append('</tr></thead><tbody>')
            while i < len(lines) and lines[i].startswith('|'):
                table.append('<tr>' + ''.join('<td>' + inline(c, source, output) + '</td>' for c in cells(lines[i])) + '</tr>'); i += 1
            result.append(''.join(table) + '</tbody></table></div>')
            continue
        item = re.match(r'^(?:[-*]|\d+\.)\s+(.+)$', line)
        if item:
            ordered = bool(re.match(r'^\d+\.', line)); tag = 'ol' if ordered else 'ul'; entries = []
            while i < len(lines):
                match = re.match(r'^(?:[-*]|\d+\.)\s+(.+)$', lines[i])
                if not match:
                    break
                entries.append('<li>' + inline(match[1], source, output) + '</li>'); i += 1
            result.append('<' + tag + '>' + ''.join(entries) + '</' + tag + '>')
            continue
        paragraph = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(?:#{1,6}\s|```|[-*]\s|\d+\.\s|\|)', lines[i]):
            paragraph.append(lines[i]); i += 1
        if not paragraph:
            paragraph = [lines[i]]; i += 1
        result.append('<p>' + inline(' '.join(paragraph), source, output) + '</p>')
    return '\n'.join(result)


def section(text, title):
    match = re.search(r'^## ' + re.escape(title) + r'\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not match:
        raise ValueError(f'Missing canonical skill section: {title}')
    return match.group(1)


def examples(config):
    options, panels = [], []
    ids = set()
    for index, example in enumerate(config['examples']):
        eid = example['id']
        if not re.fullmatch('[a-z][a-z0-9-]*', eid) or eid in ids:
            raise ValueError('Fictional example IDs must be unique safe identifiers')
        ids.add(eid)
        if 'fictional' not in example['brief'].lower() or not 0 <= example['answer'] < len(example['choices']):
            raise ValueError(f'{eid}: expected an explicitly fictional brief and valid answer')
        options.append('<option value="' + eid + '">' + esc(example['name']) + '</option>')
        panel = '<article class="example-panel" data-example="' + eid + '"' + (' hidden' if index else '') + '>'
        panel += '<div class="project-brief"><strong>The same brief</strong><p>' + esc(example['brief']) + '</p></div><div class="comparison-grid">'
        for title, state, value, footnote in [('Original handoff', 'Unchecked', example['original'], 'The incoming record is a source to check, not authority to change the task.'), ('Checked resumption', 'Source-grounded', example['checked'], example['kept'] + ' ' + example['changed'])]:
            panel += '<div class="handoff-sheet' + (' checked' if state == 'Source-grounded' else '') + '"><div class="sheet-top"><b>' + title + '</b><span class="status">' + state + '</span></div><p class="sheet-content">' + esc(value) + '</p><p class="sheet-footnote">' + esc(footnote) + '</p></div>'
        panel += '</div><details class="source-evidence"><summary>Read the supplied evidence</summary><dl>'
        panel += ''.join('<dt>' + esc(item['label']) + '</dt><dd>' + esc(item['text']) + '</dd>' for item in example['sources'])
        panel += '</dl></details><div class="exercise"><fieldset><legend>' + esc(example['question']) + '</legend>'
        for choice_index, choice in enumerate(example['choices']):
            panel += '<label class="choice"><input type="radio" name="answer-' + eid + '" value="' + str(choice_index) + '"><span>' + esc(choice) + '</span></label>'
        panel += '</fieldset><button type="button" class="answer-button" data-answer="' + str(example['answer']) + '" data-feedback="' + esc(example['feedback']) + '">Check this answer</button><p class="answer-status" role="status" aria-live="polite"></p></div></article>'
        panels.append(panel)
    return '\n'.join(options), '\n'.join(panels)


def evidence(config, output):
    record = config.get('evidence_record')
    if not record:
        return '<strong>Behavioral benchmark: not measured yet.</strong><p>The plan and test apparatus can be inspected below. A live run must establish its own result; an offline wiring check cannot do that.</p>'
    path = (ROOT / record).resolve()
    if not path.is_relative_to(ROOT / 'docs/evaluations') or not path.is_file():
        raise ValueError('evidence_record must point at a dated local evaluation summary')
    summary = json.loads(path.read_text(encoding='utf-8'))
    status = summary.get('status')
    if status not in {'live-pilot', 'live-study', 'offline-smoke', 'blocked'}:
        raise ValueError('Unknown evidence status; refusing to invent a benchmark result')
    # Retained records are data: preserve exact bytes, including frozen prompts.
    # Their Markdown may deliberately retain the original source-relative links.
    shutil.copytree(path.parent, output / path.parent.relative_to(ROOT), dirs_exist_ok=True)
    report = path.with_name('REPORT.md')
    links = '<a href="./' + path.relative_to(ROOT).as_posix() + '">Frozen summary</a>'
    if report.exists():
        target = output / report.relative_to(ROOT); target.write_bytes(report.read_bytes())
        links += ' · <a href="./' + report.relative_to(ROOT).as_posix() + '">Run report</a>'
    labels = {'live-pilot': 'A live pilot is recorded; effectiveness is not established.', 'live-study': 'No credible effectiveness conclusion is supported.', 'offline-smoke': 'Offline wiring checked; behavioral benefit is not measured.', 'blocked': 'The live evaluation is blocked; behavioral benefit is not measured.'}
    details = summary.get('interpretation') or summary.get('scope') or ''
    if not isinstance(details, str):
        details = json.dumps(details, ensure_ascii=False)
    result = '<strong>' + esc(labels[status]) + '</strong><p>' + esc(details) + '</p>'
    quality = path.with_name('STUDY-QUALITY-REVIEW.md')
    if status in {'live-pilot', 'live-study'} and summary.get('metrics_by_condition'):
        quality_text = quality.read_text(encoding='utf-8') if quality.is_file() else ''
        disputed_placebo = 'Both reported placebo critical failures are disputed' in quality_text
        trials = summary.get('completed_trials')
        result += '<p>' + esc(trials) + ' transfer trials across ' + esc(summary.get('fixture_count')) + ' fictional projects, '
        result += esc(summary.get('repeats')) + ' repetitions and three conditions. These are provisional automated judge labels, not validated all-pass outcomes.</p>'
        result += '<div class="source-table-wrap" tabindex="0" role="region" aria-label="Automatic benchmark results; scroll horizontally for all columns"><table class="source-table study-results"><caption>Frozen automatic labels; semantic review disputes consequential judgments.</caption><thead><tr><th scope="col">Condition</th><th scope="col">Automatic correct / attempts</th><th scope="col">Judge critical flags</th><th scope="col">Ungraded</th></tr></thead><tbody>'
        for condition in summary.get('conditions', []):
            metrics = summary['metrics_by_condition'][condition]
            n = metrics['n']; correct = round(metrics['resume_correct_rate'] * n)
            flags = str(metrics['critical_failures'])
            if condition == 'placebo' and disputed_placebo and metrics['critical_failures']:
                flags += ' (both disputed)'
            result += '<tr><th scope="row">' + esc(condition.capitalize()) + '</th><td>' + str(correct) + '/' + str(n) + '</td><td>' + esc(flags) + '</td><td>' + esc(metrics.get('ungraded_trials', 0)) + '</td></tr>'
        result += '</tbody></table></div>'
        result += '<p>The ungraded trial stays in the frozen denominator. It failed judge quotation validation; that is not evidence that its handoff was wrong. Skill and baseline have the same reported primary rate.</p>'
        if quality.is_file():
            result += '<p>The secondary semantic review disputes both critical-execution labels, identifies unsupported missing-feature and approval claims in passing skill records, and disputes a clean-case penalty. It is an agent quality review, not independent human evidence. The apparent placebo deficit cannot support a benefit or safety claim.</p>'
            links += ' · <a href="./' + quality.relative_to(ROOT).as_posix() + '">Study quality review</a>'
        comparisons = summary.get('paired_comparisons', {})
        result += '<ul class="comparison-intervals">'
        for key, title in [('skill_vs_baseline', 'Skill minus baseline'), ('skill_vs_placebo', 'Skill minus placebo')]:
            item = comparisons.get(key)
            if item:
                low, high = item['ci95']
                result += '<li>' + title + ': ' + f'{item["delta_resume"] * 100:+g}' + ' percentage points; descriptive 95% fixture-cluster bootstrap interval [' + f'{low * 100:g}, {high * 100:g}' + '].</li>'
        result += '</ul><p class="note">These intervals describe disputed automatic labels on ten curated fixtures. The sampled [0, 0] tie is not a population guarantee. Repetitions are not independent new projects, and no advantage over baseline is shown.</p>'
        models = summary.get('models', {})
        if models:
            result += '<p class="note">Evaluated: ' + esc(models.get('evaluated')) + '. Judge: ' + esc(models.get('judge')) + '. Separate stateless calls in a virtual text/file interface; no actual host tools executed. Only Capture-to-neutral-resumer transfer was tested. Direct Resume/Check effects and real-user outcomes remain unmeasured.</p>'
        if summary.get('nominal_uncached_usd') is not None:
            result += '<p class="note">' + esc(summary.get('provider_calls')) + ' provider calls; nominal uncached token estimate USD ' + f'{summary["nominal_uncached_usd"]:.4f}' + ', not an invoice.</p>'
    more = [('docs/evaluations/2026-10-28/pilot-3/SEMANTIC-SPOT-REVIEW.md', 'Pilot semantic review'),
            ('docs/VALIDATION.md', 'Local validation and limits'), ('docs/RIGHT-SHAPE-REVIEW.md', 'Right Shape application record')]
    for relative, title in more:
        if (ROOT / relative).is_file():
            links += ' · <a href="./' + relative + '">' + title + '</a>'
    return result + '<p class="note evidence-links">' + links + '</p>'


def build(output):
    output = output.resolve()
    if output == ROOT or not output.is_relative_to(ROOT):
        raise ValueError('Output must be a dedicated directory inside this checkout')
    config = json.loads((ROOT / 'site/site.json').read_text(encoding='utf-8'))
    skill_text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    contract_path = SKILL / 'references/handoff-contract.md'
    benchmark_path = ROOT / 'docs/BENCHMARK.md'
    benchmark = benchmark_path.read_text(encoding='utf-8')
    if output.exists():
        shutil.rmtree(output)
    (output / 'assets').mkdir(parents=True)
    for source, dest in [('site/theme/style.css', 'assets/family.css'), ('site/style.css', 'assets/style.css'), ('site/site.js', 'assets/site.js')]:
        shutil.copyfile(ROOT / source, output / dest)
    if (ROOT / 'site/film').is_dir():
        shutil.copytree(ROOT / 'site/film', output / 'film')
    (output / 'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect x="7" y="4" width="26" height="32" fill="#f6f4ee" stroke="#365e57" stroke-width="2"/><path d="M13 13h14M13 20h14M13 27h8" stroke="#365e57" stroke-width="2"/></svg>')
    copied = export_documents(output)
    archive = output / 'downloads/project-handoff-skill.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as bundle:
        for path in skill_files():
            info = ZipInfo('project-handoff/' + path.relative_to(SKILL).as_posix(), ARCHIVE_DATE)
            info.external_attr = 0o100644 << 16; info.compress_type = ZIP_DEFLATED
            bundle.writestr(info, path.read_bytes())
    options, panels = examples(config)
    method = '## Choose the mode from the request\n' + section(skill_text, 'Choose the mode from the request')
    method += '\n## Do one bounded pass\n' + section(skill_text, 'Do one bounded pass')
    intro = re.split(r'^## ', benchmark, maxsplit=1, flags=re.M)[0]
    intro = re.sub(r'^# .+\n', '', intro)
    replacements = {'DESCRIPTION': esc(config['description']), 'EXAMPLE_OPTIONS': options, 'EXAMPLE_PANELS': panels,
                    'METHOD': markdown(method, SKILL / 'SKILL.md', output),
                    'CONTRACT': markdown(contract_path.read_text(), contract_path, output),
                    'SKILL_SOURCE': esc(skill_text), 'EVIDENCE_STATUS': evidence(config, output),
                    'BENCHMARK': markdown(intro, benchmark_path, output), 'BENCHMARK_FULL': markdown(benchmark, benchmark_path, output)}
    page = (ROOT / 'site/template.html').read_text(encoding='utf-8')
    for key, value in replacements.items():
        page = page.replace('@@' + key + '@@', value)
    if re.search(r'@@[A-Z_]+@@', page):
        raise ValueError('Unresolved site template placeholder')
    (output / 'index.html').write_text(page, encoding='utf-8')
    print(f'Built {output}: {len(config["examples"])} fictional examples, {len(skill_files())} portable skill files, {len(copied)} linked source files')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    build(parser.parse_args().output)
