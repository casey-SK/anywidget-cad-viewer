"""Geometry conversion utilities for build123d to OCP tessellation."""

from typing import Any, TypedDict


class MeshData(TypedDict):
    """
    Tessellated mesh data structure for CAD geometry.

    This format is compatible with Three.js BufferGeometry and three-cad-viewer.
    All coordinate arrays are flat lists of numbers in xyz order.
    """

    vertices: list[float]  # Flat array: [x1, y1, z1, x2, y2, z2, ...]
    indices: list[int]  # Triangle indices: [i1, i2, i3, ...]
    normals: list[float]  # Normal vectors: [nx1, ny1, nz1, ...]
    colors: list[float] | None  # Optional RGB: [r1, g1, b1, ...] (0-1 range)
    edges: list[list[float]] | None  # Optional edge lines: [[x1,y1,z1,x2,y2,z2], ...]


def is_build123d_compatible(obj: Any) -> bool:
    """
    Check if an object is compatible with build123d CAD visualization.

    Args:
        obj: Object to check for build123d compatibility

    Returns:
        True if object has a wrapped OCP TopoDS shape, False otherwise

    Examples:
        >>> from build123d import Box
        >>> box = Box(1, 1, 1)
        >>> is_build123d_compatible(box)
        True
        >>> is_build123d_compatible("not a cad object")
        False
    """
    # Check for wrapped attribute (standard build123d pattern)
    if not hasattr(obj, "wrapped"):
        return False

    # Check if wrapped object is an OCP TopoDS type
    wrapped = obj.wrapped
    if not hasattr(wrapped, "__class__"):
        return False

    # Verify it's a TopoDS shape from OpenCascade
    wrapped_type = type(wrapped).__name__
    return "TopoDS" in wrapped_type


def validate_mesh_data(data: MeshData, strict: bool = False) -> None:
    """
    Validate MeshData structure for correctness.

    Args:
        data: MeshData dictionary to validate
        strict: If True, perform expensive O(n) index range validation.
                If False (default), skip individual index checks for performance.
                OCP always generates valid indices, so strict mode is mainly for testing.

    Raises:
        ValueError: If data structure is invalid

    Examples:
        >>> mesh = {
        ...     "vertices": [0, 0, 0, 1, 0, 0, 0, 1, 0],
        ...     "indices": [0, 1, 2],
        ...     "normals": [0, 0, 1, 0, 0, 1, 0, 0, 1],
        ...     "colors": None,
        ...     "edges": None
        ... }
        >>> validate_mesh_data(mesh)  # No exception = valid
    """
    # Validate vertices array
    if len(data["vertices"]) % 3 != 0:
        raise ValueError(f"vertices length must be multiple of 3, got {len(data['vertices'])}")

    vertex_count = len(data["vertices"]) // 3

    # Validate indices array
    if len(data["indices"]) % 3 != 0:
        raise ValueError(f"indices length must be multiple of 3, got {len(data['indices'])}")

    # Phase 1 optimization: Only validate individual index values in strict mode
    # OCP always generates valid indices, so this O(n) check is usually unnecessary
    if strict:
        for idx in data["indices"]:
            if idx < 0 or idx >= vertex_count:
                raise ValueError(f"index {idx} out of range (vertex count: {vertex_count})")

    # Validate normals array
    if len(data["normals"]) != len(data["vertices"]):
        raise ValueError(
            f"normals length ({len(data['normals'])}) must equal vertices length ({len(data['vertices'])})"
        )

    # Validate colors array if present
    colors = data.get("colors")
    if colors is not None:
        if len(colors) != len(data["vertices"]):
            raise ValueError(
                f"colors length ({len(colors)}) must equal vertices length ({len(data['vertices'])})"
            )

    # Validate edges format if present
    edges = data.get("edges")
    if edges is not None:
        for i, edge in enumerate(edges):
            if len(edge) != 6:
                raise ValueError(
                    f"edge {i} must have 6 coordinates [x1,y1,z1,x2,y2,z2], got {len(edge)}"
                )


