# ProKitchen Generator — Master Architecture Document

**Version:** 1.1  
**Target Platform:** Blender 5.0+  
**Use Case:** Kitchen storage product visualization and marketing renders

---

## 1. Executive Summary

ProKitchen Generator is a comprehensive Blender add-on for generating photorealistic kitchen environments, specifically designed for kitchen storage product visualization and marketing renders. The system employs a hybrid architecture combining Python orchestration with Geometry Nodes parametric geometry.

### 1.1 Key Objectives
- Generate production-ready kitchen scenes for product photography
- Support both US and EU cabinet standards
- Enable rapid iteration of cabinet configurations
- Provide construction-accurate cabinet geometry for close-up renders
- Accommodate kitchen storage product integration

### 1.2 System Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Cabinet System | Geometry Nodes | Parametric cabinet geometry generation |
| Layout Engine | Python | Room generation, layout logic, UI |
| Asset Library | Blend Files | Hardware, appliances, materials |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ProKitchen Generator                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     USER INTERFACE LAYER                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────┐  │   │
│  │  │  UI Panels  │  │  Operators  │  │  Property Definitions    │  │   │
│  │  └─────────────┘  └─────────────┘  └──────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    PYTHON "BRAIN" LAYER                           │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │    Room    │  │   Layout   │  │ Countertop │  │ Appliances │  │   │
│  │  │ Generator  │  │   Engine   │  │ Generator  │  │  Manager   │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                  │   │
│  │  │  Material  │  │  Collision │  │   Preset   │                  │   │
│  │  │  Manager   │  │  Detector  │  │   System   │                  │   │
│  │  └────────────┘  └────────────┘  └────────────┘                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                 GEOMETRY NODES "BODY" LAYER                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │              GN_Cabinet_Master (Entry Point)                │  │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │   │
│  │  │  │   Base   │ │   Wall   │ │   Tall   │ │  Specialty   │   │  │   │
│  │  │  │ Cabinets │ │ Cabinets │ │ Cabinets │ │   Cabinets   │   │  │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │   │
│  │  │  │   Door   │ │  Drawer  │ │ Hardware │ │   Interior   │   │  │   │
│  │  │  │  Styles  │ │  System  │ │ (Hinges, │ │   (Shelves,  │   │  │   │
│  │  │  │          │ │          │ │  Slides) │ │    Pins)     │   │  │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │   │
│  │  └────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      ASSET LIBRARY LAYER                          │   │
│  │  ┌─────────┐  ┌─────────┐  ┌───────────┐  ┌─────────────────┐    │   │
│  │  │Hardware │  │Materials│  │ Appliances│  │Kitchen Presets  │    │   │
│  │  │ Library │  │ Library │  │  Library  │  │  (JSON configs) │    │   │
│  │  └─────────┘  └─────────┘  └───────────┘  └─────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow

### 3.1 Cabinet Generation Flow

```
User Input (UI Panel)
         │
         ▼
┌─────────────────────┐
│  Python Layout      │
│  Engine             │
│  • Validate params  │
│  • Calculate pos    │
│  • Check collisions │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Create Object with │
│  Geometry Nodes     │
│  Modifier           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐      ┌─────────────────────┐
│  Configure GN       │─────▶│  GN_Cabinet_Master  │
│  Parameters         │      │  Node Group         │
│  • Width/Height     │      │  (Generates mesh)   │
│  • Door Style       │      └─────────────────────┘
│  • Hardware         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Position Object    │
│  • Set transform    │
│  • Align to wall    │
│  • Snap to adjacent │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Assign Materials   │
│  • Per-slot mats    │
│  • From library     │
└─────────────────────┘
```

### 3.2 Countertop Generation Flow

