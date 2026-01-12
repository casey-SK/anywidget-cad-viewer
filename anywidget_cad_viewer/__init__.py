"""
anywidget-cad-viewer: CAD viewer widget for marimo and Jupyter notebooks.

This package provides interactive 3D visualization for build123d CAD objects
using anywidget, Three.js, and OpenCascade tessellation.
"""

from .viewer import (
    CADViewer,
    CADViewerError,
    InvalidObjectError,
    OversizedGeometryError,
    TessellationError,
)

__version__ = "0.1.0"

__all__ = [
    "CADViewer",
    "CADViewerError",
    "InvalidObjectError",
    "TessellationError",
    "OversizedGeometryError",
]
