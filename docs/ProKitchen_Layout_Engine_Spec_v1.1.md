# ProKitchen Layout Engine — Python Specification

**Version:** 1.1  
**Target Platform:** Blender 5.0+ Python API  
**Document Purpose:** Technical specification for Python development (AI-assisted)  
**Use Case:** Kitchen storage product visualization and marketing renders

---

## 1. System Overview

### 1.1 Purpose
The ProKitchen Layout Engine is a Python-based "Brain" that orchestrates kitchen scene generation by:
- Managing room geometry (walls, floor, ceiling, windows)
- Intelligently placing and configuring cabinet instances
- Generating continuous countertops with proper seaming and edge profiles
- Handling appliance integration and collision avoidance
- Providing an artist-friendly UI within Blender

### 1.2 Architecture Role
```
┌─────────────────────────────────────────────────────────┐
│                  ProKitchen System                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐     ┌────────────────────────────┐ │
│  │  Python "Brain"  │────▶│  Geometry Nodes "Body"    │ │
│  │  (This Document) │     │  (Cabinet Spec Document)   │ │
│  └─────────────────┘     └────────────────────────────┘ │
│         │                            │                   │
│         ▼                            ▼                   │
│  • Room Generation           • Parametric Cabinets       │
│  • Layout Logic              • Door/Drawer Animation     │
│  • Countertop Generation     • Hardware Details          │
│  • Appliance Placement       • Construction Accuracy     │
│  • Material Assignment       • Snap Points               │
│  • UI/UX Panel                                           │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Dependencies
- Blender 5.0+ Python API (`bpy`)
- ProKitchen Cabinet GN System (`.blend` file with node groups)
- NumPy (for spatial calculations)
- Standard library: `json`, `math`, `typing`

---

## 2. Module Structure

```
prokitchen/
├── __init__.py              # Addon registration
├── core/
│   ├── __init__.py
│   ├── room.py              # Room geometry generation
│   ├── layout.py            # Cabinet layout engine
│   ├── countertop.py        # Countertop generation
│   ├── appliances.py        # Appliance management
│   └── materials.py         # Material slot management
├── operators/
│   ├── __init__.py
│   ├── room_ops.py          # Room creation operators
│   ├── cabinet_ops.py       # Cabinet manipulation operators
│   ├── layout_ops.py        # Auto-layout operators
│   └── export_ops.py        # Export/save operators
├── ui/
│   ├── __init__.py
│   ├── panels.py            # UI panels
│   ├── menus.py             # Menus and pie menus
│   └── properties.py        # Custom property definitions
├── presets/
│   ├── kitchens/            # Kitchen layout presets
│   ├── cabinets/            # Cabinet configuration presets
│   └── materials/           # Material presets
├── utils/
│   ├── __init__.py
│   ├── math_utils.py        # Vector/transform utilities
│   ├── geo_utils.py         # Geometry helpers
│   └── naming.py            # Naming conventions
└── data/
    ├── dimensions_us.json   # US standard dimensions
    └── dimensions_eu.json   # EU standard dimensions
```

---

## 3. Room Generation Module (`core/room.py`)

### 3.1 Room Class

```python
class KitchenRoom:
    """
    Manages kitchen room geometry: walls, floor, ceiling, windows, doorways.
    """
    
    def __init__(self, 
                 width: float,
                 depth: float, 
                 height: float = 2.7,  # 9ft default
                 wall_thickness: float = 0.15):
        self.width = width
        self.depth = depth
        self.height = height
        self.wall_thickness = wall_thickness
        self.walls: List[Wall] = []
        self.windows: List[Window] = []
        self.doorways: List[Doorway] = []
        self.floor_object: Optional[bpy.types.Object] = None
        self.ceiling_object: Optional[bpy.types.Object] = None
        
    def generate(self) -> bpy.types.Collection:
        """Generate all room geometry and return collection."""
        pass
        
    def add_window(self, wall_index: int, position: float, 
                   width: float, height: float, sill_height: float,
                   style: WindowStyle = WindowStyle.DOUBLE_HUNG) -> Window:
        """Add window to specified wall."""
        pass
        
    def add_doorway(self, wall_index: int, position: float,
                    width: float, height: float) -> Doorway:
        """Add doorway opening to specified wall."""
        pass
