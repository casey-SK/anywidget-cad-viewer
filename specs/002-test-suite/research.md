# Research: Test Suite Implementation

**Feature**: 002-test-suite  
**Date**: 2026-01-12

## Research Questions

### 1. pytest Best Practices for anywidget/build123d Projects

**Decision**: Use pytest with standard plugins (pytest-cov, pytest-benchmark)

**Rationale**: 
- pytest is the de facto standard for Python testing
- Already in dev dependencies
- Excellent fixture support for reusable test data
- Marker system allows categorizing tests (unit, integration, slow, etc.)

**Alternatives Considered**:
- unittest: More verbose, less flexible fixtures
- nose2: Less active development, fewer plugins

### 2. Test Organization Strategy

**Decision**: Organize tests by type in subdirectories

**Rationale**:
- Clear separation allows running specific test categories
- `pytest tests/unit/` runs only fast unit tests
- `pytest tests/integration/` runs only integration tests
- Matches pytest discovery conventions

**Structure**:
```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests
├── integration/         # End-to-end pipeline tests  
├── whitebox/            # Internal implementation tests
└── benchmark/           # Performance tests (optional run)
```

### 3. Coverage Measurement Approach

**Decision**: Use pytest-cov with HTML and terminal reporting

**Rationale**:
- pytest-cov integrates seamlessly with pytest
- HTML reports provide line-by-line visibility
- Terminal output shows quick summary
- Can enforce minimum coverage threshold

**Configuration**:
```toml
[tool.coverage.run]
source = ["anywidget_cad_viewer"]
omit = ["*/tests/*"]

[tool.coverage.report]
fail_under = 80
```

### 4. Performance Benchmarking Approach

**Decision**: Use pytest-benchmark for timing tests

**Rationale**:
- Integrates with pytest runner
- Statistical analysis of timing (mean, std dev)
- Can compare against baselines
- Non-invasive - tests run normally, benchmark decorator adds timing

**Alternative Considered**:
- Manual timing with time.perf_counter: Less accurate, no statistics
- cProfile: More overhead, harder to integrate with CI

### 5. Handling build123d Dependency in Tests

**Decision**: Create fixtures that generate real build123d shapes

**Rationale**:
- build123d is a runtime dependency, always available
- Real shapes test actual tessellation behavior
- Mock shapes would not catch OCP integration issues

**Fixtures Needed**:
- `simple_box`: Box(10, 20, 30) - basic shape
- `simple_cylinder`: Cylinder(5, 20) - curved surface
- `simple_sphere`: Sphere(10) - fully curved
- `complex_assembly`: Fused shapes - tests assembly handling

### 6. Marimo Integration Test Strategy

**Decision**: Run marimo in headless mode with timeout

**Rationale**:
- Already implemented in test_marimo_notebook.py
- 20-second timeout prevents hanging
- Captures stderr for error detection
- Does not require display/GUI

### 7. Import Test Approach

**Decision**: Dedicated test file that imports all public APIs

**Rationale**:
- Fast execution (just imports)
- Catches missing dependencies immediately
- Validates __all__ exports match available classes

**Test Cases**:
- Import package: `import anywidget_cad_viewer`
- Import main class: `from anywidget_cad_viewer import CADViewer`
- Import exceptions: `InvalidObjectError`, `TessellationError`, `OversizedGeometryError`

### 8. Whitebox Testing Internal Functions

**Decision**: Test internal functions directly with edge cases

**Rationale**:
- `extract_ocp_shape()` needs testing with invalid inputs
- `tessellate_shape()` needs testing with degenerate geometry
- `serialize_mesh_data()` needs testing with various data formats

**Edge Cases to Test**:
- Empty shape (no faces)
- Invalid object (no `wrapped` attribute)
- Very small/large shapes
- Zero-area faces

## Dependencies to Add

```bash
uv add --group test pytest-cov pytest-benchmark
```

**Justification**:
- pytest-cov: Required for coverage measurement (FR-008)
- pytest-benchmark: Required for performance profiling (FR-010, FR-011)

## pytest Configuration

Add to pyproject.toml:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Fast isolated tests",
    "integration: End-to-end pipeline tests",
    "whitebox: Internal implementation tests",
    "benchmark: Performance benchmarks (slow)",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["anywidget_cad_viewer"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```
