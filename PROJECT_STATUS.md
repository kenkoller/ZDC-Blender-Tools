# ZDC Blender Tools — Project Status Report

**Generated:** 2026-02-06
**Analyst:** Claude Opus 4.6
**Workspace:** `/Users/KK/My Drive/Ziti Creative/R&D/ZDC-Blender-tools/`

---

## Executive Summary

The workspace contains four Blender addons, a reference copy of Home Builder 4, three ProKitchen design specifications, a Component Library Master Plan, and bootstrap/project documentation. **The bootstrap process (BOOTSTRAP_PROMPT.md) has not been executed** — addons are loose at the root level, there is no git repository, and no workspace restructuring has occurred. Of the four addons, only the **cabinet-generator** is production-grade. The auto-batch-renderer and metallic-flake-shader are functional but need ZDC convention compliance. The kitchen-generator is an empty stub. The Component Library Master Plan describes an ambitious system that is largely unbuilt, though the cabinet-generator provides a strong foundation for its cabinet-related goals.

---

## 1. Workspace Bootstrap Status

The BOOTSTRAP_PROMPT.md defines 7 phases. **None have been executed.**

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Initialize workspace as git monorepo | NOT STARTED |
| **Phase 2** | Import and reorganize addons into `addons/` | NOT STARTED |
| **Phase 3** | Extract common utilities into `common/` | NOT STARTED |
| **Phase 4** | Create project README and utility scripts | NOT STARTED |
| **Phase 5** | Set up BlenderMCP | NOT STARTED |
| **Phase 6** | Archive old GitHub repositories | NOT STARTED |
| **Phase 7** | Final review and validation | NOT STARTED |

### Current Workspace Issues

- **No git repository** — `.git` does not exist at workspace root
- **No `addons/` directory** — all addons sit at the root level
- **No `common/` directory** — no shared utilities extracted
- **No `scripts/` directory** — no install_addons.py or validate_bl_info.py
- **No `tests/` directory** at root level
- **No `mcp/` directory** — no BlenderMCP setup documentation
- **No root README.md**
- **`gitignore` needs renaming** to `.gitignore` (missing leading dot)
- **Individual `.git` repos** inside each addon — need to be removed for monorepo
- **Proprietary files present** — `cabinet-generator/24_25_SpecGuide-compressed_A.pdf` and `.rtf` must not be committed
- **`__pycache__/` directories** present in addon folders

### Extra Items Not Described in Bootstrap

- `home-builder-4.5/` — Reference copy of Andrew Peel's Home Builder 5 (GPLv3). Bootstrap says to fork this separately, not include in monorepo.
- `GN Cabinet Generator/` and `Kitchen Generator/` — Empty placeholder folders (only contain macOS Icon files). Can be deleted.
- `ProKitchen_Master_Architecture_v1.1.md`, `ProKitchen_Cabinet_GN_Spec_v1.1.md`, `ProKitchen_Layout_Engine_Spec_v1.1.md` — Design specifications for a unified kitchen generation system. Not mentioned in bootstrap. Should be moved to a `docs/` or `specs/` directory.
- `COMPONENT_LIBRARY_MASTER_PLAN.md` — Not mentioned in bootstrap. Should be kept at root or moved to `docs/`.

---

## 2. Addon-by-Addon Status

### 2.1 Cabinet Generator

**Status: PRODUCTION-GRADE / Most Advanced Addon**
**Version:** 2.0.0 (bl_info) / v4.0.0 (internal PROJECT_STATUS)
**Lines of Code:** ~8,000+ across 44 Python files

