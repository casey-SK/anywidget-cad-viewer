import marimo

__generated_with = "0.19.2"
app = marimo.App()


@app.cell
def imports():
    """Import required libraries."""
    import marimo as mo
    from build123d import Box, Color, Cone, Cylinder, Location, Sphere, Torus

    from anywidget_cad_viewer import CADViewer
    return Box, CADViewer, Color, Cone, Cylinder, Location, Sphere, Torus, mo


@app.cell
def example_1(Box, CADViewer):
    """Example 1: Display a simple box."""
    box = Box(30, 30, 30)
    CADViewer(box)
    return


@app.cell
def example_2(CADViewer, Cylinder):
    """Example 2: Custom quality and display settings."""
    cylinder = Cylinder(radius=5, height=20)
    CADViewer(
        cylinder,
        quality=0.05,  # Higher quality (lower number = more detail)
        show_edges=True,
        show_axes=True,
        background_color="#FFFFFF",
        width=600,
        height=400,
    )
    return


@app.cell
def example_3(Box, CADViewer, Cylinder, Location, Sphere):
    """Example 3: Complex assembly with multiple objects."""
    # Create a simple assembly
    base = Box(20, 20, 2)
    column = Cylinder(radius=2, height=15).locate(Location((0, 0, 2)))
    top = Sphere(radius=3).locate(Location((0, 0, 17)))

    # Fuse into single solid using the fuse method
    assembly = base.fuse(column).fuse(top)

    CADViewer(assembly, quality=0.1)
    return


@app.cell
def example_4_primitives_all(
    Box,
    CADViewer,
    Cone,
    Cylinder,
    Sphere,
    Torus,
    mo,
):
    """Example 4: All build123d primitive types."""
    mo.md("## All Primitive Types")

    # Box
    mo.md("### Box")
    _box = Box(10, 10, 10)
    CADViewer(_box, quality=0.1, width=400, height=300)

    # Cylinder
    mo.md("### Cylinder")
    _cylinder = Cylinder(radius=5, height=15)
    CADViewer(_cylinder, quality=0.1, width=400, height=300)

    # Sphere
    mo.md("### Sphere")
    _sphere = Sphere(radius=8)
    CADViewer(_sphere, quality=0.1, width=400, height=300)

    # Cone
    mo.md("### Cone")
    _cone = Cone(bottom_radius=7, height=15, top_radius=0)
    CADViewer(_cone, quality=0.1, width=400, height=300)

    # Torus
    mo.md("### Torus")
    _torus = Torus(major_radius=10, minor_radius=3)
    CADViewer(_torus, quality=0.1, width=680, height=570)
    return


@app.cell
def example_5_colors(Box, CADViewer, Color, Cylinder, Sphere, mo):
    """Example 5: Colored objects."""
    mo.md("## Colored Objects")

    # Red box
    mo.md("### Red Box")
    _red_box = Box(10, 10, 10)
    _red_box.color = Color("red")
    CADViewer(_red_box, quality=0.1, width=400, height=300)

    # Green cylinder
    mo.md("### Green Cylinder")
    _green_cyl = Cylinder(radius=5, height=15)
    _green_cyl.color = Color("green")
    CADViewer(_green_cyl, quality=0.1, width=400, height=300)

    # Blue custom RGB
    mo.md("### Blue Sphere (Custom RGB)")
    _blue_sphere = Sphere(radius=8)
    _blue_sphere.color = Color(0, 0, 1)  # RGB 0-1 range
    CADViewer(_blue_sphere, quality=0.1, width=400, height=300)
    return


@app.cell
def example_6_boolean_ops(Box, CADViewer, Cylinder, Location, mo):
    """Example 6: Boolean operations."""
    mo.md("## Boolean Operations")

    # Union (fuse)
    mo.md("### Union - Two overlapping boxes")
    _box1 = Box(15, 15, 15)
    _box2 = Box(15, 15, 15).locate(Location((10, 0, 0)))
    _union = _box1.fuse(_box2)
    CADViewer(_union, quality=0.1, width=400, height=300)

    # Subtract (cut)
    mo.md("### Subtract - Box with cylindrical hole")
    _base = Box(20, 20, 10)
    _hole = Cylinder(radius=4, height=15)
    _subtracted = _base - _hole
    CADViewer(_subtracted, quality=0.1, width=400, height=300)

    # Intersect
    mo.md("### Intersect - Two overlapping boxes")
    _box3 = Box(15, 15, 15)
    _box4 = Box(15, 15, 15).locate(Location((10, 0, 0)))
    _intersected = _box3.intersect(_box4)
    CADViewer(_intersected, quality=0.1, width=400, height=300)
    return

if __name__ == "__main__":
    app.run()
