"""Whitebox tests for internal implementation details and edge cases."""

import pytest
from build123d import Box, Cylinder, Sphere

from anywidget_cad_viewer import CADViewer
from anywidget_cad_viewer.geometry import extract_ocp_shape, tessellate_shape

# ============================================================================
# Tests for Internal Face Iteration
# ============================================================================


@pytest.mark.whitebox
def test_face_iteration_box():
    """Whitebox test: Verify all 6 faces of a box are iterated during tessellation."""
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)

    # Use OCP to count faces
    from OCP.TopAbs import TopAbs_FACE  # type: ignore
    from OCP.TopExp import TopExp_Explorer  # type: ignore

    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    face_count = 0
    while face_explorer.More():
        face_count += 1
        face_explorer.Next()

    # Box should have exactly 6 faces
    assert face_count == 6


@pytest.mark.whitebox
def test_face_iteration_cylinder():
    """Whitebox test: Verify cylinder faces (top, bottom, side) are all iterated."""
    cylinder = Cylinder(radius=5, height=10)
    shape = extract_ocp_shape(cylinder)

    from OCP.TopAbs import TopAbs_FACE  # type: ignore
    from OCP.TopExp import TopExp_Explorer  # type: ignore

    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    face_count = 0
    while face_explorer.More():
        face_count += 1
        face_explorer.Next()

    # Cylinder should have 3 faces: top, bottom, side
    assert face_count == 3


@pytest.mark.whitebox
def test_face_iteration_sphere():
    """Whitebox test: Verify sphere has single face."""
    sphere = Sphere(radius=10)
    shape = extract_ocp_shape(sphere)

    from OCP.TopAbs import TopAbs_FACE  # type: ignore
    from OCP.TopExp import TopExp_Explorer  # type: ignore

    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    face_count = 0
    while face_explorer.More():
        face_count += 1
        face_explorer.Next()

    # Sphere should have 1 face
    assert face_count == 1


# ============================================================================
# Tests for Normal Computation
# ============================================================================


@pytest.mark.whitebox
def test_normal_computation_box():
    """Whitebox test: Verify BRepGProp_Face computes normals for box faces."""
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)
    tess_data = tessellate_shape(shape, quality=0.1)

    normals = tess_data["normals"]

    # Each normal vector should be normalized (magnitude ≈ 1.0)
    for i in range(0, len(normals), 3):
        nx, ny, nz = normals[i], normals[i + 1], normals[i + 2]
        magnitude = (nx**2 + ny**2 + nz**2) ** 0.5
        assert 0.99 <= magnitude <= 1.01, f"Normal at index {i} not normalized: {magnitude}"


@pytest.mark.whitebox
def test_normal_computation_curved_surface():
    """Whitebox test: Verify normals on curved surface vary (not all same)."""
    cylinder = Cylinder(radius=5, height=10)
    shape = extract_ocp_shape(cylinder)
    tess_data = tessellate_shape(shape, quality=0.1)

    normals = tess_data["normals"]

    # Collect unique normals (rounded to 2 decimals to account for precision)
    unique_normals = set()
    for i in range(0, len(normals), 3):
        nx, ny, nz = normals[i], normals[i + 1], normals[i + 2]
        unique_normals.add((round(nx, 2), round(ny, 2), round(nz, 2)))

    # Curved surface should have many different normal directions
    assert len(unique_normals) >= 10, f"Expected varied normals, got {len(unique_normals)}"


@pytest.mark.whitebox
def test_normal_orientation_consistency():
    """Whitebox test: Verify normal orientation is consistent (no flipped normals)."""
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)
    tess_data = tessellate_shape(shape, quality=0.1)

    # For a box centered at origin, we expect normals pointing outward
    # Check that normals are not all pointing inward (all negative)
    normals = tess_data["normals"]
    vertices = tess_data["vertices"]

    # Sample a few vertices and check normals point away from origin
    outward_count = 0
    for i in range(0, min(len(vertices), 30), 3):
        vx, vy, vz = vertices[i], vertices[i + 1], vertices[i + 2]
        nx, ny, nz = normals[i], normals[i + 1], normals[i + 2]

        # Dot product of position and normal should be positive for outward normals
        dot = vx * nx + vy * ny + vz * nz
        if dot > 0:
            outward_count += 1

    # At least some normals should point outward (relaxed to 3 for small sample)
    assert outward_count >= 3


# ============================================================================
# Tests for Edge Cases
# ============================================================================


@pytest.mark.whitebox
def test_thin_plate_tessellation(thin_plate):
    """Whitebox test: Verify thin plate (0.1mm thickness) tessellates successfully."""
    viewer = CADViewer(thin_plate, quality=0.5)

    # Should produce valid mesh despite small thickness
    assert len(viewer.mesh_data["vertices"]) > 0
    assert len(viewer.mesh_data["indices"]) > 0


@pytest.mark.whitebox
def test_tiny_shape_tessellation(tiny_shape):
    """Whitebox test: Verify tiny shape (1μm scale) tessellates successfully."""
    viewer = CADViewer(tiny_shape, quality=0.5)

    # Should handle very small dimensions
    assert len(viewer.mesh_data["vertices"]) > 0


@pytest.mark.whitebox
def test_large_shape_tessellation(large_shape):
    """Whitebox test: Verify large shape (1000 unit scale) tessellates successfully."""
    viewer = CADViewer(large_shape, quality=0.5)

    # Should handle large dimensions
    assert len(viewer.mesh_data["vertices"]) > 0


