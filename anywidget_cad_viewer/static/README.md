# three-cad-viewer Integration Notes

## Overview

three-cad-viewer is a Three.js-based CAD visualization library by bernhard-42, designed for OCP/OpenCascade geometry rendering in web browsers. It's used in ocp-vscode and jupyter-cadquery projects.

## Package Information

- **npm package**: `three-cad-viewer`
- **Repository**: https://github.com/bernhard-42/three-cad-viewer
- **Dependencies**: three.js (peer dependency)

## Key API Components

### 1. Viewer Initialization

```javascript
import { Viewer } from 'three-cad-viewer';

const viewer = new Viewer(containerElement, {
    theme: 'light',          // or 'dark'
    control: 'orbit',        // camera controls
    normalLen: 0,           // normal vector length (0 = hidden)
    panSpeed: 0.5,
    rotateSpeed: 1.0,
    zoomSpeed: 0.5,
    ambient: 0.5,           // ambient light intensity
    axes: true,             // show coordinate axes
    grid: [false, false, false], // grid on [xy, xz, yz] planes
    ortho: false,           // orthographic vs perspective
    transparent: false,
    blackEdges: false,
    ticks: 10              // axis tick marks
});
```

### 2. Adding Geometry

```javascript
// Add mesh data from ocp-vscode tessellation
viewer.addShape({
    id: 'shape-001',
    shape: {
        vertices: Float32Array,  // [x1,y1,z1, x2,y2,z2, ...]
        triangles: Uint32Array,  // [i1,i2,i3, ...]
        normals: Float32Array,   // [nx1,ny1,nz1, ...]
        edges: [[x1,y1,z1,x2,y2,z2], ...] // optional edge lines
    },
    color: [r, g, b],       // RGB 0-1 range
    alpha: 1.0
});
```

### 3. Camera Controls

```javascript
// Reset camera to fit all geometry
viewer.render({
    position: null,  // null = auto-calculate from bounding box
    target: [0, 0, 0],
    zoom: 1.0
});

// Get current camera state
const cameraState = viewer.getCameraState();
// Returns: { position: [x,y,z], target: [x,y,z], zoom: number }

// Set camera explicitly
viewer.setCameraState({
    position: [10, 10, 10],
    target: [0, 0, 0],
    zoom: 1.5
});
```

### 4. Interaction Events

```javascript
// Listen for camera changes (user interaction)
viewer.on('cameraChange', (state) => {
    console.log('Camera moved', state);
});

// Listen for selection events
viewer.on('select', (shapeId) => {
    console.log('Selected shape:', shapeId);
});
```

### 5. Cleanup

```javascript
// Dispose viewer and free resources
viewer.dispose();
```

## Integration Pattern for anywidget

### Initialization Flow

1. anywidget creates widget container (div)
2. Initialize three-cad-viewer with container
3. Add mesh data from Python model
4. Setup camera auto-fit to geometry bounds
5. Enable orbit controls
6. Sync camera state back to Python on interaction

### Data Format Mapping

**ocp-vscode tessellation output** → **three-cad-viewer input**:

```javascript
// From Python (ocp-vscode tessellate())
const pythonMeshData = {
    vertices: [x1, y1, z1, ...],  // flat array
    indices: [i1, i2, i3, ...],   // triangle indices
    normals: [nx1, ny1, nz1, ...],
    edges: [[x1,y1,z1,x2,y2,z2], ...],
    colors: [r1, g1, b1, ...]     // optional
};

// Convert to three-cad-viewer format
const shape = {
    vertices: new Float32Array(pythonMeshData.vertices),
    triangles: new Uint32Array(pythonMeshData.indices),
    normals: new Float32Array(pythonMeshData.normals),
    edges: pythonMeshData.edges  // already in correct format
};
```

## Performance Considerations

- three-cad-viewer handles WebGL context management
- Automatic LOD (level of detail) for large geometries
- Edge rendering can be toggled for performance
- Supports multiple shapes per viewer instance

## Browser Compatibility

- Requires WebGL 1.0 or higher
- Modern browsers: Chrome 90+, Firefox 88+, Safari 15+, Edge 90+

## References

- three-cad-viewer documentation: https://github.com/bernhard-42/three-cad-viewer
- ocp-vscode integration example: https://github.com/bernhard-42/vscode-ocp-cad-viewer
- Three.js docs: https://threejs.org/docs/
