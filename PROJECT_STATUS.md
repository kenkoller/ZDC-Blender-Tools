# ZDC Blender Tools — Project Status Report

**Updated:** 2026-02-06
**Analyst:** Claude Opus 4.6
**Workspace:** `/Users/KK/My Drive/Ziti Creative/R&D/ZDC-Blender-tools/`
**Repository:** `git@github.com:kenkoller/ZDC-Blender-Tools.git`

---

## Executive Summary

The workspace is a fully established **git monorepo** hosted on GitHub with 5 installable Blender add-ons under `addons/` plus one integrated third-party addon (Home Builder). The bootstrap process (Phases 1-5, 7) is complete — addons are restructured, shared utilities extracted, scripts created, and documentation in place. Phase 6 (archive old GitHub repos) is deferred.

Of the five ZDC addons, **cabinet-generator** is production-grade, **auto-batch-renderer** is functional and restructured, **universal-pbr-shader** is the consolidated shader addon (v2.0.0, incorporating metallic flake presets), **kitchen-generator** remains an empty stub, and **home-builder** is an integrated GPLv3 addon by Andrew Peel.

---

## 1. Bootstrap Status

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Initialize workspace as git monorepo | COMPLETE |
| **Phase 2** | Import and reorganize addons into `addons/` | COMPLETE |
| **Phase 3** | Extract common utilities into `common/` | COMPLETE |
| **Phase 4** | Create project README and utility scripts | COMPLETE |
| **Phase 5** | Set up BlenderMCP | PARTIAL — docs written, `uv` not yet installed |
| **Phase 6** | Archive old GitHub repositories | DEFERRED |
| **Phase 7** | Final review and validation | COMPLETE |

### Recent Changes (this session)

- **Metallic flake shader sunset:** The dedicated `metallic-flake-shader` addon has been removed. Its 7 built-in presets were ported to `universal-pbr-shader` v2.0.0, which was already a strict superset of the metallic flake functionality.
- **Home Builder 4.5 cleanup:** The ~300MB reference copy at workspace root (`home-builder-4.5/`) has been deleted. The addon lives at `addons/home-builder/`.
- **Auto-batch-renderer restructuring:** Previously restructured from a 2,251-line monolith into 6 modules (properties, operators, panels, handlers, src/framing).

---

## 2. Addon Status

### 2.1 Cabinet Generator

**Status: PRODUCTION-GRADE** | **Version:** 4.0.0 | **~8,000+ lines across 44 files**

The most advanced addon in the project. Pure Geometry Nodes with programmatic Python generation. Clean 5-level hierarchy (Master > Systems > Atomic > Utils > Materials).

- 10 cabinet types, 3 categories (Kitchen/Vanity/Closet)
- 15 atomic components, 10 system components
- 5 door styles, 5 handle styles, 3 hinge/slide styles
- Door/drawer animation, face frame construction
- Cut list export (CSV/JSON/clipboard), 14 built-in presets
- Rev-A-Shelf lazy susan compatibility (graceful degradation when specs unavailable)

**Known limitations:** Shelf pin count not parametric by height, glass door rotation issue with double doors, simplified molding profiles (box geometry).

### 2.2 Auto Batch Renderer

**Status: FUNCTIONAL / RESTRUCTURED** | **Version:** 5.3.0 | **6 modules**

Restructured from monolith into properties, operators, panels, handlers, and src/framing modules. Uses `ABR_` class prefix (ZDC_ rename deferred).

- Multi-view batch rendering with automatic camera framing
- Perspective and orthographic camera support
- Turntable animation (4 modes)
- Product collection management, compositor setup
- Fine-tuning controls, cancel mid-batch

**Needs:** Type hints, docstrings, `context.area` validation in timer callback.

### 2.3 Universal PBR Shader

**Status: PRODUCTION-READY** | **Version:** 2.0.0 | **~3,239 lines**

The single consolidated shader addon for ZDC tools. As of v2.0.0, includes the metallic flake sparkle system presets (formerly a separate addon).

