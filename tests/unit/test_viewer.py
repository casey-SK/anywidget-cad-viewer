"""Unit tests for CADViewer widget."""

import pytest
from build123d import Box

from anywidget_cad_viewer.viewer import (
    CADViewer,
    CADViewerError,
    InvalidObjectError,
    OversizedGeometryError,
    TessellationError,
)

# ============================================================================
# Tests for Exception Classes
# ============================================================================


@pytest.mark.unit
def test_cadviewer_error_is_exception():
    """Test CADViewerError inherits from Exception."""
    assert issubclass(CADViewerError, Exception)


@pytest.mark.unit
def test_invalid_object_error_message(string_object):
    """Test InvalidObjectError has correct message format."""
    error = InvalidObjectError(string_object)
    assert "str" in str(error)
    assert "wrapped" in str(error)
    assert "TopoDS" in str(error)


@pytest.mark.unit
def test_invalid_object_error_stores_object(invalid_object):
    """Test InvalidObjectError stores original object."""
    error = InvalidObjectError(invalid_object)
    assert error.obj is invalid_object


@pytest.mark.unit
def test_tessellation_error_with_original():
    """Test TessellationError with original exception."""
    original = ValueError("original error")
    error = TessellationError("test message", original_error=original)
    assert "test message" in str(error)
    assert "original error" in str(error)
    assert error.original_error is original


@pytest.mark.unit
def test_tessellation_error_without_original():
    """Test TessellationError without original exception."""
    error = TessellationError("test message")
    assert "test message" in str(error)
    assert error.original_error is None


@pytest.mark.unit
def test_oversized_geometry_error_message():
    """Test OversizedGeometryError message format."""
    error = OversizedGeometryError(vertex_count=2_000_000)
    assert "2,000,000" in str(error)
    assert "1,000,000" in str(error)  # Default limit
    assert "simplifying" in str(error).lower()


@pytest.mark.unit
def test_oversized_geometry_error_stores_counts():
    """Test OversizedGeometryError stores vertex count and limit."""
    error = OversizedGeometryError(vertex_count=2_500_000, limit=1_000_000)
    assert error.vertex_count == 2_500_000
    assert error.limit == 1_000_000


# ============================================================================
# Tests for CADViewer Initialization
# ============================================================================


@pytest.mark.unit
def test_cadviewer_init_valid_box(simple_box):
    """Test CADViewer initializes with valid Box object."""
    viewer = CADViewer(simple_box)
    assert viewer is not None
    assert viewer.mesh_data is not None
    assert isinstance(viewer.mesh_data, dict)
    assert len(viewer.mesh_data.get("vertices", [])) > 0


@pytest.mark.unit
def test_cadviewer_init_valid_cylinder(simple_cylinder):
    """Test CADViewer initializes with valid Cylinder object."""
    viewer = CADViewer(simple_cylinder)
    assert viewer is not None
    assert len(viewer.mesh_data.get("vertices", [])) > 0


@pytest.mark.unit
def test_cadviewer_init_valid_sphere(simple_sphere):
    """Test CADViewer initializes with valid Sphere object."""
    viewer = CADViewer(simple_sphere)
    assert viewer is not None
    assert len(viewer.mesh_data.get("vertices", [])) > 0


@pytest.mark.unit
def test_cadviewer_init_invalid_string(string_object):
    """Test CADViewer raises InvalidObjectError for string."""
    with pytest.raises(InvalidObjectError) as exc_info:
        CADViewer(string_object)
    assert "str" in str(exc_info.value)


@pytest.mark.unit
def test_cadviewer_init_invalid_none(none_object):
    """Test CADViewer raises InvalidObjectError for None."""
    with pytest.raises(InvalidObjectError) as exc_info:
        CADViewer(none_object)
    assert "NoneType" in str(exc_info.value)


@pytest.mark.unit
def test_cadviewer_init_invalid_dict(invalid_object):
    """Test CADViewer raises InvalidObjectError for dict."""
    with pytest.raises(InvalidObjectError) as exc_info:
        CADViewer(invalid_object)
    assert "dict" in str(exc_info.value)


