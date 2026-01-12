# Test Suite Contracts

**Feature**: 002-test-suite  
**Date**: 2026-01-12

## Overview

This document defines the test organization contracts - how tests are structured, run, and reported.

## Test Categories

### Markers

| Marker | Description | Run Command |
|--------|-------------|-------------|
| `unit` | Fast, isolated function tests | `pytest -m unit` |
| `integration` | End-to-end pipeline tests | `pytest -m integration` |
| `whitebox` | Internal implementation tests | `pytest -m whitebox` |
| `benchmark` | Performance benchmarks | `pytest -m benchmark` |
| `slow` | Tests taking >5 seconds | `pytest -m "not slow"` to skip |

### Directory Structure

| Directory | Purpose | Typical Runtime |
|-----------|---------|-----------------|
| `tests/unit/` | Individual function/class tests | <10 seconds total |
| `tests/integration/` | Full pipeline tests | <30 seconds total |
| `tests/whitebox/` | Edge cases, internal functions | <10 seconds total |
| `tests/benchmark/` | Performance measurements | Variable |

## Test File Contracts

### Unit Tests

**File**: `tests/unit/test_geometry.py`

| Test Function | Tests | Expected Behavior |
|---------------|-------|-------------------|
| `test_extract_ocp_shape_valid_box` | `extract_ocp_shape()` | Returns TopoDS_Shape from Box |
| `test_extract_ocp_shape_valid_cylinder` | `extract_ocp_shape()` | Returns TopoDS_Shape from Cylinder |
| `test_extract_ocp_shape_invalid` | `extract_ocp_shape()` | Raises InvalidObjectError |
| `test_tessellate_shape_box` | `tessellate_shape()` | Returns dict with vertices, indices, normals |
| `test_tessellate_shape_quality` | `tessellate_shape()` | Higher quality = more vertices |
| `test_serialize_mesh_data` | `serialize_mesh_data()` | Converts to MeshData format |

**File**: `tests/unit/test_viewer.py`

| Test Function | Tests | Expected Behavior |
|---------------|-------|-------------------|
| `test_cadviewer_init_valid` | `CADViewer.__init__` | Creates widget with mesh_data populated |
| `test_cadviewer_init_invalid_object` | `CADViewer.__init__` | Raises InvalidObjectError |
| `test_cadviewer_init_quality_bounds` | `CADViewer.__init__` | Raises ValueError for quality outside 0.01-1.0 |
| `test_cadviewer_default_options` | `CADViewer` | Default values for show_edges, show_axes, etc. |
| `test_cadviewer_custom_options` | `CADViewer` | Custom options properly stored |

### Integration Tests

**File**: `tests/integration/test_pipeline.py`

| Test Function | Tests | Expected Behavior |
|---------------|-------|-------------------|
| `test_box_to_mesh_pipeline` | Full pipeline | Box -> CADViewer produces valid mesh_data |
| `test_cylinder_to_mesh_pipeline` | Full pipeline | Cylinder produces mesh with curved surfaces |
| `test_assembly_to_mesh_pipeline` | Full pipeline | Complex assembly produces combined mesh |
| `test_viewer_traitlets_sync` | Widget model | Traitlets properly synchronized |

**File**: `tests/integration/test_marimo_notebook.py` (existing)

| Test Function | Tests | Expected Behavior |
|---------------|-------|-------------------|
| `test_marimo_notebook_runs_without_error` | Notebook execution | Notebook starts, runs 20s without errors |

### Whitebox Tests

**File**: `tests/whitebox/test_internal.py`

| Test Function | Tests | Expected Behavior |
|---------------|-------|-------------------|
| `test_face_iteration` | Internal tessellation | All faces iterated correctly |
| `test_normal_computation` | BRepGProp_Face usage | Normals computed for each vertex |
| `test_empty_shape_handling` | Edge case | Graceful handling of shapes with no faces |
| `test_degenerate_face` | Edge case | Graceful handling of zero-area faces |

### Import Tests

**File**: `tests/unit/test_imports.py`

| Test Function | Tests | Expected Behavior |
|---------------|-------|-------------------|
| `test_import_package` | `import anywidget_cad_viewer` | No ImportError |
| `test_import_cadviewer` | `from anywidget_cad_viewer import CADViewer` | Class accessible |
| `test_import_exceptions` | Exception classes | All exceptions importable |
| `test_public_api` | `__all__` | All listed exports exist |

### Benchmark Tests

**File**: `tests/benchmark/test_performance.py`

| Test Function | Tests | Expected Behavior |
|---------------|-------|-------------------|
| `test_tessellation_box_timing` | Box tessellation | Reports time, <100ms typical |
| `test_tessellation_complex_timing` | Complex assembly | Reports time, <500ms typical |
| `test_viewer_init_timing` | CADViewer creation | Reports time, <500ms typical |

## Coverage Requirements

| Module | Minimum Coverage |
|--------|------------------|
| `anywidget_cad_viewer/__init__.py` | 100% |
| `anywidget_cad_viewer/viewer.py` | 80% |
| `anywidget_cad_viewer/geometry.py` | 80% |
| **Overall** | 80% |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | Test failures |
| 2 | Test errors (exceptions) |
| 3 | Interrupted |
| 4 | Usage error |
| 5 | No tests collected |
