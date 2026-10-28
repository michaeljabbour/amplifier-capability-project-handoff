"""Verify the portable install preserves user files and works without services."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'scripts' / 'install.py'
spec = importlib.util.spec_from_file_location('handoff_install', MODULE)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def test_fresh_install_roundtrip_and_idempotence(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(installer.install(directory)['status'], 'installed')
            self.assertEqual(installer.install(directory, check=True)['status'], 'verified')
            self.assertEqual(installer.install(directory)['status'], 'unchanged')
            self.assertEqual(installer.digest(Path(directory) / 'project-handoff'), installer.digest(installer.SOURCE))

    def test_conflicting_local_edit_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            installer.install(directory)
            skill = Path(directory) / 'project-handoff' / 'SKILL.md'
            skill.write_text('Local edited instructions must survive.\n')
            with self.assertRaises(ValueError):
                installer.install(directory)
            self.assertEqual(skill.read_text(), 'Local edited instructions must survive.\n')

    def test_symlink_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            untouched = parent / 'existing'
            untouched.mkdir()
            (parent / 'project-handoff').symlink_to(untouched, target_is_directory=True)
            with self.assertRaises(ValueError):
                installer.install(parent)
            self.assertEqual(list(untouched.iterdir()), [])

    def test_all_references_travel_with_the_text(self):
        with tempfile.TemporaryDirectory() as directory:
            installer.install(directory)
            installed = Path(directory) / 'project-handoff'
            self.assertGreaterEqual(len(installer.package_files(installed)), 3)
            self.assertTrue((installed / 'references' / 'handoff-contract.md').is_file())


if __name__ == '__main__':
    unittest.main()