```
User Triggers Countertop Generation
              │
              ▼
┌──────────────────────────┐
│  Analyze Cabinet Layout   │
│  • Find continuous runs   │
│  • Identify corners       │
│  • Detect sink cabinets   │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  Generate Countertop Mesh │
│  • Create slab geometry   │
│  • Apply edge profile     │
│  • Handle corners         │
│  • Add waterfall (if any) │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  Add Non-Destructive      │
│  Sink Cutouts             │
│  • Create cutout shapes   │
│  • Add Boolean modifiers  │
│  • Keep cutouts editable  │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  Generate Backsplash      │
│  (if enabled)             │
└──────────────────────────┘
```

---

## 4. Interface Contract

### 4.1 Python → Geometry Nodes Communication

The Python layer communicates with Geometry Nodes through modifier inputs:

```python
# Example: Configuring a cabinet via Python
cabinet_obj = bpy.data.objects["Cabinet_001"]
modifier = cabinet_obj.modifiers["GeometryNodes"]

# Set parameters through modifier inputs
modifier["Input_Width"] = 0.9  # 36" cabinet
modifier["Input_Height"] = 0.876  # Standard base height
modifier["Input_Door_Style"] = 1  # Shaker
modifier["Input_Door_Count"] = 2
modifier["Input_Handle_Style"] = 0  # Bar pull
modifier["Input_Door_Open_Angle"] = 0.0  # Closed
```

### 4.2 Geometry Nodes → Python Communication (Output Attributes)

GN outputs attributes that Python can read for layout logic:

```python
# Reading output attributes from GN
evaluated = cabinet_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())

# Access named attributes
cabinet_width = evaluated.data.attributes.get("Cabinet_Width")
snap_point_left = evaluated.data.attributes.get("Snap_Point_Left")
is_corner = evaluated.data.attributes.get("Is_Corner")
```

### 4.3 Required Output Attributes (from GN)

| Attribute | Type | Used For |
|-----------|------|----------|
| `Cabinet_Type` | String | Type identification |
| `Cabinet_Width` | Float | Layout spacing |
| `Cabinet_Height` | Float | Wall cabinet placement |
| `Cabinet_Depth` | Float | Countertop depth |
| `Is_Corner` | Boolean | Corner handling |
| `Countertop_Zone` | Boolean | Countertop generation |
| `Snap_Point_Left` | Vector | Cabinet alignment |
| `Snap_Point_Right` | Vector | Cabinet alignment |
| `Bounding_Box_Min` | Vector | Collision detection |
| `Bounding_Box_Max` | Vector | Collision detection |

---

## 5. Material System Integration

### 5.1 Unified Material Slots (21 Total)

Both Python-generated geometry (room, countertops) and GN-generated geometry (cabinets) use the same material slot indices:

| Index | Slot | Generator |
|-------|------|-----------|
| 0 | Floor | Python (Room) |
| 1 | Walls | Python (Room) |
| 2 | Ceiling | Python (Room) |
| 3 | Windows | Python (Room) |
| 4 | Window_Glass | Python (Room) |
| 5 | Cabinet_Exterior | GN (Cabinet) |
| 6 | Cabinet_Interior | GN (Cabinet) |
| 7 | Door_Face | GN (Cabinet) |
| 8 | Drawer_Box | GN (Cabinet) |
| 9 | Shelf | GN (Cabinet) |
| 10 | Toe_Kick | GN (Cabinet) |
| 11 | Hardware | GN (Cabinet) |
| 12 | Hinges | GN (Cabinet) |
| 13 | Slides | GN (Cabinet) |
| 14 | Shelf_Pins | GN (Cabinet) |
| 15 | Cabinet_Glass | GN (Cabinet) |
| 16 | Countertop | Python (Countertop) |
| 17 | Countertop_Edge | Python (Countertop) |
| 18 | Backsplash | Python (Countertop) |
| 19 | Molding_Crown | Python (Molding) |
| 20 | Molding_Base | Python (Molding) |
| 21 | Molding_Light_Rail | Python (Molding) |

### 5.2 Material Assignment Flow