```

### 3.2 Wall Segment Management

```python
class Wall:
    """Individual wall segment with openings."""
    
    def __init__(self, 
                 start: Vector, 
                 end: Vector, 
                 height: float,
                 thickness: float):
        self.start = start
        self.end = end
        self.height = height
        self.thickness = thickness
        self.openings: List[WallOpening] = []  # Windows, doorways
        self.cabinets: List[CabinetPlacement] = []  # Assigned cabinets
        
    @property
    def length(self) -> float:
        return (self.end - self.start).length
        
    @property
    def direction(self) -> Vector:
        return (self.end - self.start).normalized()
        
    @property
    def normal(self) -> Vector:
        """Inward-facing normal."""
        return Vector((-self.direction.y, self.direction.x, 0))
        
    def get_available_segments(self) -> List[Tuple[float, float]]:
        """Return list of (start, end) positions not blocked by openings."""
        pass
        
    def generate_mesh(self) -> bpy.types.Object:
        """Generate wall mesh with boolean cutouts for openings."""
        pass
```

### 3.3 Window Generation

```python
class WindowStyle(Enum):
    DOUBLE_HUNG = "double_hung"
    CASEMENT = "casement"
    SLIDER = "slider"
    FIXED = "fixed"
    AWNING = "awning"

class Window:
    """
    Kitchen window with actual geometry generation.
    MVP: Static geometry only.
    Phase 2: Rigged/animated windows.
    """
    
    def __init__(self,
                 width: float,
                 height: float,
                 sill_height: float,
                 style: WindowStyle = WindowStyle.DOUBLE_HUNG,
                 frame_width: float = 0.05,
                 frame_depth: float = 0.1):
        self.width = width
        self.height = height
        self.sill_height = sill_height
        self.style = style
        self.frame_width = frame_width
        self.frame_depth = frame_depth
        
    def generate(self, wall: Wall, position: float) -> bpy.types.Object:
        """
        Generate window geometry at specified wall position.
        
        Returns window object with proper material slots:
        - Windows (frame)
        - Window_Glass (glazing)
        """
        pass
```

### 3.4 Material Slot Indices (Room)

| Index | Slot Name | Applied To |
|-------|-----------|------------|
| 0 | `Floor` | Floor surface |
| 1 | `Walls` | Wall surfaces |
| 2 | `Ceiling` | Ceiling surface |
| 3 | `Windows` | Window frames |
| 4 | `Window_Glass` | Window glazing |

---

## 4. Cabinet Layout Engine (`core/layout.py`)

### 4.1 Layout Manager Class

```python
class LayoutManager:
    """
    Manages cabinet placement, snapping, and collision detection.
    """
    
    def __init__(self, room: KitchenRoom, standard: str = "US"):
        self.room = room
        self.standard = standard  # "US" or "EU"
        self.cabinets: List[CabinetInstance] = []
        self.gn_source_file: str = ""  # Path to GN cabinet .blend
        
    def load_cabinet_library(self, filepath: str):
        """Link/append cabinet node groups from external .blend."""
        pass
        
    def place_cabinet(self, 
                      cabinet_type: str,
                      wall_index: int,
                      position: float,
                      config: CabinetConfig) -> CabinetInstance:
        """
        Place a cabinet at specified wall position.
        
        Args:
            cabinet_type: Type identifier (e.g., "Base_Standard")
            wall_index: Which wall (0-3 for rectangular room)
            position: Distance along wall from start
            config: Cabinet configuration parameters
            
        Returns:
            CabinetInstance with placed object reference
        """
        pass
        
    def auto_fill_wall(self, 
                       wall_index: int,
                       cabinet_category: str = "Base",
                       constraints: LayoutConstraints = None) -> List[CabinetInstance]:
        """
        Automatically fill wall with cabinets.
        
        Respects:
        - Window positions (wall cabinets avoid)
        - Appliance zones (sink, range, dishwasher)
        - Corner transitions
        - Locked cabinets (from selection)
        """
        pass
        
    def shuffle_layout(self, 
                       preserve_locked: bool = True,
                       constraints: LayoutConstraints = None):
        """
        Regenerate layout with variation.
        
        Args:
            preserve_locked: Keep cabinets marked as locked in place
        """
        pass
        
    def validate_layout(self) -> List[LayoutIssue]:
        """Check for collisions, gaps, code violations."""
        pass
