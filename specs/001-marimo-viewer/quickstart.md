# Quickstart: CAD Viewer in Marimo Notebooks

**Feature**: 001-marimo-viewer  
**Audience**: Engineers and data scientists using build123d in marimo notebooks  
**Time to Complete**: 5 minutes

## Prerequisites

- Python 3.13 or higher installed
- marimo notebook environment
- Basic familiarity with build123d CAD modeling

## Installation

```bash
# Install from PyPI (when published)
pip install anywidget-cad-viewer

# Or install from source
git clone https://github.com/YOUR-ORG/anywidget-cad-viewer
cd anywidget-cad-viewer
pip install -e .
```

**Dependencies Installed**:
- anywidget (widget framework)
- ocp-vscode (OCP geometry handling)
- build123d will be installed if not present

## Quick Start Example

### Step 1: Create a Marimo Notebook

```bash
marimo edit my_cad_design.py
```

### Step 2: Import Libraries

```python
import marimo as mo
```

```python
from build123d import Box, Sphere, Cylinder
from build123d import subtract, union
from anywidget_cad_viewer import CADViewer
```

### Step 3: Create and Visualize a Simple Shape

```python
# Create a box
box = Box(10, 20, 30)

# Visualize it (automatically displays in cell output)
CADViewer(box)
```

**Result**: An interactive 3D viewer appears showing your box. You can:
- Click and drag to rotate
- Scroll to zoom
- Right-click and drag to pan

### Step 4: Try More Complex Geometry

```python
# Create a cylinder
cylinder = Cylinder(5, 40)

CADViewer(cylinder)
```

```python
# Create a sphere
sphere = Sphere(15)

CADViewer(sphere, quality=0.05, background_color="#FFFFFF")
```

### Step 5: Boolean Operations

```python
# Subtract a cylinder from a box
base = Box(20, 20, 10)
hole = Cylinder(3, 15)
part = subtract(base, hole)

CADViewer(part)
```

```python
# Union multiple shapes
body = union(
    Box(10, 10, 5),
    Cylinder(3, 8).translate((0, 0, 5))
)

CADViewer(body, show_edges=True)
```

## Customization Options

### Visualization Quality

```python
# High quality (more triangles, slower)
CADViewer(complex_shape, quality=0.01)

# Balanced (default)
CADViewer(complex_shape, quality=0.1)

# Low quality (fewer triangles, faster)
CADViewer(complex_shape, quality=0.5)
```

### Display Options

```python
# Hide edge lines
CADViewer(sphere, show_edges=False)

# Hide coordinate axes
CADViewer(box, show_axes=False)

# Custom background color
CADViewer(cylinder, background_color="#2C3E50")

# Custom widget size
CADViewer(part, width=1000, height=800)
```

## Common Patterns

### Pattern 1: Parametric Design

```python
# Define parameters
length = 50
width = 30
height = 10
hole_diameter = 5

# Create design
plate = Box(length, width, height)
hole = Cylinder(hole_diameter/2, height * 2)
result = subtract(plate, hole)

CADViewer(result)
```

**Tip**: Change parameters and re-execute the cell to see updates instantly!

### Pattern 2: Multiple Views

```python
# Show original and modified side-by-side
original = Box(10, 10, 10)
CADViewer(original)
```

```python
modified = subtract(original, Sphere(6))
CADViewer(modified)
```

Each cell gets its own independent viewer.

### Pattern 3: Assembly Visualization

```python
from build123d import Location, Compound

# Create parts
base = Box(50, 50, 5)
post1 = Cylinder(3, 20).translate((15, 15, 2.5))
post2 = Cylinder(3, 20).translate((-15, 15, 2.5))
post3 = Cylinder(3, 20).translate((15, -15, 2.5))
post4 = Cylinder(3, 20).translate((-15, -15, 2.5))

# Combine into assembly
assembly = union(base, post1, post2, post3, post4)

CADViewer(assembly)
```

## Interactive Controls

### Mouse Controls

- **Rotate**: Left-click and drag
- **Zoom**: Scroll wheel or pinch gesture
- **Pan**: Right-click and drag (or Shift + left-click)

