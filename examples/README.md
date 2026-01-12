# anywidget-cad-viewer Examples

This directory contains example marimo notebooks demonstrating the anywidget-cad-viewer library.

## Quick Start

### For Library Users (Once Published)

Once anywidget-cad-viewer is published to PyPI:

```bash
# Install marimo and the library
uv tool install marimo
uv pip install anywidget-cad-viewer

# Run the example
marimo edit --sandbox examples/marimo_quickstart.py
```

### For Developers (Local Development)

When developing locally, install the package in editable mode first:

```bash
# One-time setup
cd /path/to/anywidget-cad-viewer
uv pip install -e .
uv tool install marimo

# Then run examples
marimo edit --sandbox examples/marimo_quickstart.py
```

## How Sandbox Notebooks Work

The examples use **sandbox notebooks** with [PEP 723](https://peps.python.org/pep-0723/) inline script metadata:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.10",
#     "build123d>=0.10.0",
# ]
# ///
```

When you run `marimo edit --sandbox`, it:
1. Creates an isolated virtual environment
2. Installs the dependencies listed in the PEP 723 metadata
3. Uses the anywidget-cad-viewer from your parent environment (installed via `uv pip install -e .`)
4. Launches the marimo editor

This approach:
- ✅ Avoids dependency conflicts (marimo runs in its own isolated environment)
- ✅ Uses your local development version of anywidget-cad-viewer
- ✅ Automatically manages notebook-specific dependencies (build123d, etc.)
- ✅ Works the same way for published packages

## Available Examples

### `marimo_quickstart.py`

Comprehensive introduction to anywidget-cad-viewer featuring:

1. **Basic Usage** - Simple box visualization
2. **Custom Settings** - Quality, colors, and display options  
3. **Complex Assembly** - Fusing multiple shapes
4. **Documentation** - API reference and controls

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- marimo (install via `uv tool install marimo`)

## Troubleshooting

### "ModuleNotFoundError: No module named 'anywidget_cad_viewer'"

Make sure you've installed the package in your environment:
```bash
cd /path/to/anywidget-cad-viewer
uv pip install -e .
```

### "No module named 'build123d'"

This should be automatically installed by the sandbox. If it's not, wait for marimo to finish setting up the isolated environment.

### Widget doesn't render

The widget requires JavaScript support. Make sure you're viewing the notebook in:
- marimo's web interface (`marimo edit`)
- A browser with JavaScript enabled

### Dependency conflicts with websockets

If you see websockets errors, make sure you're using the global marimo tool:
```bash
uv tool install marimo  # Install globally
marimo edit --sandbox examples/marimo_quickstart.py  # Use global marimo
```

**Don't** run `uv run marimo` from the project directory, as this uses the project's environment which has ocp-vscode (incompatible websockets version).

## Learn More

- [marimo Documentation](https://docs.marimo.io/)
- [build123d Documentation](https://build123d.readthedocs.io/)
- [anywidget Documentation](https://anywidget.dev/)
- [anywidget-cad-viewer GitHub](https://github.com/build123d/anywidget-cad-viewer)

## Available Examples

### `marimo_quickstart.py`

Comprehensive introduction to anywidget-cad-viewer featuring:

1. **Basic Usage** - Simple box visualization
2. **Custom Settings** - Quality, colors, and display options
3. **Complex Assembly** - Fusing multiple shapes
4. **Documentation** - API reference and controls

## Requirements

The examples require:
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- marimo (installed automatically via sandbox metadata)
- build123d (installed automatically via sandbox metadata)

## Sandbox Notebook Details

Each example includes PEP 723 metadata at the top:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "anywidget-cad-viewer",
#     "marimo",
#     "build123d>=0.10.0",
# ]
#
# [tool.uv.sources]
# anywidget-cad-viewer = { path = "../", editable = true }
# ///
```

This metadata:
- Specifies Python version requirements
- Lists notebook-specific dependencies
- Configures editable install of the local package
- Enables `uv run` to automatically manage environments

## Troubleshooting

### "ModuleNotFoundError: No module named 'build123d'"

Make sure you're using `uv run` to execute the notebook:
```bash
uv run examples/marimo_quickstart.py
```

### Widget doesn't render

The widget requires JavaScript support. Make sure you're viewing the notebook in:
- marimo's web interface (`marimo edit`)
- Jupyter with anywidget support
- A browser with JavaScript enabled

### Import errors in marimo editor

If you see import errors when opening with `marimo edit --sandbox`, they should resolve once marimo installs the dependencies. Wait for the installation to complete.

## Learn More

- [marimo Documentation](https://docs.marimo.io/)
- [build123d Documentation](https://build123d.readthedocs.io/)
- [anywidget Documentation](https://anywidget.dev/)
- [anywidget-cad-viewer GitHub](https://github.com/build123d/anywidget-cad-viewer)
