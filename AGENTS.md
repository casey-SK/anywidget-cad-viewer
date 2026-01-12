# anywidget-cad-viewer Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-12

## Active Technologies
- Python 3.13+ + pytest, pytest-cov, pytest-benchmark (for profiling) (002-test-suite)
- Python 3.13+ (001-marimo-viewer)

## Dependencies

### Python Dependencies
- **anywidget**: Widget framework for marimo/Jupyter integration
- **build123d**: CAD modeling library (user dependency, peer)
- **ocp-vscode**: OCP geometry handling and tessellation

### JavaScript Dependencies (bundled)
- **three**: Three.js for 3D rendering
- **OrbitControls**: Camera controls from Three.js examples

## Project Structure

```text
anywidget_cad_viewer/    # Main package
├── __init__.py          # Package exports
├── viewer.py            # CADViewer widget class
├── geometry.py          # Geometry conversion utilities
├── static/              # Frontend assets
│   ├── index.js         # Three.js rendering code
│   └── index.css        # Widget styles
└── py.typed             # Type hints marker

tests/                   # Test suite
├── unit/                # Unit tests
├── integration/         # Integration tests
├── benchmark/           # Performance tests
└── whitebox/            # Internal implementation tests

examples/                # Example notebooks
└── marimo_quickstart.py # Comprehensive examples
```

## Commands

```bash
# Run all tests
pytest

# Run unit tests only (fast)
pytest tests/unit/

# Run with coverage report
pytest --cov=anywidget_cad_viewer --cov-report=term

# Run benchmarks
pytest tests/benchmark/ --benchmark-only

# Quick validation (before commit)
pytest tests/unit/ && ruff check .

# Linting
ruff check .
```

## Code Style

Python 3.13+: Follow standard conventions

## Recent Changes
- 002-test-suite: Added Python 3.13+ + pytest, pytest-cov, pytest-benchmark (for profiling)

- 001-marimo-viewer: Added Python 3.13+

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
