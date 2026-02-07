# ProKitchen Cabinet Generator — Geometry Nodes Specification

**Version:** 1.1  
**Target Platform:** Blender 5.0+  
**Document Purpose:** Technical specification for Fiverr/freelance Geometry Nodes artist  
**Use Case:** Kitchen storage product visualization and marketing renders

---

## 1. Project Overview

### 1.1 Objective
Create a comprehensive, parametric cabinet generation system using Blender's Geometry Nodes. This system will serve as the foundational "atom" for a larger kitchen scene generator, enabling photorealistic product renders of kitchen storage solutions.

### 1.2 Use Case
- High-end product photography/rendering for catalog, marketing, and web
- Cabinets must support close-up macro shots (subdivision-ready geometry)
- Must accommodate internal organizer products (pull-out shelves, lazy susans, waste containers)
- US market primary, EU market secondary

### 1.3 Architecture Context
This Geometry Nodes system is the **"Body"** of a hybrid architecture:
- **Python "Brain"** (separate development): Handles kitchen layout logic, room generation, cabinet placement
- **Geometry Nodes "Body"** (this specification): Handles parametric cabinet geometry generation

The Python script will instance and configure these node groups. Your deliverable must expose clean input parameters for external control.

---

## 2. Deliverables Summary

| Deliverable | Description |
|-------------|-------------|
| Master Cabinet Node Group | `GN_Cabinet_Master` - Main entry point with all parameters |
| Cabinet Type Subgroups | Individual node groups for each cabinet type |
| Door/Drawer Subgroups | Parametric door styles and drawer assemblies |
| Hardware Subgroups | Hinges, slides, handles, shelf pins |
| Construction Detail Groups | Joinery, face frames, edge treatments |
| Demo .blend File | Organized file demonstrating all cabinet types |
| Documentation | Parameter reference and usage notes |

---

## 3. Cabinet Types Required

### 3.1 Base Cabinets
| Type | Node Group Name | Description |
|------|-----------------|-------------|
| Standard Base | `GN_Base_Standard` | Configurable drawer(s) on top + door(s) below with shelf |
| Drawer Base | `GN_Base_Drawer` | Full drawer stack, no doors (3-6 drawers) |
| Sink Base | `GN_Base_Sink` | False drawer front, no shelf, plumbing clearance |
| Corner Blind | `GN_Base_Corner_Blind` | L-shaped with dead space, filler required |
| Corner Diagonal | `GN_Base_Corner_Diagonal` | 45° angled face |
| Corner Lazy Susan | `GN_Base_Corner_LazySusan` | Rotating shelf system placeholder |
| Corner Magic | `GN_Base_Corner_Magic` | Pull-out swing tray placeholder |
| Appliance Garage | `GN_Base_Appliance` | Tall opening for countertop appliances |

#### 3.1.1 Standard Base Configuration Detail

The `GN_Base_Standard` cabinet is the most common configuration and must support flexible drawer/door arrangements:

**Supported Configurations:**
- 1 drawer (top) + 1 door (full width below) + shelf
- 1 drawer (top) + 2 doors (split below) + shelf
- 2 drawers (stacked top) + 1 door + shelf
- 2 drawers (stacked top) + 2 doors + shelf
- 3 drawers (stacked top) + 1 door (smaller, bottom)
- Door only (no drawer) + shelf
- Any combination within height constraints

**Key Parameters:**
- `Drawer_Count`: 0-4 drawers
- `Drawer_Heights`: Array of individual drawer face heights (e.g., [0.1, 0.15] for 4" + 6")
- `Door_Count`: 0-2 doors
- `Door_Split`: Boolean (single full-width door vs. split pair)
- `Shelf_Count`: 0-3 adjustable shelves in door section

The drawer zone occupies the top of the cabinet, doors occupy the remainder. Total drawer height + door height + gaps must equal cabinet face height minus toe kick.