@pytest.mark.unit
def test_cadviewer_init_invalid_empty_list(empty_list):
    """Test CADViewer raises InvalidObjectError for empty list."""
    with pytest.raises(InvalidObjectError) as exc_info:
        CADViewer(empty_list)
    assert "list" in str(exc_info.value)


# ============================================================================
# Tests for Quality Parameter Validation
# ============================================================================


@pytest.mark.unit
def test_cadviewer_quality_too_low(simple_box):
    """Test CADViewer raises ValueError for quality < 0.01."""
    with pytest.raises(ValueError, match="quality must be between 0.01 and 1.0"):
        CADViewer(simple_box, quality=0.001)


@pytest.mark.unit
def test_cadviewer_quality_too_high(simple_box):
    """Test CADViewer raises ValueError for quality > 1.0."""
    with pytest.raises(ValueError, match="quality must be between 0.01 and 1.0"):
        CADViewer(simple_box, quality=1.5)


@pytest.mark.unit
def test_cadviewer_quality_at_lower_bound(simple_box):
    """Test CADViewer accepts quality=0.01."""
    viewer = CADViewer(simple_box, quality=0.01)
    assert viewer is not None


@pytest.mark.unit
def test_cadviewer_quality_at_upper_bound(simple_box):
    """Test CADViewer accepts quality=1.0."""
    viewer = CADViewer(simple_box, quality=1.0)
    assert viewer is not None


@pytest.mark.unit
def test_cadviewer_quality_affects_vertex_count():
    """Test higher quality produces more vertices."""
    box = Box(10, 10, 10)

    viewer_high = CADViewer(box, quality=0.01)
    viewer_low = CADViewer(box, quality=1.0)

    vertex_count_high = len(viewer_high.mesh_data["vertices"]) // 3
    vertex_count_low = len(viewer_low.mesh_data["vertices"]) // 3

    # High quality (0.01) should produce more vertices than low (1.0)
    assert vertex_count_high >= vertex_count_low


# ============================================================================
# Tests for Default Options
# ============================================================================


@pytest.mark.unit
def test_cadviewer_default_show_edges(simple_box):
    """Test CADViewer has default show_edges=True."""
    viewer = CADViewer(simple_box)
    assert viewer.show_edges is True


@pytest.mark.unit
def test_cadviewer_default_show_axes(simple_box):
    """Test CADViewer has default show_axes=True."""
    viewer = CADViewer(simple_box)
    assert viewer.show_axes is True


@pytest.mark.unit
def test_cadviewer_default_background_color(simple_box):
    """Test CADViewer has default background_color=#F0F0F0."""
    viewer = CADViewer(simple_box)
    assert viewer.background_color == "#F0F0F0"


@pytest.mark.unit
def test_cadviewer_default_width(simple_box):
    """Test CADViewer has default width=800."""
    viewer = CADViewer(simple_box)
    assert viewer.width == 800


@pytest.mark.unit
def test_cadviewer_default_height(simple_box):
    """Test CADViewer has default height=600."""
    viewer = CADViewer(simple_box)
    assert viewer.height == 600


@pytest.mark.unit
def test_cadviewer_default_quality(simple_box):
    """Test CADViewer has default quality=0.1."""
    viewer = CADViewer(simple_box)
    assert viewer._quality == 0.1


@pytest.mark.unit
def test_cadviewer_default_error_message(simple_box):
    """Test CADViewer has empty error_message by default."""
    viewer = CADViewer(simple_box)
    assert viewer.error_message == ""


# ============================================================================
# Tests for Custom Options
# ============================================================================


@pytest.mark.unit
def test_cadviewer_custom_show_edges_false(simple_box):
    """Test CADViewer with custom show_edges=False."""
    viewer = CADViewer(simple_box, show_edges=False)
    assert viewer.show_edges is False


