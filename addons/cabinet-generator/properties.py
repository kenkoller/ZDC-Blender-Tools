# Property definitions for Cabinet Generator addon

import bpy
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup


def update_preset(self, context):
    """Update dimensions when preset changes."""
    if self.cabinet_type == 'BASE':
        self.width = 0.6
        self.height = 0.72
        self.depth = 0.55
        self.front_type = 'DOORS'
        self.has_toe_kick = True
    elif self.cabinet_type == 'WALL':
        self.width = 0.6
        self.height = 0.72
        self.depth = 0.35
        self.front_type = 'DOORS'
        self.has_toe_kick = False
    elif self.cabinet_type == 'TALL':
        self.width = 0.6
        self.height = 2.1
        self.depth = 0.55
        self.front_type = 'DOORS'
        self.has_toe_kick = True
    elif self.cabinet_type == 'DRAWER_BASE':
        self.width = 0.6
        self.height = 0.72
        self.depth = 0.55
        self.front_type = 'DRAWERS'
        self.drawer_count = 4
        self.has_toe_kick = True
    elif self.cabinet_type == 'BLIND_CORNER':
        self.width = 0.9
        self.height = 0.72
        self.depth = 0.6
        self.front_type = 'DOORS'
        self.has_toe_kick = True
        self.has_lazy_susan = True
    elif self.cabinet_type == 'SINK_BASE':
        self.width = 0.9
        self.height = 0.72
        self.depth = 0.6
        self.front_type = 'DOORS'
        self.double_doors = True
        self.has_toe_kick = True
        self.has_shelves = False
    elif self.cabinet_type == 'APPLIANCE':
        self.width = 0.6
        self.height = 0.72
        self.depth = 0.6
        self.front_type = 'DOORS'
        self.has_toe_kick = False
        self.has_shelves = False
    elif self.cabinet_type == 'OPEN_SHELVING':
        self.width = 0.8
        self.height = 1.2
        self.depth = 0.3
        self.has_toe_kick = False
        self.has_shelves = True
        self.shelf_count = 4
    elif self.cabinet_type == 'DIAGONAL_CORNER':
        self.width = 0.6
        self.height = 0.72
        self.depth = 0.6
        self.front_type = 'DOORS'
        self.has_toe_kick = True
        self.has_lazy_susan = True
    elif self.cabinet_type == 'PULLOUT_PANTRY':
        self.width = 0.15
        self.height = 2.0
        self.depth = 0.55
        self.has_toe_kick = True
        self.shelf_count = 6


