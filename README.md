# anywidget-cad-viewer

An interactive 3D CAD viewer widget for [build123d](https://github.com/gumyr/build123d) objects in [marimo](https://marimo.io/) and Jupyter notebooks.

## Features

- **Automatic Display**: Build123d objects render automatically in notebook cells
- **Interactive 3D Controls**: Orbit, zoom, and pan with smooth 60fps performance
- **Full Geometry Support**: All build123d primitives and boolean operations
- **Color Rendering**: Supports build123d color attributes
- **Edge Visualization**: Optional edge line rendering for CAD-style display
- **Adaptive Quality**: Automatically adjusts tessellation quality based on complexity
- **Configurable Appearance**: Custom background colors, widget dimensions, and display options

## Installation

### From PyPI (when published)

```bash
pip install anywidget-cad-viewer
```

### From Source

```bash
git clone https://github.com/casey-SK/anywidget-cad-viewer
cd anywidget-cad-viewer
pip install -e .
```

### Requirements

- Python 3.13 or higher
- marimo or Jupyter notebook environment
- Modern web browser with WebGL support

## Quick Start

### Basic Usage

```python
import marimo as mo
from build123d import Box
from anywidget_cad_viewer import CADViewer

# Create a build123d object
box = Box(10, 20, 30)

# Display it (automatically renders in notebook)
CADViewer(box)
```

### Custom Quality and Display Options

```python
from build123d import Cylinder

cylinder = Cylinder(radius=5, height=20)

CADViewer(
    cylinder,
    quality=0.05,              # Higher quality (0.01-1.0, lower = more detail)
    show_edges=True,           # Display edge lines
    show_axes=True,            # Display coordinate axes
    background_color="#FFFFFF", # White background
    width=800,                 # Widget width in pixels
    height=600,                # Widget height in pixels
)
```

### Colored Objects

```python
from build123d import Sphere, Color

sphere = Sphere(radius=15)
sphere.color = Color('red')  # or Color(1, 0, 0) for RGB

CADViewer(sphere)
```

### Boolean Operations

```python
from build123d import Box, Cylinder

# Create base and hole
base = Box(20, 20, 10)
hole = Cylinder(radius=3, height=15)

# Subtract to create hole
part = base - hole

CADViewer(part)
```

### Complex Assemblies

```python
from build123d import Box, Cylinder, Sphere, Location

# Build assembly
base = Box(20, 20, 2)
column = Cylinder(radius=2, height=15).locate(Location((0, 0, 2)))
top = Sphere(radius=3).locate(Location((0, 0, 17)))

# Fuse into single solid
assembly = base.fuse(column).fuse(top)

CADViewer(assembly, quality=0.1)
```

## Interactive Controls

- **Left mouse drag**: Rotate camera around target
- **Right mouse drag**: Pan view
- **Scroll wheel**: Zoom in/out
- **Double click**: Reset camera to default position

The viewer automatically:
- Positions camera to frame geometry optimally
- Maintains 60fps for smooth interaction (objects <10k vertices)
- Synchronizes camera state between Python and JavaScript
- Throttles rendering when idle to save resources

## API Reference

### CADViewer Class

```python
CADViewer(
    obj,                           # build123d object to visualize
    quality: float = 0.1,          # Tessellation quality (0.01-1.0)
    show_edges: bool = True,       # Display edge lines
    show_axes: bool = True,        # Display coordinate axes
    background_color: str = "#F0F0F0",  # Background color (hex)
    width: int = 800,              # Widget width (pixels)
    height: int = 600,             # Widget height (pixels)
)
```

#### Parameters

- **obj**: Any build123d object (Box, Sphere, Cylinder, Cone, Torus, or boolean operation result)
- **quality**: Tessellation quality factor
  - Lower values = higher quality, more vertices
  - Range: 0.01 (highest) to 1.0 (lowest)
  - Default: 0.1 (balanced)
  - Adaptive quality automatically adjusts for complex geometries
- **show_edges**: Whether to render edge lines (default: True)
- **show_axes**: Whether to display coordinate axes (default: True)
- **background_color**: Canvas background as hex color string (default: "#F0F0F0")
- **width**: Widget width in pixels (default: 800)
- **height**: Widget height in pixels (default: 600)

#### Exceptions

- **InvalidObjectError**: Raised when object is not a valid build123d CAD object
- **TessellationError**: Raised when geometry tessellation fails
- **OversizedGeometryError**: Raised when geometry exceeds 1M vertices

## Supported Geometry Types

### Primitives

- `Box(length, width, height)`
- `Cylinder(radius, height)`
- `Sphere(radius)`
- `Cone(bottom_radius, height, top_radius=0)`
- `Torus(major_radius, minor_radius)`

### Boolean Operations

- **Union** (fuse): `shape1.fuse(shape2)` or `shape1 + shape2`
- **Subtract** (cut): `shape1 - shape2`
- **Intersect**: `shape1.intersect(shape2)` or `shape1 & shape2`

### Assemblies

- Multiple objects combined via `fuse()`
- Positioned using `locate(Location(...))`

## Examples

See `examples/quickstart.py` for a complete interactive tutorial:

```bash
# Install marimo if not already installed
pip install marimo

# Run the examples
marimo edit examples/quickstart.py
```

## Development

### Running Tests

```bash
# Install dev dependencies
uv sync

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=anywidget_cad_viewer --cov-report=html

# Run specific test suite
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/benchmark/
```

### Linting

```bash
# Check code style
uv run ruff check .

# Format code
uv run ruff format .
```

## Architecture

### Tech Stack

- **Python**: anywidget for widget framework, OCP for CAD geometry handling
- **JavaScript**: Three.js for 3D rendering, OrbitControls for camera manipulation
- **Tessellation**: OCP BRepMesh for converting CAD surfaces to triangular meshes

### Data Flow

1. User creates build123d object in notebook cell
2. CADViewer extracts OCP shape and tessellates to mesh data
3. Mesh data (vertices, indices, normals, colors) serialized to JSON
4. JSON synced to JavaScript via anywidget traitlets
5. Three.js renders interactive 3D scene in browser

## License

MIT License - see [LICENSE](LICENSE) file for details

## Credits

Built with:
- [anywidget](https://github.com/manzt/anywidget) - Widget framework
- [build123d](https://github.com/gumyr/build123d) - CAD modeling library
- [Three.js](https://threejs.org/) - 3D rendering library
- [OpenCascade (OCP)](https://github.com/CadQuery/OCP) - CAD geometry kernel

## Support

- **Issues**: [GitHub Issues](https://github.com/casey-SK/anywidget-cad-viewer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/casey-SK/anywidget-cad-viewer/discussions)
- **Documentation**: See `examples/` directory for comprehensive examples
