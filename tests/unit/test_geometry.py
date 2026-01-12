"""Unit tests for geometry conversion utilities."""

import pytest
from build123d import Box

from anywidget_cad_viewer.geometry import (
    MeshData,
    extract_ocp_shape,
    is_build123d_compatible,
    serialize_mesh_data,
    tessellate_shape,
    validate_mesh_data,
)
from anywidget_cad_viewer.viewer import InvalidObjectError

# ============================================================================
# Tests for is_build123d_compatible
# ============================================================================


@pytest.mark.unit
def test_is_build123d_compatible_valid_box(simple_box):
    """Test compatibility check with valid Box object."""
    assert is_build123d_compatible(simple_box) is True


@pytest.mark.unit
def test_is_build123d_compatible_valid_cylinder(simple_cylinder):
    """Test compatibility check with valid Cylinder object."""
    assert is_build123d_compatible(simple_cylinder) is True


@pytest.mark.unit
def test_is_build123d_compatible_valid_sphere(simple_sphere):
    """Test compatibility check with valid Sphere object."""
    assert is_build123d_compatible(simple_sphere) is True


@pytest.mark.unit
def test_is_build123d_compatible_invalid_string(string_object):
    """Test compatibility check rejects string."""
    assert is_build123d_compatible(string_object) is False


@pytest.mark.unit
def test_is_build123d_compatible_invalid_none(none_object):
    """Test compatibility check rejects None."""
    assert is_build123d_compatible(none_object) is False


@pytest.mark.unit
def test_is_build123d_compatible_invalid_dict(invalid_object):
    """Test compatibility check rejects dict without wrapped."""
    assert is_build123d_compatible(invalid_object) is False


# ============================================================================
# Tests for extract_ocp_shape
# ============================================================================


@pytest.mark.unit
def test_extract_ocp_shape_valid_box(simple_box):
    """Test extracting OCP shape from Box object."""
    shape = extract_ocp_shape(simple_box)
    assert shape is not None
    # Verify it's an OCP shape by checking the type name
    assert "TopoDS" in type(shape).__name__


@pytest.mark.unit
def test_extract_ocp_shape_valid_cylinder(simple_cylinder):
    """Test extracting OCP shape from Cylinder object."""
    shape = extract_ocp_shape(simple_cylinder)
    assert shape is not None
    assert "TopoDS" in type(shape).__name__


@pytest.mark.unit
def test_extract_ocp_shape_valid_sphere(simple_sphere):
    """Test extracting OCP shape from Sphere object."""
    shape = extract_ocp_shape(simple_sphere)
    assert shape is not None
    assert "TopoDS" in type(shape).__name__


@pytest.mark.unit
def test_extract_ocp_shape_invalid_string(string_object):
    """Test extract_ocp_shape raises InvalidObjectError for string."""
    with pytest.raises(InvalidObjectError) as exc_info:
        extract_ocp_shape(string_object)
    assert "str" in str(exc_info.value)
    assert "wrapped" in str(exc_info.value)


@pytest.mark.unit
def test_extract_ocp_shape_invalid_none(none_object):
    """Test extract_ocp_shape raises InvalidObjectError for None."""
    with pytest.raises(InvalidObjectError) as exc_info:
        extract_ocp_shape(none_object)
    assert "NoneType" in str(exc_info.value)


@pytest.mark.unit
def test_extract_ocp_shape_invalid_dict(invalid_object):
    """Test extract_ocp_shape raises InvalidObjectError for dict."""
    with pytest.raises(InvalidObjectError) as exc_info:
        extract_ocp_shape(invalid_object)
    assert "dict" in str(exc_info.value)


# ============================================================================
# Tests for tessellate_shape
# ============================================================================