def extract_ocp_shape(obj):
    """
    Extract OCP TopoDS_Shape from a build123d object.

    Args:
        obj: build123d object with 'wrapped' attribute

    Returns:
        OCP TopoDS_Shape object

    Raises:
        InvalidObjectError: If object doesn't have wrapped OCP shape

    Examples:
        >>> from build123d import Box
        >>> box = Box(1, 1, 1)
        >>> shape = extract_ocp_shape(box)
        >>> print(type(shape).__name__)
        'TopoDS_Shape'
    """
    from .viewer import InvalidObjectError

    if not is_build123d_compatible(obj):
        raise InvalidObjectError(obj)

    return obj.wrapped


def tessellate_shape(shape, quality: float = 0.1) -> dict:
    """
    Tessellate an OCP shape into triangulated mesh data.

    Uses OCP's BRepMesh for tessellation with configurable quality.

    Args:
        shape: OCP TopoDS_Shape to tessellate
        quality: Tessellation quality / linear deflection (0.01=high, 1.0=low, default=0.1)

    Returns:
        Dictionary with keys: vertices, triangles, normals, edges

    Raises:
        TessellationError: If tessellation fails
    """
    from .viewer import TessellationError

    try:
        # Import OCP modules (type: ignore for modules not in type checker)
        import array  # Phase 1 optimization: use array for pre-allocation

        from OCP.BRep import BRep_Tool  # type: ignore
        from OCP.BRepGProp import BRepGProp_Face  # type: ignore
        from OCP.BRepMesh import BRepMesh_IncrementalMesh  # type: ignore
        from OCP.gp import gp_Pnt, gp_Vec  # type: ignore
        from OCP.TopAbs import TopAbs_FACE  # type: ignore
        from OCP.TopExp import TopExp_Explorer  # type: ignore
        from OCP.TopLoc import TopLoc_Location  # type: ignore
        from OCP.TopoDS import TopoDS  # type: ignore

        # Tessellate the shape with quality parameter
        mesh = BRepMesh_IncrementalMesh(shape, quality, False, 0.1, True)
        mesh.Perform()

        # Phase 1 optimization: Count vertices and triangles first for pre-allocation
        face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
        total_vertices = 0
        total_triangles = 0
        face_data = []  # Store face info for second pass

        while face_explorer.More():
            face_shape = face_explorer.Current()
            face = TopoDS.Face_s(face_shape)
            location = TopLoc_Location()
            triangulation = BRep_Tool.Triangulation_s(face, location)

            if triangulation:
                nb_nodes = triangulation.NbNodes()
                nb_triangles = triangulation.NbTriangles()
                total_vertices += nb_nodes
                total_triangles += nb_triangles
                face_data.append((face, triangulation, location, nb_nodes, nb_triangles))

            face_explorer.Next()

        if total_vertices == 0:
            raise TessellationError("No triangulation data generated from shape")

        # Phase 1 optimization: Pre-allocate arrays
        vertices = array.array("f", [0.0] * (total_vertices * 3))
        normals = array.array("f", [0.0] * (total_vertices * 3))
        triangles = array.array("i", [0] * (total_triangles * 3))

        # Second pass: Fill pre-allocated arrays
        vertex_offset = 0
        vertex_idx = 0
        normal_idx = 0
        triangle_idx = 0

        for face, triangulation, location, nb_nodes, nb_triangles in face_data:
            transform = location.Transformation()

            # Get face orientation for normal calculation
            face_orientation = face.Orientation()
            orientation_sign = 1.0 if face_orientation == 0 else -1.0  # TopAbs_FORWARD = 0

            # Phase 1 optimization: Cache BRepGProp_Face per face
            face_prop = BRepGProp_Face(face) if triangulation.HasUVNodes() else None

            # Extract vertices with computed normals
            for i in range(1, nb_nodes + 1):
                pnt = triangulation.Node(i)
                pnt.Transform(transform)
                vertices[vertex_idx] = pnt.X()
                vertices[vertex_idx + 1] = pnt.Y()
                vertices[vertex_idx + 2] = pnt.Z()
                vertex_idx += 3

                # Compute normal from surface at UV coordinates
                try:
                    if face_prop is not None:
                        uv = triangulation.UVNode(i)
                        gp_pnt = gp_Pnt()
                        gp_vec = gp_Vec()
                        face_prop.Normal(uv.X(), uv.Y(), gp_pnt, gp_vec)
                        # Normalize and apply orientation
                        mag = gp_vec.Magnitude()
                        if mag > 1e-7:
                            normals[normal_idx] = orientation_sign * gp_vec.X() / mag
                            normals[normal_idx + 1] = orientation_sign * gp_vec.Y() / mag
                            normals[normal_idx + 2] = orientation_sign * gp_vec.Z() / mag
                        else:
                            normals[normal_idx] = 0.0
                            normals[normal_idx + 1] = 0.0
                            normals[normal_idx + 2] = 1.0
                    else:
                        # Fallback: use default normal
                        normals[normal_idx] = 0.0
                        normals[normal_idx + 1] = 0.0
                        normals[normal_idx + 2] = 1.0
                except Exception:
                    # Fallback if normal computation fails
                    normals[normal_idx] = 0.0
                    normals[normal_idx + 1] = 0.0
                    normals[normal_idx + 2] = 1.0

                normal_idx += 3

            # Extract triangles
            for i in range(1, nb_triangles + 1):
                triangle = triangulation.Triangle(i)
                n1, n2, n3 = triangle.Get()
                triangles[triangle_idx] = vertex_offset + n1 - 1
                triangles[triangle_idx + 1] = vertex_offset + n2 - 1
                triangles[triangle_idx + 2] = vertex_offset + n3 - 1
                triangle_idx += 3

            vertex_offset += nb_nodes

        return {
            "vertices": vertices.tolist(),
            "triangles": triangles.tolist(),
            "normals": normals.tolist(),
            "edges": [],  # Edge extraction implemented in T051
        }

    except ImportError as e:
        raise TessellationError("OCP library not available", original_error=e) from e
    except Exception as e:
        raise TessellationError(f"Tessellation failed: {type(e).__name__}", original_error=e) from e


