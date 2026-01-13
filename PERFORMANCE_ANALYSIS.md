# Performance Analysis & Optimization Proposals

## Benchmark Results Summary

### Current Performance (from benchmark suite)

| Operation | Time | Vertices | Notes |
|-----------|------|----------|-------|
| `select_quality()` | 160ns | - | ✅ Extremely fast |
| `extract_ocp_shape()` | 1.3μs | - | ✅ Very fast |
| `serialize_mesh_data()` | 2.5μs | 24 | ✅ Very fast |
| `calculate_camera_position()` | 4.0μs | - | ✅ Very fast |
| **Box tessellation (q=0.1)** | **3.4ms** | 24 | ⚠️ Fast but OCP overhead |
| **Cylinder tessellation** | **17.2ms** | 506 | ⚠️ Moderate |
| **Sphere tessellation** | **174.4ms** | 4,066 | 🔴 Slow |
| **Complex assembly** | **98.5ms** | ~3,000 | 🔴 Slow |
| **Large assembly** | **17.1ms** | ~1,000 | ⚠️ Moderate |
| **CADViewer init (box)** | **5.2ms** | 24 | ✅ Fast |
| **CADViewer init (cylinder)** | **19.7ms** | 506 | ⚠️ Moderate |
| **End-to-end workflow** | **212.7ms** | 4,066 | 🔴 Slow (sphere) |

### Key Findings

1. **OCP tessellation is the bottleneck** (95%+ of time)
   - Sphere: 174ms for 4,066 vertices
   - The actual OCP BRepMesh code is compiled C++
   - Our Python wrapper adds minimal overhead (~5ms)

2. **Normal calculation is expensive** (lines 201-225 in geometry.py)
   - For each vertex: UV lookup + surface normal computation
   - Creates gp_Pnt() and gp_Vec() objects per vertex
   - Sphere with 4,066 vertices = 4,066 normal calculations

3. **List.extend() dominates Python time** (17,706 calls)
   - Used in tight loops for vertices, normals, triangles
   - Each call adds 3 elements (x, y, z) or (nx, ny, nz)

4. **validate_mesh_data() iterates all indices**
   - For sphere: iterates 24,006 indices (8,002 triangles × 3)
   - O(n) validation for every object

5. **Widget initialization overhead is low** (38ms for traitlets)
   - Most time in anywidget/ipywidgets internals
   - Not a concern for optimization

## Proposed Optimizations

### 🟢 HIGH IMPACT - Recommended

#### 1. **Pre-allocate arrays instead of list.extend()**
**Impact**: 20-30% faster Python loop processing
**Risk**: Low
**Effort**: Low

```python
# CURRENT (slow - repeated allocations)
vertices = []
for i in range(1, n + 1):
    pnt = triangulation.Node(i)
    vertices.extend([pnt.X(), pnt.Y(), pnt.Z()])

# OPTIMIZED (pre-allocate)
import array
n_verts = triangulation.NbNodes()
vertices = array.array('f', [0.0] * (n_verts * 3))  # Pre-allocate
idx = 0
for i in range(1, n_verts + 1):
    pnt = triangulation.Node(i)
    vertices[idx] = pnt.X()
    vertices[idx + 1] = pnt.Y()
    vertices[idx + 2] = pnt.Z()
    idx += 3
```

**Benefits**:
- Eliminates repeated memory allocations
- Reduces list.extend() calls from 17,706 to 0
- Faster memory access with array.array

#### 2. **Skip normal calculation for flat faces**
**Impact**: 30-50% faster for simple geometries (boxes, cylinders)
**Risk**: Low (fallback to [0, 0, 1] already exists)
**Effort**: Low

```python
# CURRENT: Always computes UV normals (expensive)
if triangulation.HasUVNodes():
    uv = triangulation.UVNode(i)
    gp_pnt = gp_Pnt()
    gp_vec = gp_Vec()
    BRepGProp_Face(face).Normal(uv.X(), uv.Y(), gp_pnt, gp_vec)
    # ... normalize ...

# OPTIMIZED: Check if face is planar first
if is_planar_face(face):
    # Use face normal directly (much faster)
    face_normal = get_face_normal(face)
    normals_array[i*3:i*3+3] = face_normal
else:
    # Only compute UV normals for curved surfaces
    if triangulation.HasUVNodes():
        # ... existing code ...
```

**Benefits**:
- Box: ~50% faster (all faces planar)
- Cylinder: ~30% faster (top/bottom planar, sides curved)
- Sphere: No change (all curved)

#### 3. **Optimize validate_mesh_data() - skip index range check**
**Impact**: 10-15% faster serialization
**Risk**: Low (move to optional debug mode)
**Effort**: Low