### 3.2 Wall Cabinets
| Type | Node Group Name | Description |
|------|-----------------|-------------|
| Standard Wall | `GN_Wall_Standard` | Single/double door with shelves |
| Wall Blind Corner | `GN_Wall_Corner_Blind` | L-shaped blind corner |
| Wall Diagonal Corner | `GN_Wall_Corner_Diagonal` | 45° angled face |
| Glass Door Wall | `GN_Wall_Glass` | Glass panel insert doors |
| Open Shelf | `GN_Wall_OpenShelf` | No doors, exposed shelving |
| Microwave Wall | `GN_Wall_Microwave` | Open cubby for OTR microwave |
| Plate Rack | `GN_Wall_PlateRack` | Vertical divider slots |

### 3.3 Tall Cabinets
| Type | Node Group Name | Description |
|------|-----------------|-------------|
| Pantry | `GN_Tall_Pantry` | Full-height storage with shelves |
| Utility | `GN_Tall_Utility` | Broom closet / cleaning storage |
| Oven Tower | `GN_Tall_Oven` | Cutout for wall oven + storage above/below |
| Refrigerator Surround | `GN_Tall_FridgeSurround` | Panels flanking refrigerator |

### 3.4 Specialty Cabinets
| Type | Node Group Name | Description |
|------|-----------------|-------------|
| Island Base | `GN_Island_Base` | Back panel option, waterfall prep |
| Peninsula End | `GN_Peninsula_End` | Exposed decorative end panel |
| Appliance Panel | `GN_Appliance_Panel` | Dishwasher/fridge panel overlay |
| Filler | `GN_Filler` | Gap filler strips |
| Decorative End | `GN_End_Decorative` | Furniture-style side panel |

---

## 4. Dimensional Standards

### 4.1 US Standard Dimensions (Primary - Default)

#### Base Cabinets
| Parameter | Standard Value | Range |
|-----------|---------------|-------|
| Height | 34.5" (876mm) | Fixed (+ countertop = 36") |
| Depth | 24" (610mm) | 12" - 24" |
| Widths | 9", 12", 15", 18", 21", 24", 27", 30", 33", 36", 42", 48" | Custom override |
| Toe Kick Height | 4" (102mm) | 3" - 4.5" |
| Toe Kick Depth | 3" (76mm) | 2.5" - 3.5" |

#### Wall Cabinets
| Parameter | Standard Value | Range |
|-----------|---------------|-------|
| Heights | 30", 36", 42" | 12" - 48" |
| Depth | 12" (305mm) | 12" - 15" |
| Widths | Same as base | Custom override |

#### Tall Cabinets
| Parameter | Standard Value | Range |
|-----------|---------------|-------|
| Heights | 84", 90", 96" | 72" - 96" |
| Depth | 24" (610mm) | 12" - 24" |
| Widths | 18", 24", 30", 36" | Custom override |

### 4.2 EU Standard Dimensions (Toggle Option)

#### Base Cabinets
| Parameter | Standard Value | Range |
|-----------|---------------|-------|
| Height | 720mm | Fixed (+ countertop = 900mm) |
| Depth | 560-600mm | 300mm - 600mm |
| Widths | 150, 200, 300, 400, 450, 500, 600, 800, 900, 1000, 1200mm | Custom |
| Plinth Height | 100-150mm | 80mm - 200mm |

#### Wall Cabinets
| Parameter | Standard Value | Range |
|-----------|---------------|-------|
| Heights | 600, 720, 900mm | 300mm - 1200mm |
| Depth | 300-350mm | 280mm - 400mm |

#### Tall Cabinets
| Parameter | Standard Value | Range |
|-----------|---------------|-------|
| Heights | 2000, 2100, 2400mm | 1800mm - 2400mm |
| Depth | 560-600mm | 300mm - 600mm |

