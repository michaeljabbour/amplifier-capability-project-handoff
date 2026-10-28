#!/usr/bin/env python3
"""Install the portable text skill without packages, services or credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

SOURCE = Path(__file__).resolve().parents[1] / 'skills' / 'project-handoff'


def package_files(source=SOURCE):
    if source.is_symlink() or not source.is_dir():
        raise ValueError('The portable source directory is missing or is a symlink')
    files = []
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError('Portable package must not contain symlinks')
        if path.is_file():
            if path.suffix != '.md':
                raise ValueError('Portable package contains an unexpected non-Markdown file')
            files.append(path)
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Portable package is missing SKILL.md')
    if sum(p.name == 'SKILL.md' for p in files) != 1:
        raise ValueError('Portable package must have exactly one SKILL.md')
    if 'name: project-handoff' not in (source / 'SKILL.md').read_text():
        raise ValueError('Skill name does not match project-handoff')
    for path in files:
        for link in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)', path.read_text()):
            if ':' in link or link.startswith('#'):
                continue
            linked = (path.parent / link.split('#')[0]).resolve()
            if not linked.is_relative_to(source.resolve()) or not linked.is_file():
                raise ValueError('A portable reference is missing or leaves the package')
    return files


def digest(source):
    return {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in package_files(source)}


def install(destination, check=False):
    expected = digest(SOURCE)
    parent = Path(destination).expanduser()
    target = parent / 'project-handoff'
    if parent.is_symlink() or target.is_symlink():
        raise ValueError('Refusing a symlink destination')
    if target.resolve().is_relative_to(SOURCE.resolve()) or SOURCE.resolve().is_relative_to(target.resolve()):
        raise ValueError('Destination must be separate from the source package')
    if check:
        if not target.is_dir() or digest(target) != expected:
            raise ValueError('Installed files do not match the source package')
        return {'status': 'verified', 'path': str(target), 'files': len(expected)}
    if target.exists():
        if target.is_dir() and digest(target) == expected:
            return {'status': 'unchanged', 'path': str(target), 'files': len(expected)}
        raise ValueError('Destination already contains different files; no files were changed. Review and back up that copy before replacing it.')
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.project-handoff-install-', dir=parent))
    try:
        for relative in expected:
            out = staging / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / relative, out)
        if digest(staging) != expected:
            raise ValueError('Staged copy failed integrity validation')
        # os.rename fails when an existing non-empty destination appears during
        # installation. It never merges user files with the installed skill.
        os.rename(staging, target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {'status': 'installed', 'path': str(target), 'files': len(expected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, help='Parent of the host skill directory; installs a project-handoff child')
    parser.add_argument('--check', action='store_true', help='Verify a prior install without changing files')
    args = parser.parse_args()
    try:
        result = install(args.dest, args.check)
    except (OSError, ValueError) as error:
        parser.exit(1, 'Project Handoff: ' + str(error) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
