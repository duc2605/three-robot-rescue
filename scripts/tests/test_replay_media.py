"""Video seeking, session isolation, sparse timing and window selection contracts."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from replay_media import byte_range, media_path, camera_groups, ensure_camera_videos
from record_replay_media import window_candidates


def test_byte_ranges_support_browser_seeking_and_suffix():
    assert byte_range('bytes=10-19',100) == (10,19,True)
    assert byte_range('bytes=90-',100) == (90,99,True)
    assert byte_range('bytes=-12',100) == (88,99,True)
    assert byte_range(None,100) == (0,99,False)
    for invalid in ['bytes=100-','bytes=20-10','bytes=0-1,4-5','bytes=-0']:
        with pytest.raises(ValueError):
            byte_range(invalid,100)


def test_media_path_cannot_leave_selected_recording_even_via_symlink(tmp_path):
    folder=tmp_path/'recording';(folder/'media').mkdir(parents=True)
    private=tmp_path/'other.mp4';private.write_bytes(b'not-public')
    (folder/'media'/'escape.mp4').symlink_to(private)
    for name in ['../../other.mp4','escape.mp4']:
        with pytest.raises(ValueError):
            media_path(folder,name)
    (folder/'media'/'gazebo.mp4').write_bytes(b'video')
    assert media_path(folder,'gazebo.mp4').parent == (folder/'media').resolve()


def test_camera_groups_preserve_sparse_times_and_clock_reset_epochs(tmp_path):
    rows=[dict(t=t,stamp=t,epoch=epoch,kind='camera',source='raw',image='data:image/jpeg;base64,YQ==')
          for epoch,t in [(0,1.),(0,5.),(1,.1),(1,.2)]]
    (tmp_path/'perception.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)+'{"t":')
    groups=camera_groups(tmp_path)
    assert [r['t'] for r in groups[(0,'raw')]] == [1.,5.]
    assert [r['t'] for r in groups[(1,'raw')]] == [.1,.2]


def test_live_writer_is_not_encoded_or_given_a_fake_video(tmp_path):
    (tmp_path/'perception_status.json').write_text('{"writer_finished":false}')
    assert not ensure_camera_videos(tmp_path)['streams']
    assert not (tmp_path/'media').exists()


def test_window_selector_uses_application_titles_not_replay_browser():
    text='''0x120 "Gazebo": ("gz" "gz") 1000x800+0+0
0x130 "/workspace/rviz/social_navigation.rviz - RViz": ("rviz2" "rviz2") 1000x800+0+0
0x140 "Phát lại robot – người - Firefox": ("firefox" "Firefox") 1000x800+0+0'''
    assert window_candidates(text)=={'gazebo':'0x120','rviz':'0x130'}