### Keyboard Shortcuts

- **R**: Reset camera to default view
- **F**: Fit geometry to view (auto-zoom)
- **G**: Toggle grid display
- **E**: Toggle edge lines
- **A**: Toggle axes

(Note: Keyboard shortcuts depend on three-cad-viewer implementation)

## Troubleshooting

### Issue: Widget doesn't appear

**Solution**: Make sure the cell returns the widget:
```python
# Wrong - widget created but not returned
CADViewer(box)
other_variable = 42

# Right - widget is last expression
other_variable = 42
CADViewer(box)
```

### Issue: "Invalid object" error

**Solution**: Verify your object is a build123d CAD object:
```python
print(type(my_object))  # Should show build123d class
print(hasattr(my_object, 'wrapped'))  # Should be True
```

### Issue: Slow performance

**Solutions**:
1. Reduce quality: `CADViewer(obj, quality=0.2)`
2. Hide edges: `CADViewer(obj, show_edges=False)`
3. Simplify geometry (use fewer boolean operations)

### Issue: WebGL error

**Solution**: Update your browser to a modern version:
- Chrome 90+
- Firefox 88+
- Safari 15+
- Edge 90+

## Advanced Usage

### Accessing Camera State

```python
# Create viewer
viewer = CADViewer(box)

# Later, access camera position
# (After user interacts with widget)
camera_info = viewer.camera_state
print(f"Camera at {camera_info['position']}")
print(f"Looking at {camera_info['target']}")
```

### Handling Errors

```python
try:
    viewer = CADViewer(my_object)
except ValueError as e:
    print(f"Cannot visualize: {e}")
```

### Working with Colors

```python
from build123d import Box, Color

# Create colored box
box = Box(10, 10, 10)
box.color = Color("red")

# Color is preserved in visualization
CADViewer(box)
```

## Example: Complete CAD Design

Here's a complete example creating a parametric mounting bracket:

```python
# Parameters
base_length = 60
base_width = 40
base_thickness = 5
post_diameter = 8
post_height = 25
hole_diameter = 4

# Base plate
base = Box(base_length, base_width, base_thickness)

# Mounting posts
post_spacing = base_length * 0.6
post1 = Cylinder(post_diameter/2, post_height).translate((post_spacing/2, 0, base_thickness/2))
post2 = Cylinder(post_diameter/2, post_height).translate((-post_spacing/2, 0, base_thickness/2))

# Mounting holes in base
hole1 = Cylinder(hole_diameter/2, base_thickness * 2).translate((base_length/3, 0, 0))
hole2 = Cylinder(hole_diameter/2, base_thickness * 2).translate((-base_length/3, 0, 0))

# Assemble
bracket = union(base, post1, post2)
bracket = subtract(bracket, hole1, hole2)

# Visualize
CADViewer(bracket, quality=0.05, background_color="#ECF0F1")
```

## Next Steps

- Explore build123d documentation for advanced modeling techniques
- Try creating assemblies with multiple parts
- Experiment with different visualization quality settings
- Share your marimo notebooks with embedded 3D viewers

## Performance Tips

1. **Start simple**: Begin with low-quality preview (`quality=0.2`), increase for final view
2. **Limit complexity**: Keep individual objects under 50,000 vertices
3. **Hide edges**: For complex models, `show_edges=False` improves performance
4. **Browser matters**: Chrome typically has best WebGL performance

## Getting Help

- GitHub Issues: [https://github.com/YOUR-ORG/anywidget-cad-viewer/issues](https://github.com/YOUR-ORG/anywidget-cad-viewer/issues)
- build123d Docs: [https://build123d.readthedocs.io/](https://build123d.readthedocs.io/)
- marimo Docs: [https://docs.marimo.io/](https://docs.marimo.io/)

## What's Next?

Now that you have the viewer working, try:
1. Creating parametric designs with sliders (marimo UI elements)
2. Exporting designs to STL for 3D printing (build123d export functions)
3. Building interactive CAD tutorials in marimo notebooks
4. Combining CAD visualization with matplotlib plots for engineering analysis
