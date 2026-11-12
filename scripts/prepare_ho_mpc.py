#!/usr/bin/env python3
"""Fetch pinned upstream Paper5 sources into a user cache; no build or pip install.

Run explicitly using the README. Does not vendor unlicensed upstream code into
this repository, run its setup scripts, or clone unrelated ROS submodules.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'social_navigation_planner'))
from social_navigation_planner.paper_models.upstream_sources import SOURCES, QP_COMMIT, QP_REPOSITORY


def checkout(repository, commit, directory):
    if not directory.exists():
        directory.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git','clone','--no-checkout',repository+'.git',str(directory)],check=True)
        subprocess.run(['git','-C',str(directory),'checkout','--detach',commit],check=True)
    actual=subprocess.check_output(['git','-C',str(directory),'rev-parse','HEAD'],text=True).strip()
    if actual!=commit:
        raise SystemExit(f'{directory}: expected {commit}, found {actual}; use a fresh cache path')
    subprocess.run(['git','-C',str(directory),'diff','--exit-code','--quiet','HEAD'],check=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=Path.home()/'.cache/three-robot-rescue/paper5')
    args=parser.parse_args();root=args.directory.expanduser().resolve()
    checkout(SOURCES[5]['repository'],SOURCES[5]['commit'],root/'upstream')
    checkout(QP_REPOSITORY,QP_COMMIT,root/'hierarchical_qp')
    manifest={'paper5':SOURCES[5], 'hierarchical_qp':{'repository':QP_REPOSITORY,'commit':QP_COMMIT}}
    (root/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Pinned sources prepared: {root}. Install optional Python dependencies using README_PAPER5_HO_MPC.md.')


if __name__=='__main__':main()
