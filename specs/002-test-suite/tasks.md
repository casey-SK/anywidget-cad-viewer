# Tasks: Comprehensive Test Suite

**Input**: Design documents from `/specs/002-test-suite/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: This feature IS the test implementation - all tasks create tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install pytest ecosystem and configure test environment

- [x] T001 Add pytest-cov and pytest-benchmark to dev dependencies using `uv add --group test pytest-cov pytest-benchmark`
- [x] T002 Add pytest configuration to pyproject.toml (markers, testpaths, coverage settings)
- [x] T003 Create tests/conftest.py with shared fixtures (simple_box, simple_cylinder, simple_sphere, complex_assembly, invalid_object)
- [x] T004 Create tests/whitebox/__init__.py directory
- [x] T005 Create tests/benchmark/__init__.py directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None - test suite has no foundational blockers. User stories can start immediately after Setup.

**Note**: Setup (Phase 1) provides the test infrastructure. All test categories can be implemented independently in parallel.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Developer Runs Unit Tests (Priority: P1) MVP

**Goal**: Implement unit tests for geometry.py and viewer.py that validate individual functions in isolation and execute in under 10 seconds total.

**Independent Test**: Run `uv run pytest tests/unit/` and verify all tests pass with clear failure messages showing function names and expected vs actual values.

### Implementation for User Story 1

- [x] T006 [P] [US1] Create tests/unit/test_imports.py with import validation tests (test_import_package, test_import_cadviewer, test_import_exceptions, test_public_api)
- [x] T007 [P] [US1] Create tests/unit/test_geometry.py with tests for extract_ocp_shape (valid box, valid cylinder, invalid object)
- [x] T008 [US1] Add tests to tests/unit/test_geometry.py for tessellate_shape (box, quality parameter, cylinder)
- [x] T009 [US1] Add tests to tests/unit/test_geometry.py for serialize_mesh_data (format validation, vertex count)
- [x] T010 [P] [US1] Create tests/unit/test_viewer.py with CADViewer initialization tests (valid object, invalid object, quality bounds)
- [x] T011 [US1] Add tests to tests/unit/test_viewer.py for default options (show_edges, show_axes, background_color, width, height)
- [x] T012 [US1] Add tests to tests/unit/test_viewer.py for custom options validation
- [x] T013 [US1] Run `uv run pytest tests/unit/ -v` and verify all tests pass in under 10 seconds

**Checkpoint**: Unit tests complete and passing. Can be run independently with `uv run pytest tests/unit/`

---

## Phase 4: User Story 2 - Developer Runs Integration Tests (Priority: P1)

**Goal**: Implement integration tests that verify the full tessellation pipeline from build123d object to widget mesh_data, completing in under 30 seconds (excluding marimo startup).

**Independent Test**: Run `uv run pytest tests/integration/` and verify the marimo notebook test and pipeline tests pass.

### Implementation for User Story 2

- [x] T014 [P] [US2] Create tests/integration/test_pipeline.py with test_box_to_mesh_pipeline (Box → CADViewer produces valid mesh_data)
- [x] T015 [US2] Add test_cylinder_to_mesh_pipeline to tests/integration/test_pipeline.py (verify curved surfaces tessellated)
- [x] T016 [US2] Add test_assembly_to_mesh_pipeline to tests/integration/test_pipeline.py (complex assembly produces combined mesh)
- [x] T017 [US2] Add test_viewer_traitlets_sync to tests/integration/test_pipeline.py (verify model.get() returns correct values)
- [x] T018 [US2] Run `uv run pytest tests/integration/ -v` and verify all tests pass in under 30 seconds

**Checkpoint**: Integration tests complete and passing. Can be run independently with `uv run pytest tests/integration/`

---

## Phase 5: User Story 3 - Developer Validates Package Imports (Priority: P2)

**Goal**: Ensure import tests (already created in T006) catch packaging issues and missing dependencies.

**Independent Test**: Run `uv run pytest tests/unit/test_imports.py -v` in a fresh environment and verify zero import errors.

### Implementation for User Story 3

- [x] T019 [US3] Create a fresh virtual environment and run `uv sync` to verify clean install
- [x] T020 [US3] Run `uv run pytest tests/unit/test_imports.py -v` in fresh environment and verify all imports succeed
- [x] T021 [US3] Document any platform-specific import requirements in specs/002-test-suite/quickstart.md if discovered

**Checkpoint**: Import tests validated in fresh environment. Package structure verified.

---

## Phase 6: User Story 4 - Developer Runs Whitebox Tests (Priority: P2)

**Goal**: Implement whitebox tests that examine internal implementation details and edge cases not visible through the public API.

**Independent Test**: Run `uv run pytest tests/whitebox/ -v` and verify all edge cases are handled gracefully with appropriate exceptions.

### Implementation for User Story 4

- [x] T022 [P] [US4] Create tests/whitebox/test_internal.py with test_face_iteration (verify all faces on box are iterated)
- [x] T023 [US4] Add test_normal_computation to tests/whitebox/test_internal.py (verify BRepGProp_Face computes normals)
- [x] T024 [US4] Add test_empty_shape_handling to tests/whitebox/test_internal.py (test shape with no faces raises TessellationError)
- [x] T025 [US4] Add test_degenerate_face to tests/whitebox/test_internal.py (test zero-area face handling)
- [x] T026 [US4] Add edge case tests for thin_plate, tiny_shape, large_shape fixtures
- [x] T027 [US4] Run `uv run pytest tests/whitebox/ -v` and verify all tests pass

**Checkpoint**: Whitebox tests complete and passing. Edge cases properly handled.

---

## Phase 7: User Story 5 - Developer Checks Code Coverage (Priority: P2)

**Goal**: Achieve 80% minimum code coverage on Python modules and generate HTML coverage reports.

**Independent Test**: Run `uv run pytest --cov=anywidget_cad_viewer --cov-report=html --cov-report=term-missing` and verify coverage meets 80% threshold.

### Implementation for User Story 5

- [x] T028 [US5] Run `uv run pytest --cov=anywidget_cad_viewer --cov-report=term-missing` and identify uncovered lines
- [x] T029 [US5] Add missing tests to reach 80% coverage in anywidget_cad_viewer/geometry.py
- [x] T030 [US5] Add missing tests to reach 80% coverage in anywidget_cad_viewer/viewer.py
- [x] T031 [US5] Add missing tests to reach 100% coverage in anywidget_cad_viewer/__init__.py
- [x] T032 [US5] Run `uv run pytest --cov=anywidget_cad_viewer --cov-report=html` and verify HTML report is generated in htmlcov/
- [x] T033 [US5] Verify fail_under = 80 setting in pyproject.toml causes build to fail if coverage drops below threshold

**Checkpoint**: 80% coverage achieved. Coverage reports available in htmlcov/ directory.

---

## Phase 8: User Story 6 - Developer Profiles Code Performance (Priority: P3)

**Goal**: Implement performance benchmark tests that measure tessellation timing and detect regressions.

**Independent Test**: Run `uv run pytest tests/benchmark/ -v` and verify timing metrics are reported with less than 10% variance.

### Implementation for User Story 6

- [x] T034 [P] [US6] Create tests/benchmark/test_performance.py with test_tessellation_box_timing (benchmark Box tessellation)
- [x] T035 [US6] Add test_tessellation_complex_timing to tests/benchmark/test_performance.py (benchmark complex assembly)
- [x] T036 [US6] Add test_viewer_init_timing to tests/benchmark/test_performance.py (benchmark CADViewer initialization)
- [x] T037 [US6] Run `uv run pytest tests/benchmark/ -v --benchmark-only` and review timing statistics
- [x] T038 [US6] Document baseline performance metrics in specs/002-test-suite/quickstart.md

**Checkpoint**: Performance benchmarks complete. Timing baselines established.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T039 Run full test suite `uv run pytest` and verify all tests pass in under 2 minutes
- [x] T040 Run `uv run pytest --cov=anywidget_cad_viewer --cov-report=term` and verify 80% coverage
- [x] T041 Test quick validation workflow: `uv run pytest tests/unit/ && uv run ruff check .`
- [x] T042 Update specs/002-test-suite/quickstart.md with any discovered troubleshooting tips
- [x] T043 Update AGENTS.md with test commands if not already present

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phase 3+)**: All depend on Setup (Phase 1) completion only
  - User stories can proceed in parallel after Setup
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5 → US6)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Unit Tests)**: Can start after Setup - No dependencies on other stories
- **User Story 2 (P1 - Integration Tests)**: Can start after Setup - No dependencies on other stories
- **User Story 3 (P2 - Import Tests)**: Depends on US1 (test_imports.py created in T006)
- **User Story 4 (P2 - Whitebox Tests)**: Can start after Setup - No dependencies on other stories
- **User Story 5 (P2 - Coverage)**: Depends on US1, US2, US4 being complete (needs tests to measure coverage of)
- **User Story 6 (P3 - Benchmarks)**: Can start after Setup - No dependencies on other stories

### Within Each User Story

- Tests marked [P] can run in parallel (different files)
- Tests within same file must run sequentially
- Story complete before moving to next priority

### Parallel Opportunities

- Setup tasks T004, T005 can run in parallel (different directories)
- US1: T006 (test_imports.py) and T007 (test_geometry.py) and T010 (test_viewer.py) can run in parallel
- US2: T014 can start immediately, then T015-T017 add to same file sequentially
- US4: T022 can start immediately, then T023-T027 add to same file sequentially
- US6: T034 can start immediately, then T035-T036 add to same file sequentially

---

## Parallel Example: User Story 1 (Unit Tests)

```bash
# Launch all test files for User Story 1 together:
Task: "Create tests/unit/test_imports.py with import validation tests"
Task: "Create tests/unit/test_geometry.py with tests for extract_ocp_shape"
Task: "Create tests/unit/test_viewer.py with CADViewer initialization tests"

# These three files can be created in parallel by different developers or agents
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (pytest configuration and fixtures)
2. Complete Phase 3: User Story 1 (Unit tests)
3. **STOP and VALIDATE**: Run `uv run pytest tests/unit/ -v`
4. Verify unit tests provide fast feedback (<10 seconds)

### Incremental Delivery

1. Complete Setup → Test infrastructure ready
2. Add User Story 1 → Unit tests working (MVP!)
3. Add User Story 2 → Integration tests working
4. Add User Story 3 → Import validation confirmed
5. Add User Story 4 → Edge cases covered
6. Add User Story 5 → Coverage threshold met
7. Add User Story 6 → Performance baselines established
8. Each story adds test coverage without breaking previous tests

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup together (T001-T005)
2. Once Setup is done:
   - Developer A: User Story 1 (Unit tests)
   - Developer B: User Story 2 (Integration tests)
   - Developer C: User Story 4 (Whitebox tests)
   - Developer D: User Story 6 (Benchmarks)
3. Then sequentially:
   - User Story 3 (depends on US1)
   - User Story 5 (depends on US1, US2, US4)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently runnable and testable
- Run full suite after each story to ensure no regressions
- Commit after each task or logical group
- Coverage target (US5) requires other tests to be complete first