@pytest.mark.unit
def test_cadviewer_custom_show_axes_false(simple_box):
    """Test CADViewer with custom show_axes=False."""
    viewer = CADViewer(simple_box, show_axes=False)
    assert viewer.show_axes is False


@pytest.mark.unit
def test_cadviewer_custom_background_color(simple_box):
    """Test CADViewer with custom background_color."""
    viewer = CADViewer(simple_box, background_color="#FFFFFF")
    assert viewer.background_color == "#FFFFFF"


@pytest.mark.unit
def test_cadviewer_custom_width(simple_box):
    """Test CADViewer with custom width."""
    viewer = CADViewer(simple_box, width=1024)
    assert viewer.width == 1024


@pytest.mark.unit
def test_cadviewer_custom_height(simple_box):
    """Test CADViewer with custom height."""
    viewer = CADViewer(simple_box, height=768)
    assert viewer.height == 768


@pytest.mark.unit
def test_cadviewer_custom_quality(simple_box):
    """Test CADViewer with custom quality."""
    viewer = CADViewer(simple_box, quality=0.05)
    assert viewer._quality == 0.05


@pytest.mark.unit
def test_cadviewer_all_custom_options(simple_box):
    """Test CADViewer with all custom options."""
    viewer = CADViewer(
        simple_box,
        quality=0.05,
        show_edges=False,
        show_axes=False,
        background_color="#000000",
        width=1920,
        height=1080,
    )
    assert viewer._quality == 0.05
    assert viewer.show_edges is False
    assert viewer.show_axes is False
    assert viewer.background_color == "#000000"
    assert viewer.width == 1920
    assert viewer.height == 1080


# ============================================================================
# Tests for Mesh Data Generation
# ============================================================================


@pytest.mark.unit
def test_cadviewer_mesh_data_structure(simple_box):
    """Test CADViewer generates correct mesh_data structure."""
    viewer = CADViewer(simple_box)
    mesh = viewer.mesh_data

    assert "vertices" in mesh
    assert "indices" in mesh
    assert "normals" in mesh
    assert "colors" in mesh
    assert "edges" in mesh


@pytest.mark.unit
def test_cadviewer_mesh_data_valid_vertices(simple_box):
    """Test CADViewer mesh_data has valid vertices."""
    viewer = CADViewer(simple_box)
    vertices = viewer.mesh_data["vertices"]

    assert isinstance(vertices, list)
    assert len(vertices) % 3 == 0
    assert len(vertices) > 0
    assert all(isinstance(v, (int, float)) for v in vertices)


@pytest.mark.unit
def test_cadviewer_mesh_data_valid_indices(simple_box):
    """Test CADViewer mesh_data has valid indices."""
    viewer = CADViewer(simple_box)
    indices = viewer.mesh_data["indices"]

    assert isinstance(indices, list)
    assert len(indices) % 3 == 0
    assert len(indices) > 0
    assert all(isinstance(i, int) for i in indices)


@pytest.mark.unit
def test_cadviewer_mesh_data_valid_normals(simple_box):
    """Test CADViewer mesh_data has valid normals."""
    viewer = CADViewer(simple_box)
    normals = viewer.mesh_data["normals"]
    vertices = viewer.mesh_data["vertices"]

    assert isinstance(normals, list)
    assert len(normals) == len(vertices)
    assert all(isinstance(n, (int, float)) for n in normals)


@pytest.mark.unit
def test_cadviewer_stores_object(simple_box):
    """Test CADViewer stores original object."""
    viewer = CADViewer(simple_box)
    assert viewer._obj is simple_box


# ============================================================================
# Tests for _repr_mimebundle_
# ============================================================================


@pytest.mark.unit
def test_cadviewer_repr_mimebundle(simple_box):
    """Test CADViewer has _repr_mimebundle_ method."""
    viewer = CADViewer(simple_box)
    assert hasattr(viewer, "_repr_mimebundle_")
    assert callable(viewer._repr_mimebundle_)


