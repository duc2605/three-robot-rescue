"""Three-stage comparison wrapper; see README_PAPERS_03_12.md."""
import os
from launch.launch_description_sources.python_launch_file_utilities import load_python_launch_file_as_module


def generate_launch_description():
    helper = load_python_launch_file_as_module(
        os.path.join(os.path.dirname(__file__), '_comparison_backend.py'))
    return helper.comparison_launch(3)
