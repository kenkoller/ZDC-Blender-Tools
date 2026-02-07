# ZDC Blender Tools — Project Intelligence

## Project Overview

This is the unified development workspace for **Ziti Design & Creative (ZDC)** Blender add-ons and tools. All add-ons target **Blender 5.0+** exclusively (no backward compatibility with 4.x). Development happens on both macOS and Windows — all code must be cross-platform.

These tools support professional 3D product visualization workflows including high-volume batch rendering, procedural material creation, and parametric model generation.

**Private context:** If the file `CLAUDE.local.md` exists in this project root, read it for additional private context about specific clients, color standards, and production pipeline details that are not included in this public-facing document.

## Architecture

```
ZDC-Blender-Tools/
├── CLAUDE.md                      ← You are here (public project conventions)
├── CLAUDE.local.md                ← Private client context (gitignored, local only)
├── BOOTSTRAP_PROMPT.md            ← One-time setup prompt for workspace initialization
├── README.md                      ← Project overview and add-on index
├── .gitignore
├── addons/                        ← All installable Blender add-ons
│   ├── auto-batch-renderer/       ← Automated batch rendering pipeline
│   ├── cabinet-generator/         ← Parametric cabinet generation system
│   ├── home-builder/              ← Room/house construction (Andrew Peel, GPLv3)
│   ├── kitchen-generator/         ← Kitchen scene/layout generation
│   ├── universal-pbr-shader/      ← PBR shader with texture maps and metallic flake sparkle
│   └── [future-addons]/           ← New add-ons get created here
├── common/                        ← Shared utilities (extract when patterns emerge)
│   ├── __init__.py
│   ├── node_utils.py              ← Shared node tree manipulation helpers
│   ├── color_standards.py         ← Calibrated color accuracy constants/utilities
│   └── naming.py                  ← Consistent naming conventions and ID prefixes
├── scripts/                       ← Standalone utility scripts (not add-ons)
│   ├── install_addons.py          ← Script to symlink/install all addons into Blender
│   └── validate_bl_info.py        ← Validate all add-on bl_info metadata
└── tests/                         ← Cross-addon test resources
    ├── test_scenes/               ← .blend files for validation
    └── run_tests.py               ← Test runner (blender --background --python)
```

## Coding Conventions

### Operator and Class Naming

All ZDC operators, panels, and property groups follow this prefix convention:

**Operators:** `ZDC_OT_{AddonName}_{action}` (e.g., `ZDC_OT_BatchRender_execute`). The `bl_idname` for operators uses dots: `zdc.batchrender_execute`

**Panels:** `ZDC_PT_{AddonName}_{section}` (e.g., `ZDC_PT_UniversalPBR_settings`)

**Property Groups:** `ZDC_PG_{AddonName}_{name}` (e.g., `ZDC_PG_CabinetGen_dimensions`)

**Menus:** `ZDC_MT_{AddonName}_{name}`

### Add-on Structure Standard

Every add-on in `addons/` should follow this structure at minimum:

```
addon-name/
├── __init__.py          ← bl_info, register/unregister, imports
├── operators.py         ← All operator classes
├── panels.py            ← UI panel classes
├── properties.py        ← PropertyGroup definitions
├── README.md            ← Add-on specific docs, usage, known issues
└── src/                 ← Business logic (not Blender-dependent where possible)
    ├── __init__.py
    └── core_logic.py    ← Separates computation from Blender API calls
```

Larger add-ons (like cabinet-generator) can have additional subdirectories (`nodes/`, `atomic/`, `systems/`) as appropriate.

### bl_info Standard

Every add-on's `__init__.py` must include:

```python
bl_info = {
    "name": "ZDC - [Add-on Name]",
    "author": "Ziti Design & Creative",
    "version": (X, Y, Z),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > ZDC",
    "description": "...",
    "category": "ZDC Tools",
}
```

All ZDC add-ons appear under the **ZDC** sidebar tab in the 3D Viewport.

### Python Style