```

### 4.2 Cabinet Instance Class

```python
class CabinetInstance:
    """
    Represents a placed cabinet in the scene.
    """
    
    def __init__(self,
                 object_ref: bpy.types.Object,
                 cabinet_type: str,
                 wall: Wall,
                 position: float):
        self.object = object_ref
        self.cabinet_type = cabinet_type
        self.wall = wall
        self.position = position  # Along wall
        self.is_locked = False  # For shuffle preservation
        
    @property
    def width(self) -> float:
        """Get width from GN output attribute."""
        return self.object.get("Cabinet_Width", 0.6)
        
    @property
    def snap_left(self) -> Vector:
        """World position of left snap point."""
        pass
        
    @property
    def snap_right(self) -> Vector:
        """World position of right snap point."""
        pass
        
    def configure(self, **params):
        """
        Update cabinet GN parameters.
        
        Example:
            cabinet.configure(
                Door_Style="Shaker",
                Door_Count=2,
                Drawer_Count=1,
                Handle_Style="Bar"
            )
        """
        for key, value in params.items():
            if key in self.object.modifiers["GeometryNodes"]:
                self.object.modifiers["GeometryNodes"][key] = value
```

### 4.3 Cabinet Locking System

```python
class LockingSystem:
    """
    Selection-based cabinet locking for shuffle operations.
    """
    
    @staticmethod
    def lock_selected():
        """Mark selected cabinet objects as locked."""
        for obj in bpy.context.selected_objects:
            if obj.get("prokitchen_cabinet"):
                obj["is_locked"] = True
                # Visual feedback
                obj.color = (0.2, 0.8, 0.2, 1.0)  # Green tint
                
    @staticmethod
    def unlock_selected():
        """Remove lock from selected cabinet objects."""
        for obj in bpy.context.selected_objects:
            if obj.get("prokitchen_cabinet"):
                obj["is_locked"] = False
                obj.color = (1.0, 1.0, 1.0, 1.0)  # Reset
                
    @staticmethod
    def get_locked_cabinets() -> List[bpy.types.Object]:
        """Return all locked cabinet objects."""
        return [obj for obj in bpy.context.scene.objects 
                if obj.get("prokitchen_cabinet") and obj.get("is_locked")]
                
    @staticmethod
    def get_unlocked_cabinets() -> List[bpy.types.Object]:
        """Return all unlocked cabinet objects."""
        return [obj for obj in bpy.context.scene.objects 
                if obj.get("prokitchen_cabinet") and not obj.get("is_locked")]
```

### 4.4 Layout Constraints

```python
@dataclass
class LayoutConstraints:
    """Constraints for auto-layout operations."""
    
    min_cabinet_width: float = 0.3  # 12" minimum
    max_cabinet_width: float = 1.2  # 48" maximum
    
    # Appliance zones (position along wall, width)
    sink_zone: Optional[Tuple[float, float]] = None
    range_zone: Optional[Tuple[float, float]] = None
    dishwasher_zone: Optional[Tuple[float, float]] = None
    refrigerator_zone: Optional[Tuple[float, float]] = None
    
    # Work triangle constraints
    enforce_work_triangle: bool = False
    min_work_distance: float = 1.2  # 4 feet
    max_work_distance: float = 2.7  # 9 feet
    
    # ADA compliance
    ada_compliant: bool = False
    ada_counter_height: float = 0.86  # 34" ADA maximum
    ada_knee_clearance: float = 0.69  # 27" minimum
    
    # Filler requirements
    max_gap_without_filler: float = 0.003  # 1/8" tolerance
    auto_add_fillers: bool = True
