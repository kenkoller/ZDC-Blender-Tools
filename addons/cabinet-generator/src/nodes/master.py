# CabinetMaster node group generator
# Top-level orchestrator that combines all cabinet components
# Coordinate system: X=width, Y=depth, Z=height (Z-up, origin at floor)

import bpy
from .utils import (
    create_node_group,
    add_geometry_output,
    add_float_socket,
    add_int_socket,
    add_bool_socket,
    add_material_socket,
    create_panel,
    create_group_input,
    create_group_output,
    create_math,
    create_combine_xyz,
    create_transform,
    create_join_geometry,
    create_switch,
    create_compare,
    create_boolean_math,
    link,
    set_default,
    add_metadata,
)

# Import system generators to ensure node groups exist
from .systems import (
    cabinet_box, shelf_array, door_assembly, drawer_stack, blind_corner,
    sink_base, appliance_cabinet, open_shelving, diagonal_corner, pullout_pantry
)
from .atomic import (
    toe_kick, lazy_susan, hinges, drawer_slides, trash_pullout, spice_rack, shelf_pins,
    led_strip, crown_molding, light_rail
)


def create_cabinet_master_nodegroup():
    """Generate the CabinetMaster node group.

    Top-level orchestrator that creates a complete parametric cabinet
    by combining:
    - CabinetBox (carcass)
    - ShelfArray (internal shelves)
    - DoorAssembly or DrawerStack (front)

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back, front at Y=0)
    - Z = height (floor to ceiling, bottom at Z=0)
    - Origin at front-bottom-center

    Inputs:
        Cabinet Type (int): 0=Base, 1=Wall, 2=Tall
        Width (float): External cabinet width
        Height (float): External cabinet height
        Depth (float): External cabinet depth
        Panel Thickness (float): Carcass panel thickness
        Front Type (int): 0=Doors, 1=Drawers
        Door Style (int): 0=Flat, 1=Shaker, 2=Raised
        Double Doors (bool): Use double doors
        Drawer Count (int): Number of drawers (if front type is drawers)
        Shelf Count (int): Number of internal shelves
        Handle Style (int): 0=Bar, 1=Wire, 2=Knob
        Has Back (bool): Include back panel
        Carcass Material (material): Material for box
        Front Material (material): Material for doors/drawers
        Handle Material (material): Material for handles

    Outputs:
        Geometry: The complete cabinet mesh

    Returns:
        The created node group
    """
    ng = create_node_group("CabinetMaster")

    # Create interface panels
    type_panel = create_panel(ng, "Cabinet Type")
    dims_panel = create_panel(ng, "Dimensions")
    front_panel = create_panel(ng, "Front")
    interior_panel = create_panel(ng, "Interior")
    materials_panel = create_panel(ng, "Materials")

    # Cabinet type: 0=Base, 1=Wall, 2=Tall, 3=Drawer Base, 4=Blind Corner,
    # 5=Sink Base, 6=Appliance, 7=Open Shelving, 8=Diagonal Corner, 9=Pullout Pantry
    add_int_socket(ng, "Cabinet Type", default=0, min_val=0, max_val=9, panel=type_panel)
    # Cabinet Category: 0=Kitchen (24" depth), 1=Vanity (21" depth), 2=Closet (14" depth)
    add_int_socket(ng, "Cabinet Category", default=0, min_val=0, max_val=2, panel=type_panel)

    # Dimension inputs
    add_float_socket(ng, "Width", default=0.6, min_val=0.2, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.72, min_val=0.3, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.55, min_val=0.3, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Front options
    add_int_socket(ng, "Front Type", default=0, min_val=0, max_val=1, panel=front_panel)
    add_int_socket(ng, "Door Style", default=1, min_val=0, max_val=4, panel=front_panel)
    add_bool_socket(ng, "Double Doors", default=False, panel=front_panel)
    add_int_socket(ng, "Hinge Side", default=0, min_val=0, max_val=1, panel=front_panel)
    add_float_socket(ng, "Auto Double Width", default=0.6, min_val=0.4, max_val=1.0,
                     subtype='DISTANCE', panel=front_panel)
    add_int_socket(ng, "Drawer Count", default=3, min_val=1, max_val=6, panel=front_panel)
    add_int_socket(ng, "Handle Style", default=0, min_val=0, max_val=4, panel=front_panel)

    # Glass door options
    glass_panel = create_panel(ng, "Glass Door")
    add_bool_socket(ng, "Glass Insert", default=False, panel=glass_panel)
    add_float_socket(ng, "Glass Frame Width", default=0.04, min_val=0.02, max_val=0.1,
                     subtype='DISTANCE', panel=glass_panel)

    # Animation options
    anim_panel = create_panel(ng, "Animation")
    add_float_socket(ng, "Door Open Angle", default=0.0, min_val=0.0, max_val=120.0,
                     subtype='NONE', panel=anim_panel)
    add_float_socket(ng, "Drawer Open", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='FACTOR', panel=anim_panel)

    # Interior options
    add_int_socket(ng, "Shelf Count", default=1, min_val=0, max_val=10, panel=interior_panel)
    add_bool_socket(ng, "Has Back", default=True, panel=interior_panel)
    add_bool_socket(ng, "Has Lazy Susan", default=False, panel=interior_panel)
    add_int_socket(ng, "Lazy Susan Count", default=2, min_val=1, max_val=4, panel=interior_panel)
    # 0=Full Round, 1=Kidney, 2=Pie Cut, 3=D-Shape, 4=Half-Moon
    add_int_socket(ng, "Lazy Susan Style", default=0, min_val=0, max_val=4, panel=interior_panel)
    # Override diameter (0 = auto-calculate from interior dimensions)
    add_float_socket(ng, "Lazy Susan Diameter", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='DISTANCE', panel=interior_panel)

    # Toe kick options
    toekick_panel = create_panel(ng, "Toe Kick")
    add_bool_socket(ng, "Has Toe Kick", default=True, panel=toekick_panel)
    add_float_socket(ng, "Toe Kick Height", default=0.1, min_val=0.05, max_val=0.15,
                     subtype='DISTANCE', panel=toekick_panel)
    add_float_socket(ng, "Toe Kick Depth", default=0.06, min_val=0.03, max_val=0.1,
                     subtype='DISTANCE', panel=toekick_panel)

    # Corner cabinet options
    corner_panel = create_panel(ng, "Corner Options")
    add_int_socket(ng, "Corner Type", default=0, min_val=0, max_val=1, panel=corner_panel)
    add_float_socket(ng, "Blind Width", default=0.15, min_val=0.1, max_val=0.25,
                     subtype='DISTANCE', panel=corner_panel)

    # Bevel options
    bevel_panel = create_panel(ng, "Bevel")
    add_float_socket(ng, "Bevel Width", default=0.001, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=bevel_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=bevel_panel)

    # Hardware options
    hardware_panel = create_panel(ng, "Hardware")
    add_bool_socket(ng, "Show Hardware", default=True, panel=hardware_panel)
    add_int_socket(ng, "Hinge Style", default=0, min_val=0, max_val=2, panel=hardware_panel)
    add_int_socket(ng, "Drawer Slide Style", default=0, min_val=0, max_val=2, panel=hardware_panel)
    add_material_socket(ng, "Hardware Material", panel=hardware_panel)

    # Face frame options
    construction_panel = create_panel(ng, "Construction")
    add_bool_socket(ng, "Has Face Frame", default=False, panel=construction_panel)
    add_float_socket(ng, "Face Frame Width", default=0.038, min_val=0.025, max_val=0.075,
                     subtype='DISTANCE', panel=construction_panel)
    # Overlay Type: 0=Full Overlay (door covers frame), 1=Half Overlay (partial coverage), 2=Inset (door flush with frame)
    add_int_socket(ng, "Overlay Type", default=0, min_val=0, max_val=2, panel=construction_panel)

    # Appliance options
    appliance_panel = create_panel(ng, "Appliance")
    add_int_socket(ng, "Appliance Type", default=0, min_val=0, max_val=2, panel=appliance_panel)
    add_float_socket(ng, "Appliance Opening Height", default=0.4, min_val=0.25, max_val=1.0,
                     subtype='DISTANCE', panel=appliance_panel)
    add_bool_socket(ng, "Has Trim Frame", default=True, panel=appliance_panel)

    # Sink base options
    sink_panel = create_panel(ng, "Sink Base")
    add_bool_socket(ng, "Has Plumbing Cutout", default=True, panel=sink_panel)

    # Open shelving options
    shelving_panel = create_panel(ng, "Open Shelving")
    add_bool_socket(ng, "Has Sides", default=True, panel=shelving_panel)

    # Pull-out options
    pullout_panel = create_panel(ng, "Pull-out")
    add_float_socket(ng, "Pullout Extension", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='FACTOR', panel=pullout_panel)

    # Insert options
    inserts_panel = create_panel(ng, "Inserts")
    add_bool_socket(ng, "Has Trash Pullout", default=False, panel=inserts_panel)
    add_bool_socket(ng, "Double Trash Bins", default=True, panel=inserts_panel)
    add_bool_socket(ng, "Has Spice Rack", default=False, panel=inserts_panel)
    add_int_socket(ng, "Spice Rack Tiers", default=4, min_val=2, max_val=6, panel=inserts_panel)

    # Shelf pin options
    shelf_pins_panel = create_panel(ng, "Shelf Pins")
    add_bool_socket(ng, "Has Adjustable Shelves", default=True, panel=shelf_pins_panel)
    add_int_socket(ng, "Shelf Pin Rows", default=10, min_val=4, max_val=20, panel=shelf_pins_panel)

    # Molding options
    molding_panel = create_panel(ng, "Molding")
    add_bool_socket(ng, "Has Crown Molding", default=False, panel=molding_panel)
    add_float_socket(ng, "Crown Height", default=0.075, min_val=0.03, max_val=0.15,
                     subtype='DISTANCE', panel=molding_panel)
    add_float_socket(ng, "Crown Projection", default=0.03, min_val=0.01, max_val=0.06,
                     subtype='DISTANCE', panel=molding_panel)
    add_bool_socket(ng, "Has Light Rail", default=False, panel=molding_panel)
    add_float_socket(ng, "Light Rail Height", default=0.045, min_val=0.025, max_val=0.075,
                     subtype='DISTANCE', panel=molding_panel)

    # LED Lighting options
    lighting_panel = create_panel(ng, "Lighting")
    add_bool_socket(ng, "Has Under Cabinet Light", default=False, panel=lighting_panel)
    add_bool_socket(ng, "Has Interior Light", default=False, panel=lighting_panel)
    add_material_socket(ng, "LED Material", panel=lighting_panel)

    # Materials
    add_material_socket(ng, "Carcass Material", panel=materials_panel)
    add_material_socket(ng, "Front Material", panel=materials_panel)
    add_material_socket(ng, "Handle Material", panel=materials_panel)
    add_material_socket(ng, "Glass Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1200, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ ENSURE CHILD NODE GROUPS EXIST ============
    _required_groups = [
        ("CabinetBox", cabinet_box, "create_cabinet_box_nodegroup"),
        ("ShelfArray", shelf_array, "create_shelf_array_nodegroup"),
        ("DoorAssembly", door_assembly, "create_door_assembly_nodegroup"),
        ("DrawerStack", drawer_stack, "create_drawer_stack_nodegroup"),
        ("ToeKick", toe_kick, "create_toe_kick_nodegroup"),
        ("BlindCorner", blind_corner, "create_blind_corner_nodegroup"),
        ("SinkBase", sink_base, "create_sink_base_nodegroup"),
        ("ApplianceCabinet", appliance_cabinet, "create_appliance_cabinet_nodegroup"),
        ("OpenShelving", open_shelving, "create_open_shelving_nodegroup"),
        ("DiagonalCorner", diagonal_corner, "create_diagonal_corner_nodegroup"),
        ("PulloutPantry", pullout_pantry, "create_pullout_pantry_nodegroup"),
    ]
    _failed = []
    for group_name, module, func_name in _required_groups:
        if group_name not in bpy.data.node_groups:
            try:
                getattr(module, func_name)()
            except Exception as e:
                _failed.append(f"{group_name}: {e}")
                print(f"[CabinetMaster] Failed to create {group_name}: {e}")
    if _failed:
        raise RuntimeError(
            f"CabinetMaster: Failed to create required node groups:\n"
            + "\n".join(f"  - {f}" for f in _failed)
        )

    # ============ CABINET BOX NODE GROUP ============
    box_node = ng.nodes.new('GeometryNodeGroup')
    box_node.name = "Cabinet Box"
    box_node.node_tree = bpy.data.node_groups["CabinetBox"]
    box_node.location = (-600, 300)

    # Connect box inputs
    link(ng, group_in, "Width", box_node, "Width")
    link(ng, group_in, "Height", box_node, "Height")
    link(ng, group_in, "Depth", box_node, "Depth")
    link(ng, group_in, "Panel Thickness", box_node, "Panel Thickness")
    link(ng, group_in, "Has Back", box_node, "Has Back")
    link(ng, group_in, "Bevel Width", box_node, "Bevel Width")
    link(ng, group_in, "Bevel Segments", box_node, "Bevel Segments")
    link(ng, group_in, "Carcass Material", box_node, "Carcass Material")

    # ============ FRONT TYPE COMPARISON (used by multiple sections) ============
    is_drawers = create_compare(ng, 'EQUAL', 'INT', name="Is Drawers", location=(0, -400))
    link(ng, group_in, "Front Type", is_drawers, 2)
    set_default(is_drawers, 3, 1)

    # ============ SHELF ARRAY NODE GROUP ============
    shelf_node = ng.nodes.new('GeometryNodeGroup')
    shelf_node.name = "Shelf Array"
    shelf_node.node_tree = bpy.data.node_groups["ShelfArray"]
    shelf_node.location = (-600, 0)

    # Connect shelf inputs from box outputs
    link(ng, box_node, "Interior Width", shelf_node, "Interior Width")
    link(ng, box_node, "Interior Height", shelf_node, "Interior Height")
    link(ng, box_node, "Interior Depth", shelf_node, "Interior Depth")
    link(ng, group_in, "Shelf Count", shelf_node, "Shelf Count")
    link(ng, group_in, "Panel Thickness", shelf_node, "Shelf Thickness")
    link(ng, group_in, "Carcass Material", shelf_node, "Material")

    # ============ DOOR ASSEMBLY NODE GROUP ============
    door_node = ng.nodes.new('GeometryNodeGroup')
    door_node.name = "Door Assembly"
    door_node.node_tree = bpy.data.node_groups["DoorAssembly"]
    door_node.location = (-600, -300)

    # Connect door inputs
    link(ng, box_node, "Interior Width", door_node, "Opening Width")
    link(ng, box_node, "Interior Height", door_node, "Opening Height")
    link(ng, group_in, "Panel Thickness", door_node, "Door Thickness")
    link(ng, group_in, "Double Doors", door_node, "Double Doors")
    link(ng, group_in, "Hinge Side", door_node, "Hinge Side")
    link(ng, group_in, "Glass Insert", door_node, "Glass Insert")
    link(ng, group_in, "Glass Frame Width", door_node, "Glass Frame Width")
    link(ng, group_in, "Door Open Angle", door_node, "Door Open Angle")
    link(ng, group_in, "Bevel Width", door_node, "Bevel Width")
    link(ng, group_in, "Bevel Segments", door_node, "Bevel Segments")
    link(ng, group_in, "Front Material", door_node, "Door Material")
    link(ng, group_in, "Handle Material", door_node, "Handle Material")
    link(ng, group_in, "Glass Material", door_node, "Glass Material")
    link(ng, group_in, "Face Frame Width", door_node, "Face Frame Width")
    link(ng, group_in, "Overlay Type", door_node, "Overlay Type")

    # ============ DRAWER STACK NODE GROUP ============
    drawer_node = ng.nodes.new('GeometryNodeGroup')
    drawer_node.name = "Drawer Stack"
    drawer_node.node_tree = bpy.data.node_groups["DrawerStack"]
    drawer_node.location = (-600, -600)

    # Connect drawer inputs
    link(ng, box_node, "Interior Width", drawer_node, "Opening Width")
    link(ng, box_node, "Interior Height", drawer_node, "Opening Height")
    link(ng, group_in, "Drawer Count", drawer_node, "Drawer Count")
    link(ng, group_in, "Panel Thickness", drawer_node, "Front Thickness")
    link(ng, group_in, "Drawer Open", drawer_node, "Drawer Open")
    link(ng, box_node, "Interior Depth", drawer_node, "Drawer Depth")
    link(ng, group_in, "Bevel Width", drawer_node, "Bevel Width")
    link(ng, group_in, "Bevel Segments", drawer_node, "Bevel Segments")
    link(ng, group_in, "Front Material", drawer_node, "Front Material")
    link(ng, group_in, "Handle Material", drawer_node, "Handle Material")

    # ============ NOTE: FRONT ASSEMBLIES ARE ALREADY POSITIONED ============
    # DoorAssembly and DrawerStack now handle their own positioning
    # They are built with front face at Y=0 and bottom at Z=panel_thickness
    # No additional transform needed - they align with CabinetBox automatically

    # ============ TOE KICK NODE GROUP ============
    tk_node = ng.nodes.new('GeometryNodeGroup')
    tk_node.name = "Toe Kick"
    tk_node.node_tree = bpy.data.node_groups["ToeKick"]
    tk_node.location = (-600, -900)

    # Connect toe kick inputs
    link(ng, group_in, "Width", tk_node, "Width")
    link(ng, group_in, "Toe Kick Height", tk_node, "Height")
    link(ng, group_in, "Toe Kick Depth", tk_node, "Depth")
    link(ng, group_in, "Depth", tk_node, "Cabinet Depth")
    link(ng, group_in, "Panel Thickness", tk_node, "Panel Thickness")
    link(ng, group_in, "Carcass Material", tk_node, "Material")

    # Switch for toe kick
    switch_tk = create_switch(ng, 'GEOMETRY', name="Toe Kick Switch", location=(-300, -900))
    link(ng, group_in, "Has Toe Kick", switch_tk, "Switch")
    link(ng, tk_node, "Geometry", switch_tk, "True")

    # ============ BLIND CORNER NODE GROUP ============
    bc_node = ng.nodes.new('GeometryNodeGroup')
    bc_node.name = "Blind Corner"
    bc_node.node_tree = bpy.data.node_groups["BlindCorner"]
    bc_node.location = (-600, -1200)

    # Connect blind corner inputs
    link(ng, group_in, "Width", bc_node, "Width")
    link(ng, group_in, "Depth", bc_node, "Depth")
    link(ng, group_in, "Height", bc_node, "Height")
    link(ng, group_in, "Blind Width", bc_node, "Blind Width")
    link(ng, group_in, "Panel Thickness", bc_node, "Panel Thickness")
    link(ng, group_in, "Has Lazy Susan", bc_node, "Has Lazy Susan")
    link(ng, group_in, "Lazy Susan Count", bc_node, "Lazy Susan Count")
    link(ng, group_in, "Lazy Susan Style", bc_node, "Lazy Susan Style")
    link(ng, group_in, "Lazy Susan Diameter", bc_node, "Lazy Susan Diameter")
    link(ng, group_in, "Corner Type", bc_node, "Corner Type")
    link(ng, group_in, "Has Back", bc_node, "Has Back")
    link(ng, group_in, "Has Toe Kick", bc_node, "Has Toe Kick")
    link(ng, group_in, "Toe Kick Height", bc_node, "Toe Kick Height")
    link(ng, group_in, "Toe Kick Depth", bc_node, "Toe Kick Depth")
    link(ng, group_in, "Bevel Width", bc_node, "Bevel Width")
    link(ng, group_in, "Bevel Segments", bc_node, "Bevel Segments")
    link(ng, group_in, "Carcass Material", bc_node, "Carcass Material")
    link(ng, group_in, "Front Material", bc_node, "Door Material")
    link(ng, group_in, "Carcass Material", bc_node, "Shelf Material")

    # ============ NEW CABINET TYPE NODE GROUPS ============

    # Sink Base
    sb_node = ng.nodes.new('GeometryNodeGroup')
    sb_node.name = "Sink Base"
    sb_node.node_tree = bpy.data.node_groups["SinkBase"]
    sb_node.location = (-600, -1500)

    link(ng, group_in, "Width", sb_node, "Width")
    link(ng, group_in, "Height", sb_node, "Height")
    link(ng, group_in, "Depth", sb_node, "Depth")
    link(ng, group_in, "Panel Thickness", sb_node, "Panel Thickness")
    link(ng, group_in, "Has Plumbing Cutout", sb_node, "Has Plumbing Cutout")
    link(ng, group_in, "Has Toe Kick", sb_node, "Has Toe Kick")
    link(ng, group_in, "Toe Kick Height", sb_node, "Toe Kick Height")
    link(ng, group_in, "Toe Kick Depth", sb_node, "Toe Kick Depth")
    link(ng, group_in, "Carcass Material", sb_node, "Carcass Material")
    link(ng, group_in, "Front Material", sb_node, "Front Material")

    # Appliance Cabinet
    app_node = ng.nodes.new('GeometryNodeGroup')
    app_node.name = "Appliance Cabinet"
    app_node.node_tree = bpy.data.node_groups["ApplianceCabinet"]
    app_node.location = (-600, -1800)

    link(ng, group_in, "Width", app_node, "Width")
    link(ng, group_in, "Height", app_node, "Height")
    link(ng, group_in, "Depth", app_node, "Depth")
    link(ng, group_in, "Panel Thickness", app_node, "Panel Thickness")
    link(ng, group_in, "Appliance Type", app_node, "Appliance Type")
    link(ng, group_in, "Appliance Opening Height", app_node, "Opening Height")
    link(ng, group_in, "Has Trim Frame", app_node, "Has Trim")
    link(ng, group_in, "Carcass Material", app_node, "Carcass Material")

    # Open Shelving
    os_node = ng.nodes.new('GeometryNodeGroup')
    os_node.name = "Open Shelving"
    os_node.node_tree = bpy.data.node_groups["OpenShelving"]
    os_node.location = (-600, -2100)

    link(ng, group_in, "Width", os_node, "Width")
    link(ng, group_in, "Height", os_node, "Height")
    link(ng, group_in, "Depth", os_node, "Depth")
    link(ng, group_in, "Panel Thickness", os_node, "Panel Thickness")
    link(ng, group_in, "Shelf Count", os_node, "Shelf Count")
    link(ng, group_in, "Has Sides", os_node, "Has Sides")
    link(ng, group_in, "Has Back", os_node, "Has Back")
    # Note: OpenShelving uses Shelf/Side/Back Material instead of Carcass Material
    link(ng, group_in, "Carcass Material", os_node, "Shelf Material")
    link(ng, group_in, "Carcass Material", os_node, "Side Material")
    link(ng, group_in, "Carcass Material", os_node, "Back Material")

    # Diagonal Corner
    dc_node = ng.nodes.new('GeometryNodeGroup')
    dc_node.name = "Diagonal Corner"
    dc_node.node_tree = bpy.data.node_groups["DiagonalCorner"]
    dc_node.location = (-600, -2400)

    link(ng, group_in, "Width", dc_node, "Width")
    link(ng, group_in, "Depth", dc_node, "Depth")
    link(ng, group_in, "Height", dc_node, "Height")
    link(ng, group_in, "Panel Thickness", dc_node, "Panel Thickness")
    link(ng, group_in, "Has Lazy Susan", dc_node, "Has Lazy Susan")
    link(ng, group_in, "Lazy Susan Count", dc_node, "Lazy Susan Count")
    link(ng, group_in, "Lazy Susan Style", dc_node, "Lazy Susan Style")
    link(ng, group_in, "Lazy Susan Diameter", dc_node, "Lazy Susan Diameter")
    link(ng, group_in, "Has Back", dc_node, "Has Back")
    link(ng, group_in, "Has Toe Kick", dc_node, "Has Toe Kick")
    link(ng, group_in, "Toe Kick Height", dc_node, "Toe Kick Height")
    link(ng, group_in, "Carcass Material", dc_node, "Carcass Material")
    link(ng, group_in, "Front Material", dc_node, "Door Material")

    # Pullout Pantry
    pp_node = ng.nodes.new('GeometryNodeGroup')
    pp_node.name = "Pullout Pantry"
    pp_node.node_tree = bpy.data.node_groups["PulloutPantry"]
    pp_node.location = (-600, -2700)

    link(ng, group_in, "Width", pp_node, "Width")
    link(ng, group_in, "Height", pp_node, "Height")
    link(ng, group_in, "Depth", pp_node, "Depth")
    link(ng, group_in, "Panel Thickness", pp_node, "Panel Thickness")
    link(ng, group_in, "Shelf Count", pp_node, "Shelf Count")
    link(ng, group_in, "Pullout Extension", pp_node, "Extension")
    link(ng, group_in, "Has Toe Kick", pp_node, "Has Toe Kick")
    link(ng, group_in, "Toe Kick Height", pp_node, "Toe Kick Height")
    link(ng, group_in, "Carcass Material", pp_node, "Carcass Material")
    link(ng, group_in, "Front Material", pp_node, "Front Material")

    # ============ HARDWARE NODE GROUPS ============
    # Ensure hardware node groups exist
    if "Hinge" not in bpy.data.node_groups:
        hinges.create_hinge_nodegroup()
    if "DrawerSlides" not in bpy.data.node_groups:
        drawer_slides.create_drawer_slides_nodegroup()
    if "ShelfPins" not in bpy.data.node_groups:
        shelf_pins.create_shelf_pins_nodegroup()
    if "TrashPullout" not in bpy.data.node_groups:
        trash_pullout.create_trash_pullout_nodegroup()
    if "SpiceRack" not in bpy.data.node_groups:
        spice_rack.create_spice_rack_nodegroup()
    if "LEDStrip" not in bpy.data.node_groups:
        led_strip.create_led_strip_nodegroup()
    if "CrownMolding" not in bpy.data.node_groups:
        crown_molding.create_crown_molding_nodegroup()
    if "LightRail" not in bpy.data.node_groups:
        light_rail.create_light_rail_nodegroup()

    # Hinge node (for doors)
    hinge_node = ng.nodes.new('GeometryNodeGroup')
    hinge_node.name = "Hinge"
    hinge_node.node_tree = bpy.data.node_groups["Hinge"]
    hinge_node.location = (-200, -400)

    link(ng, group_in, "Hinge Style", hinge_node, "Style")
    link(ng, group_in, "Panel Thickness", hinge_node, "Door Thickness")
    link(ng, group_in, "Hardware Material", hinge_node, "Material")

    # Position hinges on cabinet side panel (two hinges per door)
    # Top hinge position
    hinge_top_z = create_math(ng, 'SUBTRACT', name="Hinge Top Z", location=(-400, -450))
    link(ng, group_in, "Height", hinge_top_z, 0)
    set_default(hinge_top_z, 1, 0.1)  # 100mm from top

    hinge_top_pos = create_combine_xyz(ng, name="Hinge Top Pos", location=(-300, -450))
    # X = half width (on side panel)
    half_width = create_math(ng, 'DIVIDE', name="Half Width", location=(-500, -500))
    link(ng, group_in, "Width", half_width, 0)
    set_default(half_width, 1, -2.0)
    link(ng, half_width, 0, hinge_top_pos, "X")
    set_default(hinge_top_pos, "Y", -0.037)  # 37mm from front (standard cup hinge)
    link(ng, hinge_top_z, 0, hinge_top_pos, "Z")

    hinge_top_transform = create_transform(ng, name="Hinge Top", location=(-100, -420))
    link(ng, hinge_node, "Geometry", hinge_top_transform, "Geometry")
    link(ng, hinge_top_pos, "Vector", hinge_top_transform, "Translation")

    # Bottom hinge position
    hinge_bottom_pos = create_combine_xyz(ng, name="Hinge Bottom Pos", location=(-300, -550))
    link(ng, half_width, 0, hinge_bottom_pos, "X")
    set_default(hinge_bottom_pos, "Y", -0.037)
    hinge_bottom_z = create_math(ng, 'ADD', name="Hinge Bottom Z", location=(-400, -550))
    link(ng, group_in, "Panel Thickness", hinge_bottom_z, 0)
    set_default(hinge_bottom_z, 1, 0.1)  # 100mm from bottom panel
    link(ng, hinge_bottom_z, 0, hinge_bottom_pos, "Z")

    hinge_bottom_transform = create_transform(ng, name="Hinge Bottom", location=(-100, -550))
    link(ng, hinge_node, "Geometry", hinge_bottom_transform, "Geometry")
    link(ng, hinge_bottom_pos, "Vector", hinge_bottom_transform, "Translation")

    # Join hinges
    join_hinges = create_join_geometry(ng, name="Join Hinges", location=(0, -480))
    link(ng, hinge_top_transform, "Geometry", join_hinges, "Geometry")
    link(ng, hinge_bottom_transform, "Geometry", join_hinges, "Geometry")

    # Switch hinges on/off based on Show Hardware AND Front Type == Doors
    is_doors = create_compare(ng, 'EQUAL', 'INT', name="Is Doors", location=(100, -520))
    link(ng, group_in, "Front Type", is_doors, 2)
    set_default(is_doors, 3, 0)

    show_hinges = create_boolean_math(ng, 'AND', name="Show Hinges", location=(200, -520))
    link(ng, group_in, "Show Hardware", show_hinges, 0)
    link(ng, is_doors, "Result", show_hinges, 1)

    switch_hinges = create_switch(ng, 'GEOMETRY', name="Hinge Switch", location=(300, -480))
    link(ng, show_hinges, 0, switch_hinges, "Switch")
    link(ng, join_hinges, "Geometry", switch_hinges, "True")

    # Drawer Slides node
    slides_node = ng.nodes.new('GeometryNodeGroup')
    slides_node.name = "Drawer Slides"
    slides_node.node_tree = bpy.data.node_groups["DrawerSlides"]
    slides_node.location = (-200, -700)

    link(ng, group_in, "Drawer Slide Style", slides_node, "Style")
    link(ng, group_in, "Depth", slides_node, "Depth")
    link(ng, box_node, "Interior Width", slides_node, "Drawer Width")
    link(ng, group_in, "Drawer Open", slides_node, "Extension")
    link(ng, group_in, "Hardware Material", slides_node, "Material")

    # Position drawer slides
    slides_pos = create_combine_xyz(ng, name="Slides Pos", location=(-100, -750))
    set_default(slides_pos, "X", 0.0)
    slides_y = create_math(ng, 'DIVIDE', name="Slides Y", location=(-200, -780))
    link(ng, group_in, "Depth", slides_y, 0)
    set_default(slides_y, 1, -2.0)
    link(ng, slides_y, 0, slides_pos, "Y")
    link(ng, group_in, "Panel Thickness", slides_pos, "Z")

    slides_transform = create_transform(ng, name="Slides Transform", location=(0, -700))
    link(ng, slides_node, "Geometry", slides_transform, "Geometry")
    link(ng, slides_pos, "Vector", slides_transform, "Translation")

    # Switch drawer slides on/off based on Show Hardware AND Front Type == Drawers
    show_slides = create_boolean_math(ng, 'AND', name="Show Slides", location=(200, -720))
    link(ng, group_in, "Show Hardware", show_slides, 0)
    link(ng, is_drawers, "Result", show_slides, 1)

    switch_slides = create_switch(ng, 'GEOMETRY', name="Slides Switch", location=(300, -700))
    link(ng, show_slides, 0, switch_slides, "Switch")
    link(ng, slides_transform, "Geometry", switch_slides, "True")

    # Shelf Pins node (for left and right side panels)
    pins_node = ng.nodes.new('GeometryNodeGroup')
    pins_node.name = "Shelf Pins"
    pins_node.node_tree = bpy.data.node_groups["ShelfPins"]
    pins_node.location = (-200, -900)

    link(ng, box_node, "Interior Height", pins_node, "Height")
    link(ng, box_node, "Interior Depth", pins_node, "Depth")
    link(ng, group_in, "Panel Thickness", pins_node, "Panel Thickness")

    # Position shelf pins on left side
    left_pins_pos = create_combine_xyz(ng, name="Left Pins Pos", location=(-100, -950))
    link(ng, half_width, 0, left_pins_pos, "X")
    set_default(left_pins_pos, "Y", 0.0)
    link(ng, group_in, "Panel Thickness", left_pins_pos, "Z")

    left_pins_transform = create_transform(ng, name="Left Pins", location=(0, -920))
    link(ng, pins_node, "Geometry", left_pins_transform, "Geometry")
    link(ng, left_pins_pos, "Vector", left_pins_transform, "Translation")

    # Right side pins (mirror X)
    right_half_width = create_math(ng, 'MULTIPLY', name="Right Half Width", location=(-300, -1000))
    link(ng, half_width, 0, right_half_width, 0)
    set_default(right_half_width, 1, -1.0)

    right_pins_pos = create_combine_xyz(ng, name="Right Pins Pos", location=(-100, -1030))
    link(ng, right_half_width, 0, right_pins_pos, "X")
    set_default(right_pins_pos, "Y", 0.0)
    link(ng, group_in, "Panel Thickness", right_pins_pos, "Z")

    right_pins_transform = create_transform(ng, name="Right Pins", location=(0, -1000))
    link(ng, pins_node, "Geometry", right_pins_transform, "Geometry")
    link(ng, right_pins_pos, "Vector", right_pins_transform, "Translation")

    # Join shelf pins
    join_pins = create_join_geometry(ng, name="Join Pins", location=(100, -960))
    link(ng, left_pins_transform, "Geometry", join_pins, "Geometry")
    link(ng, right_pins_transform, "Geometry", join_pins, "Geometry")

    # Switch shelf pins based on Has Adjustable Shelves AND Show Hardware
    show_pins = create_boolean_math(ng, 'AND', name="Show Pins", location=(200, -960))
    link(ng, group_in, "Show Hardware", show_pins, 0)
    link(ng, group_in, "Has Adjustable Shelves", show_pins, 1)

    switch_pins = create_switch(ng, 'GEOMETRY', name="Pins Switch", location=(300, -920))
    link(ng, show_pins, 0, switch_pins, "Switch")
    link(ng, join_pins, "Geometry", switch_pins, "True")

    # ============ INSERT NODE GROUPS ============
    # Trash Pullout
    trash_node = ng.nodes.new('GeometryNodeGroup')
    trash_node.name = "Trash Pullout"
    trash_node.node_tree = bpy.data.node_groups["TrashPullout"]
    trash_node.location = (-200, -1150)

    link(ng, box_node, "Interior Width", trash_node, "Width")
    link(ng, box_node, "Interior Depth", trash_node, "Depth")
    link(ng, box_node, "Interior Height", trash_node, "Height")
    link(ng, group_in, "Double Trash Bins", trash_node, "Double Bin")
    link(ng, group_in, "Drawer Open", trash_node, "Extension")
    link(ng, group_in, "Hardware Material", trash_node, "Frame Material")
    link(ng, group_in, "Carcass Material", trash_node, "Bin Material")

    # Position trash pullout inside cabinet
    trash_pos = create_combine_xyz(ng, name="Trash Pos", location=(-100, -1200))
    set_default(trash_pos, "X", 0.0)
    link(ng, slides_y, 0, trash_pos, "Y")
    link(ng, group_in, "Panel Thickness", trash_pos, "Z")

    trash_transform = create_transform(ng, name="Trash Transform", location=(0, -1150))
    link(ng, trash_node, "Geometry", trash_transform, "Geometry")
    link(ng, trash_pos, "Vector", trash_transform, "Translation")

    switch_trash = create_switch(ng, 'GEOMETRY', name="Trash Switch", location=(200, -1150))
    link(ng, group_in, "Has Trash Pullout", switch_trash, "Switch")
    link(ng, trash_transform, "Geometry", switch_trash, "True")

    # Spice Rack
    spice_node = ng.nodes.new('GeometryNodeGroup')
    spice_node.name = "Spice Rack"
    spice_node.node_tree = bpy.data.node_groups["SpiceRack"]
    spice_node.location = (-200, -1350)

    set_default(spice_node, "Width", 0.1)  # Typical spice rack width
    link(ng, box_node, "Interior Depth", spice_node, "Depth")
    link(ng, box_node, "Interior Height", spice_node, "Height")
    link(ng, group_in, "Spice Rack Tiers", spice_node, "Tier Count")
    link(ng, group_in, "Drawer Open", spice_node, "Extension")
    link(ng, group_in, "Carcass Material", spice_node, "Frame Material")
    link(ng, group_in, "Handle Material", spice_node, "Lip Material")

    # Position spice rack on side of cabinet
    spice_pos = create_combine_xyz(ng, name="Spice Pos", location=(-100, -1400))
    spice_x = create_math(ng, 'ADD', name="Spice X", location=(-200, -1400))
    link(ng, half_width, 0, spice_x, 0)
    set_default(spice_x, 1, 0.07)  # Offset from side panel
    link(ng, spice_x, 0, spice_pos, "X")
    link(ng, slides_y, 0, spice_pos, "Y")
    link(ng, group_in, "Panel Thickness", spice_pos, "Z")

    spice_transform = create_transform(ng, name="Spice Transform", location=(0, -1350))
    link(ng, spice_node, "Geometry", spice_transform, "Geometry")
    link(ng, spice_pos, "Vector", spice_transform, "Translation")

    switch_spice = create_switch(ng, 'GEOMETRY', name="Spice Switch", location=(200, -1350))
    link(ng, group_in, "Has Spice Rack", switch_spice, "Switch")
    link(ng, spice_transform, "Geometry", switch_spice, "True")

    # ============ MOLDING NODE GROUPS ============
    # Crown Molding (for wall and tall cabinets)
    crown_node = ng.nodes.new('GeometryNodeGroup')
    crown_node.name = "Crown Molding"
    crown_node.node_tree = bpy.data.node_groups["CrownMolding"]
    crown_node.location = (-200, -1550)

    link(ng, group_in, "Width", crown_node, "Width")
    link(ng, group_in, "Depth", crown_node, "Depth")
    link(ng, group_in, "Crown Height", crown_node, "Profile Height")
    link(ng, group_in, "Crown Projection", crown_node, "Profile Projection")
    link(ng, group_in, "Front Material", crown_node, "Material")

    # Position crown at top of cabinet
    crown_pos = create_combine_xyz(ng, name="Crown Pos", location=(-100, -1600))
    set_default(crown_pos, "X", 0.0)
    set_default(crown_pos, "Y", 0.0)
    link(ng, group_in, "Height", crown_pos, "Z")

    crown_transform = create_transform(ng, name="Crown Transform", location=(0, -1550))
    link(ng, crown_node, "Geometry", crown_transform, "Geometry")
    link(ng, crown_pos, "Vector", crown_transform, "Translation")

    switch_crown = create_switch(ng, 'GEOMETRY', name="Crown Switch", location=(200, -1550))
    link(ng, group_in, "Has Crown Molding", switch_crown, "Switch")
    link(ng, crown_transform, "Geometry", switch_crown, "True")

    # Light Rail (for wall cabinets - under cabinet)
    rail_node = ng.nodes.new('GeometryNodeGroup')
    rail_node.name = "Light Rail"
    rail_node.node_tree = bpy.data.node_groups["LightRail"]
    rail_node.location = (-200, -1750)

    link(ng, group_in, "Width", rail_node, "Width")
    link(ng, group_in, "Light Rail Height", rail_node, "Rail Height")
    link(ng, group_in, "Panel Thickness", rail_node, "Rail Thickness")
    link(ng, group_in, "Front Material", rail_node, "Material")

    # Light rail hangs from bottom of cabinet (Z=0 for wall cabinet bottom)
    switch_rail = create_switch(ng, 'GEOMETRY', name="Rail Switch", location=(200, -1750))
    link(ng, group_in, "Has Light Rail", switch_rail, "Switch")
    link(ng, rail_node, "Geometry", switch_rail, "True")

    # ============ LED LIGHTING ============
    # Under cabinet LED strip
    led_under_node = ng.nodes.new('GeometryNodeGroup')
    led_under_node.name = "LED Under"
    led_under_node.node_tree = bpy.data.node_groups["LEDStrip"]
    led_under_node.location = (-200, -1950)

    link(ng, group_in, "Width", led_under_node, "Length")
    link(ng, group_in, "LED Material", led_under_node, "LED Material")
    link(ng, group_in, "Hardware Material", led_under_node, "Housing Material")

    # Position LED under cabinet (behind light rail if present)
    led_under_pos = create_combine_xyz(ng, name="LED Under Pos", location=(-100, -2000))
    set_default(led_under_pos, "X", 0.0)
    set_default(led_under_pos, "Y", -0.03)  # Recessed from front
    set_default(led_under_pos, "Z", -0.01)  # Just below bottom

    led_under_transform = create_transform(ng, name="LED Under Transform", location=(0, -1950))
    link(ng, led_under_node, "Geometry", led_under_transform, "Geometry")
    link(ng, led_under_pos, "Vector", led_under_transform, "Translation")

    switch_led_under = create_switch(ng, 'GEOMETRY', name="LED Under Switch", location=(200, -1950))
    link(ng, group_in, "Has Under Cabinet Light", switch_led_under, "Switch")
    link(ng, led_under_transform, "Geometry", switch_led_under, "True")

    # Interior LED strip
    led_int_node = ng.nodes.new('GeometryNodeGroup')
    led_int_node.name = "LED Interior"
    led_int_node.node_tree = bpy.data.node_groups["LEDStrip"]
    led_int_node.location = (-200, -2150)

    link(ng, box_node, "Interior Width", led_int_node, "Length")
    link(ng, group_in, "LED Material", led_int_node, "LED Material")
    link(ng, group_in, "Hardware Material", led_int_node, "Housing Material")

    # Position interior LED at top inside cabinet
    led_int_pos = create_combine_xyz(ng, name="LED Int Pos", location=(-100, -2200))
    set_default(led_int_pos, "X", 0.0)
    led_int_y = create_math(ng, 'DIVIDE', name="LED Int Y", location=(-200, -2200))
    link(ng, group_in, "Depth", led_int_y, 0)
    set_default(led_int_y, 1, -2.0)
    link(ng, led_int_y, 0, led_int_pos, "Y")
    # Z at top panel minus small offset
    led_int_z = create_math(ng, 'SUBTRACT', name="LED Int Z", location=(-200, -2250))
    link(ng, group_in, "Height", led_int_z, 0)
    set_default(led_int_z, 1, 0.02)
    link(ng, led_int_z, 0, led_int_pos, "Z")

    led_int_transform = create_transform(ng, name="LED Int Transform", location=(0, -2150))
    link(ng, led_int_node, "Geometry", led_int_transform, "Geometry")
    link(ng, led_int_pos, "Vector", led_int_transform, "Translation")

    switch_led_int = create_switch(ng, 'GEOMETRY', name="LED Int Switch", location=(200, -2150))
    link(ng, group_in, "Has Interior Light", switch_led_int, "Switch")
    link(ng, led_int_transform, "Geometry", switch_led_int, "True")

    # Join all hardware, inserts, molding, and lighting
    join_hardware = create_join_geometry(ng, name="Join Hardware", location=(400, -800))
    link(ng, switch_hinges, "Output", join_hardware, "Geometry")
    link(ng, switch_slides, "Output", join_hardware, "Geometry")
    link(ng, switch_pins, "Output", join_hardware, "Geometry")
    link(ng, switch_trash, "Output", join_hardware, "Geometry")
    link(ng, switch_spice, "Output", join_hardware, "Geometry")
    link(ng, switch_crown, "Output", join_hardware, "Geometry")
    link(ng, switch_rail, "Output", join_hardware, "Geometry")
    link(ng, switch_led_under, "Output", join_hardware, "Geometry")
    link(ng, switch_led_int, "Output", join_hardware, "Geometry")

    # ============ SWITCH DOORS VS DRAWERS ============
    # (is_drawers node created earlier in file)
    switch_front = create_switch(ng, 'GEOMETRY', name="Front Switch", location=(200, -350))
    link(ng, is_drawers, "Result", switch_front, "Switch")
    link(ng, door_node, "Geometry", switch_front, "False")
    link(ng, drawer_node, "Geometry", switch_front, "True")

    # ============ JOIN STANDARD CABINET COMPONENTS ============
    join_standard = create_join_geometry(ng, name="Join Standard", location=(400, 0))
    link(ng, box_node, "Geometry", join_standard, "Geometry")
    link(ng, shelf_node, "Geometry", join_standard, "Geometry")
    link(ng, switch_front, "Output", join_standard, "Geometry")
    link(ng, switch_tk, "Output", join_standard, "Geometry")
    link(ng, join_hardware, "Geometry", join_standard, "Geometry")

    # ============ CABINET TYPE SWITCHING ============
    # Types: 0=Base, 1=Wall, 2=Tall, 3=Drawer Base, 4=Blind Corner,
    #        5=Sink Base, 6=Appliance, 7=Open Shelving, 8=Diagonal Corner, 9=Pullout Pantry

    # Switch for Blind Corner (type 4)
    is_blind_corner = create_compare(ng, 'EQUAL', 'INT', name="Is Blind Corner", location=(500, -200))
    link(ng, group_in, "Cabinet Type", is_blind_corner, 2)
    set_default(is_blind_corner, 3, 4)

    switch_bc = create_switch(ng, 'GEOMETRY', name="BC Switch", location=(600, -100))
    link(ng, is_blind_corner, "Result", switch_bc, "Switch")
    link(ng, join_standard, "Geometry", switch_bc, "False")
    link(ng, bc_node, "Geometry", switch_bc, "True")

    # Switch for Sink Base (type 5)
    is_sink = create_compare(ng, 'EQUAL', 'INT', name="Is Sink Base", location=(500, -350))
    link(ng, group_in, "Cabinet Type", is_sink, 2)
    set_default(is_sink, 3, 5)

    switch_sink = create_switch(ng, 'GEOMETRY', name="Sink Switch", location=(700, -200))
    link(ng, is_sink, "Result", switch_sink, "Switch")
    link(ng, switch_bc, "Output", switch_sink, "False")
    link(ng, sb_node, "Geometry", switch_sink, "True")

    # Switch for Appliance (type 6)
    is_appliance = create_compare(ng, 'EQUAL', 'INT', name="Is Appliance", location=(500, -500))
    link(ng, group_in, "Cabinet Type", is_appliance, 2)
    set_default(is_appliance, 3, 6)

    switch_app = create_switch(ng, 'GEOMETRY', name="Appliance Switch", location=(800, -300))
    link(ng, is_appliance, "Result", switch_app, "Switch")
    link(ng, switch_sink, "Output", switch_app, "False")
    link(ng, app_node, "Geometry", switch_app, "True")

    # Switch for Open Shelving (type 7)
    is_open = create_compare(ng, 'EQUAL', 'INT', name="Is Open Shelving", location=(500, -650))
    link(ng, group_in, "Cabinet Type", is_open, 2)
    set_default(is_open, 3, 7)

    switch_open = create_switch(ng, 'GEOMETRY', name="Open Switch", location=(900, -400))
    link(ng, is_open, "Result", switch_open, "Switch")
    link(ng, switch_app, "Output", switch_open, "False")
    link(ng, os_node, "Geometry", switch_open, "True")

    # Switch for Diagonal Corner (type 8)
    is_diag = create_compare(ng, 'EQUAL', 'INT', name="Is Diagonal Corner", location=(500, -800))
    link(ng, group_in, "Cabinet Type", is_diag, 2)
    set_default(is_diag, 3, 8)

    switch_diag = create_switch(ng, 'GEOMETRY', name="Diagonal Switch", location=(1000, -500))
    link(ng, is_diag, "Result", switch_diag, "Switch")
    link(ng, switch_open, "Output", switch_diag, "False")
    link(ng, dc_node, "Geometry", switch_diag, "True")

    # Switch for Pullout Pantry (type 9)
    is_pullout = create_compare(ng, 'EQUAL', 'INT', name="Is Pullout Pantry", location=(500, -950))
    link(ng, group_in, "Cabinet Type", is_pullout, 2)
    set_default(is_pullout, 3, 9)

    switch_pullout = create_switch(ng, 'GEOMETRY', name="Pullout Switch", location=(1100, -600))
    link(ng, is_pullout, "Result", switch_pullout, "Switch")
    link(ng, switch_diag, "Output", switch_pullout, "False")
    link(ng, pp_node, "Geometry", switch_pullout, "True")

    # ============ OUTPUT ============
    link(ng, switch_pullout, "Output", group_out, "Geometry")

    # Add metadata
    add_metadata(ng, version="4.0.0",
                 script_path="src/nodes/master.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the CabinetMaster node group applied."""
    if nodegroup is None:
        nodegroup = create_cabinet_master_nodegroup()

    mesh = bpy.data.meshes.new("Cabinet")
    obj = bpy.data.objects.new("Cabinet", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


def generate_all_nodegroups():
    """Generate all required node groups in the correct order."""
    # Generate atomic components first
    from .atomic import shelf, door_panel, drawer, hardware
    shelf.create_shelf_nodegroup()
    door_panel.create_door_panel_nodegroup()
    drawer.create_drawer_nodegroup()
    hardware.create_handle_nodegroup()
    toe_kick.create_toe_kick_nodegroup()
    lazy_susan.create_lazy_susan_nodegroup()

    # Generate new atomic components
    hinges.create_hinge_nodegroup()
    drawer_slides.create_drawer_slides_nodegroup()
    trash_pullout.create_trash_pullout_nodegroup()
    spice_rack.create_spice_rack_nodegroup()
    shelf_pins.create_shelf_pins_nodegroup()
    led_strip.create_led_strip_nodegroup()
    crown_molding.create_crown_molding_nodegroup()
    light_rail.create_light_rail_nodegroup()

    # Generate system components
    cabinet_box.create_cabinet_box_nodegroup()
    shelf_array.create_shelf_array_nodegroup()
    door_assembly.create_door_assembly_nodegroup()
    drawer_stack.create_drawer_stack_nodegroup()
    blind_corner.create_blind_corner_nodegroup()

    # Generate new cabinet type systems
    sink_base.create_sink_base_nodegroup()
    appliance_cabinet.create_appliance_cabinet_nodegroup()
    open_shelving.create_open_shelving_nodegroup()
    diagonal_corner.create_diagonal_corner_nodegroup()
    pullout_pantry.create_pullout_pantry_nodegroup()

    # Generate master
    create_cabinet_master_nodegroup()

    return True


if __name__ == "__main__":
    generate_all_nodegroups()
    print("Generated all cabinet node groups")