@pytest.mark.unit
def test_tessellate_shape_box(simple_box):
    """Test tessellating a Box shape."""
    shape = extract_ocp_shape(simple_box)
    result = tessellate_shape(shape, quality=0.1)

    # Verify structure
    assert isinstance(result, dict)
    assert "vertices" in result
    assert "triangles" in result
    assert "normals" in result
    assert "edges" in result

    # Verify data types
    assert isinstance(result["vertices"], list)
    assert isinstance(result["triangles"], list)
    assert isinstance(result["normals"], list)

    # Verify vertices are multiples of 3 (x, y, z)
    assert len(result["vertices"]) % 3 == 0
    assert len(result["vertices"]) > 0

    # Verify triangles are multiples of 3 (i1, i2, i3)
    assert len(result["triangles"]) % 3 == 0
    assert len(result["triangles"]) > 0

    # Verify normals match vertices
    assert len(result["normals"]) == len(result["vertices"])


@pytest.mark.unit
def test_tessellate_shape_cylinder(simple_cylinder):
    """Test tessellating a Cylinder shape."""
    shape = extract_ocp_shape(simple_cylinder)
    result = tessellate_shape(shape, quality=0.1)

    # Verify structure
    assert isinstance(result, dict)
    assert len(result["vertices"]) % 3 == 0
    assert len(result["vertices"]) > 0
    assert len(result["normals"]) == len(result["vertices"])


@pytest.mark.unit
def test_tessellate_shape_sphere(simple_sphere):
    """Test tessellating a Sphere shape."""
    shape = extract_ocp_shape(simple_sphere)
    result = tessellate_shape(shape, quality=0.1)

    # Verify structure
    assert isinstance(result, dict)
    assert len(result["vertices"]) % 3 == 0
    assert len(result["vertices"]) > 0
    assert len(result["normals"]) == len(result["vertices"])


@pytest.mark.unit
def test_tessellate_shape_quality_high():
    """Test higher quality produces more vertices."""
    box = Box(10, 10, 10)
    shape = extract_ocp_shape(box)

    # High quality (lower value) should produce more vertices
    high_quality = tessellate_shape(shape, quality=0.01)
    low_quality = tessellate_shape(shape, quality=1.0)

    vertex_count_high = len(high_quality["vertices"]) // 3
    vertex_count_low = len(low_quality["vertices"]) // 3

    # High quality should have more vertices
    assert vertex_count_high >= vertex_count_low


@pytest.mark.unit
def test_tessellate_shape_default_quality(simple_box):
    """Test tessellation with default quality parameter."""
    shape = extract_ocp_shape(simple_box)
    result = tessellate_shape(shape)  # Default quality=0.1

    assert len(result["vertices"]) > 0
    assert len(result["triangles"]) > 0


# ============================================================================
# Tests for validate_mesh_data
# ============================================================================


@pytest.mark.unit
def test_validate_mesh_data_valid():
    """Test validation passes for valid mesh data."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "indices": [0, 1, 2],
        "normals": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        "colors": None,
        "edges": None,
    }
    # Should not raise
    validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_with_colors():
    """Test validation passes for mesh with colors."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "indices": [0, 1, 2],
        "normals": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        "colors": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        "edges": None,
    }
    validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_with_edges():
    """Test validation passes for mesh with edges."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "indices": [0, 1, 2],
        "normals": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        "colors": None,
        "edges": [[0.0, 0.0, 0.0, 1.0, 0.0, 0.0]],
    }
    validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_invalid_vertices_length():
    """Test validation fails for vertices not multiple of 3."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0],  # Not multiple of 3
        "indices": [0, 1, 2],
        "normals": [0.0, 0.0, 1.0, 0.0],
        "colors": None,
        "edges": None,
    }
    with pytest.raises(ValueError, match="vertices length must be multiple of 3"):
        validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_invalid_indices_length():
    """Test validation fails for indices not multiple of 3."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        "indices": [0, 1],  # Not multiple of 3
        "normals": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        "colors": None,
        "edges": None,
    }
    with pytest.raises(ValueError, match="indices length must be multiple of 3"):
        validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_invalid_index_out_of_range():
    """Test validation fails for index out of range."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        "indices": [0, 1, 5],  # Index 5 out of range (only 2 vertices)
        "normals": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        "colors": None,
        "edges": None,
    }
    with pytest.raises(ValueError, match="index .* out of range"):
        validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_invalid_normals_length():
    """Test validation fails for normals length mismatch."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "indices": [0, 1, 2],
        "normals": [0.0, 0.0, 1.0],  # Too short
        "colors": None,
        "edges": None,
    }
    with pytest.raises(ValueError, match="normals length .* must equal vertices length"):
        validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_invalid_colors_length():
    """Test validation fails for colors length mismatch."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "indices": [0, 1, 2],
        "normals": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        "colors": [1.0, 0.0, 0.0],  # Too short
        "edges": None,
    }
    with pytest.raises(ValueError, match="colors length .* must equal vertices length"):
        validate_mesh_data(mesh)


