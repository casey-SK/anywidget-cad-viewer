"""
Marimo Quickstart Example - anywidget-cad-viewer

This example demonstrates basic usage of the CAD viewer widget
with build123d objects in a marimo notebook.

To run this example:
    1. Install the package: uv pip install -e .
    2. Install marimo: uv pip install marimo
    3. Run: uv run marimo edit examples/marimo_quickstart.py
"""

import marimo

__generated_with = "0.19.2"
app = marimo.App()


@app.cell
def imports():
    """Import required libraries."""
    import marimo as mo
    from build123d import Box, Cylinder, Location, Sphere

    from anywidget_cad_viewer import CADViewer

    return Box, CADViewer, Cylinder, Location, Sphere, mo


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
def documentation(mo):
    """Display usage information."""
    mo.md(
        """
        # anywidget-cad-viewer Examples

        ## Features
        - Automatic display of build123d objects
        - Interactive 3D controls (orbit, zoom, pan)
        - Configurable quality and appearance
        - Error handling and validation

        ## Interactive Controls
        - **Left mouse drag**: Rotate camera around target
        - **Right mouse drag**: Pan view
        - **Scroll wheel**: Zoom in/out
        - **Double click**: Reset camera to default position
        
        The viewer automatically:
        - Positions camera to frame the geometry optimally
        - Maintains 60fps for smooth interaction (objects <10k vertices)
        - Synchronizes camera state between Python and JavaScript
        - Throttles rendering when not interacting to save resources

        ## Performance Tips
        - For complex geometry (>50k vertices), increase quality value (0.3-0.5)
        - Monitor browser console for FPS warnings
        - Use `show_edges=False` for large meshes to improve performance
        - The adaptive quality system automatically adjusts for complex shapes

        ## API Reference
        ```python
        CADViewer(
            obj,                           # build123d object
            quality=0.1,                   # 0.01-1.0 (lower = higher quality)
            show_edges=True,               # Display edge lines
            show_axes=True,                # Display coordinate axes
            background_color="#F0F0F0",    # Hex color
            width=800,                     # Widget width (pixels)
            height=600,                    # Widget height (pixels)
        )
        ```
        """
    )
    return


if __name__ == "__main__":
    app.run()