- Full PBR shader with 10 texture map slots (albedo, normal, roughness, metallic, AO, displacement, emission, opacity, SSS, clearcoat)
- 3-layer sparkle system (Voronoi + view-based flake visibility)
- Base material with IOR, roughness, surface grain, anisotropic, clearcoat
- 13 built-in presets: 6 general (default, chrome, matte plastic, brushed metal, glossy ceramic, frosted glass) + 7 metallic flake (silver automotive, gold, midnight blue pearl, candy apple red, gunmetal gray, champagne, plastic toy coarse)
- Preset system (built-in + user-saved JSON)
- Uses `MATERIAL_` class prefix (ZDC_ rename deferred)

### 2.4 Kitchen Generator

**Status: EMPTY STUB** | **Version:** 1.0.0 | **21 lines**

Single `__init__.py` with empty `register()`/`unregister()`. No operators, panels, properties, or logic. Three ProKitchen specification documents in `docs/` describe what this should become.

### 2.5 Home Builder

**Status: INTEGRATED (Third-Party)** | **Author:** Andrew Peel | **License:** GPLv3

Complete interior design asset library using PyClone architecture. Includes wall generation, asset placement, material libraries, and product libraries. Architecturally different from ZDC's Geometry Nodes approach — uses pre-modeled assets. See `addons/home-builder/ATTRIBUTION.md`.

---

## 3. Shared Infrastructure

### `common/`

| Module | Purpose |
|--------|---------|
| `naming.py` | ZDC naming conventions, addon prefix mapping, class name builders |
| `node_utils.py` | Cross-addon node tree manipulation helpers (get/create node groups, ensure sockets) |
| `color_standards.py` | Calibrated color accuracy constants |

### `scripts/`

| Script | Purpose |
|--------|---------|
| `install_addons.py` | Symlink installer for all addons into Blender user directory |
| `validate_bl_info.py` | Validates bl_info metadata across all addons |

---

## 4. Class Naming Status

The ZDC naming convention (`ZDC_OT_`, `ZDC_PT_`, `ZDC_PG_`) is defined in `common/naming.py` and `CLAUDE.md` but has **not been applied** to addon class names yet. Current prefixes:

| Addon | Current Prefix | Target Prefix |
|-------|---------------|---------------|
| cabinet-generator | `CABINET_` | `ZDC_OT_CabinetGen_` etc. |
| auto-batch-renderer | `ABR_` | `ZDC_OT_BatchRender_` etc. |
| universal-pbr-shader | `MATERIAL_` | `ZDC_OT_UniversalPBR_` etc. |

This rename is deferred as a dedicated branch task due to the number of classes involved.

---

## 5. Dependency Graph

```
kitchen-generator (future)
  └── depends on → cabinet-generator (GN body)
  └── depends on → component-library (future, materials/profiles/assets)
  └── may use → auto-batch-renderer (rendering pipeline)

cabinet-generator (standalone)
  └── optional → reference/revashelf_specs.py (graceful degradation)

auto-batch-renderer (standalone)
  └── no dependencies

universal-pbr-shader (standalone)
  └── no dependencies

home-builder (standalone, third-party)
  └── no dependencies on ZDC addons
```

---

## 6. What's Next — Priority Recommendations

### Immediate

1. **BlenderMCP setup** — Install `uv` package manager, configure Claude Desktop MCP server, test live Blender connection
2. **ZDC class prefix rename** — Apply `ZDC_OT_`/`ZDC_PT_`/`ZDC_PG_` convention across all addons (dedicated branch)

### Short-Term

3. **Auto-batch-renderer polish** — Add type hints, docstrings, fix `context.area` validation
4. **Component Library infrastructure** — Create library API, .blend file format, tier separation
5. **Procedural master wood shader** — Highest-value material work for cabinet-generator

### Medium-Term

