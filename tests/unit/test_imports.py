"""Import tests for anywidget-cad-viewer package.

Tests that verify the package can be imported correctly and all public
APIs are accessible. These tests catch packaging issues and missing
dependencies early.
"""

import pytest


def test_import_package():
    """Test that the main package can be imported without errors."""
    try:
        import anywidget_cad_viewer

        assert anywidget_cad_viewer is not None
    except ImportError as e:
        pytest.fail(f"Failed to import anywidget_cad_viewer: {e}")


def test_import_cadviewer():
    """Test that CADViewer class is accessible from package."""
    try:
        from anywidget_cad_viewer import CADViewer

        assert CADViewer is not None
        assert callable(CADViewer)
    except ImportError as e:
        pytest.fail(f"Failed to import CADViewer: {e}")


def test_import_exceptions():
    """Test that all exception classes are importable."""
    try:
        from anywidget_cad_viewer import (
            InvalidObjectError,
            OversizedGeometryError,
            TessellationError,
        )

        assert InvalidObjectError is not None
        assert TessellationError is not None
        assert OversizedGeometryError is not None

        # Verify they are actually exception classes
        assert issubclass(InvalidObjectError, Exception)
        assert issubclass(TessellationError, Exception)
        assert issubclass(OversizedGeometryError, Exception)
    except ImportError as e:
        pytest.fail(f"Failed to import exception classes: {e}")


def test_public_api():
    """Test that all listed exports in __all__ exist and are accessible."""
    import anywidget_cad_viewer

    # Check if __all__ is defined
    if not hasattr(anywidget_cad_viewer, "__all__"):
        pytest.skip("Package does not define __all__")

    # Verify all listed exports exist
    for name in anywidget_cad_viewer.__all__:
        assert hasattr(anywidget_cad_viewer, name), (
            f"Public API member '{name}' not found in package"
        )
