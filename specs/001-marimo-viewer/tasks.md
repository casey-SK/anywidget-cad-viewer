# Tasks: Marimo Notebook Viewer Integration

**Input**: Design documents from `/specs/001-marimo-viewer/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/widget-api.md

**Tests**: Tests are NOT explicitly requested in the feature specification. Per Constitution Principle IV (Test When It Matters), this feature focuses on manual visual verification. Test tasks are excluded from this implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Project uses single package structure:
- **Source**: `anywidget_cad_viewer/` at repository root
- **Tests**: `tests/` at repository root (manual verification focus)
- **Examples**: `examples/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Python package structure: anywidget_cad_viewer/__init__.py, viewer.py, geometry.py
- [x] T002 Create static assets directory: anywidget_cad_viewer/static/ with index.js, index.css, assets/
- [x] T003 Create tests directory structure: tests/integration/, tests/unit/
- [x] T004 Create examples directory: examples/ with marimo_quickstart.py placeholder
- [x] T005 Add anywidget dependency using uv: uv add anywidget
- [x] T006 Create anywidget_cad_viewer/py.typed marker file for type hints
- [x] T007 Update pyproject.toml with project metadata (description, authors, urls)
- [x] T008 Synchronize uv.lock after dependency additions: uv lock

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Setup JavaScript bundling with ESBuild configuration in package.json
- [x] T010 [P] Configure development dependency group for linting: uv add --group dev ruff
- [x] T011 [P] Configure ruff linting in pyproject.toml (line length, exclude patterns)
- [x] T012 Implement build123d object detection utility function in anywidget_cad_viewer/geometry.py:is_build123d_compatible()
- [x] T013 Research and document three-cad-viewer JavaScript API in anywidget_cad_viewer/static/README.md
- [x] T014 Create MeshData TypedDict schema in anywidget_cad_viewer/geometry.py with validation
- [x] T015 Implement basic error handling framework with custom exceptions in anywidget_cad_viewer/viewer.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Display Build123d Objects in Marimo (Priority: P1) MVP

**Goal**: Automatically display build123d objects with interactive 3D viewer when cells execute in marimo notebooks

**Independent Test**: Create marimo notebook with `Box(1, 1, 1)`, execute cell, verify viewer renders inline with rotation/zoom/pan controls

### Implementation for User Story 1

- [x] T016 [P] [US1] Implement CADViewer anywidget class skeleton in anywidget_cad_viewer/viewer.py with traitlets
- [x] T017 [P] [US1] Implement geometry extraction from build123d in anywidget_cad_viewer/geometry.py:extract_ocp_shape()
- [x] T018 [US1] Integrate OCP BRepMesh tessellation in anywidget_cad_viewer/geometry.py:tessellate_shape()
- [x] T019 [US1] Implement MeshData JSON serialization in anywidget_cad_viewer/geometry.py:serialize_mesh_data()
- [x] T020 [US1] Connect tessellation pipeline to CADViewer widget initialization in anywidget_cad_viewer/viewer.py:__init__()
- [x] T021 [US1] Implement widget _repr_mimebundle_ for automatic marimo display in anywidget_cad_viewer/viewer.py
- [x] T022 [US1] Bundle three-cad-viewer library via CDN imports in anywidget_cad_viewer/static/index.js
- [x] T023 [US1] Implement JavaScript widget render() function in anywidget_cad_viewer/static/index.js
- [x] T024 [US1] Implement JavaScript render() method with Three.js scene setup in anywidget_cad_viewer/static/index.js
- [x] T025 [US1] Convert MeshData to Three.js BufferGeometry in anywidget_cad_viewer/static/index.js:createGeometry()
- [x] T026 [US1] Integrate Three.js OrbitControls for scene rendering in anywidget_cad_viewer/static/index.js
- [x] T027 [US1] Add basic CSS styling for widget canvas in anywidget_cad_viewer/static/index.css
- [x] T028 [US1] Implement widget error display UI in anywidget_cad_viewer/static/index.js
- [x] T029 [US1] Add validation for mesh data schema in anywidget_cad_viewer/geometry.py:validate_mesh_data()
- [x] T030 [US1] Export CADViewer from package __init__ in anywidget_cad_viewer/__init__.py
- [x] T031 [US1] Create marimo quickstart example in examples/marimo_quickstart.py with Box, Sphere, Cylinder
- [x] T032 [US1] Manual verification: Test Box(1,1,1) displays in marimo with rotation/zoom/pan

**Checkpoint**: At this point, User Story 1 should be fully functional - basic primitives render automatically in marimo cells

---