### 4.3 Construction Dimensions (Both Standards)
| Component | US Value | EU Value |
|-----------|----------|----------|
| Panel Thickness (sides/top/bottom) | 0.75" (19mm) | 18-19mm |
| Back Panel Thickness | 0.25" (6mm) | 3-6mm |
| Shelf Thickness | 0.75" (19mm) | 18-19mm |
| Face Frame Width | 1.5" (38mm) | N/A (frameless) |
| Face Frame Thickness | 0.75" (19mm) | N/A |
| Door/Drawer Gap | 0.125" (3mm) | 3-4mm |
| Shelf Pin Spacing | 32mm (1.26") | 32mm |

### 4.4 Semi-Custom and Full Custom Support

**CRITICAL REQUIREMENT:** The cabinet system must support arbitrary dimensions beyond standard sizes. This is essential for rendering kitchen storage products in real-world cabinet configurations that may not conform to stock sizes.

#### Custom Dimension Philosophy

The standard width/height values listed above are **presets for convenience**, not constraints. Every dimensional parameter must accept user-specified values within reasonable physical limits.

#### Custom Width Support
- **Stock:** 3" increments (US) or 50-100mm increments (EU)
- **Semi-Custom:** 1" increments (US) or 10mm increments (EU)  
- **Full Custom:** Any value within min/max range

| Parameter | Minimum | Maximum | Notes |
|-----------|---------|---------|-------|
| Cabinet Width | 6" (150mm) | 60" (1500mm) | Structural limits |
| Cabinet Height | 12" (300mm) | 108" (2700mm) | Floor to ceiling |
| Cabinet Depth | 10" (250mm) | 30" (750mm) | Practical limits |

#### Custom Configuration Support
- **Drawer Heights:** Individual specification per drawer (not uniform)
- **Door Heights:** Automatically calculated from remaining space, or manually specified
- **Shelf Positions:** Arbitrary positioning, not locked to 32mm grid
- **Toe Kick:** Variable height and depth
- **Face Frame:** Variable rail/stile widths

#### Implementation Requirement

```
Input Parameters:
├── Standard_System (Enum): US, EU, CUSTOM
├── Width_Preset (Enum): Standard sizes OR "Custom"
├── Width_Custom (Float): Used when "Custom" selected
├── Height_Preset (Enum): Standard sizes OR "Custom"
├── Height_Custom (Float): Used when "Custom" selected
└── [Same pattern for all dimensional parameters]
```

When `Standard_System = CUSTOM`, all preset enums are ignored and custom float values are used directly. This allows complete dimensional freedom for any cabinet configuration.

---

## 5. Construction Styles

### 5.1 Face Frame (US Traditional)
- Full face frame attached to carcass front
- Doors overlay or inset into frame
- Exposed hinges or concealed cup hinges
- Face frame geometry: assembled appearance (no visible joinery detail required for MVP)

**Parameters:**
- `Frame_Rail_Width`: Top/bottom horizontal members
- `Frame_Stile_Width`: Vertical side members
- `Frame_Mullion_Width`: Center dividers (if applicable)
- `Door_Overlay`: Full overlay, partial overlay, or inset

### 5.2 Frameless / European (EU Standard)
- No face frame, doors attach directly to carcass
- Full-access to interior
- 32mm system drilling for hardware
- Concealed cup hinges standard

**Parameters:**
- `Drilling_System`: 32mm (default), 37mm (option)
- `Edge_Banding`: Boolean (handled via materials, not geometry)

---

## 6. Door Styles

### 6.1 Door Style Node Groups

| Style | Node Group | Description |
|-------|------------|-------------|
| Shaker | `GN_Door_Shaker` | Recessed center panel, square inner edge |
| Raised Panel | `GN_Door_RaisedPanel` | Center panel with beveled edges |
| Slab | `GN_Door_Slab` | Flat, no detail |
| Beadboard | `GN_Door_Beadboard` | Vertical groove pattern |
| Glass Frame | `GN_Door_GlassFrame` | Frame with glass panel insert |
| Mullion Glass | `GN_Door_MullionGlass` | Glass with decorative grid |
| Louvered | `GN_Door_Louvered` | Horizontal slat pattern |

### 6.2 Door Parameters (All Styles)

| Parameter | Type | Description |
|-----------|------|-------------|
| `Width` | Float | Door width |
| `Height` | Float | Door height |
| `Thickness` | Float | Overall door thickness (default 0.75") |
| `Panel_Depth` | Float | Recess depth for panel styles |
| `Frame_Width` | Float | Width of door frame rails/stiles |
| `Profile_Index` | Integer | Edge profile selection |
| `Hinge_Side` | Enum | Left, Right, Top (flipper), Bottom (flipper) |

### 6.3 Edge Profiles
Implement as curve-based profiles that can be swapped:
- Square
- Ogee
- Bevel
- Roundover
- Cove

---

## 7. Drawer System

### 7.1 Drawer Assembly Structure

The drawer assembly must be **construction-accurate** with separate components:

```
Drawer Assembly
├── Drawer Face (visible front)
├── Drawer Box
│   ├── Front Panel (behind face)
│   ├── Back Panel
│   ├── Left Side
│   ├── Right Side
│   └── Bottom Panel
└── Slide Mounts (attachment points)
```

### 7.2 Drawer Node Groups

| Component | Node Group | Description |
|-----------|------------|-------------|
| Full Assembly | `GN_Drawer_Assembly` | Complete drawer with face |
| Drawer Box | `GN_Drawer_Box` | Box construction only |
| Drawer Face | `GN_Drawer_Face` | Decorative front (uses door styles) |

### 7.3 Joinery (MVP Phase)

**MVP Implementation:**
- Simple butt joints (edges meet cleanly)
- Optional dovetail toggle for drawer box front corners
- Dado slot for bottom panel insertion

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `Joint_Type` | Enum | Butt, Dovetail |
| `Dovetail_Count` | Integer | Number of dovetail pins (when enabled) |
| `Dovetail_Angle` | Float | Pin angle (default 14°) |
| `Bottom_Dado_Depth` | Float | Dado groove depth for bottom panel |

**Future Enhancement (Phase 2):**
- Full joint library: dado, rabbet, box joint, finger joint, lock miter
- Exposed joinery detail for extreme close-ups

### 7.4 Drawer Dimensions

| Parameter | Default | Range |
|-----------|---------|-------|
| Box Height | 4" - 10" | Varies by drawer tier |
| Box Depth | Cabinet depth - 3" | Account for face and clearance |
| Side Thickness | 0.5" - 0.75" | |
| Bottom Thickness | 0.25" | |
| Face Gap | 0.125" | Between drawer faces |

#### 7.4.1 Multi-Drawer Configuration

For cabinets with multiple drawers (standard base or drawer base), each drawer can have an independent height:

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `Drawer_Count` | Integer | Number of drawers (0-6) |
| `Drawer_Heights` | Float Array | Height of each drawer face, top to bottom |
| `Drawer_Uniform` | Boolean | If true, ignore array and distribute equally |

**Example Configurations:**
- Pots & Pans: `[0.254, 0.254, 0.254]` (three 10" drawers)
- Standard Base: `[0.102]` (one 4" drawer over doors)
- Graduated: `[0.102, 0.127, 0.178]` (4", 5", 7" top to bottom)
- Full Drawer Stack: `[0.102, 0.102, 0.152, 0.203]` (4", 4", 6", 8")

**Implementation Note:** The Geometry Nodes system should accept a maximum of 6 drawer height inputs. Unused slots (when `Drawer_Count` is less than max) are ignored. If `Drawer_Uniform = True`, total available height is divided equally among `Drawer_Count` drawers.

---

## 8. Hardware Systems

### 8.1 Hinges

**Requirement:** Accurate representations, fully rigged, animate with doors

| Hinge Type | Node Group | Description |
|------------|------------|-------------|
| Concealed Cup | `GN_Hinge_Cup` | European style, 35mm cup |
| Face Frame | `GN_Hinge_FaceFrame` | For face frame cabinets |
| Inset | `GN_Hinge_Inset` | For inset door applications |
| Soft-Close | `GN_Hinge_SoftClose` | Integrated damper version |

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `Opening_Angle` | Float | 0° (closed) to 170° (full open) |
| `Overlay` | Float | Door overlay amount |
| `Mounting_Plate` | Enum | Clip-on, Screw-on |
| `Damper` | Boolean | Soft-close mechanism |

**Rigging Requirements:**
- Hinge must drive door rotation
- Expose `Opening_Angle` for animation
- Support realistic hinge pivot point (not simple edge rotation)

### 8.2 Drawer Slides

**Requirement:** Accurate representations, swappable for product slides

| Slide Type | Node Group | Description |
|------------|------------|-------------|
| Side Mount | `GN_Slide_SideMount` | Standard side-mounted slide |
| Under Mount | `GN_Slide_UnderMount` | Hidden beneath drawer |
| Center Mount | `GN_Slide_CenterMount` | Single center rail |

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `Extension` | Float | 0 (closed) to 1 (full extension) |
| `Length` | Float | Slide length (matches drawer depth) |
| `Load_Rating` | Enum | Light (50lb), Medium (100lb), Heavy (150lb+) |
| `Soft_Close` | Boolean | Damper mechanism |

**Swappability Requirement:**
- Slides must be a separate instanced object/collection
- Clear attachment point transforms for replacing with external product geometry

### 8.3 Handles & Pulls

| Type | Node Group | Description |
|------|------------|-------------|
| Bar Pull | `GN_Handle_Bar` | Straight bar, variable length |
| Cup Pull | `GN_Handle_Cup` | Shell/bin pull |
| Knob | `GN_Handle_Knob` | Simple round knob |
| Ring Pull | `GN_Handle_Ring` | Decorative ring |

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `Length` | Float | For bar pulls |
| `Diameter` | Float | Handle thickness |
| `Projection` | Float | How far it sticks out |
| `Mounting_Holes` | Integer | 1 (knob) or 2 (pull) |
| `Hole_Spacing` | Float | Center-to-center distance |

### 8.4 Shelf Pins

**Requirement:** Multiple real-world inspired options

| Type | Node Group | Description |
|------|------------|-------------|
| Standard Spoon | `GN_ShelfPin_Spoon` | Common metal spoon pin |
| Flat Bracket | `GN_ShelfPin_Bracket` | L-shaped support |
| Clear Plastic | `GN_ShelfPin_Plastic` | Budget plastic pin |
| Decorative Metal | `GN_ShelfPin_Decorative` | Premium brass/nickel |
| Locking Pin | `GN_ShelfPin_Locking` | Pin with retention clip |

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `Pin_Diameter` | Float | 5mm or 6mm standard |
| `Shelf_Thickness` | Float | To calculate support depth |

---

## 9. Interior Features

### 9.1 Adjustable Shelf System

**Peg Hole Grid:**
- Default spacing: 32mm vertical, line-bored pattern
- Holes on left and right interior side panels
- Hole diameter: 5mm or 6mm (configurable)
- Starting height: 2" from bottom
- Ending height: 2" from top

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `Shelf_Count` | Integer | Number of shelves |
| `Shelf_Positions` | Float Array | Normalized heights (0-1) |
| `Peg_Spacing` | Enum | 32mm (US/EU), 37mm (option) |
| `Hole_Diameter` | Float | 5mm or 6mm |
| `Shelf_Depth_Offset` | Float | How far shelf sits from front |
| `Shelf_Setback` | Float | Gap from back panel |

### 9.2 Fixed Shelves
- Some cabinets require structural fixed shelves
- No peg holes at fixed shelf location
- Connected to dado groove in side panels

### 9.3 Interior Components (Placeholders)

For kitchen storage product integration, provide empty transforms at:
- Lazy Susan center rotation point
- Pull-out shelf rail mounting positions
- Waste container floor position
- Door-mount bracket locations

---

## 10. Material Slot System

### 10.1 Material Index Assignments

**CRITICAL:** These indices are part of the unified ProKitchen material system. Indices 0-4 are reserved for room geometry (floor, walls, ceiling, windows). Cabinet geometry uses indices 5-15. Indices 16+ are reserved for countertops and molding.

All geometry must have proper material index assignments for the following slots:

| Index | Slot Name | Applied To |
|-------|-----------|------------|
| 5 | `Cabinet_Exterior` | Outer carcass faces, end panels |
| 6 | `Cabinet_Interior` | Inner carcass faces |
| 7 | `Door_Face` | Door front surfaces |
| 8 | `Drawer_Box` | Drawer box interior surfaces |
| 9 | `Shelf` | Adjustable shelf surfaces |
| 10 | `Toe_Kick` | Plinth/toe kick faces |
| 11 | `Hardware` | Handles, pulls, knobs |
| 12 | `Hinges` | Hinge components |
| 13 | `Slides` | Drawer slide components |
| 14 | `Shelf_Pins` | Shelf pin hardware |
| 15 | `Cabinet_Glass` | Glass panel inserts |

### 10.2 Implementation Notes
- Use `Set Material Index` node for assignment
- All faces must have an assigned material index
- Indices must match the unified system exactly for Python integration
- Separate materials allow per-component control in final render
- Edge banding is handled via material shaders, not geometry

---

## 11. Output Attributes

### 11.1 Required Output Attributes

The master node group must output these attributes for the Python layout engine:

| Attribute | Type | Description |
|-----------|------|-------------|
| `Cabinet_Type` | String | Type identifier (e.g., "Base_Standard") |
| `Cabinet_Width` | Float | Actual cabinet width |
| `Cabinet_Height` | Float | Actual cabinet height |
| `Cabinet_Depth` | Float | Actual cabinet depth |
| `Is_Corner` | Boolean | Corner cabinet flag |
| `Corner_Angle` | Float | Angle for diagonal corners (45° or 90°) |
| `Door_Count` | Integer | Number of doors |
| `Drawer_Count` | Integer | Number of drawers |
| `Hinge_Side` | String | "Left", "Right", "Both", "Top", "Bottom" |
| `Door_Open_Angle` | Float | Current door opening angle |
| `Drawer_Extension` | Float | Current drawer extension (0-1) |
| `Countertop_Zone` | Boolean | Requires countertop above |
| `Snap_Point_Left` | Vector | Left edge snap position |
| `Snap_Point_Right` | Vector | Right edge snap position |
| `Snap_Point_Top` | Vector | Top surface snap position |
| `Bounding_Box_Min` | Vector | AABB minimum corner |
| `Bounding_Box_Max` | Vector | AABB maximum corner |

### 11.2 Snap Point System

Each cabinet must expose snap points for the Python layout engine:

```
    [Top Center]
         │
[Left]───┼───[Right]
         │
    [Bottom Center]
```

- Snap points are empty transforms at cabinet edges
- Used for aligning adjacent cabinets
- Corner cabinets have additional angled snap points

---

## 12. Master Node Group Interface

### 12.1 `GN_Cabinet_Master` Input Parameters

```
CATEGORY: Dimensions
├── Standard_System (Enum): US, EU, CUSTOM
├── Width_Preset (Enum): Standard widths + "Custom"
├── Width_Custom (Float): Custom width value
├── Height_Preset (Enum): Standard heights + "Custom"
├── Height_Custom (Float): Custom height value
├── Depth_Preset (Enum): Standard depths + "Custom"
├── Depth_Custom (Float): Custom depth value
│
CATEGORY: Type
├── Cabinet_Category (Enum): Base, Wall, Tall, Specialty
├── Cabinet_Type (Enum): [Type-specific list]
├── Construction_Style (Enum): Face_Frame, Frameless
│
CATEGORY: Doors
├── Door_Style (Enum): Shaker, Slab, Raised, etc.
├── Door_Count (Integer): 0, 1, or 2
├── Door_Split (Boolean): Single full-width vs. pair
├── Door_Open_Angle (Float): 0-170
├── Hinge_Type (Enum): Cup, Face_Frame, Inset
├── Hinge_Side (Enum): Left, Right, Both
│
CATEGORY: Drawers
├── Drawer_Count (Integer): 0-6
├── Drawer_Uniform (Boolean): Equal heights vs. individual
├── Drawer_Height_1 (Float): First drawer height
├── Drawer_Height_2 (Float): Second drawer height
├── Drawer_Height_3 (Float): Third drawer height
├── Drawer_Height_4 (Float): Fourth drawer height
├── Drawer_Height_5 (Float): Fifth drawer height
├── Drawer_Height_6 (Float): Sixth drawer height
├── Drawer_Extension (Float): 0-1 (animation)
├── Drawer_Joint (Enum): Butt, Dovetail
├── Slide_Type (Enum): Side_Mount, Under_Mount, Center
│
CATEGORY: Interior
├── Shelf_Count (Integer): Adjustable shelf count
├── Shelf_Positions (Float Array): Normalized positions (0-1)
├── Fixed_Shelf (Boolean): Include structural shelf
├── Peg_System (Enum): 32mm, 37mm
├── Shelf_Pin_Style (Enum): Spoon, Bracket, Plastic, etc.
│
CATEGORY: Hardware
├── Handle_Style (Enum): Bar, Cup, Knob, Ring, None
├── Handle_Size (Float): Length or diameter
├── Handle_Position (Float): Normalized Y position
│
CATEGORY: Features
├── Toe_Kick (Boolean): Include toe kick
├── Toe_Kick_Height (Float): Plinth height
├── Toe_Kick_Depth (Float): Plinth setback
├── End_Panel_Left (Boolean): Decorative end
├── End_Panel_Right (Boolean): Decorative end
├── Glass_Panels (Boolean): For glass door variants
├── Soft_Close (Boolean): Soft-close hardware
```

**Note on Drawer Heights:** Blender Geometry Nodes does not natively support array inputs of variable length. The workaround is to expose 6 individual float inputs (`Drawer_Height_1` through `Drawer_Height_6`). The node group reads only the first N values where N = `Drawer_Count`. When `Drawer_Uniform = True`, these individual values are ignored and heights are calculated automatically.

---

## 13. Node Group Naming Convention

All node groups must follow this naming convention:

| Prefix | Category | Examples |
|--------|----------|----------|
| `GN_Cabinet_` | Main cabinet generators | `GN_Cabinet_Master`, `GN_Cabinet_Base` |
| `GN_Base_` | Base cabinet types | `GN_Base_Standard`, `GN_Base_Sink` |
| `GN_Wall_` | Wall cabinet types | `GN_Wall_Standard`, `GN_Wall_Glass` |
| `GN_Tall_` | Tall cabinet types | `GN_Tall_Pantry`, `GN_Tall_Oven` |
| `GN_Door_` | Door style generators | `GN_Door_Shaker`, `GN_Door_Slab` |
| `GN_Drawer_` | Drawer components | `GN_Drawer_Assembly`, `GN_Drawer_Box` |
| `GN_Hinge_` | Hinge types | `GN_Hinge_Cup`, `GN_Hinge_Inset` |
| `GN_Slide_` | Slide types | `GN_Slide_SideMount` |
| `GN_Handle_` | Handle types | `GN_Handle_Bar`, `GN_Handle_Knob` |
| `GN_ShelfPin_` | Shelf pin types | `GN_ShelfPin_Spoon` |
| `GN_Profile_` | Edge profiles | `GN_Profile_Ogee` |
| `GN_Utility_` | Helper functions | `GN_Utility_BoundingBox` |

---

## 14. Quality Requirements

### 14.1 Geometry Standards
- **Manifold geometry:** All meshes must be watertight (no holes, no flipped normals)
- **Subdivision-ready:** Edge loops placed for smooth subdivision at level 2
- **No N-gons:** Quads only where subdivision is expected
- **Consistent scale:** All geometry in real-world units (meters in Blender)
- **Clean topology:** No overlapping vertices, no zero-area faces

### 14.2 Performance Targets
- Single cabinet instantiation: < 50ms
- 50-cabinet kitchen generation: < 5 seconds
- Viewport performance: Smooth orbit with 20+ cabinets at subdivision level 0

### 14.3 File Organization
```
ProKitchen_Cabinets.blend
├── Node Groups (all GN_ prefixed)
├── Collections
│   ├── Cabinet_Demos
│   │   ├── Base_Cabinets
│   │   ├── Wall_Cabinets
│   │   ├── Tall_Cabinets
│   │   └── Corner_Cabinets
│   └── Hardware_Library
│       ├── Hinges
│       ├── Slides
│       ├── Handles
│       └── Shelf_Pins
└── Materials (placeholder with correct indices)
```

---

## 15. Acceptance Criteria

### 15.1 Core Functionality
- [ ] All cabinet types listed in Section 3 are implemented
- [ ] US and EU dimensional standards switchable via parameter
- [ ] Face Frame and Frameless construction styles work correctly
- [ ] All door styles render correctly
- [ ] Drawer assembly has separate construction-accurate components
- [ ] MVP joinery (butt + dovetail option) implemented

### 15.2 Hardware
- [ ] Hinges animate doors correctly (pivot point accurate)
- [ ] Drawer slides extend/retract properly
- [ ] All handle styles implemented
- [ ] Shelf pin options available

### 15.3 Integration
- [ ] All output attributes documented and functional
- [ ] Snap points correctly positioned
- [ ] Material indices correctly assigned to all faces
- [ ] Node group inputs match specification

### 15.4 Quality
- [ ] Geometry is manifold and subdivision-ready
- [ ] No visual artifacts at subdivision level 2
- [ ] Performance targets met
- [ ] File organized per specification

---

## 16. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-06 | Initial specification |

---

## Appendix A: Reference Dimensions Quick Sheet

### US Standard Cabinet Widths (inches)
`9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 42, 48`

### EU Standard Cabinet Widths (mm)
`150, 200, 300, 400, 450, 500, 600, 800, 900, 1000, 1200`

### Standard Heights Summary
| Type | US | EU |
|------|----|----|
| Base | 34.5" | 720mm |
| Wall | 30", 36", 42" | 600, 720, 900mm |
| Tall | 84", 90", 96" | 2000, 2100, 2400mm |

### Toe Kick / Plinth
| | US | EU |
|--|----|----|
| Height | 4" | 100-150mm |
| Depth | 3" | 50-80mm |

---

## Appendix B: Corner Cabinet Geometry Reference

### Blind Corner (Base)
```
        ┌─────────────┐
        │             │
  Filler│    Blind    │
   ───▶ │    Space    │
        │             │
        └──────┬──────┘
               │
          Door │
               │
```

### Diagonal Corner (Base)
```
        ╲           ╱
          ╲   45° ╱
            ╲   ╱
              │
         Door │
              │
```

### Lazy Susan (Base)
```
        ┌─────────────┐
        │      ○      │ ← Rotation axis
        │    ╱   ╲    │
        │  ╱       ╲  │
        │╱    └┘    ╲│ ← Pie-cut doors
        └─────────────┘
```
