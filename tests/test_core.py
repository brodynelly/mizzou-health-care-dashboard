import sys
import os
import pathlib

def test_python_version():
    """Python 3.8+ required."""
    assert sys.version_info >= (3, 8), "Python 3.8+ is required"

def test_readme_exists():
    """README should be present."""
    root = pathlib.Path(__file__).parent.parent
    readme = root / "README.md"
    assert readme.exists(), "README.md not found"

def test_project_structure():
    """Project root should contain expected files."""
    root = pathlib.Path(__file__).parent.parent
    files = list(root.iterdir())
    assert len(files) > 0, "Project directory is empty"
