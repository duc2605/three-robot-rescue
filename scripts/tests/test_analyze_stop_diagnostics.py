import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze_stop_diagnostics import analyze


def test_contact_context_matches_epoch_and_preserves_missing_data(tmp_path):
    samples=[{'kind':'controller','epoch':0,'t':9.8,'reason':'escape_all_rollouts_rejected',
              'command':[0,0,0]},
             {'kind':'controller','epoch':1,'t':9.9,'reason':'wrong_epoch'}]
    (tmp_path/'stop_robot3.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in samples))
    frame={'epoch':0,'t':10.05,'contacts':[{'a':'robot3','b':'person','first_t':10.,'last_t':10.02},
                                         {'a':'robot3','b':'person','first_t':10.01,'last_t':10.04}]}
    (tmp_path/'world_frames.jsonl').write_text(json.dumps(frame)+'\n'+ '{"unfinished":')
    result=analyze(tmp_path)
    assert len(result['physics_contact_context'])==1
    event=result['physics_contact_context'][0]
    assert event['first_t']==10. and event['last_t']==10.04
    assert event['context']['robot3']==samples[:1]
    assert 'missing' in event['context']['coordinator']


def test_missing_diagnostics_not_synthesized(tmp_path):
    assert analyze(tmp_path)['streams']=={}
    assert analyze(tmp_path)['physics_contact_context']==[]
