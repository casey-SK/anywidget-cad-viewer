# Data Model: Marimo Notebook Viewer Integration

**Feature**: 001-marimo-viewer  
**Created**: 2026-01-11  
**Status**: Complete

## Overview

The CAD viewer widget maintains a simple data model focused on geometry visualization. There are no persistent entities or database requirements. All data flows from notebook cell execution (build123d objects) through the widget to the browser-based Three.js renderer.

## Entity: MeshData

**Description**: Tessellated mesh representation of a build123d CAD object, suitable for Three.js rendering.

**Attributes**:
- `vertices`: Array of floating point numbers (x, y, z coordinates flattened)
  - Format: `[x1, y1, z1, x2, y2, z2, ...]`
  - Validation: Length must be multiple of 3
  - Source: ocp-vscode tessellation output

- `indices`: Array of integers (triangle vertex indices)
  - Format: `[i1, i2, i3, ...]` where each triplet defines a triangle
  - Validation: Length must be multiple of 3, all indices < len(vertices)/3
  - Source: ocp-vscode face triangulation

- `normals`: Array of floating point numbers (normal vectors)
  - Format: `[nx1, ny1, nz1, nx2, ny2, nz2, ...]`
  - Validation: Length must equal vertices length
  - Source: ocp-vscode computed normals

- `colors`: Optional array of RGB values (0-1 range)
  - Format: `[r1, g1, b1, r2, g2, b2, ...]`
  - Validation: If present, length must equal vertices length
  - Source: build123d object color/material properties
  - Default: `null` (use default gray material)

- `edges`: Optional array of edge line segments
  - Format: `[[x1, y1, z1, x2, y2, z2], ...]`
  - Source: ocp-vscode edge tessellation
  - Purpose: Render sharp edges for CAD visualization

**Relationships**: None (stateless, ephemeral data structure)

**Lifecycle**:
1. Created when widget receives build123d object
2. Serialized to JSON for Python-to-JavaScript transfer
3. Deserialized in JavaScript, converted to Three.js BufferGeometry
4. Discarded when cell re-executed or widget destroyed

**Validation Rules**:
- vertices array length % 3 == 0
- indices array length % 3 == 0
- All index values < (len(vertices) / 3)
- If normals present: len(normals) == len(vertices)
- If colors present: len(colors) == len(vertices)

## Entity: WidgetState

**Description**: anywidget model state that syncs between Python and JavaScript.

**Attributes**:
- `mesh_data`: MeshData object (JSON-serialized)
  - Validation: Must conform to MeshData schema
  - Update trigger: Full re-render of geometry

- `camera_position`: Optional array `[x, y, z]`
  - Stores camera position for view persistence
  - Updated from JavaScript when user interacts
  - Default: `null` (auto-calculated from bounding box)

- `camera_target`: Optional array `[x, y, z]`
  - Camera look-at target
  - Default: `[0, 0, 0]`

- `background_color`: Optional hex color string
  - Format: `"#RRGGBB"`
  - Default: `"#F0F0F0"` (light gray)

- `show_edges`: Boolean flag
  - Whether to render edge lines
  - Default: `true`

- `show_axes`: Boolean flag
  - Whether to render coordinate axes
  - Default: `true`

- `error_message`: Optional string
  - Displayed when tessellation or rendering fails
  - Default: `null`

**State Transitions**:
1. **Initial**: Widget created with build123d object
   - mesh_data populated from tessellation
   - camera/display settings use defaults
   
2. **Updated**: User re-executes cell with modified object
   - mesh_data replaced with new tessellation
   - camera position optionally preserved
   
3. **Interaction**: User rotates/zooms view
   - camera_position and camera_target updated
   - mesh_data unchanged
   
4. **Error**: Tessellation or rendering fails
   - error_message set with diagnostic info
   - mesh_data may be null or partial

## Entity: Build123dObject (External)

**Description**: User's CAD model created with build123d library. Not owned by this widget, but defines input contract.

**Expected Interface**:
- `wrapped`: Attribute containing OCP `TopoDS_Shape`
- `color`: Optional `Color` object or tuple
- `label`: Optional string for identification

**Detection Logic**:
```python
def is_build123d_compatible(obj):
    # Check for wrapped OCP shape attribute
    if not hasattr(obj, 'wrapped'):
        return False
    
    # Check if wrapped is TopoDS type
    wrapped_type = type(obj.wrapped).__name__
    return 'TopoDS' in wrapped_type
```

