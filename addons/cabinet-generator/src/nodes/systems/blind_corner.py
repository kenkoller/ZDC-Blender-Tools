# Blind Corner Cabinet node group generator
# System component: L-shaped corner cabinet with optional lazy susan

import bpy
from ..utils import (
    create_node_group,
    add_geometry_output,
    add_float_socket,
    add_int_socket,
    add_bool_socket,
    add_material_socket,
    create_panel,
    create_group_input,
    create_group_output,
    create_cube,
    create_math,
    create_combine_xyz,
    create_set_material,
    create_transform,
    create_join_geometry,
    create_switch,
    create_compare,
    create_bevel,
    link,
    set_default,
    add_metadata,
)


def create_blind_corner_nodegroup():
    """Generate the BlindCorner node group.

    Creates an L-shaped blind corner cabinet for kitchen corners.
    The "blind" refers to the portion that extends behind an adjacent cabinet.

    Configuration options:
    - Left-hand or right-hand corner orientation
    - Optional lazy susan shelf
    - Single door (angled or straight)
    - Standard or diagonal front

    Standard dimensions:
    - Width: 36-42" (including blind portion)
    - Blind portion: 6-9" (hidden behind adjacent cabinet)
    - Door opening: 12-15"

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back)
    - Z = height (floor to ceiling)
    - Origin at front-bottom-center of door opening

    Inputs:
        Width (float): Total cabinet width (including blind)
        Depth (float): Total cabinet depth
        Height (float): Cabinet height
        Blind Width (float): Width of blind (hidden) portion
        Panel Thickness (float): Carcass panel thickness
        Has Lazy Susan (bool): Include lazy susan shelves
        Lazy Susan Count (int): Number of lazy susan tiers
        Corner Type (int): 0=Left corner, 1=Right corner
        Door Type (int): 0=Standard, 1=Diagonal
        Has Back (bool): Include back panels
        Has Toe Kick (bool): Include toe kick
        Toe Kick Height (float): Height of toe kick
        Carcass Material (material): Material for box
        Door Material (material): Material for door
        Shelf Material (material): Material for shelves

    Outputs:
        Geometry: The complete blind corner cabinet mesh

    Returns:
        The created node group
    """
    ng = create_node_group("BlindCorner")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    corner_panel = create_panel(ng, "Corner Options")
    interior_panel = create_panel(ng, "Interior")
    toekick_panel = create_panel(ng, "Toe Kick")
    materials_panel = create_panel(ng, "Materials")

    # Dimension inputs
    add_float_socket(ng, "Width", default=0.9, min_val=0.6, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.6, min_val=0.5, max_val=0.8,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.72, min_val=0.3, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Blind Width", default=0.15, min_val=0.1, max_val=0.25,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Corner options
    add_int_socket(ng, "Corner Type", default=0, min_val=0, max_val=1, panel=corner_panel)
    add_int_socket(ng, "Door Type", default=0, min_val=0, max_val=1, panel=corner_panel)

    # Interior options
    add_bool_socket(ng, "Has Lazy Susan", default=True, panel=interior_panel)
    add_int_socket(ng, "Lazy Susan Count", default=2, min_val=1, max_val=4, panel=interior_panel)
    # 0=Full Round, 1=Kidney, 2=Pie Cut, 3=D-Shape, 4=Half-Moon
    add_int_socket(ng, "Lazy Susan Style", default=0, min_val=0, max_val=4, panel=interior_panel)
    # Override diameter (0 = auto-calculate from interior dimensions)
    add_float_socket(ng, "Lazy Susan Diameter", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='DISTANCE', panel=interior_panel)
    add_bool_socket(ng, "Has Back", default=True, panel=interior_panel)
    add_int_socket(ng, "Shelf Count", default=1, min_val=0, max_val=3, panel=interior_panel)

    # Toe kick options
    add_bool_socket(ng, "Has Toe Kick", default=True, panel=toekick_panel)
    add_float_socket(ng, "Toe Kick Height", default=0.1, min_val=0.05, max_val=0.15,
                     subtype='DISTANCE', panel=toekick_panel)
    add_float_socket(ng, "Toe Kick Depth", default=0.06, min_val=0.03, max_val=0.1,
                     subtype='DISTANCE', panel=toekick_panel)

    # Bevel options
    bevel_panel = create_panel(ng, "Bevel")
    add_float_socket(ng, "Bevel Width", default=0.001, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=bevel_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=bevel_panel)

    # Materials
    add_material_socket(ng, "Carcass Material", panel=materials_panel)
    add_material_socket(ng, "Door Material", panel=materials_panel)
    add_material_socket(ng, "Shelf Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1200, 0))
    group_out = create_group_output(ng, location=(1200, 0))

    # ============ CALCULATE DIMENSIONS ============
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-1000, -100))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)

    # Door opening width = Width - Blind Width
    door_opening = create_math(ng, 'SUBTRACT', name="Door Opening", location=(-1000, 100))
    link(ng, group_in, "Width", door_opening, 0)
    link(ng, group_in, "Blind Width", door_opening, 1)

    # Box height (minus toe kick if applicable)
    box_height = create_math(ng, 'SUBTRACT', name="Box Height Base", location=(-1000, 0))
    link(ng, group_in, "Height", box_height, 0)
    link(ng, group_in, "Toe Kick Height", box_height, 1)

    # Interior dimensions
    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-900, -200))
    link(ng, group_in, "Width", interior_width, 0)
    link(ng, panel_x2, 0, interior_width, 1)

    interior_depth = create_math(ng, 'SUBTRACT', name="Interior Depth", location=(-900, -300))
    link(ng, group_in, "Depth", interior_depth, 0)
    link(ng, panel_x2, 0, interior_depth, 1)

    interior_height = create_math(ng, 'SUBTRACT', name="Interior Height", location=(-900, -400))
    link(ng, box_height, 0, interior_height, 0)
    link(ng, panel_x2, 0, interior_height, 1)

    # ============ L-SHAPED CARCASS ============
    # The carcass is built from multiple panels forming an L-shape

    # ===== OUTER LEFT SIDE PANEL =====
    left_side = create_cube(ng, name="Left Side", location=(-600, 400))
    left_size = create_combine_xyz(ng, name="Left Size", location=(-750, 450))
    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-750, 350))
    left_transform = create_transform(ng, name="Left Transform", location=(-450, 400))

    link(ng, group_in, "Panel Thickness", left_size, "X")
    link(ng, group_in, "Depth", left_size, "Y")
    link(ng, box_height, 0, left_size, "Z")
    link(ng, left_size, "Vector", left_side, "Size")

    # Left X position
    left_x_sub = create_math(ng, 'SUBTRACT', name="Left X Sub", location=(-900, 400))
    link(ng, group_in, "Width", left_x_sub, 0)
    link(ng, group_in, "Panel Thickness", left_x_sub, 1)

    left_x = create_math(ng, 'DIVIDE', name="Left X", location=(-800, 400))
    link(ng, left_x_sub, 0, left_x, 0)
    set_default(left_x, 1, -2.0)

    depth_half_neg = create_math(ng, 'DIVIDE', name="Depth Half Neg", location=(-900, 300))
    link(ng, group_in, "Depth", depth_half_neg, 0)
    set_default(depth_half_neg, 1, -2.0)

    # Z position for toe kick
    box_z = create_math(ng, 'DIVIDE', name="Box Z", location=(-900, 200))
    link(ng, box_height, 0, box_z, 0)
    set_default(box_z, 1, 2.0)

    toe_kick_offset = create_math(ng, 'ADD', name="Toe Kick Offset", location=(-800, 200))
    link(ng, box_z, 0, toe_kick_offset, 0)
    link(ng, group_in, "Toe Kick Height", toe_kick_offset, 1)

    link(ng, left_x, 0, left_pos, "X")
    link(ng, depth_half_neg, 0, left_pos, "Y")
    link(ng, toe_kick_offset, 0, left_pos, "Z")
    link(ng, left_pos, "Vector", left_transform, "Translation")
    link(ng, left_side, "Mesh", left_transform, "Geometry")

    # ===== BLIND SIDE PANEL (back portion of L) =====
    blind_side = create_cube(ng, name="Blind Side", location=(-600, 200))
    blind_size = create_combine_xyz(ng, name="Blind Size", location=(-750, 250))
    blind_pos = create_combine_xyz(ng, name="Blind Pos", location=(-750, 150))
    blind_transform = create_transform(ng, name="Blind Transform", location=(-450, 200))

    # Blind side depth = Width - door_opening - panel_thickness
    blind_depth = create_math(ng, 'SUBTRACT', name="Blind Depth", location=(-900, 150))
    link(ng, group_in, "Blind Width", blind_depth, 0)
    link(ng, group_in, "Panel Thickness", blind_depth, 1)

    link(ng, group_in, "Panel Thickness", blind_size, "X")
    link(ng, blind_depth, 0, blind_size, "Y")
    link(ng, box_height, 0, blind_size, "Z")
    link(ng, blind_size, "Vector", blind_side, "Size")

    # Blind side position (at back, on right side of opening)
    door_half = create_math(ng, 'DIVIDE', name="Door Half", location=(-900, 50))
    link(ng, door_opening, 0, door_half, 0)
    set_default(door_half, 1, 2.0)

    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-900, -50))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)

    blind_x = create_math(ng, 'ADD', name="Blind X", location=(-800, 50))
    link(ng, door_half, 0, blind_x, 0)
    link(ng, panel_half, 0, blind_x, 1)

    blind_depth_half = create_math(ng, 'DIVIDE', name="Blind D Half", location=(-800, 0))
    link(ng, blind_depth, 0, blind_depth_half, 0)
    set_default(blind_depth_half, 1, 2.0)

    blind_y = create_math(ng, 'SUBTRACT', name="Blind Y", location=(-700, -50))
    link(ng, group_in, "Depth", blind_y, 0)
    link(ng, blind_depth_half, 0, blind_y, 1)
    blind_y_neg = create_math(ng, 'MULTIPLY', name="Blind Y Neg", location=(-600, -50))
    link(ng, blind_y, 0, blind_y_neg, 0)
    set_default(blind_y_neg, 1, -1.0)

    link(ng, blind_x, 0, blind_pos, "X")
    link(ng, blind_y_neg, 0, blind_pos, "Y")
    link(ng, toe_kick_offset, 0, blind_pos, "Z")
    link(ng, blind_pos, "Vector", blind_transform, "Translation")
    link(ng, blind_side, "Mesh", blind_transform, "Geometry")

    # ===== FRONT RIGHT SIDE (next to door opening) =====
    right_front = create_cube(ng, name="Right Front", location=(-600, 0))
    right_front_size = create_combine_xyz(ng, name="R Front Size", location=(-750, 50))
    right_front_pos = create_combine_xyz(ng, name="R Front Pos", location=(-750, -50))
    right_front_transform = create_transform(ng, name="R Front Transform", location=(-450, 0))

    # This panel goes from front to where blind side starts
    right_depth = create_math(ng, 'SUBTRACT', name="Right Depth", location=(-900, -100))
    link(ng, group_in, "Depth", right_depth, 0)
    link(ng, blind_depth, 0, right_depth, 1)

    link(ng, group_in, "Panel Thickness", right_front_size, "X")
    link(ng, right_depth, 0, right_front_size, "Y")
    link(ng, box_height, 0, right_front_size, "Z")
    link(ng, right_front_size, "Vector", right_front, "Size")

    right_depth_half = create_math(ng, 'DIVIDE', name="R Depth Half", location=(-800, -150))
    link(ng, right_depth, 0, right_depth_half, 0)
    set_default(right_depth_half, 1, -2.0)

    link(ng, blind_x, 0, right_front_pos, "X")
    link(ng, right_depth_half, 0, right_front_pos, "Y")
    link(ng, toe_kick_offset, 0, right_front_pos, "Z")
    link(ng, right_front_pos, "Vector", right_front_transform, "Translation")
    link(ng, right_front, "Mesh", right_front_transform, "Geometry")

    # ===== TOP PANEL =====
    top = create_cube(ng, name="Top", location=(-600, -200))
    top_size = create_combine_xyz(ng, name="Top Size", location=(-750, -150))
    top_pos = create_combine_xyz(ng, name="Top Pos", location=(-750, -250))
    top_transform = create_transform(ng, name="Top Transform", location=(-450, -200))

    link(ng, interior_width, 0, top_size, "X")
    link(ng, group_in, "Depth", top_size, "Y")
    link(ng, group_in, "Panel Thickness", top_size, "Z")
    link(ng, top_size, "Vector", top, "Size")

    top_z = create_math(ng, 'SUBTRACT', name="Top Z", location=(-900, -250))
    link(ng, group_in, "Height", top_z, 0)
    link(ng, panel_half, 0, top_z, 1)

    link(ng, depth_half_neg, 0, top_pos, "Y")
    link(ng, top_z, 0, top_pos, "Z")
    link(ng, top_pos, "Vector", top_transform, "Translation")
    link(ng, top, "Mesh", top_transform, "Geometry")

    # ===== BOTTOM PANEL =====
    bottom = create_cube(ng, name="Bottom", location=(-600, -400))
    bottom_pos = create_combine_xyz(ng, name="Bottom Pos", location=(-750, -450))
    bottom_transform = create_transform(ng, name="Bottom Transform", location=(-450, -400))

    link(ng, top_size, "Vector", bottom, "Size")

    bottom_z = create_math(ng, 'ADD', name="Bottom Z", location=(-900, -450))
    link(ng, group_in, "Toe Kick Height", bottom_z, 0)
    link(ng, panel_half, 0, bottom_z, 1)

    link(ng, depth_half_neg, 0, bottom_pos, "Y")
    link(ng, bottom_z, 0, bottom_pos, "Z")
    link(ng, bottom_pos, "Vector", bottom_transform, "Translation")
    link(ng, bottom, "Mesh", bottom_transform, "Geometry")

    # ===== BACK PANELS =====
    back_left = create_cube(ng, name="Back Left", location=(-600, -600))
    back_left_size = create_combine_xyz(ng, name="Back L Size", location=(-750, -550))
    back_left_pos = create_combine_xyz(ng, name="Back L Pos", location=(-750, -650))
    back_left_transform = create_transform(ng, name="Back L Transform", location=(-450, -600))

    back_thickness = create_math(ng, 'MULTIPLY', name="Back Thick", location=(-950, -550))
    link(ng, group_in, "Panel Thickness", back_thickness, 0)
    set_default(back_thickness, 1, 0.333)  # Back is thinner

    # Back left covers from left side to blind corner
    back_left_width = create_math(ng, 'SUBTRACT', name="Back L Width", location=(-850, -550))
    link(ng, group_in, "Width", back_left_width, 0)
    link(ng, group_in, "Blind Width", back_left_width, 1)

    link(ng, back_left_width, 0, back_left_size, "X")
    link(ng, back_thickness, 0, back_left_size, "Y")
    link(ng, interior_height, 0, back_left_size, "Z")
    link(ng, back_left_size, "Vector", back_left, "Size")

    back_thick_half = create_math(ng, 'DIVIDE', name="Back T Half", location=(-850, -600))
    link(ng, back_thickness, 0, back_thick_half, 0)
    set_default(back_thick_half, 1, 2.0)

    back_y = create_math(ng, 'SUBTRACT', name="Back Y", location=(-750, -650))
    link(ng, back_thick_half, 0, back_y, 0)
    link(ng, group_in, "Depth", back_y, 1)

    back_left_x = create_math(ng, 'DIVIDE', name="Back L X", location=(-850, -700))
    link(ng, group_in, "Blind Width", back_left_x, 0)
    set_default(back_left_x, 1, -2.0)

    link(ng, back_left_x, 0, back_left_pos, "X")
    link(ng, back_y, 0, back_left_pos, "Y")
    link(ng, toe_kick_offset, 0, back_left_pos, "Z")
    link(ng, back_left_pos, "Vector", back_left_transform, "Translation")
    link(ng, back_left, "Mesh", back_left_transform, "Geometry")

    # Switch for back panel
    switch_back = create_switch(ng, 'GEOMETRY', name="Back Switch", location=(-200, -600))
    link(ng, group_in, "Has Back", switch_back, "Switch")
    link(ng, back_left_transform, "Geometry", switch_back, "True")

    # ============ JOIN CARCASS ============
    join_carcass = create_join_geometry(ng, name="Join Carcass", location=(-100, 100))
    link(ng, left_transform, "Geometry", join_carcass, "Geometry")
    link(ng, blind_transform, "Geometry", join_carcass, "Geometry")
    link(ng, right_front_transform, "Geometry", join_carcass, "Geometry")
    link(ng, top_transform, "Geometry", join_carcass, "Geometry")
    link(ng, bottom_transform, "Geometry", join_carcass, "Geometry")
    link(ng, switch_back, "Output", join_carcass, "Geometry")

    # Set carcass material
    carcass_mat = create_set_material(ng, name="Carcass Material", location=(100, 100))
    link(ng, join_carcass, "Geometry", carcass_mat, "Geometry")
    link(ng, group_in, "Carcass Material", carcass_mat, "Material")

    # ============ LAZY SUSAN SHELVES ============
    # Import lazy susan generator if needed
    from ..atomic import lazy_susan
    if "LazySusan" not in bpy.data.node_groups:
        lazy_susan.create_lazy_susan_nodegroup()

    # --- Diameter logic: use override if > 0, else auto-calculate ---
    # Auto-calc: min(interior_width, interior_depth) * 0.9
    ls_auto_diam = create_math(ng, 'MINIMUM', name="LS Auto Diam", location=(-100, -300))
    link(ng, interior_width, 0, ls_auto_diam, 0)
    link(ng, interior_depth, 0, ls_auto_diam, 1)

    ls_auto_adj = create_math(ng, 'MULTIPLY', name="LS Auto Adj", location=(0, -300))
    link(ng, ls_auto_diam, 0, ls_auto_adj, 0)
    set_default(ls_auto_adj, 1, 0.9)

    # Check if override > 0
    ls_has_override = create_compare(ng, 'GREATER_THAN', 'FLOAT', name="LS Has Override", location=(0, -350))
    link(ng, group_in, "Lazy Susan Diameter", ls_has_override, 0)
    set_default(ls_has_override, 1, 0.001)

    # Switch: override vs auto
    ls_diam_switch = create_switch(ng, 'FLOAT', name="LS Diam Switch", location=(100, -320))
    link(ng, ls_has_override, "Result", ls_diam_switch, "Switch")
    link(ng, ls_auto_adj, 0, ls_diam_switch, "False")
    link(ng, group_in, "Lazy Susan Diameter", ls_diam_switch, "True")

    # --- Create lazy susan tiers (up to 4 via manual duplication) ---
    # Calculate tier spacing: interior_height / (count + 1) for even distribution
    ls_count_plus1 = create_math(ng, 'ADD', name="LS Count+1", location=(-200, -450))
    link(ng, group_in, "Lazy Susan Count", ls_count_plus1, 0)
    set_default(ls_count_plus1, 1, 1.0)

    ls_tier_spacing = create_math(ng, 'DIVIDE', name="LS Tier Spacing", location=(-100, -450))
    link(ng, interior_height, 0, ls_tier_spacing, 0)
    link(ng, ls_count_plus1, 0, ls_tier_spacing, 1)

    # Create 4 lazy susan tier nodes (switch off unused ones)
    ls_tiers_join = create_join_geometry(ng, name="LS Tiers Join", location=(350, -250))

    for tier_idx in range(4):
        tier_num = tier_idx + 1
        y_loc = -200 - tier_idx * 120

        ls_node = ng.nodes.new('GeometryNodeGroup')
        ls_node.name = f"Lazy Susan T{tier_num}"
        ls_node.node_tree = bpy.data.node_groups["LazySusan"]
        ls_node.location = (100, y_loc)

        # Wire diameter and style
        link(ng, ls_diam_switch, "Output", ls_node, "Diameter")
        link(ng, group_in, "Lazy Susan Style", ls_node, "Style")
        link(ng, group_in, "Shelf Material", ls_node, "Material")

        # Position: Z = bottom_z + tier_spacing * tier_num
        ls_tier_z_mult = create_math(ng, 'MULTIPLY', name=f"LS T{tier_num} ZMul", location=(-50, y_loc - 30))
        link(ng, ls_tier_spacing, 0, ls_tier_z_mult, 0)
        set_default(ls_tier_z_mult, 1, float(tier_num))

        ls_tier_z = create_math(ng, 'ADD', name=f"LS T{tier_num} Z", location=(0, y_loc - 30))
        link(ng, bottom_z, 0, ls_tier_z, 0)
        link(ng, ls_tier_z_mult, 0, ls_tier_z, 1)

        ls_tier_pos = create_combine_xyz(ng, name=f"LS T{tier_num} Pos", location=(50, y_loc - 30))
        link(ng, depth_half_neg, 0, ls_tier_pos, "Y")
        link(ng, ls_tier_z, 0, ls_tier_pos, "Z")

        ls_tier_xform = create_transform(ng, name=f"LS T{tier_num} Xform", location=(200, y_loc))
        link(ng, ls_node, "Geometry", ls_tier_xform, "Geometry")
        link(ng, ls_tier_pos, "Vector", ls_tier_xform, "Translation")

        # Enable this tier only if tier_num <= Lazy Susan Count
        ls_tier_active = create_compare(ng, 'GREATER_EQUAL', 'INT',
                                        name=f"LS T{tier_num} Active", location=(250, y_loc - 30))
        link(ng, group_in, "Lazy Susan Count", ls_tier_active, 2)
        set_default(ls_tier_active, 3, tier_num)

        ls_tier_switch = create_switch(ng, 'GEOMETRY',
                                       name=f"LS T{tier_num} Switch", location=(300, y_loc))
        link(ng, ls_tier_active, "Result", ls_tier_switch, "Switch")
        link(ng, ls_tier_xform, "Geometry", ls_tier_switch, "True")

        link(ng, ls_tier_switch, "Output", ls_tiers_join, "Geometry")

    # Master switch for lazy susan
    switch_ls = create_switch(ng, 'GEOMETRY', name="LS Switch", location=(450, -300))
    link(ng, group_in, "Has Lazy Susan", switch_ls, "Switch")
    link(ng, ls_tiers_join, "Geometry", switch_ls, "True")

    # ============ DOOR ============
    door = create_cube(ng, name="Door", location=(100, -600))
    door_size = create_combine_xyz(ng, name="Door Size", location=(-50, -550))
    door_pos = create_combine_xyz(ng, name="Door Pos", location=(-50, -650))
    door_transform = create_transform(ng, name="Door Transform", location=(200, -600))

    door_gap = 0.003
    door_width = create_math(ng, 'SUBTRACT', name="Door Width", location=(-150, -550))
    link(ng, door_opening, 0, door_width, 0)
    set_default(door_width, 1, door_gap * 2)

    door_height = create_math(ng, 'SUBTRACT', name="Door Height", location=(-150, -600))
    link(ng, box_height, 0, door_height, 0)
    set_default(door_height, 1, door_gap * 2)

    link(ng, door_width, 0, door_size, "X")
    link(ng, group_in, "Panel Thickness", door_size, "Y")
    link(ng, door_height, 0, door_size, "Z")
    link(ng, door_size, "Vector", door, "Size")

    door_y = create_math(ng, 'DIVIDE', name="Door Y", location=(-150, -700))
    link(ng, group_in, "Panel Thickness", door_y, 0)
    set_default(door_y, 1, 2.0)

    door_x = create_math(ng, 'DIVIDE', name="Door X", location=(-150, -750))
    link(ng, door_opening, 0, door_x, 0)
    set_default(door_x, 1, -2.0)

    door_x_adj = create_math(ng, 'ADD', name="Door X Adj", location=(-50, -750))
    link(ng, left_x, 0, door_x_adj, 0)
    link(ng, door_x, 0, door_x_adj, 1)
    door_x_final = create_math(ng, 'MULTIPLY', name="Door X Final", location=(50, -750))
    link(ng, door_x_adj, 0, door_x_final, 0)
    set_default(door_x_final, 1, -1.0)

    link(ng, door_x_final, 0, door_pos, "X")
    link(ng, door_y, 0, door_pos, "Y")
    link(ng, toe_kick_offset, 0, door_pos, "Z")
    link(ng, door_pos, "Vector", door_transform, "Translation")
    link(ng, door, "Mesh", door_transform, "Geometry")

    door_mat = create_set_material(ng, name="Door Material", location=(350, -600))
    link(ng, door_transform, "Geometry", door_mat, "Geometry")
    link(ng, group_in, "Door Material", door_mat, "Material")

    # ============ TOE KICK ============
    from ..atomic import toe_kick
    if "ToeKick" not in bpy.data.node_groups:
        toe_kick.create_toe_kick_nodegroup()

    tk_node = ng.nodes.new('GeometryNodeGroup')
    tk_node.name = "Toe Kick"
    tk_node.node_tree = bpy.data.node_groups["ToeKick"]
    tk_node.location = (100, -900)

    link(ng, group_in, "Width", tk_node, "Width")
    link(ng, group_in, "Toe Kick Height", tk_node, "Height")
    link(ng, group_in, "Toe Kick Depth", tk_node, "Depth")
    link(ng, group_in, "Depth", tk_node, "Cabinet Depth")
    link(ng, group_in, "Panel Thickness", tk_node, "Panel Thickness")
    link(ng, group_in, "Carcass Material", tk_node, "Material")

    # Position toe kick
    tk_pos = create_combine_xyz(ng, name="TK Pos", location=(0, -950))
    link(ng, door_x_final, 0, tk_pos, "X")

    tk_transform = create_transform(ng, name="TK Transform", location=(200, -900))
    link(ng, tk_node, "Geometry", tk_transform, "Geometry")
    link(ng, tk_pos, "Vector", tk_transform, "Translation")

    switch_tk = create_switch(ng, 'GEOMETRY', name="TK Switch", location=(350, -900))
    link(ng, group_in, "Has Toe Kick", switch_tk, "Switch")
    link(ng, tk_transform, "Geometry", switch_tk, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(600, 0))
    link(ng, carcass_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_ls, "Output", join_all, "Geometry")
    link(ng, door_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_tk, "Output", join_all, "Geometry")

    # ============ BEVEL ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(800, 0))
    if bevel is not None:
        link(ng, join_all, "Geometry", bevel, "Mesh")
        link(ng, group_in, "Bevel Width", bevel, "Width")
        link(ng, group_in, "Bevel Segments", bevel, "Segments")
        pre_mirror_geo = bevel
        pre_mirror_socket = "Mesh"
    else:
        pre_mirror_geo = join_all
        pre_mirror_socket = "Geometry"

    # ============ CORNER TYPE MIRROR ============
    # If right corner, mirror the geometry
    is_right = create_compare(ng, 'EQUAL', 'INT', name="Is Right", location=(900, -100))
    link(ng, group_in, "Corner Type", is_right, 2)
    set_default(is_right, 3, 1)

    mirror_scale = create_combine_xyz(ng, name="Mirror Scale", location=(900, -200))
    set_default(mirror_scale, "X", -1.0)
    set_default(mirror_scale, "Y", 1.0)
    set_default(mirror_scale, "Z", 1.0)

    mirror_transform = create_transform(ng, name="Mirror Transform", location=(1000, 0))
    link(ng, pre_mirror_geo, pre_mirror_socket, mirror_transform, "Geometry")
    link(ng, mirror_scale, "Vector", mirror_transform, "Scale")

    switch_mirror = create_switch(ng, 'GEOMETRY', name="Mirror Switch", location=(1100, 0))
    link(ng, is_right, "Result", switch_mirror, "Switch")
    link(ng, pre_mirror_geo, pre_mirror_socket, switch_mirror, "False")
    link(ng, mirror_transform, "Geometry", switch_mirror, "True")

    # Output
    link(ng, switch_mirror, "Output", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/systems/blind_corner.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the BlindCorner node group applied."""
    if nodegroup is None:
        nodegroup = create_blind_corner_nodegroup()

    mesh = bpy.data.meshes.new("BlindCorner_Test")
    obj = bpy.data.objects.new("BlindCorner_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_blind_corner_nodegroup()
    print(f"Created node group: {ng.name}")
