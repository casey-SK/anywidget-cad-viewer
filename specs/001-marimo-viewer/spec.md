# Feature Specification: Marimo Notebook Viewer Integration

**Feature Branch**: `001-marimo-viewer`  
**Created**: 2026-01-11  
**Status**: Draft  
**Input**: User description: "the ocp_vscode viewer is shown when a build123d code block is run in marimo."

## User Scenarios & Testing

### User Story 1 - Display Build123d Objects in Marimo (Priority: P1)

A data scientist or engineer working in a marimo notebook writes build123d code to create a CAD model. When they execute the cell containing build123d object creation code, the interactive 3D viewer automatically appears inline in the notebook output, showing the generated geometry.

**Why this priority**: This is the core value proposition of the entire project. Without automatic visualization in marimo, the tool has no purpose. Engineers need immediate visual feedback when designing CAD models in notebooks.

**Independent Test**: Can be fully tested by creating a marimo notebook with a simple build123d shape (e.g., `Box(1, 1, 1)`) and executing it. Success means the viewer renders inline without manual invocation.

**Acceptance Scenarios**:

1. **Given** a marimo notebook is open, **When** user executes a cell that creates a build123d `Box` object, **Then** the ocp_vscode viewer displays the box with rotation, zoom, and pan controls
2. **Given** a marimo notebook with multiple cells, **When** user executes multiple cells each creating different build123d objects, **Then** each cell output shows its corresponding object in a separate viewer instance
3. **Given** a cell that creates a build123d object, **When** user re-executes the cell after modifying parameters, **Then** the viewer updates to show the modified geometry
4. **Given** a marimo notebook, **When** user executes a cell with no build123d objects, **Then** no viewer appears (normal output behavior)

---

### User Story 2 - Interactive 3D Manipulation (Priority: P2)

After a build123d object is displayed in the viewer, the user can interact with it using mouse or touch controls to rotate, zoom, and pan the view. This allows thorough inspection of the geometry from all angles.

**Why this priority**: Static 2D renderings are insufficient for CAD work. Engineers need to rotate models to verify features, check clearances, and understand spatial relationships. This is essential for practical use but secondary to basic display.

**Independent Test**: Display any build123d object in marimo, then use mouse drag to rotate, scroll wheel to zoom, and right-click-drag to pan. Verify smooth interaction at 60fps for objects under 10,000 vertices.

**Acceptance Scenarios**:

1. **Given** a viewer displaying a build123d object, **When** user clicks and drags on the viewer, **Then** the object rotates smoothly around its center following the mouse movement
2. **Given** a viewer displaying an object, **When** user scrolls the mouse wheel, **Then** the camera zooms in or out maintaining the center point
3. **Given** a viewer displaying an object, **When** user right-clicks and drags, **Then** the camera pans across the scene
4. **Given** a viewer with an object, **When** user interacts with controls, **Then** the view updates at 60fps without frame drops for models under 10,000 vertices

---

### User Story 3 - Multiple Object Types Support (Priority: P3)

The viewer correctly displays all standard build123d geometric primitives and assemblies, including boxes, cylinders, spheres, boolean operations, sketches, and compound assemblies.

**Why this priority**: Comprehensive geometry support is necessary for real-world CAD work, but basic primitives (P1) provide initial value. This extends the tool to handle complex designs.

**Independent Test**: Create a marimo notebook with cells containing each build123d primitive type and boolean operations. Execute all cells and verify each renders correctly with appropriate visual fidelity.

**Acceptance Scenarios**:

1. **Given** a cell creating a build123d `Cylinder`, **When** executed, **Then** the viewer shows a smooth cylindrical surface with correct dimensions
2. **Given** a cell with boolean operations (union, subtract, intersect), **When** executed, **Then** the viewer shows the resulting combined geometry
3. **Given** a cell creating a build123d assembly with multiple parts, **When** executed, **Then** the viewer shows all parts in their correct relative positions
4. **Given** a cell with a 2D sketch, **When** executed, **Then** the viewer displays the sketch in the XY plane with appropriate rendering

---

### Edge Cases

- What happens when a build123d object creation fails due to invalid parameters?
- How does the viewer handle extremely large models (100,000+ vertices) that may cause performance issues?
- What occurs when a marimo cell output contains both build123d objects and other data (text, plots)?
- How does the system behave when the user rapidly re-executes cells with geometry?
- What happens when build123d objects have custom materials or colors applied?
- How does the viewer handle objects with zero volume or degenerate geometry?

## Requirements

### Functional Requirements

- **FR-001**: Viewer MUST automatically display when a marimo cell execution returns a build123d object
- **FR-002**: Viewer MUST render all standard build123d primitives (Box, Sphere, Cylinder, Cone, Torus)
- **FR-003**: Viewer MUST support boolean operations results (union, difference, intersection)
- **FR-004**: Viewer MUST provide interactive rotation via mouse drag controls
- **FR-005**: Viewer MUST provide zoom controls via mouse wheel or pinch gestures
- **FR-006**: Viewer MUST provide pan controls via right-click drag or touch gestures
- **FR-007**: Viewer MUST render objects with smooth surfaces and appropriate tessellation
- **FR-008**: Viewer MUST display multiple independent viewer instances when multiple cells contain build123d objects
- **FR-009**: Viewer MUST update geometry when a cell is re-executed with modified parameters
- **FR-010**: Viewer MUST preserve build123d object colors and materials when specified
- **FR-011**: Viewer MUST show appropriate error messages when geometry cannot be visualized
- **FR-012**: Viewer MUST initialize within 500ms for objects with fewer than 1000 vertices
- **FR-013**: Viewer MUST maintain 60fps interaction for objects with fewer than 10,000 vertices

### Key Entities

- **Build123d Object**: A CAD geometry object created using build123d library, containing solid, shell, or compound geometry data that needs visualization
- **Viewer Instance**: An embedded ocp_vscode-based 3D visualization widget that appears in marimo notebook cell output, bound to a specific build123d object
- **Notebook Cell**: A marimo code execution unit that may produce build123d objects as output requiring automatic visualization

## Success Criteria

### Measurable Outcomes

- **SC-001**: Engineers can visualize any build123d object by simply executing the cell, with no manual viewer invocation required
- **SC-002**: Viewer appears within 500ms of cell execution completion for simple objects (less than 1000 vertices)
- **SC-003**: Interactive controls (rotate, zoom, pan) respond at 60fps for objects under 10,000 vertices
- **SC-004**: Users can inspect models from any angle with smooth interaction comparable to standalone CAD viewers
- **SC-005**: All standard build123d primitives and boolean operations render correctly with no visual artifacts
- **SC-006**: Multiple cells with different objects each display independent viewer instances without conflicts
- **SC-007**: Viewer updates immediately (under 500ms) when cells are re-executed with modified geometry
- **SC-008**: 95% of build123d objects created in typical engineering workflows render successfully on first attempt

## Assumptions

- Marimo notebook environment supports embedding interactive widgets similar to Jupyter
- OCP_vscode library is already integrated and provides the core rendering capabilities
- Build123d objects follow standard OpenCascade geometry conventions
- Users have modern browsers with WebGL support
- Network connectivity is available for loading widget assets (or assets are bundled)
- Marimo handles widget lifecycle (creation, updates, disposal) automatically