class CABINET_PG_Settings(PropertyGroup):
    """Main settings for cabinet generation."""

    # Cabinet type/preset
    cabinet_type: EnumProperty(
        name="Cabinet Type",
        description="Type of cabinet to generate",
        items=[
            ('BASE', "Base Cabinet", "Floor-standing base cabinet with doors"),
            ('WALL', "Wall Cabinet", "Wall-mounted upper cabinet"),
            ('TALL', "Tall Cabinet", "Full-height pantry/utility cabinet"),
            ('DRAWER_BASE', "Drawer Base", "Base cabinet with drawers"),
            ('BLIND_CORNER', "Blind Corner", "L-shaped corner cabinet with lazy susan"),
            ('SINK_BASE', "Sink Base", "Base cabinet with open front for sink plumbing"),
            ('APPLIANCE', "Appliance Cabinet", "Cabinet with opening for microwave/oven"),
            ('OPEN_SHELVING', "Open Shelving", "Exposed shelf unit without doors"),
            ('DIAGONAL_CORNER', "Diagonal Corner", "45-degree angled front corner cabinet"),
            ('PULLOUT_PANTRY', "Pull-out Pantry", "Narrow cabinet with pull-out rack"),
        ],
        default='BASE',
        update=update_preset,
    )

    # Dimensions
    width: FloatProperty(
        name="Width",
        description="Cabinet width",
        default=0.6,
        min=0.2,
        max=1.2,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    height: FloatProperty(
        name="Height",
        description="Cabinet height",
        default=0.72,
        min=0.3,
        max=2.4,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    depth: FloatProperty(
        name="Depth",
        description="Cabinet depth",
        default=0.55,
        min=0.3,
        max=0.7,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    # Material thickness
    panel_thickness: FloatProperty(
        name="Panel Thickness",
        description="Thickness of cabinet panels",
        default=0.018,
        min=0.012,
        max=0.025,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    shelf_thickness: FloatProperty(
        name="Shelf Thickness",
        description="Thickness of shelves",
        default=0.018,
        min=0.012,
        max=0.025,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    # Front type
    front_type: EnumProperty(
        name="Front Type",
        description="Type of cabinet front",
        items=[
            ('DOORS', "Doors", "Cabinet doors"),
            ('DRAWERS', "Drawers", "Drawer stack"),
        ],
        default='DOORS',
    )

    # Door options
    door_style: EnumProperty(
        name="Door Style",
        description="Style of door panels",
        items=[
            ('FLAT', "Flat", "Simple flat panel"),
            ('SHAKER', "Shaker", "Recessed center panel"),
            ('RAISED', "Raised", "Raised center panel"),
            ('RECESSED', "Recessed Flat", "Flat with frame detail"),
            ('DOUBLE_SHAKER', "Double Shaker", "Nested shaker frames"),
        ],
        default='SHAKER',
    )

    double_doors: BoolProperty(
        name="Double Doors",
        description="Use two doors instead of one",
        default=False,
    )

    # Glass door options
    glass_insert: BoolProperty(
        name="Glass Insert",
        description="Add glass panel to door",
        default=False,
    )

    glass_frame_width: FloatProperty(
        name="Frame Width",
        description="Width of frame around glass",
        default=0.04,
        min=0.02,
        max=0.1,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    # Drawer options
    drawer_count: IntProperty(
        name="Drawer Count",
        description="Number of drawers",
        default=3,
        min=1,
        max=6,
    )

    # Handle options
    handle_style: EnumProperty(
        name="Handle Style",
        description="Style of handles",
        items=[
            ('BAR', "Bar Pull", "Rectangular bar handle"),
            ('WIRE', "Wire Pull", "Thin wire handle"),
            ('KNOB', "Knob", "Round knob"),
            ('CUP', "Cup Pull", "Bin-style cup pull"),
            ('EDGE', "Edge Pull", "Modern edge grip"),
        ],
        default='BAR',
    )

    handle_offset_x: FloatProperty(
        name="Handle Offset X",
        description="Horizontal handle position offset",
        default=0.05,
        min=0.02,
        max=0.2,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    handle_offset_z: FloatProperty(
        name="Handle Offset Z",
        description="Vertical handle position offset",
        default=0.0,
        min=-0.3,
        max=0.3,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    # Interior options
    has_back: BoolProperty(
        name="Back Panel",
        description="Include back panel",
        default=True,
    )

    has_shelves: BoolProperty(
        name="Shelves",
        description="Include internal shelves",
        default=True,
    )

    shelf_count: IntProperty(
        name="Shelf Count",
        description="Number of internal shelves",
        default=1,
        min=0,
        max=10,
    )

    # Bevel options
    bevel_width: FloatProperty(
        name="Bevel Width",
        description="Width of edge bevels",
        default=0.001,
        min=0.0,
        max=0.01,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    bevel_segments: IntProperty(
        name="Bevel Segments",
        description="Number of bevel segments",
        default=2,
        min=1,
        max=6,
    )

    # Animation options
    door_open_angle: FloatProperty(
        name="Door Open",
        description="Door opening angle (degrees)",
        default=0.0,
        min=0.0,
        max=120.0,
        subtype='ANGLE',
    )

    drawer_open: FloatProperty(
        name="Drawer Open",
        description="Drawer slide out amount (0-100%)",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
    )

    # Toe kick options
    has_toe_kick: BoolProperty(
        name="Toe Kick",
        description="Include recessed toe kick base",
        default=True,
    )

    toe_kick_height: FloatProperty(
        name="Toe Kick Height",
        description="Height of toe kick recess",
        default=0.1,
        min=0.05,
        max=0.15,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    toe_kick_depth: FloatProperty(
        name="Toe Kick Depth",
        description="Depth of toe kick recess from front",
        default=0.06,
        min=0.03,
        max=0.1,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    # Lazy susan options (for corner cabinets)
    has_lazy_susan: BoolProperty(
        name="Lazy Susan",
        description="Include rotating lazy susan shelves",
        default=False,
    )

    lazy_susan_count: IntProperty(
        name="Lazy Susan Tiers",
        description="Number of lazy susan shelf tiers",
        default=2,
        min=1,
        max=4,
    )

    lazy_susan_style: EnumProperty(
        name="Lazy Susan Style",
        description="Shape of the lazy susan tray",
        items=[
            ('FULL_CIRCLE', "Full Circle", "Complete circular shelf"),
            ('KIDNEY', "Kidney", "270° kidney-shaped shelf"),
            ('PIE_CUT', "Pie Cut", "180° pie-cut shelf (hinged door)"),
            ('D_SHAPE', "D-Shape", "Half-circle with flat back"),
            ('HALF_MOON', "Half-Moon", "Semi-circular for large corner cabinets"),
        ],
        default='FULL_CIRCLE',
    )

    lazy_susan_diameter: FloatProperty(
        name="Lazy Susan Diameter",
        description="Override tray diameter (0 = auto-calculate from cabinet interior)",
        default=0.0,
        min=0.0,
        max=1.0,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    lazy_susan_rotation: FloatProperty(
        name="Lazy Susan Rotation",
        description="Current rotation of lazy susan (for animation)",
        default=0.0,
        min=0.0,
        max=360.0,
        subtype='ANGLE',
    )

    # Corner cabinet options
    corner_type: EnumProperty(
        name="Corner Type",
        description="Corner cabinet orientation",
        items=[
            ('LEFT', "Left Corner", "L-shaped corner on left side"),
            ('RIGHT', "Right Corner", "L-shaped corner on right side"),
        ],
        default='LEFT',
    )

    blind_width: FloatProperty(
        name="Blind Width",
        description="Width of blind (hidden) portion",
        default=0.15,
        min=0.1,
        max=0.25,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    # Hardware options
    hinge_style: EnumProperty(
        name="Hinge Style",
        description="Style of door hinges",
        items=[
            ('EUROPEAN', "European Cup", "Concealed European cup hinges"),
            ('BARREL', "Exposed Barrel", "Visible barrel hinges"),
            ('PIANO', "Piano Hinge", "Continuous piano hinge"),
        ],
        default='EUROPEAN',
    )

    drawer_slide_style: EnumProperty(
        name="Drawer Slide Style",
        description="Style of drawer slides",
        items=[
            ('SIDE_MOUNT', "Side Mount", "Traditional side-mounted slides"),
            ('UNDERMOUNT', "Undermount", "Hidden undermount slides"),
            ('CENTER_MOUNT', "Center Mount", "Single center-mounted slide"),
        ],
        default='SIDE_MOUNT',
    )

    # Face frame options
    has_face_frame: BoolProperty(
        name="Face Frame",
        description="Use traditional face frame construction",
        default=False,
    )

    face_frame_width: FloatProperty(
        name="Frame Width",
        description="Width of face frame stiles and rails",
        default=0.038,
        min=0.025,
        max=0.075,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    # Appliance cabinet options
    appliance_type: EnumProperty(
        name="Appliance Type",
        description="Type of appliance opening",
        items=[
            ('MICROWAVE', "Microwave", "Standard microwave opening"),
            ('WALL_OVEN', "Wall Oven", "Wall oven opening"),
            ('BUILT_IN_FRIDGE', "Built-in Fridge", "Built-in refrigerator surround"),
        ],
        default='MICROWAVE',
    )

    appliance_opening_height: FloatProperty(
        name="Opening Height",
        description="Height of appliance opening",
        default=0.4,
        min=0.25,
        max=1.0,
        unit='LENGTH',
        subtype='DISTANCE',
    )

    has_trim_frame: BoolProperty(
        name="Trim Frame",
        description="Add decorative trim around appliance opening",
        default=True,
    )

    # Sink base options
    has_plumbing_cutout: BoolProperty(
        name="Plumbing Cutout",
        description="Include cutout in back panel for plumbing",
        default=True,
    )

    # Open shelving options
    has_side_panels: BoolProperty(
        name="Side Panels",
        description="Include side panels on open shelving",
        default=True,
    )

    # Pull-out options
    pullout_extension: FloatProperty(
        name="Pull-out Extension",
        description="How far pull-out components are extended (for animation)",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
    )

    # Trash pull-out options
    has_trash_pullout: BoolProperty(
        name="Trash Pull-out",
        description="Include pull-out trash bin insert",
        default=False,
    )

    double_trash_bins: BoolProperty(
        name="Double Bins",
        description="Use two bins for trash and recycling",
        default=True,
    )

    # Spice rack options
    has_spice_rack: BoolProperty(
        name="Spice Rack",
        description="Include pull-out spice rack",
        default=False,
    )

    spice_rack_tiers: IntProperty(
        name="Spice Tiers",
        description="Number of spice rack tiers",
        default=4,
        min=2,
        max=6,
    )

    # Shelf pin options
    has_adjustable_shelves: BoolProperty(
        name="Adjustable Shelves",
        description="Add shelf pin holes for adjustable shelves",
        default=True,
    )

    shelf_pin_rows: IntProperty(
        name="Pin Rows",
        description="Number of shelf pin hole rows",
        default=10,
        min=4,
        max=20,
    )

    # Material presets
    carcass_preset: EnumProperty(
        name="Carcass Material",
        description="Material preset for cabinet box",
        items=[
            ('NONE', "None", "No material"),
            ('OAK', "Oak", "Natural oak wood"),
            ('WALNUT', "Walnut", "Dark walnut wood"),
            ('MAPLE', "Maple", "Light maple wood"),
            ('WHITE', "White Laminate", "Clean white laminate"),
            ('GRAY', "Gray Laminate", "Modern gray laminate"),
        ],
        default='NONE',
    )

    front_preset: EnumProperty(
        name="Front Material",
        description="Material preset for doors/drawer fronts",
        items=[
            ('NONE', "None", "No material"),
            ('OAK', "Oak", "Natural oak wood"),
            ('WALNUT', "Walnut", "Dark walnut wood"),
            ('MAPLE', "Maple", "Light maple wood"),
            ('WHITE', "White Laminate", "Clean white laminate"),
            ('NAVY', "Navy Laminate", "Deep navy laminate"),
            ('SAGE', "Sage Laminate", "Sage green laminate"),
        ],
        default='NONE',
    )

    handle_preset: EnumProperty(
        name="Handle Material",
        description="Material preset for handles",
        items=[
            ('NONE', "None", "No material"),
            ('BRUSHED_NICKEL', "Brushed Nickel", "Brushed nickel finish"),
            ('CHROME', "Chrome", "Polished chrome"),
            ('MATTE_BLACK', "Matte Black", "Matte black metal"),
            ('BRASS', "Brass", "Warm brass finish"),
            ('OIL_RUBBED_BRONZE', "Oil Rubbed Bronze", "Oil rubbed bronze"),
        ],
        default='NONE',
    )


# Test result item for collection property
class CABINET_PG_TestResult(PropertyGroup):
    """Individual test result"""
    name: bpy.props.StringProperty(name="Test Name")
    passed: BoolProperty(name="Passed", default=False)
    message: bpy.props.StringProperty(name="Message")
    category: bpy.props.StringProperty(name="Category")  # 'atomic', 'system', 'master'


# Test results container
class CABINET_PG_TestResults(PropertyGroup):
    """Container for all test results"""
    results: bpy.props.CollectionProperty(type=CABINET_PG_TestResult)
    active_index: IntProperty(name="Active Index", default=0)

    # Summary counts
    total_tests: IntProperty(name="Total", default=0)
    passed_tests: IntProperty(name="Passed", default=0)
    failed_tests: IntProperty(name="Failed", default=0)

    # Last run timestamp
    last_run: bpy.props.StringProperty(name="Last Run", default="Never")

    # Test state
    is_running: BoolProperty(name="Running", default=False)


# Registration
classes = (
    CABINET_PG_TestResult,
    CABINET_PG_TestResults,
    CABINET_PG_Settings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cabinet_settings = PointerProperty(type=CABINET_PG_Settings)
    bpy.types.Scene.cabinet_test_results = PointerProperty(type=CABINET_PG_TestResults)


def unregister():
    del bpy.types.Scene.cabinet_test_results
    del bpy.types.Scene.cabinet_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
