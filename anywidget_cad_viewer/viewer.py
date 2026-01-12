"""CAD Viewer widget implementation using anywidget."""

import pathlib

import anywidget
import traitlets


class CADViewerError(Exception):
    """Base exception for CAD viewer errors."""

    pass


class InvalidObjectError(CADViewerError):
    """Raised when object is not a valid build123d CAD object."""

    def __init__(self, obj: object):
        self.obj = obj
        obj_type = type(obj).__name__
        super().__init__(
            f"Cannot visualize object of type '{obj_type}': "
            f"Object must have 'wrapped' attribute containing OCP TopoDS shape"
        )


class TessellationError(CADViewerError):
    """Raised when geometry tessellation fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        if original_error:
            super().__init__(f"Failed to tessellate geometry: {message} ({original_error})")
        else:
            super().__init__(f"Failed to tessellate geometry: {message}")


class OversizedGeometryError(CADViewerError):
    """Raised when geometry exceeds size limits."""

    def __init__(self, vertex_count: int, limit: int = 1_000_000):
        self.vertex_count = vertex_count
        self.limit = limit
        super().__init__(
            f"Geometry too complex ({vertex_count:,} vertices). "
            f"Limit is {limit:,} vertices. "
            f"Consider simplifying or using lower quality setting."
        )


class CADViewer(anywidget.AnyWidget):
    """
    An anywidget for visualizing build123d CAD objects in notebooks.

    This widget automatically displays build123d geometry with interactive
    3D controls in marimo, Jupyter, and other anywidget-compatible environments.

    Args:
        obj: build123d object to visualize (must have 'wrapped' OCP shape)
        quality: Tessellation quality (0.01-1.0, lower=higher quality, default=0.1)
        show_edges: Display edge lines (default=True)
        show_axes: Display coordinate axes (default=True)
        background_color: Canvas background color as hex string (default="#F0F0F0")
        width: Widget width in pixels (default=800)
        height: Widget height in pixels (default=600)

    Examples:
        >>> from build123d import Box
        >>> from anywidget_cad_viewer import CADViewer
        >>> box = Box(10, 20, 30)
        >>> CADViewer(box)  # Auto-displays in notebook cell

        >>> # Custom quality and display options
        >>> CADViewer(box, quality=0.05, show_edges=False, background_color="#FFFFFF")
    """

    # Widget metadata - load from static files
    _esm = pathlib.Path(__file__).parent / "static" / "index.js"
    _css = pathlib.Path(__file__).parent / "static" / "index.css"

    # Traitlets for model synchronization
    mesh_data = traitlets.Dict(default_value={}).tag(sync=True)
    camera_position = traitlets.List(
        trait=traitlets.Float(), default_value=None, allow_none=True
    ).tag(sync=True)
    camera_target = traitlets.List(trait=traitlets.Float(), default_value=[0, 0, 0]).tag(sync=True)
    background_color = traitlets.Unicode(default_value="#F0F0F0").tag(sync=True)
    show_edges = traitlets.Bool(default_value=True).tag(sync=True)
    show_axes = traitlets.Bool(default_value=True).tag(sync=True)
    width = traitlets.Int(default_value=800).tag(sync=True)
    height = traitlets.Int(default_value=600).tag(sync=True)
    error_message = traitlets.Unicode(default_value="").tag(sync=True)

    def __init__(
        self,
        obj,
        *,
        quality: float = 0.1,
        show_edges: bool = True,
        show_axes: bool = True,
        background_color: str = "#F0F0F0",
        width: int = 800,
        height: int = 600,
    ):
        """
        Initialize CADViewer widget with a build123d object.

        Args:
            obj: build123d object to visualize
            quality: Tessellation quality factor (0.01-1.0)
            show_edges: Display edge lines
            show_axes: Display coordinate axes
            background_color: Background color (hex string)
            width: Widget width in pixels
            height: Widget height in pixels

        Raises:
            InvalidObjectError: If obj is not a valid build123d object
            ValueError: If quality is out of range
        """
        super().__init__()

        # Store the build123d object
        self._obj = obj
        self._quality = quality

        # Validate quality parameter
        if not 0.01 <= quality <= 1.0:
            raise ValueError(f"quality must be between 0.01 and 1.0, got {quality}")

        # Set display options
        self.show_edges = show_edges
        self.show_axes = show_axes
        self.background_color = background_color
        self.width = width
        self.height = height

        # Tessellation pipeline: obj -> OCP shape -> mesh data -> serialized format
        from .geometry import (
            calculate_camera_position,
            create_color_array,
            extract_color,
            extract_ocp_shape,
            serialize_mesh_data,
            tessellate_shape,
        )

        try:
            # Step 1: Extract OCP shape from build123d object
            shape = extract_ocp_shape(obj)

            # Step 2: Tessellate the shape
            tessellation_data = tessellate_shape(shape, quality=quality)

            # Step 3: Extract color from build123d object
            color_rgb = extract_color(obj)
            if color_rgb:
                # Calculate vertex count from tessellation
                vertex_count = len(tessellation_data.get("vertices", [])) // 3
                # Create per-vertex color array
                tessellation_data["colors"] = create_color_array(vertex_count, color_rgb)

            # Step 4: Serialize to MeshData format
            mesh = serialize_mesh_data(tessellation_data)

            # Step 5: Check size limits (1M vertices = 3M floats)
            vertex_count = len(mesh["vertices"]) // 3
            if vertex_count > 1_000_000:
                raise OversizedGeometryError(vertex_count)

            # Step 6: Calculate optimal camera position
            cam_position, cam_target = calculate_camera_position(mesh)
            self.camera_position = cam_position
            self.camera_target = cam_target

            # Step 7: Store in traitlet for sync to frontend
            self.mesh_data = mesh

        except (InvalidObjectError, TessellationError, OversizedGeometryError) as e:
            # Store error message for frontend display
            self.error_message = str(e)
            raise

    def _repr_mimebundle_(self, **kwargs):
        """
        Return mimebundle for rich display in marimo and Jupyter notebooks.

        This method enables automatic widget rendering when the CADViewer
        instance is the last expression in a notebook cell.

        Args:
            **kwargs: Passed to parent's _repr_mimebundle_ (include, exclude, etc.)

        Returns:
            Dictionary with mimetype keys and display data values
        """
        # Delegate to anywidget's built-in mimebundle generation
        # This returns application/vnd.jupyter.widget-view+json for proper rendering
        return super()._repr_mimebundle_(**kwargs)
