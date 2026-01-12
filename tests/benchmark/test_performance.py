"""Performance benchmark tests for tessellation and viewer initialization."""

import pytest
from build123d import Box, Cylinder, Sphere

from anywidget_cad_viewer import CADViewer
from anywidget_cad_viewer.geometry import extract_ocp_shape, serialize_mesh_data, tessellate_shape

# ============================================================================
# Benchmark: Box Tessellation
# ============================================================================


@pytest.mark.benchmark
def test_tessellation_box_timing(benchmark):
    """Benchmark tessellation performance for a simple Box."""

    def tessellate_box():
        box = Box(10, 10, 10)
        shape = extract_ocp_shape(box)
        tess_data = tessellate_shape(shape, quality=0.1)
        mesh = serialize_mesh_data(tess_data)
        return mesh

    result = benchmark(tessellate_box)

    # Verify result is valid
    assert len(result["vertices"]) > 0
    assert len(result["indices"]) > 0


@pytest.mark.benchmark
def test_tessellation_box_high_quality(benchmark):
    """Benchmark tessellation with high quality (0.01) setting."""

    def tessellate_box_hq():
        box = Box(10, 10, 10)
        shape = extract_ocp_shape(box)
        tess_data = tessellate_shape(shape, quality=0.01)
        mesh = serialize_mesh_data(tess_data)
        return mesh

    result = benchmark(tessellate_box_hq)

    # High quality should produce valid mesh (at least 8 vertices for box corners)
    assert len(result["vertices"]) >= 72


@pytest.mark.benchmark
def test_tessellation_box_low_quality(benchmark):
    """Benchmark tessellation with low quality (1.0) setting."""

    def tessellate_box_lq():
        box = Box(10, 10, 10)
        shape = extract_ocp_shape(box)
        tess_data = tessellate_shape(shape, quality=1.0)
        mesh = serialize_mesh_data(tess_data)
        return mesh

    result = benchmark(tessellate_box_lq)

    assert len(result["vertices"]) > 0


# ============================================================================
# Benchmark: Cylinder Tessellation (Curved Surfaces)
# ============================================================================


@pytest.mark.benchmark
def test_tessellation_cylinder_timing(benchmark):
    """Benchmark tessellation for curved surface (Cylinder)."""

    def tessellate_cylinder():
        cylinder = Cylinder(radius=5, height=10)
        shape = extract_ocp_shape(cylinder)
        tess_data = tessellate_shape(shape, quality=0.1)
        mesh = serialize_mesh_data(tess_data)
        return mesh

    result = benchmark(tessellate_cylinder)

    # Cylinder should have more vertices than simple box due to curved surface
    assert len(result["vertices"]) >= 90


@pytest.mark.benchmark
def test_tessellation_sphere_timing(benchmark):
    """Benchmark tessellation for doubly-curved surface (Sphere)."""

    def tessellate_sphere():
        sphere = Sphere(radius=10)
        shape = extract_ocp_shape(sphere)
        tess_data = tessellate_shape(shape, quality=0.1)
        mesh = serialize_mesh_data(tess_data)
        return mesh

    result = benchmark(tessellate_sphere)

    # Sphere should have substantial tessellation
    assert len(result["vertices"]) >= 150


# ============================================================================
# Benchmark: Complex Assembly Tessellation
# ============================================================================


@pytest.mark.benchmark
def test_tessellation_complex_timing(benchmark, complex_assembly):
    """Benchmark tessellation for complex assembly (multiple fused shapes)."""

    def tessellate_assembly():
        shape = extract_ocp_shape(complex_assembly)
        tess_data = tessellate_shape(shape, quality=0.5)
        mesh = serialize_mesh_data(tess_data)
        return mesh

    result = benchmark(tessellate_assembly)

    # Assembly should have vertices from multiple boxes
    assert len(result["vertices"]) >= 72


@pytest.mark.benchmark
def test_tessellation_large_assembly_timing(benchmark):
    """Benchmark tessellation for larger assembly (5 separate boxes)."""

    def create_and_tessellate_large():
        # Create 5 separate boxes and tessellate them individually
        # This simulates handling multiple objects
        meshes = []
        for _ in range(5):
            box = Box(10, 10, 10)
            shape = extract_ocp_shape(box)
            tess_data = tessellate_shape(shape, quality=0.5)
            mesh = serialize_mesh_data(tess_data)
            meshes.append(mesh)

        # Return combined vertex count
        total_vertices = sum(len(m["vertices"]) for m in meshes)
        return total_vertices

    result = benchmark(create_and_tessellate_large)

    # 5 boxes should have significant vertex count (at least 72 * 5 = 360)
    assert result >= 360