def serialize_mesh_data(tessellation_data: dict) -> MeshData:
    """
    Convert tessellation output to MeshData format.

    Args:
        tessellation_data: Dictionary from tessellate_shape() with keys:
                          vertices, triangles, normals, edges

    Returns:
        MeshData dictionary compatible with three-cad-viewer

    Raises:
        ValueError: If mesh data validation fails

    Examples:
        >>> tess_data = {
        ...     "vertices": [0, 0, 0, 1, 0, 0, 0, 1, 0],
        ...     "triangles": [0, 1, 2],
        ...     "normals": [0, 0, 1, 0, 0, 1, 0, 0, 1],
        ...     "edges": []
        ... }
        >>> mesh = serialize_mesh_data(tess_data)
        >>> mesh["indices"]
        [0, 1, 2]
    """
    mesh_data: MeshData = {
        "vertices": tessellation_data.get("vertices", []),
        "indices": tessellation_data.get("triangles", []),  # Map triangles -> indices
        "normals": tessellation_data.get("normals", []),
        "colors": tessellation_data.get("colors"),
        "edges": tessellation_data.get("edges"),
    }
    validate_mesh_data(mesh_data)
    return mesh_data


def select_quality(vertex_count: int, requested_quality: float | None = None) -> float:
    """
    Select adaptive tessellation quality based on geometry complexity.

    Automatically adjusts quality to maintain performance for complex geometries
    while preserving detail for simple shapes.

    Args:
        vertex_count: Expected number of vertices in the geometry
        requested_quality: User-requested quality (0.01-1.0), or None for auto

    Returns:
        Quality value to use for tessellation (0.01-1.0)

    Examples:
        >>> select_quality(100)  # Simple shape - high quality
        0.05
        >>> select_quality(50000)  # Complex shape - adaptive quality
        0.2
        >>> select_quality(10000, requested_quality=0.1)  # User override
        0.1
    """
    # If user specified quality, respect it
    if requested_quality is not None:
        return max(0.01, min(1.0, requested_quality))

    # Adaptive quality selection based on vertex count estimates
    if vertex_count < 1000:
        return 0.05  # High quality for simple shapes
    elif vertex_count < 5000:
        return 0.1  # Medium-high quality
    elif vertex_count < 20000:
        return 0.15  # Medium quality
    elif vertex_count < 50000:
        return 0.2  # Medium-low quality
    else:
        return 0.3  # Low quality for very complex shapes