```

### 4.5 Collision Detection

```python
class CollisionDetector:
    """
    Detect and resolve cabinet collisions.
    """
    
    @staticmethod
    def check_cabinet_overlap(cab1: CabinetInstance, 
                               cab2: CabinetInstance) -> bool:
        """Check if two cabinets on same wall overlap."""
        if cab1.wall != cab2.wall:
            return False
        cab1_end = cab1.position + cab1.width
        cab2_end = cab2.position + cab2.width
        return not (cab1_end <= cab2.position or cab2_end <= cab1.position)
        
    @staticmethod
    def check_window_conflict(cabinet: CabinetInstance,
                               window: Window) -> bool:
        """Check if wall cabinet conflicts with window."""
        pass
        
    @staticmethod
    def get_corner_clearance(corner_type: str) -> float:
        """
        Return required clearance for corner cabinet type.
        
        Blind corners need filler space for door swing.
        """
        clearances = {
            "Corner_Blind": 0.076,  # 3" filler
            "Corner_Diagonal": 0.0,
            "Corner_LazySusan": 0.0,
            "Corner_Magic": 0.0
        }
        return clearances.get(corner_type, 0.0)
```

---

## 5. Countertop Generation (`core/countertop.py`)

### 5.1 Countertop Generator Class

```python
class CountertopGenerator:
    """
    Generates continuous countertops with proper seaming,
    edge profiles, and sink cutouts.
    
    Non-destructive approach: Uses modifier stack for cutouts.
    """
    
    def __init__(self, layout: LayoutManager):
        self.layout = layout
        self.segments: List[CountertopSegment] = []
        
    def generate(self) -> List[bpy.types.Object]:
        """
        Generate countertop geometry for all base cabinets.
        
        Returns list of countertop objects (one per continuous run).
        """
        runs = self._identify_runs()
        countertops = []
        
        for run in runs:
            ct = self._generate_run(run)
            countertops.append(ct)
            
        return countertops
        
    def _identify_runs(self) -> List[List[CabinetInstance]]:
        """
        Identify continuous cabinet runs for countertop generation.
        
        A run breaks at:
        - Wall corners
        - Appliance gaps (range, refrigerator)
        - Explicit breaks
        """
        pass
        
    def _generate_run(self, cabinets: List[CabinetInstance]) -> bpy.types.Object:
        """Generate single countertop run."""
        pass
        
    def add_sink_cutout(self, 
                        countertop: bpy.types.Object,
                        sink_cabinet: CabinetInstance,
                        sink_type: str) -> None:
        """
        Add sink cutout using non-destructive boolean modifier.
        
        This allows the cutout to be repositioned or resized
        without regenerating the countertop.
        """
        # Create cutout shape based on sink type
        cutout = self._create_sink_cutout_shape(sink_type)
        
        # Position over sink cabinet
        cutout.location = sink_cabinet.object.location
        cutout.location.z = countertop.location.z + 0.02  # Slight offset
        
        # Add boolean modifier (non-destructive)
        bool_mod = countertop.modifiers.new(name="Sink_Cutout", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutout
        bool_mod.solver = 'EXACT'
        
        # Hide cutout object
        cutout.hide_viewport = True
        cutout.hide_render = True
```

### 5.2 Edge Profile System

```python
class EdgeProfile(Enum):
    SQUARE = "square"
    EASED = "eased"
    BULLNOSE = "bullnose"
    OGEE = "ogee"
    BEVEL = "bevel"
    DUPONT = "dupont"
    WATERFALL = "waterfall"

class CountertopConfig:
    """Configuration for countertop generation."""
    
    thickness: float = 0.03  # 1.25" standard
    overhang_front: float = 0.025  # 1" front overhang
    overhang_side: float = 0.025  # 1" side overhang (exposed ends)
    
    edge_profile: EdgeProfile = EdgeProfile.EASED
    edge_profile_front: bool = True
    edge_profile_sides: bool = True  # Exposed ends only
    
    backsplash: bool = True
    backsplash_height: float = 0.1  # 4" standard
    backsplash_thickness: float = 0.01
    
    # Seaming
    max_segment_length: float = 3.0  # 10' max before seam
    seam_width: float = 0.003  # Visible seam line
```

### 5.3 Waterfall Island Support

```python
class WaterfallConfig:
    """Configuration for waterfall countertop edges."""
    
    left_waterfall: bool = False
    right_waterfall: bool = False
    
    # Waterfall runs to floor or stops at specified height
    waterfall_to_floor: bool = True
    waterfall_height: float = 0.0  # If not to floor
    
    # Miter joint angle
    miter_angle: float = 45.0
    
    # Seating overhang (one side only typically)
    seating_overhang: float = 0.0
    seating_side: str = "right"  # "left", "right", "both"
```

### 5.4 Material Slots (Countertop)

**CRITICAL:** These indices are part of the unified ProKitchen material system. Countertop geometry uses indices 16-18. Indices 0-4 are for room, 5-15 for cabinets, 19-21 for molding.

| Index | Slot Name | Applied To |
|-------|-----------|------------|
| 16 | `Countertop` | Top surface |
| 17 | `Countertop_Edge` | Edge profile faces |
| 18 | `Backsplash` | Backsplash faces |

---

## 6. Appliance Management (`core/appliances.py`)

### 6.1 Appliance Library

```python
class ApplianceType(Enum):
    RANGE_30 = "range_30"
    RANGE_36 = "range_36"
    RANGE_48 = "range_48"
    REFRIGERATOR_30 = "refrigerator_30"
    REFRIGERATOR_36 = "refrigerator_36"
    REFRIGERATOR_42 = "refrigerator_42"
    REFRIGERATOR_48 = "refrigerator_48"
    DISHWASHER_24 = "dishwasher_24"
    HOOD_30 = "hood_30"
    HOOD_36 = "hood_36"
    HOOD_48 = "hood_48"
    MICROWAVE_OTR = "microwave_otr"
    MICROWAVE_DRAWER = "microwave_drawer"
    WINE_FRIDGE_15 = "wine_fridge_15"
    WINE_FRIDGE_18 = "wine_fridge_18"
    WINE_FRIDGE_24 = "wine_fridge_24"
    SINK_SINGLE = "sink_single"
    SINK_DOUBLE = "sink_double"
    SINK_FARMHOUSE = "sink_farmhouse"

# Appliance dimensions (width, depth, height) in meters
APPLIANCE_DIMENSIONS = {
    ApplianceType.RANGE_30: (0.762, 0.686, 0.914),      # 30" x 27" x 36"
    ApplianceType.RANGE_36: (0.914, 0.686, 0.914),      # 36" x 27" x 36"
    ApplianceType.RANGE_48: (1.219, 0.686, 0.914),      # 48" x 27" x 36"
    ApplianceType.REFRIGERATOR_36: (0.914, 0.762, 1.778),  # 36" x 30" x 70"
    ApplianceType.DISHWASHER_24: (0.610, 0.610, 0.864),    # 24" x 24" x 34"
    # ... etc
}
```

### 6.2 Appliance Manager

```python
class ApplianceManager:
    """
    Manages appliance placeholder geometry and cabinet integration.
    """
    
    def __init__(self, layout: LayoutManager):
        self.layout = layout
        self.appliances: Dict[str, AppliancePlacement] = {}
        
    def place_appliance(self,
                        appliance_type: ApplianceType,
                        position: Vector,
                        rotation: float = 0.0) -> bpy.types.Object:
        """
        Place appliance placeholder at specified location.
        
        Returns placeholder object with correct dimensions.
        """
        pass
        
    def auto_place_hood(self, range_placement: AppliancePlacement) -> bpy.types.Object:
        """Automatically place hood above range."""
        pass
        
    def get_cabinet_gap(self, appliance_type: ApplianceType) -> Tuple[float, float]:
        """
        Return (left_gap, right_gap) required around appliance.
        
        Some appliances need clearance for doors/operation.
        """
        pass
```

---

## 7. Material System (`core/materials.py`)

### 7.1 Complete Material Slot Registry

```python
class MaterialSlots(Enum):
    """
    Complete material slot registry for ProKitchen system.
    21 slots total covering all geometry types.
    """
    
    # Room geometry (0-4)
    FLOOR = 0
    WALLS = 1
    CEILING = 2
    WINDOWS = 3
    WINDOW_GLASS = 4
    
    # Cabinet structure (5-10)
    CABINET_EXTERIOR = 5
    CABINET_INTERIOR = 6
    DOOR_FACE = 7
    DRAWER_BOX = 8
    SHELF = 9
    TOE_KICK = 10
    
    # Hardware (11-14)
    HARDWARE = 11
    HINGES = 12
    SLIDES = 13
    SHELF_PINS = 14
    
    # Cabinet glass (15)
    CABINET_GLASS = 15
    
    # Countertop (16-18)
    COUNTERTOP = 16
    COUNTERTOP_EDGE = 17
    BACKSPLASH = 18
    
    # Moldings (19-21)
    MOLDING_CROWN = 19
    MOLDING_BASE = 20
    MOLDING_LIGHT_RAIL = 21
    
    # Appliances (22)
    APPLIANCES = 22
```

### 7.2 Material Manager

```python
class MaterialManager:
    """
    Manages material creation and assignment for ProKitchen objects.
    """
    
    def __init__(self):
        self.materials: Dict[MaterialSlots, bpy.types.Material] = {}
        
    def create_placeholder_materials(self):
        """Create placeholder materials for all slots."""
        for slot in MaterialSlots:
            mat = bpy.data.materials.new(name=f"PK_{slot.name}")
            mat.use_nodes = True
            # Set distinctive viewport color for each slot
            mat.diffuse_color = self._get_placeholder_color(slot)
            self.materials[slot] = mat
            
    def assign_to_object(self, 
                         obj: bpy.types.Object, 
                         slot_mapping: Dict[int, MaterialSlots]):
        """
        Assign materials to object based on face material indices.
        
        Args:
            obj: Target object
            slot_mapping: Dict mapping face material index to MaterialSlot
        """
        for face_index, slot in slot_mapping.items():
            if slot in self.materials:
                if len(obj.data.materials) <= face_index:
                    obj.data.materials.append(self.materials[slot])
                else:
                    obj.data.materials[face_index] = self.materials[slot]
```

---

## 8. UI System (`ui/`)

### 8.1 Main Panel

```python
class PROKITCHEN_PT_main_panel(bpy.types.Panel):
    """Main ProKitchen panel in 3D View sidebar."""
    
    bl_label = "ProKitchen"
    bl_idname = "PROKITCHEN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ProKitchen'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pk = scene.prokitchen
        
        # Room Setup
        box = layout.box()
        box.label(text="Room Setup", icon='HOME')
        col = box.column(align=True)
        col.prop(pk, "room_width")
        col.prop(pk, "room_depth")
        col.prop(pk, "room_height")
        col.prop(pk, "standard_system")
        box.operator("prokitchen.generate_room", icon='MESH_CUBE')
        
        # Cabinet Placement
        box = layout.box()
        box.label(text="Cabinets", icon='MESH_CUBE')
        col = box.column(align=True)
        col.prop(pk, "cabinet_category")
        col.prop(pk, "cabinet_type")
        col.prop(pk, "door_style")
        box.operator("prokitchen.place_cabinet", icon='ADD')
        box.operator("prokitchen.auto_fill_wall", icon='ALIGN_JUSTIFY')
        
        # Cabinet Locking
        row = box.row(align=True)
        row.operator("prokitchen.lock_selected", text="Lock", icon='LOCKED')
        row.operator("prokitchen.unlock_selected", text="Unlock", icon='UNLOCKED')
        box.operator("prokitchen.shuffle_layout", icon='FILE_REFRESH')
        
        # Countertop
        box = layout.box()
        box.label(text="Countertop", icon='SURFACE_NSPHERE')
        col = box.column(align=True)
        col.prop(pk, "countertop_thickness")
        col.prop(pk, "edge_profile")
        col.prop(pk, "backsplash_enabled")
        box.operator("prokitchen.generate_countertop", icon='SURFACE_NCURVE')
        
        # Appliances
        box = layout.box()
        box.label(text="Appliances", icon='EVENT_A')
        col = box.column(align=True)
        col.prop(pk, "appliance_type")
        box.operator("prokitchen.place_appliance", icon='ADD')
```

### 8.2 Properties Registration

```python
class ProKitchenProperties(bpy.types.PropertyGroup):
    """ProKitchen scene properties."""
    
    # Room
    room_width: FloatProperty(
        name="Width",
        default=4.0,
        min=2.0,
        max=20.0,
        unit='LENGTH'
    )
    room_depth: FloatProperty(
        name="Depth",
        default=3.5,
        min=2.0,
        max=20.0,
        unit='LENGTH'
    )
    room_height: FloatProperty(
        name="Height",
        default=2.7,
        min=2.4,
        max=4.0,
        unit='LENGTH'
    )
    standard_system: EnumProperty(
        name="Standard",
        items=[
            ('US', "US Standard", "US imperial dimensions"),
            ('EU', "EU Standard", "European metric dimensions")
        ],
        default='US'
    )
    
    # Cabinet
    cabinet_category: EnumProperty(
        name="Category",
        items=[
            ('BASE', "Base", "Base cabinets"),
            ('WALL', "Wall", "Wall cabinets"),
            ('TALL', "Tall", "Tall cabinets"),
            ('SPECIALTY', "Specialty", "Specialty cabinets")
        ]
    )
    cabinet_type: EnumProperty(
        name="Type",
        items=get_cabinet_types  # Dynamic based on category
    )
    door_style: EnumProperty(
        name="Door Style",
        items=[
            ('SHAKER', "Shaker", ""),
            ('SLAB', "Slab", ""),
            ('RAISED', "Raised Panel", ""),
            ('BEADBOARD', "Beadboard", ""),
            ('GLASS', "Glass Frame", "")
        ]
    )
    
    # Countertop
    countertop_thickness: FloatProperty(
        name="Thickness",
        default=0.03,
        min=0.02,
        max=0.05,
        unit='LENGTH'
    )
    edge_profile: EnumProperty(
        name="Edge",
        items=[
            ('SQUARE', "Square", ""),
            ('EASED', "Eased", ""),
            ('BULLNOSE', "Bullnose", ""),
            ('OGEE', "Ogee", ""),
            ('BEVEL', "Bevel", "")
        ]
    )
    backsplash_enabled: BoolProperty(
        name="Backsplash",
        default=True
    )
```

---

## 9. Operators (`operators/`)

### 9.1 Key Operators

```python
class PROKITCHEN_OT_generate_room(bpy.types.Operator):
    """Generate kitchen room geometry."""
    bl_idname = "prokitchen.generate_room"
    bl_label = "Generate Room"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        pk = context.scene.prokitchen
        room = KitchenRoom(
            width=pk.room_width,
            depth=pk.room_depth,
            height=pk.room_height
        )
        collection = room.generate()
        return {'FINISHED'}


class PROKITCHEN_OT_place_cabinet(bpy.types.Operator):
    """Place cabinet at cursor location."""
    bl_idname = "prokitchen.place_cabinet"
    bl_label = "Place Cabinet"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Implementation
        return {'FINISHED'}


class PROKITCHEN_OT_lock_selected(bpy.types.Operator):
    """Lock selected cabinets from shuffle operations."""
    bl_idname = "prokitchen.lock_selected"
    bl_label = "Lock Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        LockingSystem.lock_selected()
        return {'FINISHED'}


class PROKITCHEN_OT_shuffle_layout(bpy.types.Operator):
    """Shuffle unlocked cabinets."""
    bl_idname = "prokitchen.shuffle_layout"
    bl_label = "Shuffle Layout"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        layout_manager.shuffle_layout(preserve_locked=True)
        return {'FINISHED'}


class PROKITCHEN_OT_generate_countertop(bpy.types.Operator):
    """Generate countertop for placed base cabinets."""
    bl_idname = "prokitchen.generate_countertop"
    bl_label = "Generate Countertop"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        generator = CountertopGenerator(layout_manager)
        countertops = generator.generate()
        
        # Add sink cutouts (non-destructive)
        for cab in layout_manager.cabinets:
            if "Sink" in cab.cabinet_type:
                for ct in countertops:
                    if cab in ct.get("cabinets", []):
                        generator.add_sink_cutout(ct, cab, "double")
                        
        return {'FINISHED'}
```

---

## 10. Preset System

### 10.1 Kitchen Presets

```json
// presets/kitchens/galley.json
{
    "name": "Galley Kitchen",
    "description": "Two parallel runs, efficient for narrow spaces",
    "room": {
        "width": 3.0,
        "depth": 4.5,
        "height": 2.7
    },
    "layout": {
        "walls": [
            {
                "index": 0,
                "cabinets": [
                    {"type": "Base_Standard", "width": 0.6},
                    {"type": "Base_Sink", "width": 0.9},
                    {"type": "Base_Standard", "width": 0.6}
                ]
            },
            {
                "index": 2,
                "cabinets": [
                    {"type": "Base_Standard", "width": 0.45},
                    {"type": "Base_Drawer", "width": 0.6},
                    {"type": "Base_Standard", "width": 0.45},
                    {"type": "Base_Standard", "width": 0.6}
                ]
            }
        ],
        "appliances": [
            {"type": "RANGE_30", "wall": 2, "position": 1.2},
            {"type": "REFRIGERATOR_36", "wall": 0, "position": 2.8}
        ]
    }
}
```

### 10.2 Preset Loader

```python
class PresetLoader:
    """Load and apply kitchen presets."""
    
    @staticmethod
    def load_preset(filepath: str) -> dict:
        """Load preset from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)
            
    @staticmethod
    def apply_preset(preset: dict, layout: LayoutManager):
        """Apply loaded preset to layout manager."""
        # Generate room
        room = KitchenRoom(**preset['room'])
        room.generate()
        
        # Place cabinets
        for wall_config in preset['layout']['walls']:
            wall_index = wall_config['index']
            position = 0.0
            for cab_config in wall_config['cabinets']:
                layout.place_cabinet(
                    cabinet_type=cab_config['type'],
                    wall_index=wall_index,
                    position=position,
                    config=CabinetConfig(**cab_config)
                )
                position += cab_config.get('width', 0.6)
```

---

## 11. Asset Library Structure

```
/ProKitchen_Assets/
├── Cabinets/
│   ├── ProKitchen_Cabinets.blend      # All GN cabinet node groups
│   └── Cabinet_Presets/
│       ├── base_configs.json
│       ├── wall_configs.json
│       └── tall_configs.json
├── Hardware/
│   ├── Handles/
│   │   ├── bar_pulls.blend
│   │   ├── cup_pulls.blend
│   │   └── knobs.blend
│   ├── Hinges/
│   │   ├── concealed_cup.blend
│   │   └── face_frame.blend
│   ├── Slides/
│   │   ├── side_mount.blend
│   │   └── under_mount.blend
│   └── Shelf_Pins/
│       └── pin_styles.blend
├── Moldings/
│   ├── Crown/
│   │   └── crown_profiles.blend
│   ├── Baseboard/
│   │   └── base_profiles.blend
│   └── Light_Rail/
│       └── rail_profiles.blend
├── Appliances/
│   ├── ranges.blend
│   ├── refrigerators.blend
│   ├── dishwashers.blend
│   ├── hoods.blend
│   └── sinks.blend
├── Windows/
│   └── window_styles.blend
├── Materials/
│   ├── wood_grains/
│   ├── laminates/
│   ├── stones/
│   └── metals/
└── Presets/
    ├── kitchens/
    │   ├── galley.json
    │   ├── l_shape.json
    │   ├── u_shape.json
    │   └── island.json
    └── styles/
        ├── modern.json
        ├── traditional.json
        └── transitional.json
```

---

## 12. Development Phases

### Phase 1: Core Foundation (MVP)
- [ ] Room generation (walls, floor, ceiling)
- [ ] Basic cabinet placement on walls
- [ ] Integration with GN cabinet system
- [ ] Simple countertop generation
- [ ] Material slot system
- [ ] Basic UI panel

### Phase 2: Layout Intelligence
- [ ] Auto-fill wall algorithm
- [ ] Collision detection
- [ ] Cabinet locking system
- [ ] Shuffle functionality
- [ ] Corner cabinet handling
- [ ] Filler auto-insertion

### Phase 3: Advanced Features
- [ ] Window generation (static geometry)
- [ ] Appliance placeholders
- [ ] Non-destructive sink cutouts
- [ ] Waterfall countertops
- [ ] Backsplash generation
- [ ] Edge profile system

### Phase 4: Polish & Presets
- [ ] Kitchen preset system
- [ ] Style presets
- [ ] Advanced UI (pie menus, gizmos)
- [ ] Performance optimization
- [ ] Documentation & tutorials

### Future Enhancements
- [ ] Animated windows
- [ ] Molding generation
- [ ] LED lighting geometry
- [ ] Work triangle validation
- [ ] ADA compliance checking

---

## 13. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-06 | Initial specification |