# ============================================================================
# Benchmark: CADViewer Initialization
# ============================================================================


@pytest.mark.benchmark
def test_viewer_init_timing(benchmark):
    """Benchmark CADViewer initialization with Box."""

    def init_viewer():
        box = Box(10, 10, 10)
        viewer = CADViewer(box, quality=0.1)
        return viewer

    result = benchmark(init_viewer)

    # Verify viewer created successfully
    assert result.mesh_data is not None
    assert len(result.mesh_data["vertices"]) > 0


@pytest.mark.benchmark
def test_viewer_init_cylinder_timing(benchmark):
    """Benchmark CADViewer initialization with Cylinder."""

    def init_viewer_cylinder():
        cylinder = Cylinder(radius=5, height=10)
        viewer = CADViewer(cylinder, quality=0.1)
        return viewer

    result = benchmark(init_viewer_cylinder)

    assert len(result.mesh_data["vertices"]) > 0


@pytest.mark.benchmark
def test_viewer_init_high_quality_timing(benchmark):
    """Benchmark CADViewer with high quality setting."""

    def init_viewer_hq():
        box = Box(10, 10, 10)
        viewer = CADViewer(box, quality=0.01)
        return viewer

    result = benchmark(init_viewer_hq)

    # High quality should produce valid mesh (at least 8 vertices for box corners)
    assert len(result.mesh_data["vertices"]) >= 72


# ============================================================================
# Benchmark: End-to-End Workflow
# ============================================================================


@pytest.mark.benchmark
def test_end_to_end_workflow_timing(benchmark):
    """Benchmark complete workflow: create shape → viewer → mesh data."""

    def complete_workflow():
        # Create multiple shapes
        box = Box(10, 10, 10)
        cylinder = Cylinder(radius=5, height=10)
        sphere = Sphere(radius=8)

        # Create viewers for each
        viewer1 = CADViewer(box, quality=0.2)
        viewer2 = CADViewer(cylinder, quality=0.2)
        viewer3 = CADViewer(sphere, quality=0.2)

        # Return combined vertex count
        total_vertices = (
            len(viewer1.mesh_data["vertices"])
            + len(viewer2.mesh_data["vertices"])
            + len(viewer3.mesh_data["vertices"])
        )

        return total_vertices

    result = benchmark(complete_workflow)

    # Three shapes should have substantial combined vertices
    assert result >= 300


@pytest.mark.benchmark
def test_extract_ocp_shape_timing(benchmark):
    """Benchmark extract_ocp_shape performance."""

    box = Box(10, 10, 10)

    def extract_shape():
        return extract_ocp_shape(box)

    result = benchmark(extract_shape)

    assert "TopoDS" in type(result).__name__


@pytest.mark.benchmark
def test_serialize_mesh_data_timing(benchmark):
    """Benchmark serialize_mesh_data performance."""

    # Pre-create tessellation data
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)
    tess_data = tessellate_shape(shape, quality=0.1)

    def serialize():
        return serialize_mesh_data(tess_data)

    result = benchmark(serialize)

    assert len(result["vertices"]) > 0
    assert len(result["indices"]) > 0


# ============================================================================
# User Story 2 Benchmarks - Camera Positioning
# ============================================================================


@pytest.mark.benchmark
def test_calculate_camera_position_timing(benchmark):
    """Benchmark calculate_camera_position performance."""
    from anywidget_cad_viewer.geometry import calculate_camera_position

    # Pre-create mesh data
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)
    tess_data = tessellate_shape(shape, quality=0.1)
    mesh = serialize_mesh_data(tess_data)

    def calc_camera():
        return calculate_camera_position(mesh)

    position, target = benchmark(calc_camera)

    assert len(position) == 3
    assert len(target) == 3


@pytest.mark.benchmark
def test_select_quality_timing(benchmark):
    """Benchmark select_quality performance."""
    from anywidget_cad_viewer.geometry import select_quality

    def select():
        return select_quality(10000)

    result = benchmark(select)

    assert 0.01 <= result <= 1.0


@pytest.mark.benchmark
def test_full_pipeline_with_camera_timing(benchmark):
    """Benchmark full CADViewer initialization including camera calculation."""
    box = Box(10, 10, 10)

    def create_viewer():
        return CADViewer(box, quality=0.1)

    viewer = benchmark(create_viewer)

    assert viewer.camera_position is not None
    assert viewer.camera_target is not None
    assert len(viewer.mesh_data["vertices"]) > 0
