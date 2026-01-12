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


def validate_mesh_data(data: MeshData) -> None:
    """
    Validate MeshData structure for correctness.

    Args:
        data: MeshData dictionary to validate

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

    # Validate index values
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

        vertices = []
        triangles = []
        normals = []

        # Extract face triangulation
        face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
        vertex_offset = 0

        while face_explorer.More():
            face_shape = face_explorer.Current()
            # Cast TopoDS_Shape to TopoDS_Face
            face = TopoDS.Face_s(face_shape)
            location = TopLoc_Location()
            triangulation = BRep_Tool.Triangulation_s(face, location)

            if triangulation:
                transform = location.Transformation()

                # Get face orientation for normal calculation
                face_orientation = face.Orientation()
                orientation_sign = 1.0 if face_orientation == 0 else -1.0  # TopAbs_FORWARD = 0

                # Extract vertices with computed normals
                for i in range(1, triangulation.NbNodes() + 1):
                    pnt = triangulation.Node(i)
                    pnt.Transform(transform)
                    vertices.extend([pnt.X(), pnt.Y(), pnt.Z()])

                    # Compute normal from surface at UV coordinates
                    try:
                        if triangulation.HasUVNodes():
                            uv = triangulation.UVNode(i)
                            gp_pnt = gp_Pnt()
                            gp_vec = gp_Vec()
                            BRepGProp_Face(face).Normal(uv.X(), uv.Y(), gp_pnt, gp_vec)
                            # Normalize and apply orientation
                            mag = gp_vec.Magnitude()
                            if mag > 1e-7:
                                normals.extend(
                                    [
                                        orientation_sign * gp_vec.X() / mag,
                                        orientation_sign * gp_vec.Y() / mag,
                                        orientation_sign * gp_vec.Z() / mag,
                                    ]
                                )
                            else:
                                normals.extend([0.0, 0.0, 1.0])
                        else:
                            # Fallback: use default normal
                            normals.extend([0.0, 0.0, 1.0])
                    except Exception:
                        # Fallback if normal computation fails
                        normals.extend([0.0, 0.0, 1.0])

                # Extract triangles
                for i in range(1, triangulation.NbTriangles() + 1):
                    triangle = triangulation.Triangle(i)
                    n1, n2, n3 = triangle.Get()
                    triangles.extend(
                        [vertex_offset + n1 - 1, vertex_offset + n2 - 1, vertex_offset + n3 - 1]
                    )

                vertex_offset += triangulation.NbNodes()

            face_explorer.Next()

        if not vertices:
            raise TessellationError("No triangulation data generated from shape")

        return {
            "vertices": vertices,
            "triangles": triangles,
            "normals": normals,
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