```python
# CURRENT: O(n) iteration of all indices
for idx in data["indices"]:
    if idx < 0 or idx >= vertex_count:
        raise ValueError(...)

# OPTIMIZED: Only check length, skip individual validation
# (OCP always generates valid indices)
def validate_mesh_data(data: MeshData, strict: bool = False) -> None:
    # Always validate lengths
    if len(data["vertices"]) % 3 != 0:
        raise ValueError(...)
    
    # Only iterate indices in strict mode (testing)
    if strict:
        for idx in data["indices"]:
            if idx < 0 or idx >= vertex_count:
                raise ValueError(...)
```

**Benefits**:
- Sphere: Saves ~0.5ms (24,006 checks removed)
- Assumes OCP generates valid data (safe assumption)
- Keep strict mode for testing

### 🟡 MEDIUM IMPACT - Consider

#### 4. **Cache BRepGProp_Face creation**
**Impact**: 5-10% faster normal calculation
**Risk**: Low
**Effort**: Low

```python
# CURRENT: Creates BRepGProp_Face for every vertex
BRepGProp_Face(face).Normal(uv.X(), uv.Y(), gp_pnt, gp_vec)

# OPTIMIZED: Create once per face
face_prop = BRepGProp_Face(face)
for i in range(1, triangulation.NbNodes() + 1):
    # ... vertex code ...
    face_prop.Normal(uv.X(), uv.Y(), gp_pnt, gp_vec)
```

#### 5. **Use numpy for large meshes**
**Impact**: 30-40% faster for large objects (>5000 vertices)
**Risk**: Medium (adds dependency)
**Effort**: Medium

```python
import numpy as np

# Convert OCP data to numpy arrays
vertices_np = np.zeros((n_verts, 3), dtype=np.float32)
for i in range(n_verts):
    pnt = triangulation.Node(i + 1)
    vertices_np[i] = [pnt.X(), pnt.Y(), pnt.Z()]

# Return as flat list for compatibility
return vertices_np.flatten().tolist()
```

**Trade-off**: Adds numpy dependency, but ~40% faster for spheres

### 🔴 LOW IMPACT - Skip for now

#### 6. **Parallel face processing**
**Impact**: 20-40% faster for multi-face objects
**Risk**: High (thread safety with OCP)
**Effort**: High

OCP objects may not be thread-safe. Would need careful testing.

#### 7. **Use OCP compute normals instead of UV**
**Impact**: Unknown (need research)
**Risk**: Medium
**Effort**: Medium

OCP's PolyTriangulation might have faster normal computation methods.

## Recommended Implementation Plan

### Phase 1: Quick Wins (30 minutes)
1. Optimize validate_mesh_data() - make index check optional (#3)
2. Pre-allocate arrays with array.array (#1)
3. Cache BRepGProp_Face per face (#4)

**Expected speedup**: 25-35% for typical objects

### Phase 2: Geometry-Specific Optimization (1 hour)
4. Detect planar faces and skip UV normal calculation (#2)

**Expected speedup**: Additional 20-30% for simple geometries

### Phase 3: Advanced (optional, 2+ hours)
5. Add numpy backend for large meshes (#5)
6. Research OCP built-in normal methods (#7)

**Expected speedup**: Additional 30-40% for complex objects

## Benchmark Improvements Estimate

| Operation | Current | After Phase 1 | After Phase 2 |
|-----------|---------|---------------|---------------|
| Box tessellation | 3.4ms | 2.5ms (-26%) | 1.7ms (-50%) |
| Cylinder tessellation | 17.2ms | 12.9ms (-25%) | 10.3ms (-40%) |
| Sphere tessellation | 174.4ms | 130.8ms (-25%) | 139.5ms (-20%) |
| CADViewer init (box) | 5.2ms | 3.9ms (-25%) | 2.6ms (-50%) |

**Note**: Sphere won't improve much from planar optimization since all faces are curved.

## Questions for Approval

1. **Should we add numpy dependency?** (Phase 3, #5)
   - Pro: 30-40% faster for large meshes
   - Con: Adds external dependency to minimal project

2. **Should we keep strict validation in production?** (#3)
   - Pro: Safety (catches invalid data)
   - Con: ~10% performance hit for no benefit (OCP is reliable)
   - Proposal: Off by default, enable with `CADViewer(..., validate=True)`

3. **Priority order**:
   - Implement Phase 1 (quick wins) immediately?
   - Skip Phase 2 if Phase 1 is sufficient?
   - Leave Phase 3 as future enhancement?