6. **Kitchen generator implementation** — Room generation, layout engine (per ProKitchen specs)
7. **Profile curve library** — Replace simplified box moldings with proper swept curves
8. **Countertop generation system**

### Long-Term

9. Appliance and fixture libraries
10. Backsplash tile pattern system
11. Style preset system (coordinated whole-kitchen looks)

---

## 7. File Tree — Current State

```
ZDC-Blender-Tools/                          (git monorepo)
├── .git/
├── .gitattributes                          (LFS tracking: .blend, .png, .jpg, .jpeg)
├── .gitignore
├── BOOTSTRAP_PROMPT.md
├── CLAUDE.md                               (project intelligence / conventions)
├── CLAUDE.local.md                         (gitignored — private client context)
├── COMPONENT_LIBRARY_MASTER_PLAN.md
├── LICENSE                                 (GPLv3)
├── PROJECT_STATUS.md                       (this file)
├── README.md
│
├── addons/
│   ├── auto-batch-renderer/                (6 modules, v5.3.0)
│   │   ├── __init__.py
│   │   ├── properties.py
│   │   ├── operators.py
│   │   ├── panels.py
│   │   ├── handlers.py
│   │   ├── README.md
│   │   └── src/
│   │       └── framing.py
│   │
│   ├── cabinet-generator/                  (44 files, v4.0.0)
│   │   ├── __init__.py
│   │   ├── operators.py
│   │   ├── panels.py
│   │   ├── properties.py
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   └── src/
│   │       ├── cut_list_export.py
│   │       ├── cabinet_presets.py
│   │       ├── batch_generation.py
│   │       ├── batch_lazy_susan.py
│   │       └── nodes/  (utils, master, material_presets, atomic/, systems/)
│   │
│   ├── home-builder/                       (GPLv3, Andrew Peel)
│   │   ├── __init__.py
│   │   ├── ATTRIBUTION.md
│   │   ├── LICENSE
│   │   └── ... (full PyClone addon)
│   │
│   ├── kitchen-generator/                  (empty stub)
│   │   └── __init__.py
│   │
│   └── universal-pbr-shader/               (v2.0.0, consolidated shader)
│       ├── __init__.py
│       ├── universal_pbr_shader.py
│       └── README.md
│
├── common/
│   ├── __init__.py
│   ├── naming.py
│   ├── node_utils.py
│   └── color_standards.py
│
├── docs/
│   ├── ProKitchen_Master_Architecture_v1.1.md
│   ├── ProKitchen_Cabinet_GN_Spec_v1.1.md
│   └── ProKitchen_Layout_Engine_Spec_v1.1.md
│
├── mcp/
│   └── README.md
│
├── reference/                              (gitignored — local only)
│   ├── revashelf_specs.py
│   └── 24_25_SpecGuide-compressed_A.*
│
├── scripts/
│   ├── install_addons.py
│   └── validate_bl_info.py
│
└── tests/
    ├── run_tests.py
    └── test_scenes/
```

---

## 8. Summary Scorecard

| Area | Score | Notes |
|------|-------|-------|
| **Workspace Setup** | 9/10 | Monorepo established, structured, on GitHub. BlenderMCP not yet connected. |
| **Cabinet Generator** | 8/10 | Production-grade, well-architected, needs ZDC naming compliance |
| **Auto Batch Renderer** | 6/10 | Functional, restructured from monolith, needs polish (types, docs) |
| **Universal PBR Shader** | 7/10 | Consolidated shader with 13 presets, needs ZDC naming compliance |
| **Kitchen Generator** | 0/10 | Empty stub |
| **Home Builder** | N/A | Third-party integration, working as-is |
| **Component Library** | 0/10 | Planned but not started |
| **Documentation** | 8/10 | CLAUDE.md, README, addon READMEs, ProKitchen specs, master plan |
| **Cross-Addon Integration** | 3/10 | Common utilities extracted but no library API or shared material system |

---

*End of report. Updated 2026-02-06 by Claude Opus 4.6.*
