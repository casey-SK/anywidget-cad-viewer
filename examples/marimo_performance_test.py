"""
Marimo Performance Test - anywidget-cad-viewer

This notebook is specifically designed for T041 manual verification:
Testing 60fps interaction with medium complexity objects (~5000 vertices).

To run this example:
    1. Install the package: uv pip install -e .
    2. Install marimo: uv pip install marimo
    3. Run: uv run marimo edit examples/marimo_performance_test.py
    4. Open browser console (F12) to monitor FPS warnings
    5. Interact with each viewer (rotate, zoom, pan) and verify smooth 60fps

Expected Results:
- All viewers should render smoothly at 60fps during interaction
- No FPS warnings in console for objects <10k vertices
- Camera should position automatically to frame geometry
- Animation should throttle when not interacting (check console)
"""

import marimo

__generated_with = "0.19.2"
app = marimo.App(width="full")


@app.cell
def imports():
    """Import required libraries."""
    import marimo as mo
    from build123d import Box, Cone, Cylinder, Location, Sphere, Torus

    from anywidget_cad_viewer import CADViewer

    return Box, CADViewer, Cone, Cylinder, Location, Sphere, Torus, mo


@app.cell
def test_instructions(mo):
    """Display test instructions."""
    mo.md(
        """
        # Performance Test Suite - T041 Verification
        
        ## Test Objective
        Verify 60fps interaction with medium complexity objects (~5000 vertices)
        
        ## How to Test
        1. **Open Browser Console** (F12 or Cmd+Option+I)
        2. **Interact with each viewer** below:
           - Left drag to rotate
           - Right drag to pan  
           - Scroll to zoom
        3. **Check for smooth animation** - should feel responsive at 60fps
        4. **Watch console** for FPS warnings (warns if <30fps)
        
        ## Expected Results
        ✅ Smooth 60fps interaction during mouse movement  
        ✅ No console warnings for objects shown below  
        ✅ Throttled rendering when idle (saves CPU)  
        ✅ Camera automatically frames geometry  
        
        ## Performance Metrics
        Objects below range from ~1000 to ~8000 vertices.
        All should maintain 60fps on modern hardware.
        """
    )
    return


@app.cell
def test_1_simple_cylinder(CADViewer, Cylinder, mo):
    """Test 1: Simple cylinder (~1000 vertices)."""
    mo.md("### Test 1: Simple Cylinder (~1000 vertices)")

    cylinder = Cylinder(radius=10, height=30)
    viewer = CADViewer(cylinder, quality=0.1)

    # Display vertex count
    vertex_count = len(viewer.mesh_data["vertices"]) // 3
    mo.md(f"**Vertex count**: {vertex_count:,} vertices")

    return (viewer,)


@app.cell
def test_2_detailed_sphere(CADViewer, Sphere, mo):
    """Test 2: Detailed sphere (~5000 vertices)."""
    mo.md("### Test 2: Detailed Sphere (~5000 vertices)")
    mo.md("This is the TARGET complexity for T041 verification")

    sphere = Sphere(radius=15)
    viewer = CADViewer(sphere, quality=0.08)  # Higher detail

    vertex_count = len(viewer.mesh_data["vertices"]) // 3
    mo.md(f"**Vertex count**: {vertex_count:,} vertices")

    return (viewer,)


@app.cell
def test_3_complex_cylinder(CADViewer, Cylinder, mo):
    """Test 3: High-quality cylinder (~3000 vertices)."""
    mo.md("### Test 3: High-Quality Cylinder (~3000 vertices)")

    cylinder = Cylinder(radius=8, height=25)
    viewer = CADViewer(cylinder, quality=0.05)  # Very high quality

    vertex_count = len(viewer.mesh_data["vertices"]) // 3
    mo.md(f"**Vertex count**: {vertex_count:,} vertices")

    return (viewer,)


@app.cell
def test_4_torus(CADViewer, Torus, mo):
    """Test 4: Torus with curved surfaces (~4000 vertices)."""
    mo.md("### Test 4: Torus (~4000 vertices)")
    mo.md("Complex topology with inner/outer curved surfaces")

    torus = Torus(major_radius=15, minor_radius=5)
    viewer = CADViewer(torus, quality=0.1)

    vertex_count = len(viewer.mesh_data["vertices"]) // 3
    mo.md(f"**Vertex count**: {vertex_count:,} vertices")

    return (viewer,)


@app.cell
def test_5_assembly(Box, CADViewer, Cylinder, Location, Sphere, mo):
    """Test 5: Medium assembly (~6000 vertices)."""
    mo.md("### Test 5: Medium Assembly (~6000 vertices)")
    mo.md("Multiple fused objects with different geometries")

    # Create a more complex assembly
    base = Box(30, 30, 5)
    column1 = Cylinder(radius=3, height=20).locate(Location((10, 10, 5)))
    column2 = Cylinder(radius=3, height=20).locate(Location((-10, 10, 5)))
    column3 = Cylinder(radius=3, height=20).locate(Location((10, -10, 5)))
    column4 = Cylinder(radius=3, height=20).locate(Location((-10, -10, 5)))
    top = Sphere(radius=5).locate(Location((0, 0, 25)))

    assembly = base.fuse(column1).fuse(column2).fuse(column3).fuse(column4).fuse(top)
    viewer = CADViewer(assembly, quality=0.1)

    vertex_count = len(viewer.mesh_data["vertices"]) // 3
    mo.md(f"**Vertex count**: {vertex_count:,} vertices")

    return (viewer,)


