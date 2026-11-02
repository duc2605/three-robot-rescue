import json
from social_navigation_planner.goal_history import GoalHistory


def test_goals_remember_each_selection_and_clock_reset(tmp_path):
    history=GoalHistory(tmp_path)
    history.update_clock(1.)
    assert not history.path.exists()
    history.select(2.,(1.,2.))
    history.select(4.,(3.,4.))
    history.update_clock(.1)
    rows=[json.loads(line) for line in history.path.read_text().splitlines()]
    assert [r['xy'] for r in rows]==[[1.,2.],[3.,4.],[3.,4.]]
    assert [r['epoch'] for r in rows]==[0,0,1]
    assert rows[-1]['source']=='retained_after_clock_reset'


def test_goal_recording_disabled_and_nonfinite_ignored(tmp_path,monkeypatch):
    monkeypatch.delenv('SOCIAL_REPLAY_DIRECTORY',raising=False)
    assert GoalHistory.from_environment() is None
    history=GoalHistory(tmp_path)
    history.select(1.,(float('nan'),0.))
    assert not history.path.exists()
