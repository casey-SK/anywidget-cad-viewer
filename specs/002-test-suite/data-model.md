# Data Model: Test Fixtures

**Feature**: 002-test-suite  
**Date**: 2026-01-12

## Overview

This document defines the test fixtures (reusable test data) for the test suite. Fixtures provide consistent, well-defined inputs for testing the tessellation pipeline and CADViewer widget.

## Test Fixtures

### Shape Fixtures

| Fixture Name | Shape Type | Properties | Purpose |
|--------------|------------|------------|---------|
| `simple_box` | Box | 10x20x30 | Basic rectangular solid, 6 faces |
| `simple_cylinder` | Cylinder | r=5, h=20 | Curved lateral surface + 2 flat ends |
| `simple_sphere` | Sphere | r=10 | Fully curved surface, tests tessellation quality |
| `complex_assembly` | Fused | Box + Cylinder + Sphere | Tests assembly handling, multiple primitives |
| `thin_plate` | Box | 100x100x0.1 | Extreme aspect ratio edge case |
| `tiny_shape` | Box | 0.001x0.001x0.001 | Very small geometry edge case |
| `large_shape` | Box | 1000x1000x1000 | Large geometry edge case |

### Invalid Input Fixtures

| Fixture Name | Type | Purpose |
|--------------|------|---------|
| `invalid_object` | dict | Object without `wrapped` attribute |
| `none_object` | None | Null input handling |
| `string_object` | str | Wrong type handling |
| `empty_list` | list | Empty collection handling |

### Expected Output Fixtures

| Fixture Name | Format | Purpose |
|--------------|--------|---------|
| `box_mesh_data` | MeshData dict | Expected tessellation output for simple_box |
| `expected_vertex_count` | dict[str, int] | Vertex counts for each shape at quality=0.1 |

## Fixture Implementation

### conftest.py Structure

```python
@pytest.fixture
def simple_box():
    """Create a simple box for testing."""
    from build123d import Box
    return Box(10, 20, 30)

@pytest.fixture
def simple_cylinder():
    """Create a simple cylinder for testing."""
    from build123d import Cylinder
    return Cylinder(radius=5, height=20)

@pytest.fixture
def simple_sphere():
    """Create a simple sphere for testing."""
    from build123d import Sphere
    return Sphere(radius=10)

@pytest.fixture
def complex_assembly():
    """Create a fused assembly for testing."""
    from build123d import Box, Cylinder, Sphere, Location
    base = Box(20, 20, 2)
    column = Cylinder(radius=2, height=15).locate(Location((0, 0, 2)))
    top = Sphere(radius=3).locate(Location((0, 0, 17)))
    return base.fuse(column).fuse(top)

@pytest.fixture
def invalid_object():
    """Return an object without wrapped attribute."""
    return {"not": "a shape"}
```

## Validation Rules

### Mesh Data Validation

A valid MeshData dict must contain:
- `vertices`: list[float] with length divisible by 3
- `indices`: list[int] with length divisible by 3
- `normals`: list[float] with same length as vertices
- `colors`: list[float] (optional)

### Vertex Count Bounds

For quality=0.1 (default):
- Box: 24 vertices (4 per face x 6 faces)
- Cylinder: 100-500 vertices (depends on tessellation)
- Sphere: 500-2000 vertices (depends on tessellation)
- Complex assembly: Sum of components + shared vertices

## State Transitions

N/A - Test fixtures are stateless factory functions.
