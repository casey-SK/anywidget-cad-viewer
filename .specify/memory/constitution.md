<!--
Sync Impact Report - Constitution Update
================================================================================
Version change: 1.1.0 → 1.2.0
Modified principles: N/A
Added sections:
  - Core Principles: VII. uv and pyproject.toml as Source of Truth (new principle)
  - Technical Standards: Package Management subsection added
Removed sections: N/A
Templates requiring updates:
  [PENDING] .specify/templates/plan-template.md (Constitution Check section needs Principle VII gates)
  [OK] .specify/templates/spec-template.md (No changes needed - no dependency management)
  [OK] .specify/templates/tasks-template.md (No changes needed - tasks reference plan decisions)
  [OK] Command files (.opencode/command/*.md) (No changes needed - enforce via checks)
Follow-up TODOs:
  - Document pyproject.toml structure example in plan-template
  - Add uv sync validation to implementation workflow
Previous updates:
  - v1.0.0 → v1.1.0: Added Principle VI (No Emojis)
================================================================================
-->

# anywidget-cad-viewer Constitution

## Core Principles

### I. Widget-First Architecture

Every feature must be designed as a reusable anywidget component. The widget must:
- Be self-contained with clear input/output contracts
- Work independently in marimo notebooks, Jupyter notebooks, and other anywidget-compatible environments
- Expose a clean Python API for build123d object visualization
- Maintain compatibility with the anywidget specification

**Rationale**: As a visualization tool built on anywidget, the core value proposition is providing a reusable, embeddable widget. All features must support this primary use case to ensure the tool remains focused and interoperable.

### II. Build123d Integration

All visualization features must correctly interpret and render build123d objects. The viewer must:
- Support all standard build123d geometric primitives and assemblies
- Preserve build123d object properties (materials, colors, metadata)
- Handle coordinate systems and transformations correctly
- Provide feedback when objects cannot be visualized

**Rationale**: The tool exists specifically to visualize build123d CAD objects. Integration correctness is non-negotiable and must be validated for every feature that touches object rendering.

### III. Minimal Dependencies

Dependency additions require explicit justification. The project must:
- Leverage existing OCP ecosystem libraries (ocp-vscode, jupyter-cadquery patterns)
- Avoid redundant functionality that duplicates existing dependencies
- Document rationale for each new dependency in design artifacts
- Prefer lightweight solutions over feature-rich but heavy alternatives

**Rationale**: Based on bernhard-42's tooling philosophy and the marimo notebook use case, users expect fast load times and minimal setup. Every dependency adds installation complexity, load time, and maintenance burden.

### IV. Test When It Matters

Testing is encouraged but not mandatory. Tests are required when:
- User explicitly requests tests in the feature specification
- Feature involves geometric calculations or transformations (correctness-critical)
- Feature changes existing rendering behavior (regression risk)
- Feature adds new build123d object type support (integration validation)

When tests are written:
- Integration tests must verify actual rendering output
- Unit tests should focus on data transformation and coordinate math
- Visual regression tests (if implemented) must be deterministic

**Rationale**: For a visualization tool, manual inspection during development often provides better feedback than extensive unit testing. However, geometric correctness and object compatibility are critical areas where automated tests add significant value.

### V. Notebook-Centric Experience

Features must prioritize the notebook user experience. This means:
- Interactive controls embedded in the widget when possible
- Clear error messages visible in notebook output cells
- Reasonable default visualizations requiring minimal configuration
- Documentation with inline notebook examples

**Rationale**: The primary users are engineers and designers working in notebooks (marimo, Jupyter). Features optimized for other contexts (CLIs, standalone apps) dilute focus and add complexity without serving the core audience.

### VI. No Emojis

Emojis are banned from all project artifacts. This prohibition applies to:
- Source code (Python, JavaScript, TypeScript, etc.)
- Code comments and docstrings
- Documentation files (README, guides, specs, plans, tasks)
- Commit messages and pull request descriptions
- Issue titles and comments
- Configuration files and schemas

**Rationale**: Emojis introduce visual noise, reduce searchability, complicate internationalization, and create inconsistent presentation across different tools and terminals. Professional engineering projects benefit from text-only communication that is universally readable and machine-parseable.

### VII. uv and pyproject.toml as Source of Truth

All Python dependency management must use uv with pyproject.toml as the single source of truth. This requires:

**Dependency Structure**:
- `[project.dependencies]` for runtime requirements
- `[project.optional-dependencies]` for user-facing extras (e.g., `[examples]`, `[visualization]`)
- `[dependency-groups.dev]` for development tools (linters, formatters)
- `[dependency-groups.test]` for testing frameworks (pytest, coverage)
- `[dependency-groups.docs]` for documentation generation

**Lock File Management**:
- `uv.lock` must be committed to version control
- Regenerate lock with `uv lock` after every pyproject.toml modification
- Lock file must sync before commits (auto-sync policy)
- CI must validate lock file is up-to-date

**uv Commands Only**:
- Install: `uv pip install` or `uv sync` (NOT pip install)
- Add dependency: `uv add <package>` (NOT manual pyproject.toml edits)
- Add dev dependency: `uv add --group dev <package>`
- Remove: `uv remove <package>`
- Upgrade: `uv lock --upgrade-package <package>`

**Prohibited Practices**:
- Manual pyproject.toml dependency edits (use `uv add` instead)
- Using pip, poetry, or other package managers
- requirements.txt files (except for legacy compatibility exports)
- Uncommitted or out-of-sync uv.lock files

**Rationale**: uv provides fast, deterministic dependency resolution with a clear workflow. Using pyproject.toml as the single source of truth eliminates dependency drift, simplifies onboarding, and ensures reproducible environments. The PEP 735 dependency groups standard allows fine-grained control for different workflows while maintaining compatibility.

## Technical Standards

### Python Version & Dependencies

- **Python Version**: 3.13+ (as specified in pyproject.toml)
- **Core Dependencies**: ocp-vscode 3.0.1+ (established OCP visualization library)
- **Widget Framework**: anywidget (version TBD based on compatibility requirements)

**Package Management**:
- All dependency operations use uv exclusively (Principle VII)
- pyproject.toml: single source of truth for all dependencies
- uv.lock: committed and synchronized on every change
- Dependency groups: dev (development tools), test (testing), docs (documentation)
- User extras: [project.optional-dependencies] for installable features

### Code Quality

- Type hints required for public APIs
- Docstrings required for widget parameters and public methods
- Linting and formatting tools must be configured before Phase 1 implementation
- No hardcoded paths or platform-specific assumptions
- No emojis in any code or documentation (Principle VI)

### Performance Expectations

- Widget initialization: <500ms for simple objects (<1000 vertices)
- Rendering: 60fps for interactive rotation/zoom on medium-complexity objects
- Memory: <100MB overhead per widget instance for typical notebook usage
- File size: Widget bundle <2MB compressed

## Development Workflow

### Feature Development Process

1. **Specification** (`/speckit.specify`): Define what users need (no implementation details)
2. **Planning** (`/speckit.plan`): Research and design technical approach
3. **Tasks** (`/speckit.tasks`): Break down into implementation tasks
4. **Implementation** (`/speckit.implement`): Execute tasks with constitution compliance

### Constitution Compliance Gates

**Before Phase 0 Research**:
- [ ] Feature designed as anywidget component (Principle I)
- [ ] Build123d integration requirements identified (Principle II)
- [ ] New dependencies justified in plan (Principle III)
- [ ] Test requirements clarified if needed (Principle IV)
- [ ] Notebook UX considered in user scenarios (Principle V)
- [ ] No emojis in specification or planning documents (Principle VI)
- [ ] pyproject.toml structure follows uv conventions (Principle VII)
- [ ] No manual dependency edits or requirements.txt files (Principle VII)

**After Phase 1 Design**:
- [ ] Widget API contract defined in contracts/
- [ ] Build123d object types supported documented
- [ ] Dependencies reviewed and justified
- [ ] Test strategy documented if tests required
- [ ] Example notebook usage in quickstart.md
- [ ] All design artifacts emoji-free (Principle VI)
- [ ] uv.lock synchronized with pyproject.toml (Principle VII)
- [ ] All dependencies added via uv commands (Principle VII)

### Breaking Changes

- **Widget API changes**: MAJOR version bump (breaks existing notebooks)
- **New visualization features**: MINOR version bump (backward compatible)
- **Bug fixes and optimizations**: PATCH version bump

## Governance

### Constitution Authority

This constitution supersedes all other documentation and practices. When conflicts arise:
1. Constitution principles take precedence
2. Template guidance defers to constitution
3. Command workflows enforce constitution gates

### Amendment Process

1. **Proposal**: Document proposed change with rationale
2. **Impact Analysis**: Identify affected templates, commands, and features
3. **Version Bump**: Apply semantic versioning to constitution version
4. **Propagation**: Update all dependent artifacts (templates, commands)
5. **Documentation**: Record in Sync Impact Report

### Compliance Review

- All specifications must pass Constitution Check gates
- Code reviews must verify principle adherence
- Complexity violations require documented justification in plan.md
- Feature branches must reference constitution version in plan.md
- All artifacts must be emoji-free (Principle VI)

### Runtime Guidance

For development workflow and command execution guidance, refer to:
- `.opencode/command/speckit.*.md` - Command execution workflows
- `.specify/templates/*-template.md` - Artifact structure and requirements

**Version**: 1.2.0 | **Ratified**: 2026-01-11 | **Last Amended**: 2026-01-11
