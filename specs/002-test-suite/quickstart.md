# Test Suite Quickstart

**Feature**: 002-test-suite  
**Date**: 2026-01-12

## Prerequisites

Ensure the package is installed in development mode:

```bash
uv sync --group test
```

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run by Category

```bash
# Unit tests only (fast)
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Whitebox tests only
uv run pytest tests/whitebox/

# Benchmarks only
uv run pytest tests/benchmark/
```

### Run with Markers

```bash
# Only unit tests
uv run pytest -m unit

# Skip slow tests
uv run pytest -m "not slow"

# Only benchmarks
uv run pytest -m benchmark
```

### Run with Coverage

```bash
# Coverage report in terminal
uv run pytest --cov=anywidget_cad_viewer

# Coverage with HTML report
uv run pytest --cov=anywidget_cad_viewer --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run with Verbose Output

```bash
# Verbose mode
uv run pytest -v

# Extra verbose with print output
uv run pytest -vv -s
```

## Common Workflows

### Quick Validation (Before Commit)

```bash
# Fast unit tests + linting
uv run pytest tests/unit/ && uv run ruff check .
```

### Full Test Suite (Before PR)

```bash
# All tests with coverage
uv run pytest --cov=anywidget_cad_viewer --cov-report=term-missing
```

### Debugging Failed Tests

```bash
# Stop on first failure
uv run pytest -x

# Drop into debugger on failure
uv run pytest --pdb

# Run specific test
uv run pytest tests/unit/test_geometry.py::test_extract_ocp_shape_valid_box
```

### Performance Profiling

```bash
# Run benchmarks
uv run pytest tests/benchmark/ -v

# Run benchmarks only (skip other tests)
uv run pytest tests/benchmark/ --benchmark-only

# Compare against baseline
uv run pytest tests/benchmark/ --benchmark-compare
```

## Baseline Performance Metrics

Performance benchmarks measured on Linux (Python 3.13.11):

| Operation | Mean Time | Description |
|-----------|-----------|-------------|
| **Extract OCP Shape** | 0.001 ms | Extract TopoDS shape from build123d object |
| **Serialize Mesh** | 0.002 ms | Convert tessellation to MeshData format |
| **Tessellate Box (quality=0.1)** | 3.4 ms | Tessellate simple 10x10x10 box |
| **Tessellate Box (quality=0.01)** | 3.5 ms | High-quality tessellation |
| **Tessellate Box (quality=1.0)** | 3.7 ms | Low-quality tessellation |
| **Tessellate Cylinder** | 13.4 ms | Tessellate curved surface (r=5, h=10) |
| **Tessellate Sphere** | 161.9 ms | Tessellate doubly-curved surface (r=10) |
| **Tessellate Complex Assembly** | 92.4 ms | Tessellate fused multi-box assembly |
| **Large Assembly (5 boxes)** | 18.3 ms | Process 5 separate boxes |
| **CADViewer Init (Box)** | 5.6 ms | Complete viewer initialization |
| **CADViewer Init (Cylinder)** | 17.7 ms | Viewer with curved surface |
| **End-to-End Workflow** | 200.8 ms | Create 3 shapes + viewers |

**Notes:**
- Box tessellation quality setting (0.01-1.0) has minimal impact on performance for simple shapes
- Sphere tessellation is significantly slower due to doubly-curved surface
- Cylinder tessellation is ~4x slower than box due to curved surface
- Most operations complete in <20ms, making them suitable for interactive use
- End-to-end workflow (3 shapes) completes in ~200ms

**Performance Variance:**
- Typical standard deviation: <10% for most operations
- Operations run with 5+ iterations for statistical significance
- Benchmarks use pytest-benchmark with calibrated warmup rounds

## Configuration

All pytest configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Fast isolated tests",
    "integration: End-to-end pipeline tests",
    "whitebox: Internal implementation tests",
    "benchmark: Performance benchmarks (slow)",
]

[tool.coverage.run]
source = ["anywidget_cad_viewer"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Troubleshooting

### Tests Not Found

Ensure you're running from the repository root:
```bash
cd /path/to/anywidget-cad-viewer
uv run pytest
```

### Import Errors

Sync dependencies:
```bash
uv sync --group test
```

### Marimo Test Hanging

The marimo notebook test has a 20-second timeout. If it hangs, check:
- Port 2718 is available
- No existing marimo processes running

### Coverage Below 80%

Run with `--cov-report=term-missing` to see uncovered lines:
```bash
uv run pytest --cov=anywidget_cad_viewer --cov-report=term-missing
```
