# Widget API Contract: CADViewer

**Version**: 1.0.0  
**Feature**: 001-marimo-viewer  
**Created**: 2026-01-11

## Python API

### Class: CADViewer

**Module**: `anywidget_cad_viewer.viewer`

**Constructor**:
```python
CADViewer(
    obj: Any,
    *,
    quality: float = 0.1,
    show_edges: bool = True,
    show_axes: bool = True,
    background_color: str = "#F0F0F0",
    width: int = 800,
    height: int = 600
) -> CADViewer
```

**Parameters**:
- `obj` (required): build123d object to visualize
  - Must have `wrapped` attribute containing OCP `TopoDS_Shape`
  - Examples: `Box(1, 1, 1)`, `Sphere(2)`, boolean operation results
  
- `quality` (optional): Tessellation quality factor
  - Type: float
  - Range: 0.01 (highest quality) to 1.0 (lowest quality)
  - Default: 0.1 (balanced)
  - Lower values = more triangles, smoother surfaces, slower performance
  
- `show_edges` (optional): Display edge lines
  - Type: bool
  - Default: True
  - Purpose: Shows sharp edges for CAD-style visualization
  
- `show_axes` (optional): Display coordinate axes
  - Type: bool
  - Default: True
  - Purpose: Shows X (red), Y (green), Z (blue) axes at origin
  
- `background_color` (optional): Canvas background color
  - Type: str (hex color)
  - Default: "#F0F0F0" (light gray)
  - Format: "#RRGGBB"
  
- `width` (optional): Widget width in pixels
  - Type: int
  - Default: 800
  - Range: 200-2000
  
- `height` (optional): Widget height in pixels
  - Type: int
  - Default: 600
  - Range: 200-2000

**Returns**: CADViewer widget instance

**Raises**:
- `ValueError`: If `obj` is not a build123d-compatible object
- `ValueError`: If quality is outside 0.01-1.0 range
- `RuntimeError`: If tessellation fails

**Example Usage**:
```python
from build123d import Box, Sphere
from anywidget_cad_viewer import CADViewer

# Basic usage (auto-displays in marimo cell)
box = Box(10, 20, 30)
CADViewer(box)

# Custom quality and display options
sphere = Sphere(5)
CADViewer(sphere, quality=0.05, show_edges=False, background_color="#FFFFFF")

# Boolean operations
from build123d import subtract
result = subtract(Box(10, 10, 10), Cylinder(3, 15))
CADViewer(result)
```

### Widget Properties (Traitlets)

**model_name**: `"CADViewerModel"`
- Widget model name for JavaScript synchronization

**view_name**: `"CADViewerView"`
- Widget view name for JavaScript rendering

**mesh_data**: `Dict`
- Synchronized property containing tessellated geometry
- Type: dict with keys `vertices`, `indices`, `normals`, `colors`, `edges`
- Auto-populated on widget creation
- Read-only from Python side after initialization

**camera_state**: `Dict`
- Current camera position and target
- Type: dict with keys `position: [x, y, z]`, `target: [x, y, z]`
- Updated when user interacts with 3D view
- Can be read from Python to save/restore views

**error_message**: `Unicode`
- Error message if visualization fails
- Type: str or None
- Empty string if no error

## JavaScript API

### Model: CADViewerModel

**Extends**: `anywidget.AnyModel`

**Synchronized Properties**:
```typescript
interface CADViewerModel {
    mesh_data: MeshData;
    camera_state: CameraState;
    show_edges: boolean;
    show_axes: boolean;
    background_color: string;
    error_message: string;
}

interface MeshData {
    vertices: number[];      // Flat array: [x1, y1, z1, x2, y2, z2, ...]
    indices: number[];       // Triangle indices: [i1, i2, i3, ...]
    normals: number[];       // Normal vectors: [nx1, ny1, nz1, ...]
    colors?: number[];       // Optional RGB: [r1, g1, b1, ...]
    edges?: number[][];      // Optional edge lines: [[x1,y1,z1,x2,y2,z2], ...]
}

interface CameraState {
    position: [number, number, number];
    target: [number, number, number];
}
```

### View: CADViewerView

**Extends**: `anywidget.AnyView`

**Methods**:

**render()**:
- Called by anywidget when widget displayed
- Initializes three-cad-viewer instance
- Creates Three.js scene with geometry
- Sets up camera controls
- Returns: HTMLElement containing canvas

**remove()**:
- Called when widget removed from DOM
- Disposes Three.js resources
- Removes event listeners

**model_changed()**:
- Called when model properties update
- Re-renders geometry if mesh_data changed
- Updates camera if camera_state changed

## Widget Lifecycle

**1. Initialization** (Python):
```python
viewer = CADViewer(build123d_obj)
# - Validates object has .wrapped attribute
# - Tessellates geometry via ocp-vscode
# - Populates mesh_data property
# - Calculates default camera position
```

**2. Display** (marimo/Jupyter):
```python
# Marimo auto-displays last cell expression
CADViewer(obj)
# - Calls _repr_mimebundle_() internally
# - Returns anywidget display data
# - Marimo renders widget in output cell
```

**3. Render** (JavaScript):
```javascript
render() {
    // - Get mesh_data from model
    // - Convert to Three.js BufferGeometry
    // - Initialize three-cad-viewer
    // - Create scene, camera, lights
    // - Start animation loop
    // - Attach to DOM
}
```

**4. Interaction** (User):
```
User drags mouse
→ three-cad-viewer orbit controls
→ Update camera position
→ Sync camera_state to model
→ Python can read updated camera
```

**5. Update** (Cell re-execution):
```python
# User modifies object and re-runs cell
box = Box(5, 5, 5)  # Changed dimensions
CADViewer(box)
# - New widget instance created
# - Old widget disposed
# - New geometry tessellated
# - Displayed in same output cell
```

**6. Cleanup** (Widget destroyed):
```javascript
remove() {
    // - Dispose Three.js geometries
    // - Dispose materials and textures
    // - Remove canvas from DOM
    // - Clear event listeners
}
```

## Error Handling Contract

**Python Side**:
```python
# Error 1: Invalid object type
CADViewer("not a build123d object")
# Raises: ValueError("Object must have 'wrapped' attribute containing OCP shape")

# Error 2: Tessellation failure
CADViewer(malformed_shape)
# Sets error_message property, displays error in widget

# Error 3: Out of range quality
CADViewer(box, quality=5.0)
# Raises: ValueError("quality must be between 0.01 and 1.0")
```

**JavaScript Side**:
```javascript
// Error 1: Invalid mesh data
model.mesh_data = { vertices: [1, 2] };  // Invalid length
// Displays error: "Invalid geometry data: vertices length must be multiple of 3"

// Error 2: WebGL not available
// Displays error: "WebGL required for 3D visualization"

// Error 3: Geometry too large
// Displays warning: "Performance may be degraded for large models (50000+ vertices)"
```

## Performance Guarantees

**Initialization Time** (FR-012):
- Objects <1000 vertices: <500ms from CADViewer() call to display
- Includes: Tessellation, JSON serialization, JavaScript parsing, Three.js setup

**Interactive Frame Rate** (FR-013):
- Objects <10,000 vertices: 60fps during rotation/zoom/pan
- Measured: Animation loop maintains 16.67ms per frame

**Memory Usage**:
- Per widget instance: <100MB overhead
- Includes: Three.js library, three-cad-viewer, geometry buffers

## Compatibility Requirements

**Python**:
- Python 3.13+
- anywidget 0.9.0+
- ocp-vscode 3.0.1+

**JavaScript/Browser**:
- WebGL 1.0 or higher
- ES6 module support
- Modern browsers: Chrome 90+, Firefox 88+, Safari 15+, Edge 90+

**Notebook Environments**:
- marimo 0.1.0+
- Jupyter Notebook 6.0+
- JupyterLab 3.0+
- Google Colab
- VS Code Jupyter extension

## Data Size Limits

**Recommended Limits**:
- Vertices: <50,000 per object (for 60fps)
- Triangles: <100,000 per object
- JSON payload: <5MB per widget

**Hard Limits**:
- Vertices: 1,000,000 (error if exceeded)
- JSON payload: 50MB (browser limitation)

## Extensibility Points

**Future Enhancements** (not in MVP):
- Custom materials/textures
- Animation support
- Selection/measurement tools
- Export to STL/glTF
- Multiple objects per widget
- Layer visibility controls
- Progressive loading for large assemblies

These would extend the contract without breaking existing usage.
