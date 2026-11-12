"""Evaluation-map snapshots and the browser's shortest-grid-route implementation."""
import base64
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from replay_data import evaluation_map, add_evaluation_map


def test_dynamic_reference_uses_user_selected_static_tv_zone():
    reference=evaluation_map(ROOT,'social_dynamic')
    tv=next(z for z in reference['zones'] if z['name']=='tv_group')
    assert tv['size']==[2.3,3.7]
    assert 'social_static_scene.json' in reference['tv_source']
    assert len(base64.b64decode(reference['occupied_b64'])) == reference['width']*reference['height']


def test_old_recording_identifies_current_assets_fallback():
    scene={'world':'social_static'}
    enriched=add_evaluation_map(scene,ROOT)
    assert enriched['evaluation_map']['snapshot_source']=='current_project_assets_for_old_recording'
    assert 'evaluation_map' not in scene


def test_worker_reference_grid_and_authored_zone():
    node=shutil.which('node') or shutil.which('nodejs')
    if node is None:
        pytest.skip('Node.js needed for browser worker regression')
    html=(ROOT/'scripts/replay_viewer.html').read_text()
    function=html.split('function referenceRoute(input){',1)[1].split('let routeComparisonCache=',1)[0]
    code='function referenceRoute(input){'+function
    code+='''
const assert=require('node:assert/strict');
const map={width:12,height:12,resolution:1,origin:[0,0,0],clearance:.01,
 occupied_b64:Buffer.alloc(144).toString('base64'),zones:[]};
const start=[2.5,5.5],goal=[9.5,5.5];
let result=referenceRoute({map,start,goal,candidate:[start,goal]});
assert.equal(result.length_m,7);assert.equal(result.candidate_valid,true);
map.zones=[{center:[6,5.5],size:[1,3]}];
result=referenceRoute({map,start,goal,candidate:[start,goal]});
assert.ok(result.length_m>7);assert.equal(result.candidate_valid,false);
map.zones=[{center:start,size:[1,1]}];
result=referenceRoute({map,start,goal,candidate:null});
assert.ok(result.error);
'''
    subprocess.run([node,'-'],input=code,text=True,check=True,capture_output=True)


def test_actual_distance_goal_scope_epoch_reset_and_live_append():
    node=shutil.which('node') or shutil.which('nodejs')
    if node is None:
        pytest.skip('Node.js needed for viewer distance regression')
    html=(ROOT/'scripts/replay_viewer.html').read_text()
    functions='let actualRouteCache='+html.split('let actualRouteCache=',1)[1].split('function drawPlannedRoutes',1)[0]
    code="""
const assert=require('node:assert/strict');
const pose=(x,y)=>({name:'robot3',p:[x,y,0,0,0,0]});
let frames=[{epoch:0,t:0,objects:[pose(0,0)]},
 {epoch:0,t:.5,objects:[pose(3,0)]},{epoch:0,t:1,objects:[pose(3,4)]},
 {epoch:1,t:0,objects:[pose(100,100)]},{epoch:1,t:.5,objects:[pose(100,101)]}];
function active(o){return Boolean(o)&&o.p.every(Number.isFinite)&&o.p[2]>-5;}
function goalAt(frame){return frame.epoch===0&&frame.t>=.5?{t:.5,epoch:0}:null;}
"""+functions+"""
assert.equal(actualRouteData('robot3',2,false).length,7);
assert.equal(actualRouteData('robot3',2,true).length,4);
assert.equal(actualRouteData('robot3',4,false).length,1);
frames.push({epoch:1,t:.75,objects:[pose(100,102)]});
assert.equal(actualRouteData('robot3',5,false).length,2);
frames.push({epoch:1,t:3,objects:[pose(200,200)]});
const result=actualRouteData('robot3',6,false);
assert.equal(result.length,2);assert.equal(result.gaps,1);
"""
    subprocess.run([node,'-'],input=code,text=True,check=True,capture_output=True)
