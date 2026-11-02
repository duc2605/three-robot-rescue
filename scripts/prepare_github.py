#!/usr/bin/env python3
"""Check and optionally zip the maintained source tree, excluding local state."""

import argparse
import ast
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ('social_navigation_planner', 'social_navigation_sim', 'docs', 'scripts')
EXCLUDED = {'__pycache__', '.pytest_cache', '.git', 'build', 'install', 'log'}
PRIVATE_NAMES = {'.env', '.aws', '.codex', '.agents', '.vscode', '.idea'}
TEXT_SUFFIXES = {'.py', '.xml', '.yaml', '.json', '.md', '.txt', '.cpp', '.cfg', '.xacro', '.rviz'}
SECRET_PATTERNS = (
    re.compile(r'-{5}BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-{5}'),
    re.compile(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'),
    re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
)


def source_files():
    paths = list(ROOT.glob('*.md')) + [ROOT / '.gitignore']
    for directory in SOURCE_DIRS:
        paths.extend(p for p in (ROOT / directory).rglob('*') if p.is_file())
    return sorted({p for p in paths if not (
        set(p.relative_to(ROOT).parts) & EXCLUDED
        or any(part.endswith('.egg-info') for part in p.relative_to(ROOT).parts)
    )})


def check(paths):
    for name in SOURCE_DIRS[:2]:
        package = ROOT / name
        assert ET.parse(package / 'package.xml').getroot().findtext('name') == name
    planner = ROOT / SOURCE_DIRS[0]
    assert (planner / 'resource' / planner.name).is_file()
    assert (planner / planner.name / '__init__.py').is_file()
    for path in paths:
        relative = path.relative_to(ROOT)
        assert not path.is_symlink(), f'Source symlink needs review: {relative}'
        assert not set(relative.parts) & PRIVATE_NAMES, f'Local configuration: {relative}'
        assert not path.name.startswith('.env') and path.suffix not in {'.pem', '.key'}, relative
        assert path.stat().st_size < 100 * 1024 * 1024, f'File exceeds 100 MiB: {relative}'
        if path.suffix in TEXT_SUFFIXES:
            text = path.read_text()
            assert not any(pattern.search(text) for pattern in SECRET_PATTERNS), (
                f'Potential credential requires review: {relative}')
            if path.suffix == '.py':
                ast.parse(text, filename=str(relative))
    print(f'Checked {len(paths)} source files; package names, Python syntax and size limits OK.')
    print('No matches for the checked private-key/AWS/GitHub-token patterns; not a full secret audit.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional ZIP path outside the source tree')
    args = parser.parse_args()
    paths = source_files()
    check(paths)
    if args.output:
        output = args.output.resolve()
        assert ROOT not in output.parents, 'Write the archive outside this repository.'
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                archive.write(path, Path(ROOT.name) / path.relative_to(ROOT))
        print(f'Source archive: {output}')


if __name__ == '__main__':
    main()
