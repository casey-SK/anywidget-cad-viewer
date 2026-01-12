# Implementation Plan: Marimo Notebook Viewer Integration

**Branch**: `001-marimo-viewer` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-marimo-viewer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create an anywidget-based CAD viewer that automatically displays build123d objects in marimo notebooks. The viewer leverages three-cad-viewer for 3D rendering, ocp_vscode for OCP geometry handling, and anywidget for marimo/Jupyter integration. When users execute cells containing build123d objects, the viewer automatically renders them with interactive 3D controls (rotate, zoom, pan) at 60fps for typical CAD models.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**:
- anywidget (widget framework for marimo/Jupyter integration)
- ocp-vscode 3.0.1+ (OCP geometry handling and tessellation)
- three-cad-viewer (Three.js-based 3D rendering)
- build123d (CAD modeling library - user dependency, not bundled)

**Storage**: N/A (stateless widget, geometry passed from notebook cells)  
**Testing**: pytest for Python integration tests, manual visual verification for rendering  
**Target Platform**: Web browsers with WebGL support (via marimo notebooks)  
**Project Type**: Single Python package with JavaScript widget bundle  
**Performance Goals**:
- Widget initialization: <500ms for objects <1000 vertices
- Interactive rendering: 60fps for objects <10,000 vertices
- Memory overhead: <100MB per widget instance

**Constraints**:
- Widget bundle size: <2MB compressed
- Browser compatibility: Modern browsers with WebGL 1.0+
- No server-side rendering (pure client-side widget)
- Must work offline after initial widget load

**Scale/Scope**:
- Single widget type (CAD viewer)
- Support all build123d geometric primitives and boolean operations
- Multiple concurrent widget instances per notebook
- Typical usage: 5-10 viewer instances per notebook session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Before Phase 0 Research**:
- [x] Feature designed as anywidget component (Principle I: Widget-First Architecture)
  - Widget wraps three-cad-viewer with anywidget spec for marimo/Jupyter compatibility
- [x] Build123d integration requirements identified (Principle II: Build123d Integration)
  - Must handle all build123d primitives, boolean ops, assemblies, colors/materials
- [x] New dependencies justified in plan (Principle III: Minimal Dependencies)
  - anywidget: Required for marimo integration (core framework)
  - ocp-vscode: Already in pyproject.toml, provides OCP geometry handling
  - three-cad-viewer: Bernhard-42's library, proven Three.js CAD renderer
  - All dependencies align with OCP ecosystem and project requirements
- [x] Test requirements clarified if needed (Principle IV: Test When It Matters)
  - Tests not explicitly requested in spec
  - Will use manual verification for rendering (visual correctness)
  - Integration tests for geometry conversion if transformation logic is complex
- [x] Notebook UX considered in user scenarios (Principle V: Notebook-Centric Experience)
  - Spec prioritizes automatic display in marimo cells
  - Interactive controls embedded in widget
  - Error messages visible in cell output
- [x] No emojis in specification or planning documents (Principle VI: No Emojis)
  - Verified: No emojis in spec.md or plan.md

**After Phase 1 Design**:
- [x] Widget API contract defined in contracts/
  - Python API: CADViewer class with quality, display options documented
  - JavaScript API: Model/View interfaces with MeshData schema
  - See: contracts/widget-api.md
- [x] Build123d object types supported documented
  - All primitives: Box, Sphere, Cylinder, Cone, Torus
  - Boolean operations: union, difference, intersection
  - Assemblies and compounds
  - See: data-model.md and contracts/widget-api.md
- [x] Dependencies reviewed and justified
  - anywidget: Required for widget framework (core)
  - ocp-vscode: Already present, OCP tessellation (Principle III compliant)
  - three-cad-viewer: Bernhard-42 library, proven CAD renderer (Principle III compliant)
  - No new Python dependencies beyond anywidget
- [x] Test strategy documented if tests required
  - Manual visual verification primary method (per Principle IV)
  - Integration tests for geometry conversion if complex
  - See: research.md
- [x] Example notebook usage in quickstart.md
  - Complete marimo notebook examples
  - Common patterns and troubleshooting
  - See: quickstart.md
- [x] All design artifacts emoji-free (Principle VI: No Emojis)
  - Verified: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
anywidget_cad_viewer/
├── __init__.py              # Package entry point, widget export
├── viewer.py                # Main CADViewer anywidget class
├── geometry.py              # Build123d to OCP geometry conversion
├── static/
│   ├── index.js             # Widget JavaScript (three-cad-viewer integration)
│   ├── index.css            # Widget styles
│   └── assets/              # Bundled three-cad-viewer assets
└── py.typed                 # Type hint marker

tests/
├── integration/
│   ├── test_build123d_primitives.py
│   └── test_marimo_integration.py
└── unit/
    └── test_geometry_conversion.py

examples/
└── marimo_quickstart.py     # Example marimo notebook
```

**Structure Decision**: Single Python package structure (Option 1) is appropriate because:
- This is a pure Python package with embedded JavaScript widget
- No separate backend/frontend split needed (widget is self-contained)
- JavaScript bundling happens at build time, not runtime
- Follows standard anywidget package pattern

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
