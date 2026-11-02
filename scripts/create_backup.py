#!/usr/bin/env python3
"""Create and verify a source snapshot before editing this project."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
from zoneinfo import ZoneInfo

EXCLUDED = {'.git', '.aws', '.codex', '.agents', '.vscode', 'build', 'install',
            'log', 'recordings', 'backups', '.pytest_cache', '__pycache__'}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()


def create_backup(root, reason):
    stamp = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%Y%m%d_%H%M%S_%f')
    label = re.sub(r'[^a-zA-Z0-9_-]+', '_', reason).strip('_')[:64] or 'before_change'
    folder = root / 'backups' / f'{stamp}_{label}'
    folder.mkdir(parents=True, exist_ok=False)
    archive = folder / 'source.tar.gz'
    paths = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in sorted(files):
            path = Path(current) / name
            if name.endswith(('.pyc', '.pyo')):
                continue
            paths.append(path)
        for name in dirs:
            path = Path(current) / name
            if path.is_symlink():
                paths.append(path)
    with tarfile.open(archive, 'x:gz', dereference=False) as output:
        for path in paths:
            output.add(path, arcname=path.relative_to(root), recursive=False)
    hashes, links = {}, {}
    with tarfile.open(archive, 'r:gz') as saved:
        for item in saved:
            path = root / item.name
            if item.isfile():
                value = hashlib.sha256(saved.extractfile(item).read()).hexdigest()
                if digest(path) != value:
                    raise RuntimeError(f'File changed during snapshot: {item.name}; retry before editing')
                hashes[item.name] = value
            elif item.issym():
                if os.readlink(path) != item.linkname:
                    raise RuntimeError(f'Symlink changed during snapshot: {item.name}')
                links[item.name] = item.linkname
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True)
    manifest = {'created_vietnam': datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                'reason': reason, 'git_head': head.stdout.strip(),
                'archive_sha256': digest(archive), 'file_sha256': hashes, 'symlinks': links,
                'excluded': sorted(EXCLUDED), 'verified_against_source': True,
                'scope': 'Source, assets, tests, docs; no generated build/install/log or private credentials.'}
    (folder / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    status = subprocess.run(['git', 'status', '--short'], cwd=root, capture_output=True, text=True)
    (folder / 'git-status.txt').write_text(status.stdout)
    print(folder)
    return folder


def verify_backup(folder):
    manifest = json.loads((folder / 'manifest.json').read_text())
    archive = folder / 'source.tar.gz'
    if digest(archive) != manifest['archive_sha256']:
        raise RuntimeError('Archive SHA-256 mismatch')
    hashes, links = {}, {}
    with tarfile.open(archive, 'r:gz') as saved:
        for item in saved:
            name = Path(item.name)
            if name.is_absolute() or '..' in name.parts:
                raise RuntimeError('Unsafe archive path: ' + item.name)
            if item.isfile():
                hashes[item.name] = hashlib.sha256(saved.extractfile(item).read()).hexdigest()
            elif item.issym():
                links[item.name] = item.linkname
            elif not item.isdir():
                raise RuntimeError('Unexpected archive member: ' + item.name)
    if hashes != manifest['file_sha256'] or links != manifest.get('symlinks', {}):
        raise RuntimeError('Archive contents do not match manifest')
    print(f'Verified {len(hashes)} files: {folder}')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--reason', help='Change or checkpoint about to be made')
    mode.add_argument('--verify', type=Path, help='Verify an existing snapshot without extracting')
    args = parser.parse_args()
    if args.verify:
        verify_backup(args.verify.resolve())
    else:
        create_backup(Path(__file__).resolve().parents[1], args.reason)
