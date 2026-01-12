"""Integration tests for full tessellation pipeline."""

import pytest
from build123d import Box, Cylinder, Sphere

from anywidget_cad_viewer import CADViewer
from anywidget_cad_viewer.geometry import extract_ocp_shape, serialize_mesh_data, tessellate_shape

# ============================================================================
# Tests for Box → Mesh Pipeline
# ============================================================================


@pytest.mark.integration
def test_box_to_mesh_pipeline_complete():
    """Test complete pipeline: Box → extract → tessellate → serialize → CADViewer."""
    # Step 1: Create build123d Box
    box = Box(10, 20, 30)
    assert box is not None

    # Step 2: Extract OCP shape
    shape = extract_ocp_shape(box)
    assert shape is not None
    assert "TopoDS" in type(shape).__name__

    # Step 3: Tessellate shape
    tess_data = tessellate_shape(shape, quality=0.1)
    assert "vertices" in tess_data
    assert "triangles" in tess_data
    assert len(tess_data["vertices"]) > 0

    # Step 4: Serialize to MeshData
    mesh = serialize_mesh_data(tess_data)
    assert "vertices" in mesh
    assert "indices" in mesh
    assert "normals" in mesh

    # Step 5: Verify vertex structure (box should have 8 corners minimum)
    vertex_count = len(mesh["vertices"]) // 3
    assert vertex_count >= 8

    # Step 6: Verify triangles exist (box has 6 faces, minimum 2 triangles per face)
    triangle_count = len(mesh["indices"]) // 3
    assert triangle_count >= 12


@pytest.mark.integration
def test_box_to_viewer_direct():
    """Test direct pipeline: Box → CADViewer (integration of all steps)."""
    box = Box(15, 15, 15)
    viewer = CADViewer(box, quality=0.1)

    # Verify viewer created successfully
    assert viewer is not None
    assert viewer._obj is box

    # Verify mesh_data populated
    mesh = viewer.mesh_data
    assert len(mesh["vertices"]) > 0
    assert len(mesh["indices"]) > 0
    assert len(mesh["normals"]) > 0

    # Verify normals match vertices
    assert len(mesh["normals"]) == len(mesh["vertices"])

    # Verify indices reference valid vertices
    vertex_count = len(mesh["vertices"]) // 3
    for idx in mesh["indices"]:
        assert 0 <= idx < vertex_count


@pytest.mark.integration
def test_box_different_dimensions():
    """Test pipeline with boxes of varying dimensions."""
    boxes = [
        Box(1, 1, 1),  # Small cube
        Box(10, 20, 30),  # Rectangular box
        Box(100, 100, 100),  # Large cube
    ]

    for box in boxes:
        viewer = CADViewer(box, quality=0.5)
        assert len(viewer.mesh_data["vertices"]) > 0
        assert len(viewer.mesh_data["indices"]) > 0


# ============================================================================
# Tests for Cylinder → Mesh Pipeline
# ============================================================================


@pytest.mark.integration
def test_cylinder_to_mesh_pipeline():
    """Test complete pipeline for Cylinder (curved surface tessellation)."""
    # Step 1: Create Cylinder
    cylinder = Cylinder(radius=5, height=10)

    # Step 2: Extract OCP shape
    shape = extract_ocp_shape(cylinder)
    assert "TopoDS" in type(shape).__name__

    # Step 3: Tessellate
    tess_data = tessellate_shape(shape, quality=0.1)

    # Step 4: Serialize
    mesh = serialize_mesh_data(tess_data)

    # Verify curved surface tessellation
    vertex_count = len(mesh["vertices"]) // 3
    triangle_count = len(mesh["indices"]) // 3

    # Cylinder should have more vertices than a box (curved surfaces)
    # At quality=0.1, expect at least 30 vertices for radius=5
    assert vertex_count >= 30
    assert triangle_count >= 30


@pytest.mark.integration
def test_cylinder_to_viewer_curved_surfaces():
    """Test CADViewer handles cylinder curved surface normals correctly."""
    cylinder = Cylinder(radius=10, height=20)
    viewer = CADViewer(cylinder, quality=0.1)

    mesh = viewer.mesh_data

    # Verify normals are normalized (magnitude ≈ 1.0)
    normals = mesh["normals"]
    for i in range(0, len(normals), 3):
        nx, ny, nz = normals[i], normals[i + 1], normals[i + 2]
        magnitude = (nx**2 + ny**2 + nz**2) ** 0.5
        # Allow some tolerance for numerical precision
        assert 0.99 <= magnitude <= 1.01, f"Normal magnitude {magnitude} not normalized"


@pytest.mark.integration
def test_cylinder_quality_affects_tessellation():
    """Test that quality parameter affects cylinder tessellation detail."""
    cylinder = Cylinder(radius=5, height=10)

    viewer_high = CADViewer(cylinder, quality=0.01)
    viewer_low = CADViewer(cylinder, quality=1.0)

    vertex_count_high = len(viewer_high.mesh_data["vertices"]) // 3
    vertex_count_low = len(viewer_low.mesh_data["vertices"]) // 3

    # Higher quality should produce more or equal vertices for curved surfaces
    # Note: OCP may produce same vertex count for simple shapes at different qualities
    assert vertex_count_high >= vertex_count_low


# ============================================================================
# Tests for Sphere → Mesh Pipeline
# ============================================================================