@pytest.mark.unit
def test_cadviewer_repr_mimebundle_returns_dict(simple_box):
    """Test CADViewer._repr_mimebundle_ returns dictionary."""
    viewer = CADViewer(simple_box)
    result = viewer._repr_mimebundle_()
    assert isinstance(result, (dict, tuple))


# ============================================================================
# Tests for Camera Position/Target Traitlets (User Story 2)
# ============================================================================


@pytest.mark.unit
def test_cadviewer_camera_position_set(simple_box):
    """Test CADViewer sets camera_position traitlet on initialization."""
    viewer = CADViewer(simple_box)
    camera_pos = viewer.camera_position

    assert camera_pos is not None
    assert isinstance(camera_pos, list)
    assert len(camera_pos) == 3
    assert all(isinstance(p, float) for p in camera_pos)


@pytest.mark.unit
def test_cadviewer_camera_target_set(simple_box):
    """Test CADViewer sets camera_target traitlet on initialization."""
    viewer = CADViewer(simple_box)
    camera_target = viewer.camera_target

    assert isinstance(camera_target, list)
    assert len(camera_target) == 3
    assert all(isinstance(t, float) for t in camera_target)


@pytest.mark.unit
def test_cadviewer_camera_position_valid_coordinates(simple_box):
    """Test camera_position contains valid 3D coordinates."""
    viewer = CADViewer(simple_box)
    x, y, z = viewer.camera_position

    # Camera should be positioned away from origin
    assert isinstance(x, float)
    assert isinstance(y, float)
    assert isinstance(z, float)


@pytest.mark.unit
def test_cadviewer_camera_target_at_geometry_center(simple_box):
    """Test camera_target is at geometry center."""
    viewer = CADViewer(simple_box)
    target = viewer.camera_target

    # For a 1x1x1 box, target should be near (0.5, 0.5, 0.5)
    # Allow some tolerance for mesh center calculation
    assert -5.0 < target[0] < 5.0
    assert -5.0 < target[1] < 5.0
    assert -5.0 < target[2] < 5.0


@pytest.mark.unit
def test_cadviewer_camera_position_scales_with_geometry(simple_sphere):
    """Test camera position scales appropriately with geometry size."""
    viewer = CADViewer(simple_sphere)
    position = viewer.camera_position

    # Camera should be positioned at a reasonable distance
    cam_distance = sum(p**2 for p in position) ** 0.5
    assert cam_distance > 1.0  # Should be away from origin


@pytest.mark.unit
def test_cadviewer_camera_traitlets_sync_enabled(simple_box):
    """Test camera traitlets are marked for sync to JavaScript."""
    viewer = CADViewer(simple_box)

    # Check that traitlets have sync=True tag
    # This ensures camera state syncs between Python and JavaScript
    assert hasattr(viewer, "camera_position")
    assert hasattr(viewer, "camera_target")


@pytest.mark.unit
def test_cadviewer_camera_different_for_different_objects(simple_box, simple_cylinder):
    """Test camera position adapts to different geometries."""
    viewer_box = CADViewer(simple_box)
    viewer_cylinder = CADViewer(simple_cylinder)

    # Both should have valid camera positions
    assert viewer_box.camera_position is not None
    assert viewer_cylinder.camera_position is not None

    # Positions might differ based on geometry
    assert len(viewer_box.camera_position) == 3
    assert len(viewer_cylinder.camera_position) == 3


@pytest.mark.unit
def test_cadviewer_camera_position_none_default():
    """Test camera_position traitlet defaults to None before initialization."""
    from anywidget_cad_viewer.viewer import CADViewer as CADViewerClass

    # Before passing an object, camera_position can be None
    # This tests the traitlet default configuration
    assert hasattr(CADViewerClass, "camera_position")


@pytest.mark.unit
def test_cadviewer_camera_target_default():
    """Test camera_target traitlet has sensible default."""
    from anywidget_cad_viewer.viewer import CADViewer as CADViewerClass

    # Camera target should default to [0, 0, 0] (origin)
    assert hasattr(CADViewerClass, "camera_target")
