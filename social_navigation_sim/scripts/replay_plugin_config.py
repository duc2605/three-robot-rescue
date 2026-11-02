"""Attach an evaluation-only recorder, inactive unless its output env is set."""
import xml.etree.ElementTree as ET


def add_replay_plugin(world):
    if any(p.get('name') == 'rescue::ReplayRecorder' for p in world.findall('plugin')):
        return
    ET.SubElement(world, 'plugin', filename='libreplay_recorder.so', name='rescue::ReplayRecorder')