## Phase 4: User Story 2 - Interactive 3D Manipulation (Priority: P2)

**Goal**: Smooth 60fps interaction with orbit controls, zoom, and pan for objects under 10,000 vertices

**Independent Test**: Display Box(10,10,10) in marimo, verify mouse drag rotates, scroll zooms, right-click pans at 60fps

### Implementation for User Story 2

- [x] T033 [P] [US2] Implement orbit controls integration in anywidget_cad_viewer/static/index.js using three-cad-viewer API
- [x] T034 [P] [US2] Add camera state synchronization to Python model in anywidget_cad_viewer/static/index.js:syncCameraState()
- [x] T035 [US2] Implement camera position/target traitlets in anywidget_cad_viewer/viewer.py:camera_state property
- [x] T036 [US2] Add performance monitoring for frame rate in anywidget_cad_viewer/static/index.js:monitorFPS()
- [x] T037 [US2] Implement adaptive quality selection based on vertex count in anywidget_cad_viewer/geometry.py:select_quality()
- [x] T038 [US2] Add animation loop optimization in anywidget_cad_viewer/static/index.js:animate()
- [x] T039 [US2] Implement default camera positioning from bounding box in anywidget_cad_viewer/geometry.py:calculate_camera_position()
- [x] T040 [US2] Add camera controls documentation to quickstart in examples/marimo_quickstart.py
- [x] T041 [US2] Manual verification: Test 60fps interaction with medium complexity object (5000 vertices)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - viewer displays with smooth interactive controls

---

## Phase 5: User Story 3 - Multiple Object Types Support (Priority: P3)

**Goal**: Correctly render all build123d primitives (Box, Sphere, Cylinder, Cone, Torus) and boolean operations

**Independent Test**: Create marimo cells with each primitive type and boolean ops, verify all render correctly

### Implementation for User Story 3

- [x] T042 [P] [US3] Add support for Cylinder tessellation in anywidget_cad_viewer/geometry.py
- [x] T043 [P] [US3] Add support for Sphere tessellation in anywidget_cad_viewer/geometry.py
- [x] T044 [P] [US3] Add support for Cone tessellation in anywidget_cad_viewer/geometry.py
- [x] T045 [P] [US3] Add support for Torus tessellation in anywidget_cad_viewer/geometry.py
- [x] T046 [US3] Add support for boolean operation results (union, subtract, intersect) in anywidget_cad_viewer/geometry.py
- [x] T047 [US3] Add support for Compound/Assembly objects in anywidget_cad_viewer/geometry.py:handle_compound()
- [x] T048 [US3] Add color extraction from build123d objects in anywidget_cad_viewer/geometry.py:extract_colors()
- [x] T049 [US3] Implement color attribute mapping to MeshData in anywidget_cad_viewer/geometry.py
- [x] T050 [US3] Add material color rendering in JavaScript in anywidget_cad_viewer/static/index.js:applyColors()
- [x] T051 [US3] Add edge line rendering for CAD visualization in anywidget_cad_viewer/static/index.js:renderEdges()
- [x] T052 [US3] Implement show_edges parameter handling in anywidget_cad_viewer/viewer.py and static/index.js
- [x] T053 [US3] Add coordinate axes rendering in anywidget_cad_viewer/static/index.js:renderAxes()
- [x] T054 [US3] Implement show_axes parameter handling in anywidget_cad_viewer/viewer.py and static/index.js
- [x] T055 [US3] Add examples for all primitive types in examples/marimo_quickstart.py
- [x] T056 [US3] Add boolean operations examples in examples/marimo_quickstart.py
- [ ] T057 [US3] Manual verification: Test Cylinder, Sphere, Cone, Torus render correctly
- [ ] T058 [US3] Manual verification: Test boolean operations (union, subtract, intersect) render correctly
- [ ] T059 [US3] Manual verification: Test compound assemblies render with correct positioning