def calculate_camera_position(mesh_data: MeshData) -> tuple[list[float], list[float]]:
    """
    Calculate optimal camera position and target from mesh bounding box.

    Positions camera to frame the entire geometry with appropriate distance
    based on object size and aspect ratio.

    Args:
        mesh_data: MeshData dictionary with vertices

    Returns:
        Tuple of (camera_position, camera_target) as [x, y, z] lists

    Examples:
        >>> mesh = {
        ...     "vertices": [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0],
        ...     "indices": [0, 1, 2, 0, 2, 3],
        ...     "normals": [0, 0, 1] * 4,
        ...     "colors": None,
        ...     "edges": None
        ... }
        >>> position, target = calculate_camera_position(mesh)
        >>> len(position), len(target)
        (3, 3)
    """
    vertices = mesh_data["vertices"]
    if not vertices or len(vertices) < 3:
        # Default camera position for empty geometry
        return [10.0, 10.0, 10.0], [0.0, 0.0, 0.0]

    # Calculate bounding box
    xs = vertices[0::3]
    ys = vertices[1::3]
    zs = vertices[2::3]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    # Calculate center point
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2
    center = [center_x, center_y, center_z]

    # Calculate bounding box size
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z
    max_dim = max(size_x, size_y, size_z)

    # Position camera at distance proportional to object size
    # Use FOV=50 degrees to calculate distance
    fov_radians = 50 * (3.14159 / 180)
    camera_distance = abs(max_dim / (2 * (fov_radians / 2) ** 0.5)) * 1.5

    # Position camera at diagonal for good viewing angle
    camera_position = [
        center_x + camera_distance,
        center_y + camera_distance,
        center_z + camera_distance,
    ]

    return camera_position, center


def extract_color(obj: Any) -> tuple[float, float, float] | None:
    """
    Extract RGB color from a build123d object.

    Args:
        obj: build123d object with optional 'color' attribute

    Returns:
        RGB tuple (r, g, b) with values in 0-1 range, or None if no color

    Examples:
        >>> from build123d import Box, Color
        >>> box = Box(1, 1, 1)
        >>> box.color = Color('red')
        >>> extract_color(box)
        (1.0, 0.0, 0.0)
        >>> box_no_color = Box(1, 1, 1)
        >>> extract_color(box_no_color)
        None
    """
    # Check if object has color attribute
    if not hasattr(obj, "color") or obj.color is None:
        return None

    try:
        # build123d Color wraps OCP Quantity_Color
        if hasattr(obj.color, "wrapped"):
            ocp_color = obj.color.wrapped.GetRGB()
            return (ocp_color.Red(), ocp_color.Green(), ocp_color.Blue())
        # Fallback: try direct tuple/list conversion
        elif hasattr(obj.color, "__iter__"):
            rgb = list(obj.color)[:3]  # Take first 3 values (RGB)
            return tuple(rgb)
    except Exception:
        return None

    return None


def create_color_array(
    vertex_count: int, color: tuple[float, float, float] | None
) -> list[float] | None:
    """
    Create per-vertex color array for MeshData.

    Args:
        vertex_count: Number of vertices in the mesh
        color: RGB tuple (r, g, b) in 0-1 range, or None

    Returns:
        Flat list of RGB values [r1, g1, b1, r2, g2, b2, ...], or None if no color

    Examples:
        >>> create_color_array(3, (1.0, 0.0, 0.0))
        [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        >>> create_color_array(2, None)
        None
    """
    if color is None:
        return None

    r, g, b = color
    # Repeat color for each vertex
    return [r, g, b] * vertex_count