```
┌─────────────────────────┐
│  MaterialManager        │
│  (Python singleton)     │
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌────────────┐ ┌────────────┐
│  Room Geo  │ │Cabinet Geo │
│  (Python)  │ │   (GN)     │
│  Slots 0-4 │ │ Slots 5-15 │
└────────────┘ └────────────┘
    │               │
    └───────┬───────┘
            ▼
┌─────────────────────────┐
│  Countertop/Molding Geo │
│  (Python)               │
│  Slots 16-21            │
└─────────────────────────┘
```

---

## 6. Development Strategy

### 6.1 Parallel Development Tracks

```
TRACK A: Geometry Nodes (Fiverr/Freelancer)
├── Week 1-2: Base cabinet types + door styles
├── Week 3-4: Wall/tall cabinets + drawers
├── Week 5-6: Corner cabinets + hardware
├── Week 7-8: Testing + refinement
│
TRACK B: Python Engine (AI-Assisted)
├── Week 1-2: Room generation + basic layout
├── Week 3-4: Cabinet placement + collision
├── Week 5-6: Countertop generation
├── Week 7-8: UI + presets + polish
│
INTEGRATION POINTS
├── Week 4: First integration test (basic cabinets)
├── Week 6: Full cabinet library integration
└── Week 8: Complete system test
```

### 6.2 Development Dependencies

```
GN_Cabinet_Master ────┐
                      │
GN_Door_Styles ───────┼───▶ Python Layout Engine
                      │          │
GN_Hardware ──────────┘          │
                                 ▼
                          Python Countertop
                                 │
                                 ▼
                           Python UI
```

### 6.3 Milestone Deliverables

| Milestone | GN Deliverables | Python Deliverables |
|-----------|-----------------|---------------------|
| M1 (Week 2) | Base cabinets, Shaker doors | Room generation, basic placement |
| M2 (Week 4) | Wall/tall cabinets, all door styles | Layout engine, collision detection |
| M3 (Week 6) | Corner cabinets, hinges, slides | Countertop gen, sink cutouts |
| M4 (Week 8) | Polish, all hardware, testing | UI complete, presets, export |

---

## 7. Quality Standards

### 7.1 Geometry Quality

**For Close-Up Renders:**
- All geometry must be subdivision-ready (level 2 minimum)
- No N-gons in subdividable areas
- Clean edge flow for smooth shading
- Manifold meshes (watertight, correct normals)

**For Performance:**
- Single cabinet generation: < 50ms
- Full kitchen (50 cabinets): < 5 seconds
- Viewport orbit smooth with 20+ cabinets

### 7.2 Code Quality (Python)

- Type hints on all function signatures
- Docstrings for all classes and public methods
- PEP 8 compliance
- Unit tests for core logic
- Error handling with user-friendly messages

### 7.3 Node Quality (Geometry Nodes)

- Consistent naming convention (`GN_` prefix)
- Organized node layout with frame labels
- Input/output sockets documented
- Reroute nodes for clean connections
- No unused nodes

---

## 8. File Structure

### 8.1 Addon Package

```
prokitchen/
├── __init__.py                 # bl_info, register/unregister
├── core/
│   ├── room.py                 # Room geometry generation
│   ├── layout.py               # Cabinet layout engine
│   ├── countertop.py           # Countertop generation
│   ├── appliances.py           # Appliance management
│   └── materials.py            # Material system
├── operators/
│   ├── room_ops.py
│   ├── cabinet_ops.py
│   ├── layout_ops.py
│   └── export_ops.py
├── ui/
│   ├── panels.py
│   └── properties.py
├── utils/
│   ├── math_utils.py
│   ├── geo_utils.py
│   └── naming.py
└── presets/
    └── kitchens/
```

### 8.2 Asset Library

```
ProKitchen_Assets/
├── ProKitchen_Cabinets.blend   # All GN node groups
├── Hardware/
│   ├── handles.blend
│   ├── hinges.blend
│   └── slides.blend
├── Appliances/
│   ├── ranges.blend
│   ├── refrigerators.blend
│   └── sinks.blend
├── Materials/
│   └── material_library.blend
└── Presets/
    └── kitchens/
        ├── galley.json
        ├── l_shape.json
        └── u_shape.json
```

