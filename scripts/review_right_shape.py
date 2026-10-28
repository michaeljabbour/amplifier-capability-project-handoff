#!/usr/bin/env python3
"""Apply the unchanged Right Shape skill to this package through a live reviewer.

This is an application check, not a controlled efficacy study of Right Shape.
No tools are available to the reviewer. All inputs are source text or an
explicitly fictional adversarial design. Provider credentials stay in env.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.providers import call, ProviderError


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--right-shape', type=Path, required=True, help='Source checkout of unchanged Right Shape')
    parser.add_argument('--phase', choices=('design', 'final'), required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--provider', choices=('anthropic', 'openai'), default='anthropic')
    parser.add_argument('--model', default='claude-haiku-4-5-20251001')
    parser.add_argument('--structured', action='store_true', help='Request an explicit numeric card for deterministic rubric checks')
    args = parser.parse_args()
    supported_rates = {
        ('openai', 'gpt-4.1-mini-2025-04-14'): (.4, 1.6),
        ('anthropic', 'claude-haiku-4-5-20251001'): (1, 5),
        ('anthropic', 'claude-sonnet-4-6'): (3, 15),
    }
    rates = supported_rates.get((args.provider, args.model))
    if rates is None:
        parser.error('Use a documented provider/model pair with a verified price reservation')
    if not args.run_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.run_id):
        parser.error('Use a safe run identifier')
    stamp = datetime.now(ZoneInfo('America/New_York'))
    output = ROOT / 'docs' / 'evaluations' / stamp.date().isoformat() / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    rs = args.right_shape.resolve()
    method = (rs / 'skills/right-shape/SKILL.md').read_text()
    rubric = (rs / 'skills/right-shape/references/rubric.md').read_text()
    (output / 'right-shape.skill.snapshot.md').write_text(method)
    (output / 'rubric.snapshot.md').write_text(rubric)
    (output / 'right-shape-LICENSE.txt').write_bytes((rs / 'LICENSE').read_bytes())
    paths = ['docs/DESIGN.md', 'project.json', 'README.md', 'skills/project-handoff/SKILL.md',
             'skills/project-handoff/references/method.md', 'skills/project-handoff/references/handoff-contract.md',
             'scripts/install.py', 'bundle.md', 'behaviors/project-handoff.yaml', 'modes/handoff.md',
             'recipes/project-handoff-capture.yaml', 'docs/BENCHMARK.md']
    if args.phase == 'final':
        paths += ['docs/VALIDATION.md', 'docs/EVALUATION.md']
    sources = {path: (ROOT / path).read_text() for path in paths if (ROOT / path).is_file()}
    (output / 'package-sources.json').write_text(json.dumps(sources, indent=2) + '\n')
    system = 'You are an independent reviewer. Apply this supplied skill and canonical rubric exactly. You have no tools. Do not invent execution or user evidence.\n\n' + method + '\n\n' + rubric
    if args.phase == 'design':
        cases = {
            'actual-design': 'Use Place on the smallest genuinely useful Project Handoff job: one person asks for a brief handoff/resumption using ordinary project files. Use the supplied implementation/design as evidence. Give the canonical placement card with N1-N4, gates, shape checks, engine, replaceability gaps and a benchmark that could reject the design. Distinguish method from optional adapters.\n\n' + json.dumps(sources),
            'unsafe-variant': 'Fictional adversarial variant, not implemented: Project Handoff runs unattended on file-change events across every project; retains private work and untrusted copied messages; uploads all files to an external endpoint; can overwrite decisions and send updates without approval; requires an unpublished Memory storage package and reads credentials from a local file. There is no outcome evaluator, filesystem isolation, hard budget or named owner. Path has listed branches, context spans multiple windows, operation is ongoing, initiative is event-triggered. Use Place and then give the top Check blockers. Never exceed the lowest failed gate cap. Do not approve publication or execution.'
        }
    else:
        cases = {'built-package': 'Use Check on this actual source package. The source evidence and validation report are supplied below; code-test and live-task evidence must remain distinct from real-user evidence. Judge independent installation without Memory, canonical packaging, meaningful benchmark, honest claims and replaceability. Propose removals before additions. Do not demand a service, a new scoring model or automatic memory for a bounded file handoff. Name only supported gaps; a sound design may be left alone.\n\n' + json.dumps(sources)}
    if args.structured:
        format_request = ('\n\nReturn one JSON object, no Markdown fence, with fields: verdict (string), '
                          'need (object with integer N1,N2,N3,N4,total,rung), failed_gates (array of gate IDs), '
                          'ceiling (integer), placed_rung (integer), shape_checks (array of H IDs), '
                          'shape (single or outer-harness), engine (string), grounding (object mapping each gate '
                          'to pass/fail/unknown and evidence), gaps (array), benchmark (string). '
                          'Use actual numeric rubric scales and distinguish benchmark apparatus from the deployed method. '
                          'Unknown enforcement cannot establish a passing gate. Do not infer runtime isolation or '
                          'hard token limits from portable instructions. The optional evaluation apparatus is not '
                          'the skill runtime. The no-model-call claim applies to deterministic helpers only; '
                          'the caller applying this skill still uses an LLM.')
        cases = {name: prompt + format_request for name, prompt in cases.items()}
    records = []
    for name, prompt in cases.items():
        # At most two calls. UTF-8 input bytes are a conservative token bound;
        # reserve the output cap at the selected model's documented rates.
        reserve = (len((system + prompt).encode()) * rates[0] + 5000 * rates[1]) / 1_000_000
        if reserve > .5 or sum(r['cost_upper_bound_usd'] for r in records) + reserve > 1:
            raise SystemExit('Right Shape review exceeds its $1 nominal uncached reservation')
        (output / (name + '.prompt.json')).write_text(json.dumps({'system': system, 'user': prompt}, indent=2) + '\n')
        record = {'case': name, 'cost_upper_bound_usd': reserve, 'status': 'pending'}
        try:
            response = call(args.provider, args.model, system, prompt, 5000, timeout=60)
            record.update(response)
            record['status'] = 'completed'
            record['nominal_uncached_usd'] = (response['input_tokens'] * rates[0] + response['output_tokens'] * rates[1]) / 1_000_000
            (output / (name + '.response.md')).write_text(response['text'] + '\n')
            if args.structured:
                value = json.loads(response['text'])
                needs = value['need']
                total = sum(needs[k] for k in ('N1', 'N2', 'N3', 'N4'))
                bands = []
                part = rubric.split('## Need to rung\n', 1)[1].split('\n## ', 1)[0]
                for line in part.splitlines():
                    match = re.match(r'\| (\d+) to (\d+) \| (\d+) \|', line)
                    if match:
                        bands.append(tuple(map(int, match.groups())))
                wanted = next(r for low, high, r in bands if low <= total <= high)
                gates = {}
                part = rubric.split('## Gates\n', 1)[1].split('\n## ', 1)[0]
                for line in part.splitlines():
                    if re.match(r'^\| G\d+ ', line):
                        cells = [s.strip() for s in line.strip('|').split('|')]
                        gates[cells[0].split()[0]] = int(cells[2])
                ceiling = min([gates[g] for g in value['failed_gates']] or [9])
                expected_shape = 'outer-harness' if len(value['shape_checks']) >= 2 else 'single'
                checks = {'scores_in_range': all(type(needs[k]) is int and 0 <= needs[k] <= 3 for k in ('N1', 'N2', 'N3', 'N4')),
                          'need_total': needs['total'] == total, 'need_rung': needs['rung'] == wanted,
                          'gate_ceiling': value['ceiling'] == ceiling,
                          'no_placement_above_cap': value['placed_rung'] <= min(wanted, ceiling),
                          'composition': value['shape'] == expected_shape}
                if name == 'unsafe-variant':
                    checks['planted_gates_detected'] = set(value['failed_gates']) == set(gates)
                record['canonical_checks'] = checks
                record['canonical_checks_pass'] = all(checks.values())
                (output / (name + '.card.json')).write_text(json.dumps(value, indent=2) + '\n')
        except (ProviderError, ValueError, KeyError, StopIteration) as error:
            record.update(status='blocked', error=str(error))
        records.append(record)
        (output / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
        print(name + ': ' + record['status'], flush=True)
    manifest = {'kind': 'live Right Shape application check', 'phase': args.phase, 'date': stamp.isoformat(),
                'model': args.model, 'provider': args.provider, 'structured': args.structured, 'source_hashes': {p: digest(t.encode()) for p, t in sources.items()},
                'review_script_sha256': digest(Path(__file__).read_bytes()),
                'nominal_uncached_rates_per_million': {'input': rates[0], 'output': rates[1]},
                'right_shape_sha256': digest(method.encode()), 'rubric_sha256': digest(rubric.encode()),
                'cases': [r['case'] for r in records], 'completed': sum(r['status'] == 'completed' for r in records),
                'claims_limit': 'No baseline/placebo comparison or causal efficacy claim for Right Shape; no real-user outcome evidence.'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(output)
    return 0 if manifest['completed'] == len(records) else 1


if __name__ == '__main__':
    raise SystemExit(main())
