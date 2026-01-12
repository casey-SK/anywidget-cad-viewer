"""Shared test fixtures for the anywidget-cad-viewer test suite.

This module provides reusable test fixtures for all test categories:
- Shape fixtures: Simple and complex build123d objects
- Invalid input fixtures: Various invalid object types
- Expected output fixtures: Reference data for validation
"""

import pytest

# Shape Fixtures


@pytest.fixture
def simple_box():
    """Create a simple box for testing.

    Returns:
        Box: 10x20x30 box (6 faces, 24 vertices when tessellated)
    """
    from build123d import Box

    return Box(10, 20, 30)


@pytest.fixture
def simple_cylinder():
    """Create a simple cylinder for testing.

    Returns:
        Cylinder: radius=5, height=20 (curved lateral surface + 2 flat ends)
    """
    from build123d import Cylinder

    return Cylinder(radius=5, height=20)


@pytest.fixture
def simple_sphere():
    """Create a simple sphere for testing.

    Returns:
        Sphere: radius=10 (fully curved surface)
    """
    from build123d import Sphere

    return Sphere(radius=10)


@pytest.fixture
def complex_assembly():
    """Create a fused assembly for testing.

    Returns:
        Fused shape: Box + Cylinder + Sphere assembly
    """
    from build123d import Box, Cylinder, Location, Sphere

    base = Box(20, 20, 2)
    column = Cylinder(radius=2, height=15).locate(Location((0, 0, 2)))
    top = Sphere(radius=3).locate(Location((0, 0, 17)))
    return base.fuse(column).fuse(top)


@pytest.fixture
def thin_plate():
    """Create a thin plate for edge case testing.

    Returns:
        Box: 100x100x0.1 (extreme aspect ratio)
    """
    from build123d import Box

    return Box(100, 100, 0.1)


@pytest.fixture
def tiny_shape():
    """Create a very small shape for edge case testing.

    Returns:
        Box: 0.001x0.001x0.001 (very small geometry)
    """
    from build123d import Box

    return Box(0.001, 0.001, 0.001)


@pytest.fixture
def large_shape():
    """Create a large shape for edge case testing.

    Returns:
        Box: 1000x1000x1000 (large geometry)
    """
    from build123d import Box

    return Box(1000, 1000, 1000)


# Invalid Input Fixtures


@pytest.fixture
def invalid_object():
    """Return an object without wrapped attribute.

    Returns:
        dict: Invalid object (not a build123d shape)
    """
    return {"not": "a shape"}


@pytest.fixture
def none_object():
    """Return None for null input testing.

    Returns:
        None: Null input
    """
    return None


@pytest.fixture
def string_object():
    """Return a string for wrong type testing.

    Returns:
        str: Wrong type input
    """
    return "not a shape"


@pytest.fixture
def empty_list():
    """Return an empty list for collection testing.

    Returns:
        list: Empty collection
    """
    return []