---

## 9. Budget & Timeline Summary

### 9.1 Estimated Costs

| Component | Approach | Estimated Cost |
|-----------|----------|----------------|
| GN Cabinet System | Fiverr Specialist | $150 - $400 |
| Python Layout Engine | AI-Assisted | $0 (time investment) |
| Testing & Integration | Internal | $0 (time investment) |
| **Total** | | **$150 - $400** |

### 9.2 Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | 2 weeks | Core cabinet types, room generation |
| Phase 2 | 2 weeks | Full cabinet library, layout engine |
| Phase 3 | 2 weeks | Countertops, appliances, advanced features |
| Phase 4 | 2 weeks | UI polish, presets, documentation |
| **Total** | **8 weeks** | Production-ready system |

---

## 10. Risk Mitigation

### 10.1 Technical Risks

| Risk | Mitigation |
|------|------------|
| GN complexity exceeds freelancer skill | Detailed spec, example files, phased delivery |
| Performance issues with many cabinets | Instancing strategy, LOD system |
| Material slot conflicts | Unified slot registry, validation |
| Integration issues between GN and Python | Clear interface contract, early integration testing |

### 10.2 Schedule Risks

| Risk | Mitigation |
|------|------------|
| Freelancer delays | Buffer time, parallel Python development |
| Scope creep | Strict MVP definition, phased features |
| Testing reveals issues | Dedicated testing phase, incremental delivery |

---

## 11. Related Documents

| Document | Purpose |
|----------|---------|
| `ProKitchen_Cabinet_GN_Spec.md` | Detailed GN system specification for freelancer |
| `ProKitchen_Layout_Engine_Spec.md` | Python engine specification |
| `KitchenGen_Design_Doc.md` (v4.0) | Original design document |
| `Kitchen_Artist_Brief.md` (v4.0) | Artist-friendly brief |

---

## 12. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-06 | Initial architecture document |

---

## Appendix A: Quick Reference - Parameter Mapping

### Python Property → GN Input Mapping

| Python Property | GN Input Name | Type |
|-----------------|---------------|------|
| `cabinet_width` | `Input_Width` | Float |
| `cabinet_height` | `Input_Height` | Float |
| `cabinet_depth` | `Input_Depth` | Float |
| `door_style` | `Input_Door_Style` | Integer (enum) |
| `door_count` | `Input_Door_Count` | Integer |
| `drawer_count` | `Input_Drawer_Count` | Integer |
| `handle_style` | `Input_Handle_Style` | Integer (enum) |
| `door_open_angle` | `Input_Door_Open_Angle` | Float (0-170) |
| `drawer_extension` | `Input_Drawer_Extension` | Float (0-1) |

### Door Style Enum Mapping

| Value | Style |
|-------|-------|
| 0 | Slab |
| 1 | Shaker |
| 2 | Raised Panel |
| 3 | Beadboard |
| 4 | Glass Frame |
| 5 | Mullion Glass |
| 6 | Louvered |

### Handle Style Enum Mapping

| Value | Style |
|-------|-------|
| 0 | Bar Pull |
| 1 | Cup Pull |
| 2 | Knob |
| 3 | Ring Pull |
| 4 | None |

---

## Appendix B: Standard Dimension Quick Reference

### US Standard (Imperial)

| Cabinet Type | Width Options | Height | Depth |
|--------------|---------------|--------|-------|
| Base | 9-48" (3" increments) | 34.5" | 24" |
| Wall | 9-48" | 30/36/42" | 12" |
| Tall | 18-36" | 84/90/96" | 24" |

### EU Standard (Metric)

| Cabinet Type | Width Options | Height | Depth |
|--------------|---------------|--------|-------|
| Base | 150-1200mm | 720mm | 560-600mm |
| Wall | 150-1200mm | 600/720/900mm | 300-350mm |
| Tall | 400-900mm | 2000/2100/2400mm | 560-600mm |