**Checkpoint**: All user stories should now be independently functional - full geometry support complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T060 [P] Implement background_color parameter in anywidget_cad_viewer/viewer.py and static/index.js
- [x] T061 [P] Implement width/height parameters for widget sizing in anywidget_cad_viewer/viewer.py
- [x] T062 [P] Add comprehensive docstrings to CADViewer class in anywidget_cad_viewer/viewer.py
- [x] T063 [P] Add docstrings to geometry utility functions in anywidget_cad_viewer/geometry.py
- [x] T064 [P] Add type hints to all public APIs in anywidget_cad_viewer/viewer.py and geometry.py
- [x] T065 Add parameter validation (quality range, color format) in anywidget_cad_viewer/viewer.py:__init__()
- [x] T066 Implement oversized geometry warning (>100k vertices) in anywidget_cad_viewer/geometry.py
- [x] T067 Add WebGL availability check in anywidget_cad_viewer/static/index.js
- [x] T068 Implement widget cleanup/dispose in anywidget_cad_viewer/static/index.js:remove()
- [ ] T069 Optimize JavaScript bundle size with tree-shaking in ESBuild config
- [x] T070 Add error handling for tessellation failures in anywidget_cad_viewer/geometry.py
- [x] T071 Add error handling for invalid build123d objects in anywidget_cad_viewer/viewer.py
- [x] T072 Create README.md with installation and basic usage instructions
- [x] T073 Add AGENTS.md reference to anywidget and three-cad-viewer dependencies
- [x] T074 Run ruff linting and fix any issues: ruff check . && ruff format .
- [ ] T075 Validate quickstart.md examples work end-to-end in marimo
- [x] T076 Verify uv.lock is synchronized: uv lock --check
- [ ] T077 Final manual verification: Test all scenarios from spec.md acceptance criteria

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - Delivers MVP: Basic display of build123d objects
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 with interactive controls
  - Independent but integrates with US1 viewer
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Expands geometry support beyond basic primitives
  - Independent but enhances US1 rendering capabilities

### Within Each User Story

**User Story 1 (Core Display)**:
1. Widget infrastructure (T016-T017) → parallel start
2. Geometry pipeline (T018-T020) → sequential after T017
3. Widget integration (T021) → after T020
4. JavaScript setup (T022-T024) → parallel with geometry work
5. Three.js integration (T025-T027) → sequential after T024
6. Validation and export (T028-T030) → sequential after JS complete
7. Example and verification (T031-T032) → final validation

**User Story 2 (Interaction)**:
1. Controls setup (T033-T034) → parallel start
2. Camera sync (T035, T039) → sequential after T034
3. Performance optimization (T036-T038) → parallel with camera work
4. Documentation and verification (T040-T041) → final validation

**User Story 3 (Geometry Support)**:
1. Primitive types (T042-T045) → all parallel
2. Advanced features (T046-T049) → sequential after primitives
3. Rendering enhancements (T050-T054) → parallel after T049
4. Examples and verification (T055-T059) → final validation

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks can run in parallel

**Phase 2 (Foundational)**:
- T010 and T011 can run in parallel (separate concerns)
- T012, T013, T014, T015 can run in parallel (different components)

**Phase 3 (User Story 1)**:
- T016 and T017 can start in parallel
- T022, T023, T024 can start in parallel (JavaScript work)

**Phase 4 (User Story 2)**:
- T033 and T034 can run in parallel
- T036, T037 can run in parallel

**Phase 5 (User Story 3)**:
- T042, T043, T044, T045 all parallel (different primitives)

**Phase 6 (Polish)**:
- T060, T061, T062, T063, T064 all parallel (different files/concerns)

---

## Parallel Example: User Story 1 Core Implementation

```bash
# Launch geometry pipeline and JavaScript setup together:
Task: "Implement geometry extraction from build123d in anywidget_cad_viewer/geometry.py:extract_ocp_shape()"
Task: "Bundle three-cad-viewer library in anywidget_cad_viewer/static/assets/"
Task: "Implement JavaScript widget model initialization in anywidget_cad_viewer/static/index.js"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T015) - CRITICAL
3. Complete Phase 3: User Story 1 (T016-T032)
4. **STOP and VALIDATE**: Test basic display in marimo with Box, Sphere, Cylinder
5. Deploy/demo if ready

**This delivers**: Automatic 3D visualization of basic build123d objects in marimo notebooks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - automatic display)
3. Add User Story 2 → Test independently → Deploy/Demo (adds smooth interaction)
4. Add User Story 3 → Test independently → Deploy/Demo (adds full geometry support)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Python geometry pipeline)
   - Developer B: User Story 1 (JavaScript viewer integration)
   - After US1 complete:
     - Developer C: User Story 2 (interaction)
     - Developer D: User Story 3 (geometry types)
3. Stories complete and integrate independently

---

## Notes

- **[P]** tasks = different files, no dependencies
- **[Story]** label maps task to specific user story for traceability
- **Constitution Compliance**: 
  - All dependencies added via uv commands (Principle VII)
  - pyproject.toml is source of truth
  - uv.lock synchronized after changes
  - No emojis in any artifacts (Principle VI)
- **Manual Verification**: Per Principle IV, tests not required but manual verification checklist provided
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Verify uv.lock stays synchronized throughout implementation
