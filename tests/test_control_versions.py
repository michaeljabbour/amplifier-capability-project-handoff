"""Versioned control and immutable record regressions; no provider execution."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import run
from control_selection import (Control, ControlError, CONTROL_CORPUS, CONTROL_REGISTRY, CONTROL_METADATA, CONTROL_TEXT,
                               committed_source_errors, freeze_control, read_frozen_control, select_current_control,
                               validate_length)


def fingerprints(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}


class ControlVersionTests(unittest.TestCase):
    def setUp(self):
        self.treatment = run.treatment()
        self.control = select_current_control(ROOT, self.treatment)

    def test_current_control_pins_exact_treatment_and_word_limit(self):
        metadata = self.control.metadata
        self.assertEqual(metadata['treatment_sha256'], run.digest(self.treatment))
        self.assertEqual(metadata['control_sha256'], run.digest(self.control.text))
        self.assertEqual(metadata['selection'], 'prefix_complete_sentence')
        self.assertEqual(metadata['treatment_words'], len(self.treatment.split()))
        self.assertEqual(metadata['control_words'], len(self.control.text.split()))
        self.assertLessEqual(abs(metadata['word_difference_fraction']), .05)
        self.assertTrue(self.control.text.endswith('.'))
        self.assertGreaterEqual(len((ROOT / metadata['corpus_path']).read_text().split()),
                                len(self.treatment.split()))

    def test_unknown_treatment_never_falls_back_to_old_corpus(self):
        with self.assertRaisesRegex(ControlError, 'No unique versioned neutral control'):
            select_current_control(ROOT, self.treatment + '\nA changed treatment.')

    def test_five_percent_gate_is_unchanged(self):
        self.assertEqual(validate_length('x ' * 100, 'x ' * 95), -.05)
        with self.assertRaisesRegex(ControlError, 'five percent'):
            validate_length('x ' * 100, 'x ' * 94)
        with self.assertRaisesRegex(ControlError, 'five percent'):
            validate_length('x ' * 100, 'x ' * 106)

    def test_changed_corpus_cannot_keep_recorded_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / 'evals/controls', root / 'evals/controls')
            corpus = root / self.control.metadata['corpus_path']
            corpus.write_text(corpus.read_text() + '\nAltered generic wording.\n')
            with self.assertRaisesRegex(ControlError, 'corpus hash mismatch'):
                select_current_control(root, self.treatment)

    def test_frozen_control_is_idempotent_and_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            freeze_control(folder, self.control)
            before = fingerprints(folder)
            freeze_control(folder, self.control)
            self.assertEqual(fingerprints(folder), before)
            frozen = read_frozen_control(folder, self.treatment, self.control.metadata)
            self.assertEqual(frozen.text, self.control.text)
            self.assertEqual(frozen.metadata, self.control.metadata)

    def test_freeze_collision_preserves_all_existing_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            freeze_control(folder, self.control)
            before = fingerprints(folder)
            changed = Control(self.control.text + ' changed', self.control.metadata)
            with self.assertRaisesRegex(ControlError, 'Frozen neutral-control input changed'):
                freeze_control(folder, changed)
            self.assertEqual(fingerprints(folder), before)

    def test_frozen_byte_and_metadata_tampering_are_rejected_without_writes(self):
        for name in (CONTROL_TEXT, CONTROL_METADATA):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                freeze_control(folder, self.control)
                target = folder / name
                if name == CONTROL_TEXT:
                    target.write_text(target.read_text().replace('Act', 'Work', 1))
                else:
                    value = json.loads(target.read_text())
                    value['control_id'] = 'unrecorded-control'
                    target.write_text(json.dumps(value))
                before = fingerprints(folder)
                with self.assertRaises(ControlError):
                    read_frozen_control(folder, self.treatment, self.control.metadata)
                self.assertEqual(fingerprints(folder), before)

    def test_frozen_control_cannot_be_reused_for_another_treatment(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            freeze_control(folder, self.control)
            with self.assertRaisesRegex(ControlError, 'another treatment'):
                read_frozen_control(folder, self.treatment + '\nChanged.', self.control.metadata)

    def test_offline_run_freezes_control_and_resumes_exactly(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(run, 'call', side_effect=AssertionError('No provider calls allowed')):
            args = ['--offline-smoke', '--run-id', 'control-v2', '--output-root', temp, '--date', '2026-11-02']
            self.assertEqual(run.main(args), 0)
            record = Path(temp) / '2026-11-02/control-v2'
            manifest = json.loads((record / 'manifest.json').read_text())
            metadata = manifest['configuration']['placebo_control']
            self.assertEqual(read_frozen_control(record / 'snapshots', self.treatment, metadata).text,
                             self.control.text)
            before_manifest = (record / 'manifest.json').read_bytes()
            before_snapshots = fingerprints(record / 'snapshots')
            self.assertEqual(run.main(args + ['--resume']), 0)
            self.assertEqual((record / 'manifest.json').read_bytes(), before_manifest)
            self.assertEqual(fingerprints(record / 'snapshots'), before_snapshots)
            summary = json.loads((record / 'summary.json').read_text())
            self.assertEqual(summary['provider_calls'], 0)
            self.assertIsNone(summary['metrics_by_condition'])
            self.assertIsNone(summary['paired_comparisons'])

    def test_resume_rejects_old_identity_before_any_record_write(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()), \
                patch.object(run, 'call', side_effect=AssertionError('No provider calls allowed')):
            record = Path(temp) / '2026-11-02/old-control'
            (record / 'snapshots').mkdir(parents=True)
            (record / 'manifest.json').write_text(json.dumps({'identity': 'legacy-control-identity'}))
            (record / 'snapshots/placebo.snapshot.txt').write_bytes((ROOT / 'evals/placebo.txt').read_bytes())
            (record / 'retained-outcome.json').write_text('{"old_outcome":"preserve"}')
            before = fingerprints(record)
            with self.assertRaises(SystemExit) as error:
                run.main(['--offline-smoke', '--resume', '--run-id', 'old-control',
                          '--output-root', temp, '--date', '2026-11-02'])
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(fingerprints(record), before)

    def test_resume_rejects_tampered_frozen_control_before_any_record_write(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(run, 'call', side_effect=AssertionError('No provider calls allowed')):
            args = ['--offline-smoke', '--run-id', 'tampered-control', '--output-root', temp, '--date', '2026-11-02']
            self.assertEqual(run.main(args), 0)
            record = Path(temp) / '2026-11-02/tampered-control'
            path = record / 'snapshots' / CONTROL_TEXT
            path.write_text(path.read_text().replace('Act', 'Work', 1))
            before = fingerprints(record)
            with self.assertRaisesRegex(ControlError, 'bytes differ'):
                run.main(args + ['--resume'])
            self.assertEqual(fingerprints(record), before)


    def test_frozen_corpus_and_registry_tampering_are_rejected(self):
        for name in (CONTROL_CORPUS, CONTROL_REGISTRY):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                freeze_control(folder, self.control)
                target = folder / name
                target.write_bytes(target.read_bytes() + b'\n')
                before = fingerprints(folder)
                with self.assertRaisesRegex(ControlError, 'source bytes differ'):
                    read_frozen_control(folder, self.treatment, self.control.metadata)
                self.assertEqual(fingerprints(folder), before)

    def test_live_commit_gate_checks_git_and_selected_current_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            relative = 'evals/controls/synthetic.txt'
            path = root / relative
            path.parent.mkdir(parents=True)
            path.write_text('Generic synthetic control.\n')
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                                      text=True, check=True).stdout.strip()
            git('init', '--template=')
            git('add', '--', relative)
            git('-c', 'core.hooksPath=/dev/null', '-c', 'user.name=benchmark-test',
                '-c', 'user.email=noreply@example.com', 'commit', '--no-gpg-sign', '-m', 'Synthetic test input')
            commit = git('rev-parse', 'HEAD')
            hashes = {relative: run.digest(path.read_bytes())}
            self.assertEqual(committed_source_errors(root, hashes, commit), [])
            path.write_text('Changed synthetic control.\n')
            self.assertTrue(any('changed after selection' in error
                                for error in committed_source_errors(root, hashes, commit)))
            hashes[relative] = run.digest(path.read_bytes())
            self.assertTrue(any('differs from selected Git commit' in error
                                for error in committed_source_errors(root, hashes, commit)))

    def test_live_runner_input_drift_stops_before_record_or_transport(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(run, 'call', side_effect=AssertionError('No provider calls allowed')), \
                patch.object(run, 'committed_source_errors', return_value=['Synthetic selected-input drift']):
            with self.assertRaisesRegex(ControlError, 'Synthetic selected-input drift'):
                run.main(['--pilot', '--model', 'gpt-4.1-mini-2025-04-14',
                          '--judge', 'claude-sonnet-4-6', '--run-id', 'blocked-drift',
                          '--output-root', temp, '--date', '2026-11-02'])
            self.assertEqual(list(Path(temp).iterdir()), [])


    def test_coherent_selected_text_metadata_and_manifest_tamper_fails_derivation(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            freeze_control(folder, self.control)
            text_path = folder / CONTROL_TEXT
            text_path.write_text(text_path.read_text().replace('Act', 'Work', 1))
            metadata_path = folder / CONTROL_METADATA
            metadata = json.loads(metadata_path.read_text())
            metadata['control_sha256'] = run.digest(text_path.read_text())
            metadata_path.write_text(json.dumps(metadata))
            # Treat changed metadata as if an edited manifest repeated it too.
            # Raw frozen corpus and registry remain the original proof inputs.
            before = fingerprints(folder)
            with self.assertRaisesRegex(ControlError, 'does not match corpus/registry selection'):
                read_frozen_control(folder, self.treatment, metadata)
            self.assertEqual(fingerprints(folder), before)


if __name__ == '__main__':
    unittest.main()
