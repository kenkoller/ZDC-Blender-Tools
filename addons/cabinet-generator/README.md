# ZDC - Cabinet Generator

Parametric cabinet generation system for Blender 5.0+ using Geometry Nodes.

## Features

- 10 cabinet types: Base, Upper, Vanity, Tall/Pantry, Sink Base, Blind Corner, Lazy Susan Corner, Appliance Garage, Drawer Base, Open Shelf
- Pure Geometry Nodes architecture — all geometry is procedural and non-destructive
- Real-time parameter adjustment (width, height, depth, panel thickness, etc.)
- Face frame and frameless construction modes
- Configurable doors, drawers, shelving, and lazy susan inserts
- Toe kick, back panel, and hardware options
- Cut list export
- Cabinet presets system
- Batch generation for lazy susan configurations

## Architecture

The addon uses a 5-level Geometry Nodes hierarchy, all created programmatically in Python:

```
CabinetMaster           ← Top-level node group (selects cabinet type)
├── Systems             ← Complete cabinet assemblies (BaseCabinetSystem, etc.)
│   ├── Atomic          ← Individual components (Panel, Door, Drawer, Shelf, etc.)
│   │   └── Utils       ← Low-level geometry operations
│   └── Materials       ← Material assignment nodes
```

## Structure

```
cabinet-generator/
├── __init__.py
├── properties.py          ← All PropertyGroup definitions
├── operators.py           ← Operators (generate, delete, update, etc.)
├── panels.py              ← UI panels
└── src/
    ├── nodes/             ← Geometry Nodes generation (master, systems, atomic, utils)
    ├── cut_list_export.py ← Export cut dimensions
    ├── cabinet_presets.py ← Save/load preset configurations
    ├── batch_generation.py
    └── batch_lazy_susan.py ← Batch lazy susan generation (requires proprietary specs)
```

## Notes

- `batch_lazy_susan.py` requires a proprietary specs file not included in the public repository. It degrades gracefully when the file is missing.
- Node creation uses the Blender 5.0+ `ng.interface.new_socket()` API exclusively.