| Aspect | Status | Detail |
|--------|--------|--------|
| File structure | GOOD | Follows standard layout: operators.py, panels.py, properties.py, src/ |
| bl_info compliance | PARTIAL | Name: "Cabinet Generator" (should be "ZDC - Cabinet Generator"), Category: "Add Mesh" (should be "ZDC Tools") |
| Class naming | CONSISTENT but NON-ZDC | Uses `CABINET_OT_`, `CABINET_PT_`, `CABINET_PG_` (should be `ZDC_OT_CabinetGen_`, etc.) |
| Blender 5.0 API | COMPLIANT | Uses modern `ng.interface.new_socket()` API throughout |
| Client references | PRESENT | `src/revashelf_specs.py` (629 lines of product specs) must not be committed to public repo |
| Documentation | GOOD | Has README.md, CLAUDE.md, PROJECT_STATUS.md |
| Testing | COMPREHENSIVE | 4 test scripts, JSON report generation, visual test scene |

**Implemented Features (complete):**
- 10 cabinet types (Base, Wall, Tall, Drawer Base, Blind Corner, Sink Base, Appliance, Open Shelving, Diagonal Corner, Pullout Pantry)
- 3 cabinet categories (Kitchen 24", Vanity 21", Closet 14")
- 15 atomic components (shelf, door panel, drawer, hardware, toe kick, lazy susan, hinges, drawer slides, trash pullout, spice rack, shelf pins, LED strip, crown molding, light rail)
- 10 system components
- CabinetMaster v4.0 orchestrator
- 5 door panel styles (Flat, Shaker, Raised, Recessed, Double Shaker)
- 5 handle styles (Bar, Wire, Knob, Cup Pull, Edge Pull)
- 3 hinge styles, 3 drawer slide styles, 3 lazy susan styles
- Door/drawer open animation
- Face frame construction option
- Material presets (Wood, Laminate, Metal)
- Cut list export (CSV, JSON, clipboard)
- 14 built-in cabinet presets + save/load system
- Batch generation workflows
- Rev-A-Shelf lazy susan compatibility

**Known Limitations:**
- Shelf pin count fixed (not parametric by height)
- Glass door rotation issue with double doors
- Molding profiles simplified (box geometry, not curve-based)
- Auto double-door width threshold not fully wired

**Architecture Notes:**
Pure Geometry Nodes with programmatic Python generation. Clean 5-level hierarchy (Master > Systems > Atomic > Utils > Materials). Python source is version-controlled; .blend files tracked via Git LFS. This is the strongest codebase in the project.

---

### 2.2 Auto Batch Renderer

**Status: FUNCTIONAL / NEEDS RESTRUCTURING**
**Version:** 5.3.0
**Lines of Code:** ~2,250 in a single file

| Aspect | Status | Detail |
|--------|--------|--------|
| File structure | MONOLITHIC | Everything in `auto_batch_renderer.py` (2,251 lines). No operators.py/panels.py/properties.py split. |
| bl_info compliance | WRONG | Name: "Auto Batch Renderer" (should be "ZDC - Auto Batch Renderer"), Blender: (4,2,0) (should be (5,0,0)), Category: "Render" (should be "ZDC Tools"), Author: "Gemini & Ken" |
| Class naming | CONSISTENT but NON-ZDC | Uses `ABR_OT_`, `ABR_PT_`, `ABR_PG_` (should be `ZDC_OT_AutoBatchRenderer_`, etc.) |
| Blender 5.0 API | LIKELY COMPATIBLE | No obvious 5.0 breaking changes, but bl_info claims 4.2.0 minimum |
| Client references | CLEAN | No explicit Rev-A-Shelf references. Default angles/patterns embed client workflow implicitly. |
| Documentation | MISSING | No README.md |
| Testing | NONE | No test infrastructure |

**Implemented Features:**
- Multi-view batch rendering with automatic camera framing
- Perspective and orthographic camera support
- Turntable animation (4 modes: easing, multi-segment, random, hold points)
- Light modifier exclusion from framing calculations
- Product collection management (ABR_Products, ABR_Studio_Camera, ABR_Light_Modifiers)
- Compositor setup with alpha/background control
- Fine-tuning controls (position offset, size multiplier, rotation)
- Cancel rendering mid-batch
- Timeline marker management

**Issues Requiring Attention:**
- `"blender": (4, 2, 0)` must be updated to `(5, 0, 0)`
- Default output path uses Windows backslash: `'//renders\\'` — should be `'//renders/'`
- `context.area` not validated in timer callback (could crash in background mode)
- Compositor node_tree access uses 3 fallback methods (fragile)
- No type hints on any function signatures
- Missing docstrings on most operators

---

### 2.3 Metallic Flake Shader

**Status: FUNCTIONAL / STRUCTURAL ISSUES**
**Version:** 3.5.2 (outer) / 4.0.0 (inner metallic_flake_shader.py)
**Lines of Code:** ~6,300 across 2 files (3,082 + 3,239)

| Aspect | Status | Detail |
|--------|--------|--------|
| File structure | MONOLITHIC + ORPHAN | One 3,082-line file for metallic flake. universal_pbr_shader.py (3,239 lines) is present but **never imported or registered** — dead code. |
| bl_info compliance | MISMATCHED | Outer __init__.py says Blender 5.0.0, inner files say 4.0.0. Name/category non-compliant. |
| Class naming | NON-ZDC | Uses `MATERIAL_OT_`, `MATERIAL_PT_` (should be `ZDC_OT_MetallicFlake_`, etc.) |
| Blender 5.0 API | LIKELY COMPATIBLE | Uses standard shader nodes. No deprecated calls found. |
| Client references | CLEAN | No client-specific references |
| Documentation | MISSING | No README.md |
| Testing | NONE | No test infrastructure |

**Metallic Flake Shader — Implemented Features:**
- Three independent sparkle layers (Primary/Secondary/Tertiary)
- View-based flake visibility (flakes orient toward camera)
- Per-layer: seed, density, size, intensity, SSS, HSV color variation
- Base material with IOR, roughness, surface grain
- Anisotropic directional grain
- Clearcoat layer
- Mold texture support (normal, displacement, gloss, AO maps)
- Preset system (built-in + user-saved JSON presets)
- 150+ shader nodes, fully procedural

**Universal PBR Shader (ORPHANED):**
- Complete PBR shader with 10 texture map inputs
- Optional sparkle system integration
- 11 UI panels, full property system
- **Never registered** — `__init__.py` only imports `metallic_flake_shader`

**Key Decision Needed:** Should universal_pbr_shader.py be:
1. Registered alongside metallic flake as part of this addon?
2. Moved to its own addon directory?
3. Moved to `common/` as a shared material utility?

---

### 2.4 Kitchen Generator

**Status: EMPTY STUB / NOT FUNCTIONAL**
**Version:** 1.0.0
**Lines of Code:** 21 (one file)

| Aspect | Status | Detail |
|--------|--------|--------|
| File structure | SKELETON ONLY | Single `__init__.py` with empty `register()`/`unregister()`. Empty directories: src/, nodegroups/, assets/, tests/ |
| bl_info compliance | PARTIAL | Blender version correct (5,0,0). Name/author/location/category all non-compliant. |
| Class naming | N/A | No classes defined |
| Implementation | 0% | No operators, panels, properties, or business logic |

This addon is purely a placeholder. The ProKitchen specification documents describe what it should become, but no code has been written.

---

### 2.5 Home Builder 4.5 (Reference, Not Part of Monorepo)

**Status: REFERENCE COPY / SEPARATE PROJECT**
**Author:** Andrew Peel
**License:** GPLv3

A complete interior design asset library using the PyClone architecture. Includes wall generation, asset placement via drag-and-drop, material libraries, and product libraries (cabinets, doors, windows, bathroom fixtures, decorations). This is architecturally different from ZDC's Geometry Nodes approach — it uses pre-modeled assets rather than parametric generation.

Per the bootstrap prompt, this should be handled as a separate GitHub fork, not included in the ZDC monorepo.

---

## 3. Component Library Master Plan — Gap Analysis

The COMPONENT_LIBRARY_MASTER_PLAN.md describes an extensive component library system. Here is the status of each major section mapped against actual code.

### 3.1 Architecture & Infrastructure

| Master Plan Item | Status | Evidence |
|-----------------|--------|----------|
| Library infrastructure & API | NOT STARTED | No `library_api.py`, no `component-library/` directory |
| Two-tier asset system (commercial/private) | NOT STARTED | No tier separation in any addon |
| Generator-to-library API contract | NOT STARTED | No standardized interface between generators and library |
| .blend library file format | NOT STARTED | No consolidated `.blend` library files |
| Style preset system | NOT STARTED | No `style_presets.py` or coordinated style definitions |

### 3.2 Cabinet Components (Section 3.1 of Master Plan)

| Component | Plan Status | Actual Code Status |
|-----------|-------------|-------------------|
| Door styles (Flat, Shaker, Raised, Recessed, Glass) | Phase 1 | **5 of ~20 styles implemented** in cabinet-generator (Flat, Shaker, Raised, Recessed, Double Shaker). No glass mullion, beadboard, louvered, or specialty styles. |
| Handle styles | Phase 1 | **5 of 38 styles implemented** (Bar, Wire, Knob, Cup Pull, Edge Pull). Missing: D-ring, bow, T-bar, oversized, decorative knobs, ring pulls, leather strap, etc. |
| Cabinet box construction | Phase 1 | **Implemented** — face frame and frameless. |
| Cabinet types | Phase 1 | **10 of ~20+ types implemented**. Missing: island, bookcase end, wine rack, desk base, peninsula end, appliance panel, filler, decorative end. |
| Door profile curve library | Phase 1 | **NOT STARTED** — current door styles use simplified box geometry, not swept curves. |
| Hinges | Implemented | **3 styles** (European Cup, Exposed Barrel, Piano). |
| Drawer slides | Implemented | **3 styles** (Side Mount, Undermount, Center Mount). |

### 3.3 Countertops (Section 3.2)

| Component | Status |
|-----------|--------|
| Edge profiles (10 curve types) | NOT STARTED |
| Countertop forms (straight, L, U, island) | NOT STARTED |
| Countertop generation with overhang/backsplash | NOT STARTED |
| Sink/cooktop cutouts | NOT STARTED |

### 3.4 Backsplash (Section 3.3)

| Component | Status |
|-----------|--------|
| Tile patterns (subway, herringbone, hex, etc.) | NOT STARTED |
| GN or shader-based pattern system | NOT STARTED |

### 3.5 Sinks & Faucets (Section 3.4)

| Component | Status |
|-----------|--------|
| Kitchen sinks (9 types) | NOT STARTED |
| Faucets (7 types) | NOT STARTED |

### 3.6 Appliances (Section 3.5)

| Component | Status |
|-----------|--------|
| Major appliances (refrigerator, range, etc.) | NOT STARTED |
| Small appliances / scene dressing | NOT STARTED |

### 3.7 Doors & Windows (Section 3.6)

| Component | Status |
|-----------|--------|
| Interior doors (10 types) | NOT STARTED |
| Exterior doors (5 types) | NOT STARTED |
| Windows (11+ types) | NOT STARTED |
| Window treatments | NOT STARTED |

### 3.8 Moulding & Trim (Section 3.7)

| Component | Status |
|-----------|--------|
| Crown moulding profiles (7 types) | **BASIC** — cabinet-generator has simplified crown molding (box geometry). No curve profile library. |
| Base moulding profiles (6 types) | NOT STARTED |
| Chair rail / wainscoting | NOT STARTED |
| Cabinet-specific trim | **PARTIAL** — light rail implemented in cabinet-generator. No corbels, posts, valance. |
| Casing & trim profiles | NOT STARTED |

### 3.9 Walls, Floors, Ceilings (Section 3.8)

| Component | Status |
|-----------|--------|
| Wall construction | NOT STARTED (Home Builder has this, but it's a separate project) |
| Flooring materials | NOT STARTED |
| Ceiling types | NOT STARTED |

### 3.10 Lighting (Section 3.9)

| Component | Status |
|-----------|--------|
| Under-cabinet LED strips | **IMPLEMENTED** in cabinet-generator |
| Pendant lights, recessed cans, etc. | NOT STARTED |

### 3.11 PBR Material Library (Section 4)

| Material Category | Status |
|-------------------|--------|
| Master wood shader with species presets | NOT STARTED — cabinet-generator has basic material presets but not a procedural master wood shader node group |
| Painted finishes | NOT STARTED as procedural node group |
| Master metal shader | NOT STARTED — metallic-flake-shader exists but is specialized for sparkle plastic, not general hardware metals |
| Glass shader | NOT STARTED as parameterized node group |
| Stone/countertop materials | NOT STARTED |
| Tile/ceramic materials | NOT STARTED |
| Wall finishes | NOT STARTED |
| Material naming convention | NOT STARTED — no `{Category}_{Material}_{Variant}_{Finish}` system |
| Preset system (Python dicts) | PARTIAL — cabinet-generator's `material_presets.py` has basic presets |

### 3.12 Implementation Phases (Section 6)

| Phase | Timeframe | Status |
|-------|-----------|--------|
| **Phase 1: Foundation** (library infra, door profiles, core materials, basic handles) | Weeks 1-4 | ~20% — cabinet generator covers some cabinet/handle basics, but no library infrastructure, no procedural material node groups, no profile curve library |
| **Phase 2: Completeness** (moulding, countertop, windows/doors, appliances, sinks) | Weeks 5-8 | 0% |
| **Phase 3: Polish & Depth** (commissioned hardware, backsplash, expanded materials, decorations) | Weeks 9-16 | 0% |
| **Phase 4: Differentiation** (advanced materials, lighting, specialty cabinets, style presets) | Ongoing | 0% |

---

## 4. ProKitchen Specs vs Current Code

Three detailed specification documents describe a unified "ProKitchen" system. Here is how the current code maps to those specs.

### ProKitchen Master Architecture v1.1

Describes a three-layer hybrid: UI Layer > Python "Brain" Layer > Geometry Nodes "Body" Layer.

| Layer | Spec Status | Code Status |
|-------|-------------|-------------|
| GN "Body" (Cabinet system) | Fully specified | **cabinet-generator implements ~70%** of the specified cabinet types and features |
| Python "Brain" (Layout engine) | Fully specified | **kitchen-generator is 0%** — empty stub |
| UI Layer (Panels, operators) | Fully specified | **cabinet-generator has comprehensive UI**; kitchen-generator has nothing |
| Room generation | Specified | NOT STARTED |
| Layout/placement engine | Specified | NOT STARTED |
| Countertop generation | Specified | NOT STARTED |
| Appliance management | Specified | NOT STARTED |
| Material slot system (21 slots) | Specified | NOT STARTED — cabinet-generator has simpler material system |

### ProKitchen Cabinet GN Spec v1.1

Written as a freelancer brief. Specifies exact cabinet types, dimensions (US/EU), door styles, hardware, and output attributes.

| Spec Requirement | Cabinet Generator Status |
|-----------------|-------------------------|
| Base cabinets (8 types) | **5 of 8** — Standard, Drawer, Sink, Corner Blind, Appliance Garage implemented. Missing: Corner Diagonal (partial), Corner Lazy Susan (as variation), Corner Magic. |
| Wall cabinets (7 types) | **3 of 7** — Standard, Open Shelf implemented. Missing: Blind Corner Wall, Glass Door (partial), Microwave, Plate Rack. |
| Tall cabinets (4 types) | **1 of 4** — Tall/Pantry implemented. Missing: Utility, Oven Tower, Refrigerator Surround. |
| Specialty cabinets (5 types) | **0 of 5** — Missing: Island Base, Peninsula End, Appliance Panel, Filler, Decorative End. |
| US dimensional standards | Partial — kitchen depths correct, but not all width increments |
| EU dimensional standards | NOT STARTED |
| Material slot system (indices 5-15) | NOT IMPLEMENTED — uses simpler system |
| Output attributes for Python | NOT IMPLEMENTED — no attribute output for layout engine |
| Door styles (7 specified) | **5 of 7** — Missing: Beadboard, Glass Frame |
| Hardware animation (doors, drawers) | **IMPLEMENTED** |

### ProKitchen Layout Engine Spec v1.1

Specifies the Python orchestration layer in detail: room generation, cabinet placement, collision detection, auto-fill, countertop generation, appliance management, presets.

| Module | Status |
|--------|--------|
| `core/room.py` (Room/wall generation) | NOT STARTED |
| `core/layout.py` (Cabinet placement & collision) | NOT STARTED |
| `core/countertop.py` (Countertop generation) | NOT STARTED |
| `core/appliances.py` (Appliance management) | NOT STARTED |
| `core/materials.py` (Material system) | NOT STARTED |
| Operators, UI, presets, utils | NOT STARTED |

---

## 5. Cross-Addon Analysis

### Shared Patterns Found

1. **Material presets** — cabinet-generator's `material_presets.py` and metallic-flake-shader both create shader nodes programmatically. No shared utility exists.
2. **Node creation helpers** — cabinet-generator's `src/nodes/utils.py` has 30+ reusable node creation functions. Metallic-flake-shader has similar patterns inline. These could be extracted to `common/node_utils.py`.
3. **Preset save/load** — Both cabinet-generator and metallic-flake-shader implement JSON preset systems independently. Could share a common preset utility.
4. **Registration pattern** — All addons register/unregister classes independently. A shared registration helper could reduce boilerplate.

### Duplicated or Conflicting Code

- No direct code duplication detected between addons (they're sufficiently different in scope)
- Material creation approaches differ: cabinet-generator uses simple Principled BSDF setup; metallic-flake-shader builds 150+ nodes procedurally. These will need reconciliation when the Component Library material system is built.

### Dependency Graph

```
kitchen-generator (future)
  └── depends on → cabinet-generator (GN body)
  └── depends on → component-library (future, materials/profiles/assets)
  └── may use → auto-batch-renderer (rendering pipeline)

cabinet-generator (standalone)
  └── no current dependencies

auto-batch-renderer (standalone)
  └── no current dependencies

metallic-flake-shader (standalone)
  └── no current dependencies (but related to future material system)
```

---

## 6. Items Flagged for Master Plan Update

Based on code analysis, the following items in the Component Library Master Plan need updating or clarification:

### 6.1 Master Plan Assumes Infrastructure That Doesn't Exist

The plan's directory structure (Section 8) describes a standalone `component-library/` repo referenced by generators via git submodule. **This repo does not exist.** The plan should be updated to reflect:
- Whether the library will be a separate repo or a directory within the monorepo
- How to bootstrap the library infrastructure given the current monorepo approach described in BOOTSTRAP_PROMPT.md

### 6.2 Cabinet Generator Is More Advanced Than Plan Assumes

The master plan's Phase 1 scopes "basic parametric handles" (5-6 bar pulls, 2-3 knobs). The cabinet generator already has 5 handle styles with position controls. The plan should acknowledge this existing work and adjust Phase 1 to focus on the gaps:
- Profile curve library (not box geometry)
- Procedural material node groups (not simple Principled BSDF assignments)
- Library infrastructure/API

### 6.3 Procedural Material Strategy Partially Conflicts with Cabinet Generator's Approach

The master plan calls for a "master wood shader node group" with species presets as Python dicts. The cabinet generator's current `material_presets.py` takes a different approach (creates individual materials with hardcoded color values). These will need reconciliation — the master plan's approach is architecturally superior but the cabinet generator's existing materials work and are in production use.

### 6.4 ProKitchen Specs Not Referenced in Master Plan

The three ProKitchen specification documents describe a detailed system architecture that overlaps significantly with the master plan but isn't referenced by it. Key differences:
- ProKitchen specs define a 21-slot material system; the master plan doesn't specify slot indices
- ProKitchen specs define exact output attributes for GN-to-Python communication; the master plan doesn't address this
- ProKitchen Layout Engine spec provides module-level detail for the kitchen generator; the master plan treats the generators as consumers of the library

**Recommendation:** The master plan and ProKitchen specs should be cross-referenced and reconciled. The ProKitchen specs are more technically detailed for the kitchen/cabinet system; the master plan is broader (covers bathroom, doors/windows, decorative items, architectural elements).

### 6.5 Home Builder Relationship Needs Clarification

The master plan references Home Builder in multiple sections (walls, doors/windows, bathroom fixtures) but doesn't specify whether those features should be:
1. Ported from Home Builder's GPLv3 codebase (license implications!)
2. Built from scratch using the master plan's parametric approach
3. Handled by the Home Builder fork as a separate addon

This is a significant architectural decision that affects development priority.

### 6.6 Component Library as Standalone Repo vs Monorepo Directory

The master plan (Section 8) recommends `component-library/` as a standalone repo with generators referencing it via git submodule. The BOOTSTRAP_PROMPT.md structures everything as a monorepo. These approaches conflict. The master plan should be updated to match whichever approach is chosen.

### 6.7 Universal PBR Shader is Relevant to Material Strategy

The orphaned `universal_pbr_shader.py` in metallic-flake-shader implements a full PBR shader with 10 texture map inputs and an optional sparkle system. This is directly relevant to the master plan's Tier 2/3 image-backed materials strategy (Section 4.0). It should be acknowledged in the plan and potentially repurposed as the image-texture-based material node group for materials that can't be fully procedural.

---

## 7. Priority Recommendations

### Immediate (Before Any New Development)

1. **Execute Bootstrap Phase 1-2** — Initialize git monorepo, restructure addons into `addons/` directory, remove individual `.git` repos
2. **Scrub proprietary files** — Move `cabinet-generator/24_25_SpecGuide-compressed_A.pdf` and `.rtf` to a gitignored `reference/` directory. Review `revashelf_specs.py` for public repo suitability.
3. **Fix bl_info on all addons** — Update to ZDC naming/category/blender version conventions

### Short-Term (Workspace Health)

4. **Restructure auto-batch-renderer** — Split monolithic file into operators.py/panels.py/properties.py/src/
5. **Resolve metallic-flake-shader structure** — Decide on universal_pbr_shader.py fate; restructure to ZDC convention
6. **Complete Bootstrap Phases 3-7** — Extract common utilities, create scripts, set up MCP, archive old repos

### Medium-Term (Component Library Foundation)

7. **Reconcile master plan with ProKitchen specs** — Produce a single authoritative technical spec for the kitchen system
8. **Build library infrastructure** — Create the library API, .blend file format, and tier separation before adding assets
9. **Build procedural master wood shader** — This is the highest-value material work; test quality against image textures
10. **Create profile curve library** — Replace cabinet-generator's simplified box mouldings/door styles with proper swept curves

### Long-Term (As Outlined in Master Plan Phases 2-4)

11. Countertop generation system
12. Kitchen layout engine (Python "Brain")
13. Appliance and fixture libraries
14. Commission ornate hardware and fixtures
15. Style preset system

---

## 8. File Tree — Current State

```
ZDC-Blender-tools/                          (NOT a git repo)
├── BOOTSTRAP_PROMPT.md
├── CLAUDE.md
├── CLAUDE.local.md                         (gitignored - private client context)
├── COMPONENT_LIBRARY_MASTER_PLAN.md
├── PROJECT_STATUS.md                       (this file)
├── gitignore                               (needs rename to .gitignore)
├── ProKitchen_Master_Architecture_v1.1.md
├── ProKitchen_Cabinet_GN_Spec_v1.1.md
├── ProKitchen_Layout_Engine_Spec_v1.1.md
├── GN Cabinet Generator/                   (empty - can delete)
├── Kitchen Generator/                      (empty - can delete)
│
├── auto-batch-renderer/                    (should be addons/auto-batch-renderer/)
│   ├── .git/                               (remove for monorepo)
│   ├── __init__.py                         (11 lines)
│   └── auto_batch_renderer.py              (2,251 lines - monolithic)
│
├── cabinet-generator/                      (should be addons/cabinet-generator/)
│   ├── .git/                               (remove for monorepo)
│   ├── __init__.py
│   ├── operators.py                        (1,402 lines, 31 operators)
│   ├── panels.py                           (640 lines, 20 panels)
│   ├── properties.py                       (634 lines, 80+ properties)
│   ├── CLAUDE.md
│   ├── README.md
│   ├── PROJECT_STATUS.md
│   ├── 24_25_SpecGuide-compressed_A.pdf    (PROPRIETARY - must not commit)
│   ├── 24_25_SpecGuide-compressed_A.rtf    (PROPRIETARY - must not commit)
│   ├── test_cabinet_generator.py
│   ├── validate_addon.py
│   ├── visual_test.py
│   ├── quick_test.py
│   ├── test_log.json                       (should be gitignored)
│   ├── test_report.json                    (should be gitignored)
│   └── src/
│       ├── cut_list_export.py
│       ├── cabinet_presets.py
│       ├── batch_generation.py
│       ├── batch_lazy_susan.py
│       ├── revashelf_specs.py              (629 lines - client-specific)
│       └── nodes/
│           ├── utils.py                    (30+ helpers)
│           ├── master.py                   (CabinetMaster v4.0)
│           ├── material_presets.py
│           ├── atomic/                     (14 component generators)
│           └── systems/                    (10 system generators)
│
├── kitchen-generator/                      (should be addons/kitchen-generator/)
│   ├── .git/                               (remove for monorepo)
│   ├── __init__.py                         (21 lines - empty stub)
│   ├── src/                                (empty)
│   ├── nodegroups/                         (empty)
│   ├── assets/                             (empty)
│   └── tests/                              (empty)
│
├── metallic-flake-shader/                  (should be addons/metallic-flake-shader/)
│   ├── .git/                               (remove for monorepo)
│   ├── __init__.py                         (89 bytes - imports metallic_flake only)
│   ├── metallic_flake_shader.py            (3,082 lines)
│   └── universal_pbr_shader.py             (3,239 lines - ORPHANED/DEAD CODE)
│
└── home-builder-4.5/                       (reference copy - NOT part of monorepo)
    ├── home_builder_4.zip
    ├── extendedassetlibraryv02.pdf
    └── home_builder_4/                     (full addon: GPLv3 by Andrew Peel)
        ├── __init__.py                     ("Home Builder 5" v5.0.0)
        ├── hb_*.py                         (Home Builder modules)
        ├── pyclone_*.py                    (PyClone engine)
        ├── walls/                          (Wall generation)
        ├── pyclone_ops/                    (PyClone operators)
        ├── pyclone_ui/                     (PyClone UI)
        └── assets/                         (Materials, products, decorations)
```

---

## 9. Summary Scorecard

| Area | Score | Notes |
|------|-------|-------|
| **Workspace Setup** | 1/10 | No git repo, no directory structure, bootstrap not executed |
| **Cabinet Generator** | 8/10 | Production-grade, well-architected, needs ZDC naming compliance |
| **Auto Batch Renderer** | 5/10 | Functional but monolithic, wrong bl_info, needs restructuring |
| **Metallic Flake Shader** | 4/10 | Functional shader but structural issues, dead code, no docs |
| **Kitchen Generator** | 0/10 | Empty stub |
| **Component Library** | 0/10 | Planned but not started |
| **ProKitchen System** | 0/10 | Specified in detail but no layout engine code exists |
| **Documentation** | 6/10 | Good planning docs (CLAUDE.md, master plan, ProKitchen specs), but missing READMEs and no root README |
| **Cross-Addon Integration** | 1/10 | No shared utilities, no library API, addons are fully independent |

---

*End of report. Generated by Claude Opus 4.6 analysis of the full workspace.*