## Data Flow Diagram

```
Notebook Cell
    |
    | (creates)
    v
Build123d Object
    |
    | (detects via _repr_mimebundle_)
    v
CADViewer Widget (Python)
    |
    | (tessellates via ocp-vscode)
    v
MeshData (JSON)
    |
    | (syncs via anywidget model)
    v
Widget JavaScript
    |
    | (converts to Three.js)
    v
BufferGeometry
    |
    | (renders via three-cad-viewer)
    v
Three.js Scene → Canvas
```

## Geometry Conversion Pipeline

**Step 1: Extract OCP Shape**
```python
Input: build123d object (e.g., Box(1, 1, 1))
Output: OCP TopoDS_Shape
Logic: shape = build123d_obj.wrapped
```

**Step 2: Tessellate**
```python
Input: TopoDS_Shape
Output: Tessellation dict with vertices, faces, edges, normals
Logic: ocp_vscode.tessellate(shape, quality=0.1, angular_tolerance=0.1)
```

**Step 3: Convert to MeshData**
```python
Input: Tessellation dict
Output: MeshData JSON
Logic: Flatten arrays, extract colors if present, validate schema
```

**Step 4: Serialize**
```python
Input: MeshData object
Output: JSON string
Logic: json.dumps(mesh_data)
```

**Step 5: JavaScript Conversion**
```javascript
Input: MeshData JSON (from widget model)
Output: Three.js BufferGeometry
Logic:
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geometry.setIndex(indices);
  geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  if (colors) geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
```

## Error Handling States

**Error State 1: Invalid Object**
- Trigger: Object passed to widget lacks `wrapped` attribute
- Error Message: "Cannot visualize object: not a build123d CAD object"
- Widget Display: Shows error text in red box

**Error State 2: Tessellation Failure**
- Trigger: ocp-vscode tessellation raises exception
- Error Message: "Failed to tessellate geometry: {exception_message}"
- Widget Display: Shows error text with technical details

**Error State 3: Oversized Geometry**
- Trigger: Tessellation produces >100,000 vertices
- Error Message: "Geometry too complex ({N} vertices). Consider simplifying or using lower quality setting."
- Widget Display: Warning banner, option to proceed anyway

**Error State 4: WebGL Not Available**
- Trigger: Browser lacks WebGL support (detected in JavaScript)
- Error Message: "WebGL required for 3D visualization. Please use a modern browser."
- Widget Display: Error text with browser upgrade suggestion

## Performance Considerations

**Tessellation Quality Mapping**:
- Simple objects (<1000 vertices expected): quality=0.05 (high detail)
- Medium objects (1000-10,000 vertices): quality=0.1 (balanced)
- Large objects (>10,000 vertices): quality=0.2 (performance optimized)

**Memory Estimates**:
- Typical primitive (Box, Cylinder): ~500 vertices, ~10KB JSON
- Boolean operation result: ~2000 vertices, ~40KB JSON
- Complex assembly (10 parts): ~20,000 vertices, ~400KB JSON
- Widget overhead: ~50MB (Three.js + three-cad-viewer)

**Per-Instance Budget**:
- Target: <100MB per widget
- Breakdown: 50MB libs + 50MB geometry data
- Allows ~5-10 complex assemblies per notebook session

## Schema Validation

**Python Side**:
```python
from typing import TypedDict, Optional

class MeshData(TypedDict):
    vertices: list[float]
    indices: list[int]
    normals: list[float]
    colors: Optional[list[float]]
    edges: Optional[list[list[float]]]

def validate_mesh_data(data: MeshData) -> None:
    assert len(data['vertices']) % 3 == 0
    assert len(data['indices']) % 3 == 0
    assert len(data['normals']) == len(data['vertices'])
    if data.get('colors'):
        assert len(data['colors']) == len(data['vertices'])
```

**JavaScript Side**:
```javascript
function validateMeshData(data) {
    if (!data.vertices || data.vertices.length % 3 !== 0) {
        throw new Error('Invalid vertices array');
    }
    if (!data.indices || data.indices.length % 3 !== 0) {
        throw new Error('Invalid indices array');
    }
    // Additional checks...
}
```
