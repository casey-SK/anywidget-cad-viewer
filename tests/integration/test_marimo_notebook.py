"""Integration test for marimo notebook execution.

This test runs the marimo quickstart notebook in headless mode to verify
that the notebook starts successfully and all cells execute without errors.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Path to the examples directory (relative to repo root)
REPO_ROOT = Path(__file__).parent.parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"

# Error patterns that indicate notebook execution failures
ERROR_PATTERNS = [
    "Traceback",
    "Error",
    "Exception",
    "ImportError",
    "ModuleNotFoundError",
    "SyntaxError",
    "NameError",
    "TypeError",
    "ValueError",
    "AttributeError",
]


@pytest.fixture
def marimo_quickstart_path() -> Path:
    """Return the path to the marimo quickstart notebook."""
    notebook_path = EXAMPLES_DIR / "marimo_quickstart.py"
    if not notebook_path.exists():
        pytest.skip(f"Notebook not found: {notebook_path}")
    return notebook_path


def test_marimo_notebook_runs_without_error(marimo_quickstart_path: Path) -> None:
    """Test that the marimo quickstart notebook starts successfully.

    This runs the notebook in headless mode using `marimo run`. The server
    will start and execute all cells. We monitor output for 20 seconds,
    checking for any error messages. A clean run with no errors indicates success.
    """
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "marimo",
            "run",
            "--headless",
            str(marimo_quickstart_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=REPO_ROOT,
    )

    try:
        # Wait for process to run, capturing output
        stdout, stderr = process.communicate(timeout=20)

        # Process exited before timeout - check for errors
        if process.returncode != 0:
            pytest.fail(
                f"Marimo notebook failed with exit code {process.returncode}\n"
                f"STDOUT: {stdout}\n"
                f"STDERR: {stderr}"
            )
    except subprocess.TimeoutExpired:
        # Timeout reached - read whatever output is available
        process.kill()
        stdout, stderr = process.communicate()

    # Check output for error patterns
    combined_output = f"{stdout}\n{stderr}"
    for pattern in ERROR_PATTERNS:
        if pattern in combined_output:
            pytest.fail(
                f"Found error pattern '{pattern}' in notebook output:\n"
                f"STDOUT: {stdout}\n"
                f"STDERR: {stderr}"
            )
