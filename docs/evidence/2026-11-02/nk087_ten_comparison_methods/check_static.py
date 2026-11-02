"""Validate changed source syntax/paths only; never import or execute ROS/policies."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PLANNER = ROOT/'social_navigation_planner/social_navigation_planner'
LIB = PLANNER/'comparison_methods'
LAUNCH = ROOT/'social_navigation_sim/launch'
methods = json.loads((OUT/'method_catalog.json').read_text())
paths = [PLANNER/'comparison_controller.py', ROOT/'social_navigation_planner/setup.py',
         ROOT/'social_navigation_planner/test/test_comparison_methods.py',
         ROOT/'social_navigation_planner/test/test_comparison_adapter.py']
paths += list(LIB.rglob('*.py'))
paths += [LAUNCH/x for x in ['_comparison_backend.py','comparison.launch.py',
                            'dstar_mpc.launch.py','social_navigation.launch.py']]
paths += [LAUNCH/f"paper{m['paper_number']}_{m['slug']}.launch.py" for m in methods]
for p in paths:
    tree = ast.parse(p.read_text(), filename=str(p))
    # Resolve only new relative module imports, without importing them.
    if p.is_relative_to(LIB) or p == PLANNER/'comparison_controller.py':
        for n in ast.walk(tree):
            if not isinstance(n,ast.ImportFrom) or not n.level or not n.module:
                continue
            base = p.parent
            for _ in range(n.level-1):
                base = base.parent
            target = base.joinpath(*n.module.split('.'))
            assert target.with_suffix('.py').exists() or (target/'__init__.py').exists(), (p,n.module)
assert len(methods)==10
assert len({m['module'] for m in methods})==10
for m in methods:
    launch = LAUNCH/f"paper{m['paper_number']}_{m['slug']}.launch.py"
    assert f"comparison_launch({m['id']})" in launch.read_text()
    for layer in ['formation','trajectory','control','pipeline']:
        assert (LIB/m['module']/(layer+'.py')).exists()
for name in ['dstar_mpc.launch.py','social_navigation.launch.py']:
    tree=ast.parse((LAUNCH/name).read_text())
    declares=[n for n in ast.walk(tree) if isinstance(n,ast.Call)
              and getattr(n.func,'id','')=='DeclareLaunchArgument'
              and n.args and isinstance(n.args[0],ast.Constant)
              and n.args[0].value=='navigation_backend']
    choices=ast.literal_eval(next(k.value for k in declares[0].keywords if k.arg=='choices'))
    assert choices==['baseline','paper1','paper2']+[m['backend'] for m in methods]
for name in ['scripts/run_dynamic.sh','scripts/run_comparison.sh']:
    subprocess.run(['bash','-n',str(ROOT/name)],check=True)
docs=[ROOT/'README.md',ROOT/'README_PAPERS_03_12.md']
docs += [ROOT/f"README_PAPER{m['paper_number']}_{m['slug'].upper()}.md" for m in methods]
blocks=0
for p in docs:
    s=p.read_text()
    assert sum(line.startswith('```') for line in s.splitlines())%2==0,p
    for b in re.findall(r'```bash\n(.*?)```',s,re.S):
        subprocess.run(['bash','-n'],input=b,text=True,check=True)
        blocks+=1
    for target in re.findall(r'\]\(([^)]+)\)',s):
        if '://' in target or target.startswith('#'):
            continue
        assert (p.parent/target.split('#')[0]).exists(),(p,target)
report={'python_files_syntax_checked':len(paths),'documentation_bash_blocks_syntax_checked':blocks,
        'relative_import_paths_checked':True,'launch_choices_and_wrapper_mapping_checked':True,
        'shell_scripts_parsed_not_executed':2,'build_run':False,'tests_run':False,'gazebo_run':False,
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(OUT/'static_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k!='source_sha256'})