@pytest.mark.unit
def test_validate_mesh_data_invalid_edge_format():
    """Test validation fails for edge with wrong number of coordinates."""
    mesh: MeshData = {
        "vertices": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "indices": [0, 1, 2],
        "normals": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        "colors": None,
        "edges": [[0.0, 0.0, 0.0, 1.0]],  # Only 4 coords, need 6
    }
    with pytest.raises(ValueError, match="edge .* must have 6 coordinates"):
        validate_mesh_data(mesh)


# ============================================================================
# Tests for serialize_mesh_data
# ============================================================================


@pytest.mark.unit
def test_serialize_mesh_data_format(simple_box):
    """Test serialize_mesh_data returns correct MeshData format."""
    shape = extract_ocp_shape(simple_box)
    tess_data = tessellate_shape(shape, quality=0.1)
    mesh = serialize_mesh_data(tess_data)

    # Verify MeshData structure
    assert "vertices" in mesh
    assert "indices" in mesh
    assert "normals" in mesh
    assert "colors" in mesh
    assert "edges" in mesh

    # Verify key mapping (triangles -> indices)
    assert mesh["indices"] == tess_data["triangles"]


@pytest.mark.unit
def test_serialize_mesh_data_vertex_count(simple_box):
    """Test serialize_mesh_data preserves vertex count."""
    shape = extract_ocp_shape(simple_box)
    tess_data = tessellate_shape(shape, quality=0.1)
    mesh = serialize_mesh_data(tess_data)

    # Vertex count should match
    assert len(mesh["vertices"]) == len(tess_data["vertices"])
    assert len(mesh["vertices"]) % 3 == 0


@pytest.mark.unit
def test_serialize_mesh_data_validates():
    """Test serialize_mesh_data calls validate_mesh_data."""
    # Invalid data should raise during serialization
    invalid_tess = {
        "vertices": [0.0, 0.0],  # Not multiple of 3
        "triangles": [0, 1, 2],
        "normals": [0.0, 0.0],
        "edges": [],
    }
    with pytest.raises(ValueError, match="vertices length must be multiple of 3"):
        serialize_mesh_data(invalid_tess)


@pytest.mark.unit
def test_serialize_mesh_data_from_cylinder(simple_cylinder):
    """Test serialization works for cylinder tessellation."""
    shape = extract_ocp_shape(simple_cylinder)
    tess_data = tessellate_shape(shape, quality=0.1)
    mesh = serialize_mesh_data(tess_data)

    assert len(mesh["vertices"]) > 0
    assert len(mesh["indices"]) > 0
    assert len(mesh["normals"]) == len(mesh["vertices"])


@pytest.mark.unit
def test_serialize_mesh_data_from_sphere(simple_sphere):
    """Test serialization works for sphere tessellation."""
    shape = extract_ocp_shape(simple_sphere)
    tess_data = tessellate_shape(shape, quality=0.1)
    mesh = serialize_mesh_data(tess_data)

    assert len(mesh["vertices"]) > 0
    assert len(mesh["indices"]) > 0
    assert len(mesh["normals"]) == len(mesh["vertices"])
