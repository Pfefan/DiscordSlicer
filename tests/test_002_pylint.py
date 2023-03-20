"""
This module contains test if there are no pylint issues, to ensure
a good code structure
"""
import os
import pylint.lint

def test_pylint():
    """class to test pylint"""
    # Set the path to your project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    # Run pylint on all Python files in your project directory
    results = pylint.lint.Run(['--rcfile=pylintrc', project_dir])
    # Check that there are no issues detected
    # pylint: disable=unsubscriptable-object
    assert results.linter.stats['global_note'] == 10.0
