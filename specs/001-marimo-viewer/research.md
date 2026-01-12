# Research: Marimo Notebook Viewer Integration

**Feature**: 001-marimo-viewer  
**Created**: 2026-01-11  
**Status**: Complete

## Research Objectives

1. Understand anywidget specification and marimo integration patterns
2. Evaluate three-cad-viewer API and integration approach
3. Determine ocp-vscode usage for geometry conversion
4. Identify build123d object detection and serialization strategy
5. Assess performance considerations for widget bundle size

## Decision 1: anywidget Integration Pattern

**Decision**: Use anywidget's `_repr_mimebundle_` protocol for automatic display in marimo

**Rationale**:
- Marimo (like Jupyter) supports rich display via `_repr_mimebundle_()` method
- anywidget provides `AnyWidget` base class that implements this protocol
- When cell returns object with `_repr_mimebundle_`, marimo automatically renders widget
- No manual `display()` call needed - meets FR-001 automatic display requirement

**Alternatives Considered**:
- Manual display function: Rejected - requires explicit user action, violates auto-display requirement
- Monkey-patching build123d classes: Rejected - invasive, breaks if build123d updates, violates clean integration

**Implementation Approach**:
```python
# User's notebook code (simplified conceptual example)
from build123d import Box
from anywidget_cad_viewer import CADViewer

box = Box(1, 1, 1)
# Widget detects build123d object and displays automatically
CADViewer(box)  # This returns widget with _repr_mimebundle_
```

## Decision 2: three-cad-viewer Integration

**Decision**: Bundle three-cad-viewer as ES module in widget's index.js

**Rationale**:
- three-cad-viewer is designed for web-based CAD visualization with Three.js
- Provides production-ready camera controls, lighting, and CAD-specific rendering
- Bernhard-42's library - proven in ocp-vscode ecosystem
- Handles tessellated geometry from OCP/OpenCascade format

**Alternatives Considered**:
- Raw Three.js: Rejected - would require reimplementing camera controls, lighting, tessellation display
- Other CAD viewers: Rejected - three-cad-viewer is purpose-built for OCP geometry

**Integration Pattern**:
- Import three-cad-viewer in widget JavaScript
- Initialize viewer in widget's `render()` method
- Pass tessellated geometry from Python to JavaScript via widget model
- three-cad-viewer handles all Three.js scene management

## Decision 3: ocp-vscode for Geometry Processing

**Decision**: Use ocp-vscode's tessellation functions to convert build123d objects to mesh data

**Rationale**:
- ocp-vscode 3.0.1+ already in dependencies (pyproject.toml)
- Provides `tessellate()` function that converts OCP shapes to triangulated meshes
- Outputs format compatible with three-cad-viewer expectations
- Handles edge tessellation, face triangulation, normals, colors

**Alternatives Considered**:
- Direct OCP tessellation: Rejected - ocp-vscode abstracts complexity, provides proven implementation
- Build123d's own export: Rejected - build123d focuses on modeling, not visualization tessellation

**Geometry Pipeline**:
1. User creates build123d object (e.g., `Box(1, 1, 1)`)
2. build123d object wraps OCP/OpenCascade `TopoDS_Shape`
3. Extract shape: `shape = build123d_obj.wrapped` or similar
4. Tessellate with ocp-vscode: `mesh_data = tessellate(shape, quality=0.1)`
5. Serialize mesh data to JSON for JavaScript
6. JavaScript passes to three-cad-viewer for rendering

## Decision 4: Build123d Object Detection

**Decision**: Check for `wrapped` attribute and OCP type to identify build123d objects

**Rationale**:
- build123d objects wrap OpenCascade shapes with `.wrapped` attribute
- Can check `isinstance(obj.wrapped, TopoDS_Shape)` or similar
- Avoids hard dependency on specific build123d version

**Alternatives Considered**:
- Check for specific build123d class names: Rejected - brittle across versions
- Require explicit type annotation: Rejected - reduces ease of use