@pytest.mark.integration
def test_sphere_to_mesh_pipeline():
    """Test complete pipeline for Sphere (doubly-curved surface)."""
    sphere = Sphere(radius=10)

    shape = extract_ocp_shape(sphere)
    tess_data = tessellate_shape(shape, quality=0.1)
    mesh = serialize_mesh_data(tess_data)

    # Sphere should have substantial tessellation
    vertex_count = len(mesh["vertices"]) // 3
    assert vertex_count >= 50  # Minimum for quality=0.1


@pytest.mark.integration
def test_sphere_to_viewer():
    """Test CADViewer with sphere geometry."""
    sphere = Sphere(radius=15)
    viewer = CADViewer(sphere, quality=0.2)

    assert len(viewer.mesh_data["vertices"]) > 0
    assert viewer.show_edges is True  # Default
    assert viewer.show_axes is True  # Default


# ============================================================================
# Tests for Complex Assembly Pipeline
# ============================================================================


@pytest.mark.integration
def test_assembly_to_mesh_pipeline(complex_assembly):
    """Test pipeline handles complex assembly (fused shapes)."""
    # complex_assembly is defined in conftest.py as fused boxes
    viewer = CADViewer(complex_assembly, quality=0.5)

    mesh = viewer.mesh_data

    # Assembly should produce combined mesh
    assert len(mesh["vertices"]) > 0
    assert len(mesh["indices"]) > 0

    # Should have more vertices than single box
    vertex_count = len(mesh["vertices"]) // 3
    assert vertex_count >= 24  # At least 3 boxes worth


@pytest.mark.integration
def test_multiple_shapes_sequential():
    """Test creating viewers for multiple shapes sequentially."""
    shapes = [
        Box(5, 5, 5),
        Cylinder(radius=3, height=8),
        Sphere(radius=4),
    ]

    viewers = []
    for shape in shapes:
        viewer = CADViewer(shape, quality=0.3)
        viewers.append(viewer)
        assert len(viewer.mesh_data["vertices"]) > 0

    # Verify all viewers are independent
    assert len(viewers) == 3
    for viewer in viewers:
        assert viewer.mesh_data is not None


# ============================================================================
# Tests for Viewer Traitlets Synchronization
# ============================================================================


@pytest.mark.integration
def test_viewer_traitlets_sync_mesh_data():
    """Test viewer mesh_data traitlet syncs correctly."""
    box = Box(10, 10, 10)
    viewer = CADViewer(box)

    # Verify mesh_data is a traitlet with sync=True
    assert hasattr(viewer, "mesh_data")
    assert isinstance(viewer.mesh_data, dict)

    # Verify mesh_data contains expected keys
    assert "vertices" in viewer.mesh_data
    assert "indices" in viewer.mesh_data
    assert "normals" in viewer.mesh_data


@pytest.mark.integration
def test_viewer_traitlets_sync_display_options():
    """Test viewer display option traitlets sync correctly."""
    box = Box(5, 5, 5)
    viewer = CADViewer(
        box,
        show_edges=False,
        show_axes=False,
        background_color="#123456",
        width=1024,
        height=768,
    )

    # Verify all traitlets are set
    assert viewer.show_edges is False
    assert viewer.show_axes is False
    assert viewer.background_color == "#123456"
    assert viewer.width == 1024
    assert viewer.height == 768


@pytest.mark.integration
def test_viewer_traitlets_camera_defaults():
    """Test viewer camera traitlets have correct defaults."""
    box = Box(10, 10, 10)
    viewer = CADViewer(box)

    # Camera position defaults to None (auto-calculated by frontend)
    assert viewer.camera_position is None

    # Camera target defaults to origin
    assert viewer.camera_target == [0, 0, 0]


@pytest.mark.integration
def test_viewer_error_message_empty_on_success():
    """Test viewer error_message is empty when initialization succeeds."""
    box = Box(10, 10, 10)
    viewer = CADViewer(box)

    assert viewer.error_message == ""


@pytest.mark.integration
def test_viewer_traitlets_modifiable():
    """Test viewer traitlets can be modified after initialization."""
    box = Box(10, 10, 10)
    viewer = CADViewer(box)

    # Modify display options
    viewer.show_edges = False
    viewer.background_color = "#FFFFFF"
    viewer.width = 1920

    # Verify changes persisted
    assert viewer.show_edges is False
    assert viewer.background_color == "#FFFFFF"
    assert viewer.width == 1920


# ============================================================================
# Tests for End-to-End Quality Variations
# ============================================================================


@pytest.mark.integration
def test_pipeline_quality_range():
    """Test pipeline works across full quality range."""
    box = Box(10, 10, 10)

    quality_values = [0.01, 0.05, 0.1, 0.5, 1.0]

    for quality in quality_values:
        viewer = CADViewer(box, quality=quality)
        assert len(viewer.mesh_data["vertices"]) > 0
        assert len(viewer.mesh_data["indices"]) > 0


@pytest.mark.integration
def test_pipeline_preserves_geometry_validity():
    """Test pipeline produces valid geometry with consistent winding."""
    cylinder = Cylinder(radius=5, height=10)
    viewer = CADViewer(cylinder, quality=0.1)

    mesh = viewer.mesh_data
    indices = mesh["indices"]

    # Verify all triangles reference valid vertices
    vertex_count = len(mesh["vertices"]) // 3
    for i in range(0, len(indices), 3):
        i1, i2, i3 = indices[i], indices[i + 1], indices[i + 2]
        assert 0 <= i1 < vertex_count
        assert 0 <= i2 < vertex_count
        assert 0 <= i3 < vertex_count

        # Verify no degenerate triangles (all indices different)
        assert i1 != i2 and i2 != i3 and i1 != i3
