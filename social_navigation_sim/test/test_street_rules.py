"""Pedestrian permissions without ROS or Gazebo."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from street_rules import walkable, crossing, enters_crossing


def test_road_shortcuts_are_forbidden_and_zebra_paths_are_allowed():
    assert not walkable(0,0)
    assert not walkable(3,1)
    assert walkable(10,-12)
    assert walkable(8,0) and walkable(0,-8)


def test_red_entry_gate_distinguishes_entry_from_finishing_crossing():
    assert enters_crossing((8.,-6.5),(8.,-6.2))
    assert not enters_crossing((8.,-5.),(8.,-4.))
    assert not enters_crossing((8.,6.2),(8.,6.5))
    assert crossing(0.,0.) is None


def test_robot_uses_green_of_its_own_crosswalk_axis():
    from street_rules import entry_axes, signal_allows_entry
    signal={'stamp':10.,'pedestrian_green_axes':[True,False],
            'pedestrian_remaining_axes':[5.,0.]}
    assert entry_axes((-6.5,8.),(-6.2,8.))=={0}
    assert entry_axes((8.,-6.5),(8.,-6.2))=={1}
    assert signal_allows_entry(signal,0,10.1)
    assert not signal_allows_entry(signal,1,10.1)
    assert not signal_allows_entry(signal,0,11.)
    signal['pedestrian_remaining_axes'][0]=.4
    assert not signal_allows_entry(signal,0,10.1)
