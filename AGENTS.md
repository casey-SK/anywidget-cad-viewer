# anywidget-cad-viewer Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-11

## Active Technologies
- Python 3.13+ + pytest, pytest-cov, pytest-benchmark (for profiling) (002-test-suite)

- Python 3.13+ (001-marimo-viewer)

## Project Structure

```text
src/
tests/
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