Python 3.11+ (Blender 5.0's bundled Python). Type hints on function signatures. Docstrings on all public classes and non-trivial functions. `snake_case` for functions/variables, `PascalCase` for classes. No wildcard imports (`from module import *`). Keep Blender API calls (`bpy.*`) in operators/panels; business logic in `src/` should be testable without Blender where feasible.

### Node Tree / Shader Conventions

Custom node groups use prefix: `ZDC_` (e.g., `ZDC_MetallicFlake_v2`). Node group versioning: append `_v{N}` to node group names when making breaking changes. Color-critical work must reference the calibrated color standards in `common/color_standards.py`. All procedural materials should be Cycles-compatible; EEVEE support is secondary.

### Blender 5.0 Specifics

Use the new extension system where applicable. Be aware of deprecated API changes from 4.x → 5.0 (check release notes). Test registration/unregistration cleanly — no orphaned properties or handlers.

## Production Context

The primary production workflow involves receiving engineering files (typically from Fusion 360), importing/preparing meshes in Blender (mesh export optimization from F360 is an ongoing concern), applying materials with strict color accuracy (cross-polarized photography reference workflow), automated batch rendering, and post-processing and delivery.

Color accuracy is non-negotiable in professional product visualization. Materials must match physical product samples under calibrated lighting conditions. The `common/color_standards.py` module should be the single source of truth for calibrated color values. See `CLAUDE.local.md` for client-specific color standards and pipeline details.

The rendering environment uses Cycles as the primary engine, high-end GPUs (RTX 5090 class) for GPU rendering, and handles high-volume batch rendering (32-64 renders per day at typical volume).

## BlenderMCP Integration

This project uses the BlenderMCP add-on (by ahujasid on GitHub) to connect Claude Desktop to a running Blender instance via the Model Context Protocol. This enables live scene inspection and manipulation during development, interactive testing of add-on code without manual copy-paste, and running arbitrary Python in Blender's context from Claude Desktop conversations.

The MCP connection is a **development tool** — it does not ship with the add-ons and is not required for end users.

### How it works

A Blender add-on (`addon.py` from the BlenderMCP repo) runs a socket server inside Blender on port 9876. Claude Desktop launches an MCP server process (via `uvx blender-mcp`) that bridges that socket connection to Claude through the Model Context Protocol. Claude can then send Python commands directly into Blender's interpreter, inspect scenes, manipulate objects and materials, and execute scripts.

### Setup

The bootstrap prompt (Phase 5) handles the automated portions of MCP setup: installing the `uv` package manager, downloading the BlenderMCP `addon.py`, and writing the correct Claude Desktop configuration file for your platform. Claude Code will execute these steps directly on your machine and then walk you through the three manual GUI steps it cannot perform (installing the addon in Blender, starting the MCP server, restarting Claude Desktop).

### MCP Safety Notes

The `execute_blender_code` tool runs arbitrary Python inside Blender. Always save your .blend file before using Claude to make changes. For complex operations, break requests into smaller steps. The first command after connecting sometimes fails — just retry.

## Git Workflow

This project is hosted on GitHub at `kenkoller/ZDC-Blender-Tools`. The `main` branch is stable/working code. Feature branches for new add-ons or significant changes: `feature/{addon-name}/{description}`. Commit messages: `[addon-name] description` (e.g., `[auto-batch-renderer] Add camera framing presets`). Tag releases: `{addon-name}-v{X.Y.Z}`. **Always commit working state before major refactors.**

### What does NOT go in this repository

Client-specific information (names, proprietary color values, contract details), reference PDFs or spec guides from clients, and the `CLAUDE.local.md` file are all excluded from version control and should never be committed. These live locally on your development machine only. The `.gitignore` is configured to enforce this.

## When Creating a New Add-on

1. Create directory under `addons/` following the naming convention (lowercase, hyphenated)
2. Scaffold using the standard structure above
3. Reference existing add-ons for pattern consistency (especially cabinet-generator for complex examples)
4. Add entry to the project README.md add-on index
5. Ensure the add-on registers/unregisters cleanly in isolation

## When Modifying Existing Code

1. Understand the current behavior first — read the relevant README.md and source
2. Check for cross-addon dependencies (especially anything in `common/`)
3. Test registration/unregistration after changes
4. If the change affects a production pipeline, flag it explicitly