**Detection Logic**:
```python
def is_build123d_object(obj):
    # Check for wrapped OCP shape
    return hasattr(obj, 'wrapped') and hasattr(obj.wrapped, '__class__') and 'TopoDS' in str(type(obj.wrapped))
```

## Decision 5: Widget Bundle Size Optimization

**Decision**: Use ESBuild for JavaScript bundling with tree-shaking and minification

**Rationale**:
- anywidget recommends ESBuild for fast bundling
- Tree-shaking removes unused three-cad-viewer code
- Minification compresses JavaScript
- Target <2MB compressed bundle (constitution requirement)

**Alternatives Considered**:
- Webpack: Rejected - slower build times, more complex config
- No bundling: Rejected - CDN dependencies unreliable offline

**Bundle Strategy**:
- Inline three-cad-viewer (don't CDN)
- Tree-shake unused Three.js modules
- Minify with terser
- Compress with gzip/brotli for distribution

## Decision 6: Geometry Data Transfer Format

**Decision**: Use JSON-serialized mesh data with vertices, indices, normals, colors

**Rationale**:
- anywidget's model syncing supports JSON data
- ocp-vscode tessellation output is JSON-compatible
- three-cad-viewer expects BufferGeometry-compatible format
- Avoids binary serialization complexity for MVP

**Alternatives Considered**:
- Binary format (e.g., glTF): Rejected for MVP - added complexity, optimize later if needed
- Raw OCP shape: Rejected - can't serialize across Python/JavaScript boundary

**Data Format**:
```javascript
{
  "vertices": [x1, y1, z1, x2, y2, z2, ...],
  "indices": [i1, i2, i3, ...],
  "normals": [nx1, ny1, nz1, ...],
  "colors": [r1, g1, b1, ...] // optional
}
```

## Decision 7: Multiple Viewer Instance Management

**Decision**: Each widget instance is independent with own Three.js scene

**Rationale**:
- Satisfies FR-008: independent viewer instances per cell
- Simpler state management - no global scene coordination
- Follows anywidget pattern: each widget is self-contained
- Memory overhead acceptable for typical usage (5-10 instances)

**Alternatives Considered**:
- Shared Three.js renderer: Rejected - complex lifecycle management, not worth optimization

## Decision 8: Performance Optimization Strategy

**Decision**: Implement adaptive quality tessellation based on vertex count

**Rationale**:
- Simple objects (<1000 vertices): High quality tessellation (quality=0.05)
- Medium objects (1000-10,000): Medium quality (quality=0.1)
- Large objects (>10,000): Low quality (quality=0.2) or prompt user

**Alternatives Considered**:
- Fixed quality: Rejected - either poor quality or poor performance
- No limits: Rejected - violates performance constraints FR-012, FR-013

## Dependencies Summary

**Python Dependencies**:
- anywidget: Widget framework (required)
- ocp-vscode: Tessellation and OCP handling (already present)
- build123d: User's modeling library (peer dependency, not bundled)

**JavaScript Dependencies** (bundled):
- three-cad-viewer: CAD visualization
- three: Three.js (three-cad-viewer dependency)

**No New Python Dependencies**: All required dependencies either present or standard anywidget dependencies.

## Open Questions & Risks

**Resolved**:
1. How to auto-display in marimo? → Use anywidget's `_repr_mimebundle_` protocol
2. Geometry format? → ocp-vscode tessellation to JSON
3. Bundle size concerns? → ESBuild tree-shaking, target <2MB

**Remaining Risks**:
1. three-cad-viewer version compatibility with ocp-vscode output format (mitigated: both from bernhard-42)
2. Performance for very large assemblies (>50,000 vertices) - may need progressive loading (future enhancement)
3. Marimo's widget lifecycle management details (test during implementation)

## Next Steps (Phase 1)

1. Create data-model.md: Document mesh data structure, widget state model
2. Create contracts/: Define widget Python API, JavaScript model schema
3. Create quickstart.md: Example marimo notebook usage
4. Re-validate Constitution Check gates