@app.cell
def test_6_high_detail_sphere(CADViewer, Sphere, mo):
    """Test 6: Very high detail sphere (~8000 vertices)."""
    mo.md("### Test 6: High Detail Sphere (~8000 vertices)")
    mo.md("Near upper limit for 60fps on typical hardware")

    sphere = Sphere(radius=20)
    viewer = CADViewer(sphere, quality=0.05)  # Very high quality

    vertex_count = len(viewer.mesh_data["vertices"]) // 3
    mo.md(f"**Vertex count**: {vertex_count:,} vertices")

    return (viewer,)


@app.cell
def test_7_cone_array(CADViewer, Cone, Location, mo):
    """Test 7: Array of cones (~5000 vertices)."""
    mo.md("### Test 7: Cone Array (~5000 vertices)")
    mo.md("Multiple objects combined")

    # Create 5 cones in a circle
    cone1 = Cone(bottom_radius=5, height=15, top_radius=0)
    cone2 = Cone(bottom_radius=5, height=15, top_radius=0).locate(Location((20, 0, 0)))
    cone3 = Cone(bottom_radius=5, height=15, top_radius=0).locate(Location((10, 17, 0)))
    cone4 = Cone(bottom_radius=5, height=15, top_radius=0).locate(Location((-10, 17, 0)))
    cone5 = Cone(bottom_radius=5, height=15, top_radius=0).locate(Location((-20, 0, 0)))

    array = cone1.fuse(cone2).fuse(cone3).fuse(cone4).fuse(cone5)
    viewer = CADViewer(array, quality=0.1)

    vertex_count = len(viewer.mesh_data["vertices"]) // 3
    mo.md(f"**Vertex count**: {vertex_count:,} vertices")

    return (viewer,)


@app.cell
def test_8_performance_comparison(mo):
    """Test 8: Performance comparison table."""
    mo.md(
        """
        ## Performance Comparison
        
        ### Quality vs Vertex Count
        
        | Object | Quality | Vertex Count | Expected FPS | Status |
        |--------|---------|--------------|--------------|--------|
        | Cylinder | 0.1 | ~1,000 | 60fps | ✅ |
        | Sphere | 0.08 | ~5,000 | 60fps | ✅ Target |
        | Cylinder HQ | 0.05 | ~3,000 | 60fps | ✅ |
        | Torus | 0.1 | ~4,000 | 60fps | ✅ |
        | Assembly | 0.1 | ~6,000 | 60fps | ✅ |
        | Sphere HQ | 0.05 | ~8,000 | 60fps | ✅ |
        | Cone Array | 0.1 | ~5,000 | 60fps | ✅ |
        
        ### Verification Checklist
        
        - [ ] All viewers render smoothly during interaction
        - [ ] No FPS warnings in console for tests 1-7
        - [ ] Camera automatically positions to frame geometry
        - [ ] Rotation feels responsive (no lag)
        - [ ] Zoom is smooth
        - [ ] Pan is smooth
        - [ ] Animation throttles when idle (check console logs)
        
        ### Browser Console Commands
        
        To manually check FPS in console:
        ```javascript
        // Check current FPS (if exposed)
        performance.now()
        ```
        
        ### What to Look For
        
        **Good Performance (60fps)**:
        - Smooth rotation without stuttering
        - Immediate response to mouse input
        - No visible lag or dropped frames
        
        **Poor Performance (<30fps)**:
        - Choppy rotation
        - Delayed response to input
        - Console warnings about low FPS
        - Visible frame drops
        
        ### Troubleshooting
        
        If any test shows poor performance:
        1. Check browser console for FPS warnings
        2. Try reducing quality (increase value 0.1 → 0.2)
        3. Disable edges: `show_edges=False`
        4. Check system resources (Activity Monitor/Task Manager)
        5. Try different browser (Chrome usually fastest for WebGL)
        """
    )
    return


@app.cell
def test_9_camera_features(Box, CADViewer, mo):
    """Test 9: Camera positioning features."""
    mo.md(
        """
        ## Camera Positioning Features (User Story 2)
        
        This section demonstrates the automatic camera positioning
        and synchronization features implemented in User Story 2.
        """
    )

    # Small box - camera should be close
    small_box = Box(1, 1, 1)
    viewer_small = CADViewer(small_box, quality=0.1)
    mo.md(f"**Small Box (1x1x1)**: Camera at {viewer_small.camera_position}")

    # Large box - camera should be far
    large_box = Box(100, 100, 100)
    viewer_large = CADViewer(large_box, quality=0.2)
    mo.md(f"**Large Box (100x100x100)**: Camera at {viewer_large.camera_position}")

    mo.md(
        """
        Notice how the camera distance automatically adjusts:
        - Small objects → camera closer
        - Large objects → camera farther away
        - Camera target centered on geometry
        """
    )

    return viewer_small, viewer_large


@app.cell
def test_summary(mo):
    """Display test summary."""
    mo.md(
        """
        ---
        
        ## T041 Verification Summary
        
        **Task**: Manual verification - Test 60fps interaction with medium complexity object (5000 vertices)
        
        **Status**: Ready for verification
        
        **Key Tests**:
        - Test 2: Detailed Sphere (~5000 vertices) - PRIMARY TARGET
        - All other tests validate performance across range of complexities
        
        **Acceptance Criteria**:
        1. ✅ Smooth 60fps rotation, zoom, pan
        2. ✅ No FPS warnings in console
        3. ✅ Responsive interaction (no lag)
        4. ✅ Automatic camera positioning works
        5. ✅ Animation throttles when idle
        
        **Next Steps**:
        - Run through all tests above
        - Mark T041 as complete in tasks.md if all pass
        - Document any performance issues found
        """
    )
    return


if __name__ == "__main__":
    app.run()