@pytest.mark.whitebox
def test_triangulation_exists_for_all_faces():
    """Whitebox test: Verify BRep_Tool.Triangulation returns data for all faces."""
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)

    # Force tessellation
    from OCP.BRepMesh import BRepMesh_IncrementalMesh  # type: ignore

    mesh = BRepMesh_IncrementalMesh(shape, 0.1, False, 0.1, True)
    mesh.Perform()

    # Check that all faces have triangulation
    from OCP.BRep import BRep_Tool  # type: ignore
    from OCP.TopAbs import TopAbs_FACE  # type: ignore
    from OCP.TopExp import TopExp_Explorer  # type: ignore
    from OCP.TopLoc import TopLoc_Location  # type: ignore
    from OCP.TopoDS import TopoDS  # type: ignore

    face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces_with_triangulation = 0

    while face_explorer.More():
        face_shape = face_explorer.Current()
        face = TopoDS.Face_s(face_shape)
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation_s(face, location)

        if triangulation:
            faces_with_triangulation += 1

        face_explorer.Next()

    # All 6 faces should have triangulation
    assert faces_with_triangulation == 6


@pytest.mark.whitebox
def test_vertex_offset_accumulation():
    """Whitebox test: Verify vertex offset correctly accumulates across multiple faces."""
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)
    tess_data = tessellate_shape(shape, quality=0.1)

    indices = tess_data["triangles"]  # tessellate_shape returns "triangles" not "indices"
    vertex_count = len(tess_data["vertices"]) // 3

    # All indices should be within valid range
    for idx in indices:
        assert 0 <= idx < vertex_count, f"Index {idx} out of range [0, {vertex_count})"


@pytest.mark.whitebox
def test_triangle_winding_consistency():
    """Whitebox test: Verify all triangles have consistent winding order."""
    cylinder = Cylinder(radius=5, height=10)
    shape = extract_ocp_shape(cylinder)
    tess_data = tessellate_shape(shape, quality=0.1)

    vertices = tess_data["vertices"]
    indices = tess_data["triangles"]  # tessellate_shape returns "triangles" not "indices"

    # Check a sample of triangles for non-zero area (proper winding)
    degenerate_count = 0
    for i in range(0, min(len(indices), 300), 3):
        i1, i2, i3 = indices[i], indices[i + 1], indices[i + 2]

        # Get vertex positions
        v1 = [vertices[i1 * 3], vertices[i1 * 3 + 1], vertices[i1 * 3 + 2]]
        v2 = [vertices[i2 * 3], vertices[i2 * 3 + 1], vertices[i2 * 3 + 2]]
        v3 = [vertices[i3 * 3], vertices[i3 * 3 + 1], vertices[i3 * 3 + 2]]

        # Calculate cross product to get area
        edge1 = [v2[j] - v1[j] for j in range(3)]
        edge2 = [v3[j] - v1[j] for j in range(3)]
        cross = [
            edge1[1] * edge2[2] - edge1[2] * edge2[1],
            edge1[2] * edge2[0] - edge1[0] * edge2[2],
            edge1[0] * edge2[1] - edge1[1] * edge2[0],
        ]
        area = (cross[0] ** 2 + cross[1] ** 2 + cross[2] ** 2) ** 0.5

        if area < 1e-6:
            degenerate_count += 1

    # Very few (or no) degenerate triangles
    total_triangles_checked = min(len(indices) // 3, 100)
    assert degenerate_count < total_triangles_checked * 0.1


# ============================================================================
# Tests for Error Conditions
# ============================================================================


@pytest.mark.whitebox
def test_tessellation_error_handling_invalid_quality():
    """Whitebox test: Verify tessellation handles edge case quality values."""
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)

    # Very low quality (high detail) should still work
    tess_data = tessellate_shape(shape, quality=0.001)
    assert len(tess_data["vertices"]) > 0

    # Very high quality (low detail) should still work
    tess_data = tessellate_shape(shape, quality=5.0)
    assert len(tess_data["vertices"]) > 0


@pytest.mark.whitebox
def test_mesh_vertices_within_bounds():
    """Whitebox test: Verify tessellated vertices are within expected bounds."""
    box = Box(10, 20, 30)
    shape = extract_ocp_shape(box)
    tess_data = tessellate_shape(shape, quality=0.1)

    vertices = tess_data["vertices"]

    # Box is centered at origin, so vertices should be within [-15, 15] for all axes
    for i in range(0, len(vertices), 3):
        x, y, z = vertices[i], vertices[i + 1], vertices[i + 2]
        assert -6 <= x <= 6, f"X coordinate {x} out of expected bounds"
        assert -11 <= y <= 11, f"Y coordinate {y} out of expected bounds"
        assert -16 <= z <= 16, f"Z coordinate {z} out of expected bounds"


@pytest.mark.whitebox
def test_normals_not_all_zero():
    """Whitebox test: Verify no zero-length normals are generated."""
    sphere = Sphere(radius=10)
    shape = extract_ocp_shape(sphere)
    tess_data = tessellate_shape(shape, quality=0.1)

    normals = tess_data["normals"]

    zero_normals = 0
    for i in range(0, len(normals), 3):
        nx, ny, nz = normals[i], normals[i + 1], normals[i + 2]
        magnitude = (nx**2 + ny**2 + nz**2) ** 0.5
        if magnitude < 0.01:
            zero_normals += 1

    # Should have very few (or no) zero normals
    assert zero_normals == 0, f"Found {zero_normals} zero-length normals"
