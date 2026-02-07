# Pull-out Pantry Cabinet node group generator
# System component: Narrow tall cabinet with pull-out rack system
# Coordinate system: X=width, Y=depth, Z=height (Z-up)

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
    create_bevel,
    link,
    set_default,
    add_metadata,
)


def create_pullout_pantry_nodegroup():
    """Generate the PulloutPantry node group.

    Narrow tall cabinet with full-extension pull-out rack:
    - Tall narrow form factor (typically 6-12" wide)
    - Multiple shelves on pull-out frame
    - Front panel attached to pull-out
    - Full-extension slides

    Ideal for:
    - Spice storage
    - Canned goods
    - Narrow spaces next to appliances

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back, negative Y is front)
    - Z = height (floor to ceiling)
    - Origin at front-bottom-center (floor level)
    """
    ng = create_node_group("PulloutPantry")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    shelves_panel = create_panel(ng, "Shelves")
    anim_panel = create_panel(ng, "Animation")
    toekick_panel = create_panel(ng, "Toe Kick")
    bevel_panel = create_panel(ng, "Bevel")
    materials_panel = create_panel(ng, "Materials")

    # Dimensions
    add_float_socket(ng, "Width", default=0.15, min_val=0.1, max_val=0.3,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=2.0, min_val=1.5, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.55, min_val=0.4, max_val=0.65,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Shelves
    add_int_socket(ng, "Shelf Count", default=6, min_val=3, max_val=12, panel=shelves_panel)
    add_float_socket(ng, "Shelf Lip Height", default=0.025, min_val=0.015, max_val=0.05,
                     subtype='DISTANCE', panel=shelves_panel)

    # Animation
    add_float_socket(ng, "Extension", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='FACTOR', panel=anim_panel)

    # Toe Kick
    add_bool_socket(ng, "Has Toe Kick", default=True, panel=toekick_panel)
    add_float_socket(ng, "Toe Kick Height", default=0.1, min_val=0.05, max_val=0.15,
                     subtype='DISTANCE', panel=toekick_panel)
    add_float_socket(ng, "Toe Kick Depth", default=0.06, min_val=0.03, max_val=0.1,
                     subtype='DISTANCE', panel=toekick_panel)

    # Bevel
    add_float_socket(ng, "Bevel Width", default=0.001, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=bevel_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=bevel_panel)

    # Materials
    add_material_socket(ng, "Carcass Material", panel=materials_panel)
    add_material_socket(ng, "Front Material", panel=materials_panel)
    add_material_socket(ng, "Rack Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1400, 0))
    group_out = create_group_output(ng, location=(1400, 0))

    # ============ CALCULATE DIMENSIONS ============
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-1200, -400))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)

    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-1100, -400))
    link(ng, group_in, "Width", interior_width, 0)
    link(ng, panel_x2, 0, interior_width, 1)

    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-1200, -500))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-1200, -550))
    link(ng, group_in, "Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-1200, -600))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)

    # ============ CABINET BOX (CARCASS) ============
    # Left side panel
    left_size = create_combine_xyz(ng, name="Left Size", location=(-1000, 400))
    link(ng, group_in, "Panel Thickness", left_size, "X")
    link(ng, group_in, "Depth", left_size, "Y")
    link(ng, group_in, "Height", left_size, "Z")

    left_side = create_cube(ng, name="Left Side", location=(-900, 400))
    link(ng, left_size, "Vector", left_side, "Size")

    width_half = create_math(ng, 'DIVIDE', name="Width Half", location=(-1100, 350))
    link(ng, group_in, "Width", width_half, 0)
    set_default(width_half, 1, 2.0)
    left_x = create_math(ng, 'MULTIPLY', name="Left X Neg", location=(-1000, 350))
    link(ng, width_half, 0, left_x, 0)
    set_default(left_x, 1, -1.0)
    left_x_offset = create_math(ng, 'ADD', name="Left X Offset", location=(-900, 350))
    link(ng, left_x, 0, left_x_offset, 0)
    link(ng, panel_half, 0, left_x_offset, 1)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-800, 400))
    link(ng, left_x_offset, 0, left_pos, "X")
    link(ng, depth_half, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Transform", location=(-700, 400))
    link(ng, left_side, "Mesh", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    # Right side panel
    right_side = create_cube(ng, name="Right Side", location=(-900, 250))
    link(ng, left_size, "Vector", right_side, "Size")

    right_x = create_math(ng, 'SUBTRACT', name="Right X", location=(-900, 200))
    link(ng, width_half, 0, right_x, 0)
    link(ng, panel_half, 0, right_x, 1)

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-800, 250))
    link(ng, right_x, 0, right_pos, "X")
    link(ng, depth_half, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Transform", location=(-700, 250))
    link(ng, right_side, "Mesh", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    # Top panel
    top_size = create_combine_xyz(ng, name="Top Size", location=(-1000, 100))
    link(ng, interior_width, 0, top_size, "X")
    link(ng, group_in, "Depth", top_size, "Y")
    link(ng, group_in, "Panel Thickness", top_size, "Z")

    top = create_cube(ng, name="Top", location=(-900, 100))
    link(ng, top_size, "Vector", top, "Size")

    top_z = create_math(ng, 'SUBTRACT', name="Top Z", location=(-1000, 50))
    link(ng, group_in, "Height", top_z, 0)
    link(ng, panel_half, 0, top_z, 1)

    top_pos = create_combine_xyz(ng, name="Top Pos", location=(-800, 100))
    set_default(top_pos, "X", 0.0)
    link(ng, depth_half, 0, top_pos, "Y")
    link(ng, top_z, 0, top_pos, "Z")

    top_transform = create_transform(ng, name="Top Transform", location=(-700, 100))
    link(ng, top, "Mesh", top_transform, "Geometry")
    link(ng, top_pos, "Vector", top_transform, "Translation")

    # Bottom panel
    bottom = create_cube(ng, name="Bottom", location=(-900, -50))
    link(ng, top_size, "Vector", bottom, "Size")

    bottom_pos = create_combine_xyz(ng, name="Bottom Pos", location=(-800, -50))
    set_default(bottom_pos, "X", 0.0)
    link(ng, depth_half, 0, bottom_pos, "Y")
    link(ng, panel_half, 0, bottom_pos, "Z")

    bottom_transform = create_transform(ng, name="Bottom Transform", location=(-700, -50))
    link(ng, bottom, "Mesh", bottom_transform, "Geometry")
    link(ng, bottom_pos, "Vector", bottom_transform, "Translation")

    # Back panel
    interior_height = create_math(ng, 'SUBTRACT', name="Interior Height", location=(-1100, -200))
    link(ng, group_in, "Height", interior_height, 0)
    link(ng, panel_x2, 0, interior_height, 1)

    back_size = create_combine_xyz(ng, name="Back Size", location=(-1000, -200))
    link(ng, interior_width, 0, back_size, "X")
    set_default(back_size, "Y", 0.006)
    link(ng, interior_height, 0, back_size, "Z")

    back = create_cube(ng, name="Back", location=(-900, -200))
    link(ng, back_size, "Vector", back, "Size")

    back_y = create_math(ng, 'MULTIPLY', name="Back Y Neg", location=(-1000, -250))
    link(ng, group_in, "Depth", back_y, 0)
    set_default(back_y, 1, -1.0)
    back_y_offset = create_math(ng, 'ADD', name="Back Y Offset", location=(-900, -250))
    link(ng, back_y, 0, back_y_offset, 0)
    set_default(back_y_offset, 1, 0.003)

    back_pos = create_combine_xyz(ng, name="Back Pos", location=(-800, -200))
    set_default(back_pos, "X", 0.0)
    link(ng, back_y_offset, 0, back_pos, "Y")
    link(ng, height_half, 0, back_pos, "Z")

    back_transform = create_transform(ng, name="Back Transform", location=(-700, -200))
    link(ng, back, "Mesh", back_transform, "Geometry")
    link(ng, back_pos, "Vector", back_transform, "Translation")

    # Join carcass
    join_carcass = create_join_geometry(ng, name="Join Carcass", location=(-500, 150))
    link(ng, left_transform, "Geometry", join_carcass, "Geometry")
    link(ng, right_transform, "Geometry", join_carcass, "Geometry")
    link(ng, top_transform, "Geometry", join_carcass, "Geometry")
    link(ng, bottom_transform, "Geometry", join_carcass, "Geometry")
    link(ng, back_transform, "Geometry", join_carcass, "Geometry")

    carcass_mat = create_set_material(ng, name="Carcass Material", location=(-350, 150))
    link(ng, join_carcass, "Geometry", carcass_mat, "Geometry")
    link(ng, group_in, "Carcass Material", carcass_mat, "Material")

    # ============ PULL-OUT RACK ============
    # Rack frame (side rails)
    rack_width = create_math(ng, 'SUBTRACT', name="Rack Width", location=(-1000, -400))
    link(ng, interior_width, 0, rack_width, 0)
    set_default(rack_width, 1, 0.01)  # Small gap for slides

    rack_depth = create_math(ng, 'SUBTRACT', name="Rack Depth", location=(-1000, -450))
    link(ng, group_in, "Depth", rack_depth, 0)
    set_default(rack_depth, 1, 0.03)  # Room for front panel

    rack_height = create_math(ng, 'SUBTRACT', name="Rack Height", location=(-1000, -500))
    link(ng, interior_height, 0, rack_height, 0)
    set_default(rack_height, 1, 0.02)

    # Shelf calculations
    shelf_spacing = create_math(ng, 'DIVIDE', name="Shelf Spacing", location=(-900, -550))
    link(ng, rack_height, 0, shelf_spacing, 0)
    link(ng, group_in, "Shelf Count", shelf_spacing, 1)

    # Rack side rails (thin vertical supports)
    rail_size = create_combine_xyz(ng, name="Rail Size", location=(-800, -400))
    set_default(rail_size, "X", 0.008)
    link(ng, rack_depth, 0, rail_size, "Y")
    link(ng, rack_height, 0, rail_size, "Z")

    rail = create_cube(ng, name="Rail", location=(-700, -400))
    link(ng, rail_size, "Vector", rail, "Size")

    # Rack shelves
    rack_shelf_size = create_combine_xyz(ng, name="Rack Shelf Size", location=(-800, -550))
    link(ng, rack_width, 0, rack_shelf_size, "X")
    link(ng, rack_depth, 0, rack_shelf_size, "Y")
    set_default(rack_shelf_size, "Z", 0.008)

    rack_shelf = create_cube(ng, name="Rack Shelf", location=(-700, -550))
    link(ng, rack_shelf_size, "Vector", rack_shelf, "Size")

    # Rack depth half for positioning
    rack_depth_half = create_math(ng, 'DIVIDE', name="Rack Depth Half", location=(-800, -600))
    link(ng, rack_depth, 0, rack_depth_half, 0)
    set_default(rack_depth_half, 1, -2.0)

    rack_height_half = create_math(ng, 'DIVIDE', name="Rack Height Half", location=(-800, -650))
    link(ng, rack_height, 0, rack_height_half, 0)
    set_default(rack_height_half, 1, 2.0)

    # Left rail position
    rack_width_half = create_math(ng, 'DIVIDE', name="Rack Width Half", location=(-800, -700))
    link(ng, rack_width, 0, rack_width_half, 0)
    set_default(rack_width_half, 1, -2.0)
    rail_x_offset = create_math(ng, 'ADD', name="Rail X Offset", location=(-700, -700))
    link(ng, rack_width_half, 0, rail_x_offset, 0)
    set_default(rail_x_offset, 1, 0.004)

    left_rail_pos = create_combine_xyz(ng, name="Left Rail Pos", location=(-600, -400))
    link(ng, rail_x_offset, 0, left_rail_pos, "X")
    link(ng, rack_depth_half, 0, left_rail_pos, "Y")
    link(ng, rack_height_half, 0, left_rail_pos, "Z")

    left_rail = create_transform(ng, name="Left Rail", location=(-500, -400))
    link(ng, rail, "Mesh", left_rail, "Geometry")
    link(ng, left_rail_pos, "Vector", left_rail, "Translation")

    # Right rail
    right_rail_x = create_math(ng, 'MULTIPLY', name="Right Rail X", location=(-700, -750))
    link(ng, rail_x_offset, 0, right_rail_x, 0)
    set_default(right_rail_x, 1, -1.0)

    right_rail_pos = create_combine_xyz(ng, name="Right Rail Pos", location=(-600, -500))
    link(ng, right_rail_x, 0, right_rail_pos, "X")
    link(ng, rack_depth_half, 0, right_rail_pos, "Y")
    link(ng, rack_height_half, 0, right_rail_pos, "Z")

    right_rail = create_transform(ng, name="Right Rail", location=(-500, -500))
    link(ng, rail, "Mesh", right_rail, "Geometry")
    link(ng, right_rail_pos, "Vector", right_rail, "Translation")

    # Create shelf instances at different heights
    # Shelf 0 (bottom)
    shelf_0_z = create_math(ng, 'ADD', name="Shelf 0 Z", location=(-600, -600))
    link(ng, panel_half, 0, shelf_0_z, 0)
    set_default(shelf_0_z, 1, 0.01)

    shelf_0_pos = create_combine_xyz(ng, name="Shelf 0 Pos", location=(-500, -600))
    set_default(shelf_0_pos, "X", 0.0)
    link(ng, rack_depth_half, 0, shelf_0_pos, "Y")
    link(ng, shelf_0_z, 0, shelf_0_pos, "Z")

    shelf_0 = create_transform(ng, name="Shelf 0", location=(-400, -600))
    link(ng, rack_shelf, "Mesh", shelf_0, "Geometry")
    link(ng, shelf_0_pos, "Vector", shelf_0, "Translation")

    # Shelf 1
    shelf_1_z = create_math(ng, 'ADD', name="Shelf 1 Z", location=(-600, -700))
    link(ng, shelf_0_z, 0, shelf_1_z, 0)
    link(ng, shelf_spacing, 0, shelf_1_z, 1)

    shelf_1_pos = create_combine_xyz(ng, name="Shelf 1 Pos", location=(-500, -700))
    set_default(shelf_1_pos, "X", 0.0)
    link(ng, rack_depth_half, 0, shelf_1_pos, "Y")
    link(ng, shelf_1_z, 0, shelf_1_pos, "Z")

    shelf_1 = create_transform(ng, name="Shelf 1", location=(-400, -700))
    link(ng, rack_shelf, "Mesh", shelf_1, "Geometry")
    link(ng, shelf_1_pos, "Vector", shelf_1, "Translation")

    # Shelf 2
    spacing_x2 = create_math(ng, 'MULTIPLY', name="Spacing x2", location=(-700, -800))
    link(ng, shelf_spacing, 0, spacing_x2, 0)
    set_default(spacing_x2, 1, 2.0)
    shelf_2_z = create_math(ng, 'ADD', name="Shelf 2 Z", location=(-600, -800))
    link(ng, shelf_0_z, 0, shelf_2_z, 0)
    link(ng, spacing_x2, 0, shelf_2_z, 1)

    shelf_2_pos = create_combine_xyz(ng, name="Shelf 2 Pos", location=(-500, -800))
    set_default(shelf_2_pos, "X", 0.0)
    link(ng, rack_depth_half, 0, shelf_2_pos, "Y")
    link(ng, shelf_2_z, 0, shelf_2_pos, "Z")

    shelf_2 = create_transform(ng, name="Shelf 2", location=(-400, -800))
    link(ng, rack_shelf, "Mesh", shelf_2, "Geometry")
    link(ng, shelf_2_pos, "Vector", shelf_2, "Translation")

    # Shelf 3
    spacing_x3 = create_math(ng, 'MULTIPLY', name="Spacing x3", location=(-700, -900))
    link(ng, shelf_spacing, 0, spacing_x3, 0)
    set_default(spacing_x3, 1, 3.0)
    shelf_3_z = create_math(ng, 'ADD', name="Shelf 3 Z", location=(-600, -900))
    link(ng, shelf_0_z, 0, shelf_3_z, 0)
    link(ng, spacing_x3, 0, shelf_3_z, 1)

    shelf_3_pos = create_combine_xyz(ng, name="Shelf 3 Pos", location=(-500, -900))
    set_default(shelf_3_pos, "X", 0.0)
    link(ng, rack_depth_half, 0, shelf_3_pos, "Y")
    link(ng, shelf_3_z, 0, shelf_3_pos, "Z")

    shelf_3 = create_transform(ng, name="Shelf 3", location=(-400, -900))
    link(ng, rack_shelf, "Mesh", shelf_3, "Geometry")
    link(ng, shelf_3_pos, "Vector", shelf_3, "Translation")

    # Shelf 4 and 5 (more shelves)
    spacing_x4 = create_math(ng, 'MULTIPLY', name="Spacing x4", location=(-700, -1000))
    link(ng, shelf_spacing, 0, spacing_x4, 0)
    set_default(spacing_x4, 1, 4.0)
    shelf_4_z = create_math(ng, 'ADD', name="Shelf 4 Z", location=(-600, -1000))
    link(ng, shelf_0_z, 0, shelf_4_z, 0)
    link(ng, spacing_x4, 0, shelf_4_z, 1)

    shelf_4_pos = create_combine_xyz(ng, name="Shelf 4 Pos", location=(-500, -1000))
    set_default(shelf_4_pos, "X", 0.0)
    link(ng, rack_depth_half, 0, shelf_4_pos, "Y")
    link(ng, shelf_4_z, 0, shelf_4_pos, "Z")

    shelf_4 = create_transform(ng, name="Shelf 4", location=(-400, -1000))
    link(ng, rack_shelf, "Mesh", shelf_4, "Geometry")
    link(ng, shelf_4_pos, "Vector", shelf_4, "Translation")

    spacing_x5 = create_math(ng, 'MULTIPLY', name="Spacing x5", location=(-700, -1100))
    link(ng, shelf_spacing, 0, spacing_x5, 0)
    set_default(spacing_x5, 1, 5.0)
    shelf_5_z = create_math(ng, 'ADD', name="Shelf 5 Z", location=(-600, -1100))
    link(ng, shelf_0_z, 0, shelf_5_z, 0)
    link(ng, spacing_x5, 0, shelf_5_z, 1)

    shelf_5_pos = create_combine_xyz(ng, name="Shelf 5 Pos", location=(-500, -1100))
    set_default(shelf_5_pos, "X", 0.0)
    link(ng, rack_depth_half, 0, shelf_5_pos, "Y")
    link(ng, shelf_5_z, 0, shelf_5_pos, "Z")

    shelf_5 = create_transform(ng, name="Shelf 5", location=(-400, -1100))
    link(ng, rack_shelf, "Mesh", shelf_5, "Geometry")
    link(ng, shelf_5_pos, "Vector", shelf_5, "Translation")

    # Join rack
    join_rack = create_join_geometry(ng, name="Join Rack", location=(-200, -600))
    link(ng, left_rail, "Geometry", join_rack, "Geometry")
    link(ng, right_rail, "Geometry", join_rack, "Geometry")
    link(ng, shelf_0, "Geometry", join_rack, "Geometry")
    link(ng, shelf_1, "Geometry", join_rack, "Geometry")
    link(ng, shelf_2, "Geometry", join_rack, "Geometry")
    link(ng, shelf_3, "Geometry", join_rack, "Geometry")
    link(ng, shelf_4, "Geometry", join_rack, "Geometry")
    link(ng, shelf_5, "Geometry", join_rack, "Geometry")

    rack_mat = create_set_material(ng, name="Rack Material", location=(-50, -600))
    link(ng, join_rack, "Geometry", rack_mat, "Geometry")
    link(ng, group_in, "Rack Material", rack_mat, "Material")

    # ============ FRONT PANEL ============
    front_height = create_math(ng, 'SUBTRACT', name="Front Height", location=(-1000, -1200))
    link(ng, group_in, "Height", front_height, 0)
    set_default(front_height, 1, 0.006)  # Gaps

    front_width = create_math(ng, 'SUBTRACT', name="Front Width", location=(-1000, -1250))
    link(ng, group_in, "Width", front_width, 0)
    set_default(front_width, 1, 0.006)

    front_size = create_combine_xyz(ng, name="Front Size", location=(-800, -1200))
    link(ng, front_width, 0, front_size, "X")
    link(ng, group_in, "Panel Thickness", front_size, "Y")
    link(ng, front_height, 0, front_size, "Z")

    front = create_cube(ng, name="Front", location=(-700, -1200))
    link(ng, front_size, "Vector", front, "Size")

    front_z = create_math(ng, 'DIVIDE', name="Front Z", location=(-700, -1250))
    link(ng, front_height, 0, front_z, 0)
    set_default(front_z, 1, 2.0)
    front_z_offset = create_math(ng, 'ADD', name="Front Z Offset", location=(-600, -1250))
    link(ng, front_z, 0, front_z_offset, 0)
    link(ng, group_in, "Panel Thickness", front_z_offset, 1)

    front_pos = create_combine_xyz(ng, name="Front Pos", location=(-600, -1200))
    set_default(front_pos, "X", 0.0)
    link(ng, panel_half, 0, front_pos, "Y")
    link(ng, front_z_offset, 0, front_pos, "Z")

    front_transform = create_transform(ng, name="Front Transform", location=(-500, -1200))
    link(ng, front, "Mesh", front_transform, "Geometry")
    link(ng, front_pos, "Vector", front_transform, "Translation")

    front_mat = create_set_material(ng, name="Front Material", location=(-350, -1200))
    link(ng, front_transform, "Geometry", front_mat, "Geometry")
    link(ng, group_in, "Front Material", front_mat, "Material")

    # ============ JOIN RACK AND FRONT (movable unit) ============
    join_pullout = create_join_geometry(ng, name="Join Pullout", location=(0, -900))
    link(ng, rack_mat, "Geometry", join_pullout, "Geometry")
    link(ng, front_mat, "Geometry", join_pullout, "Geometry")

    # Apply extension transform
    ext_offset = create_math(ng, 'MULTIPLY', name="Ext Offset", location=(100, -1000))
    link(ng, group_in, "Extension", ext_offset, 0)
    link(ng, group_in, "Depth", ext_offset, 1)

    ext_pos = create_combine_xyz(ng, name="Ext Pos", location=(200, -1000))
    set_default(ext_pos, "X", 0.0)
    link(ng, ext_offset, 0, ext_pos, "Y")
    set_default(ext_pos, "Z", 0.0)

    pullout_transform = create_transform(ng, name="Pullout Transform", location=(300, -900))
    link(ng, join_pullout, "Geometry", pullout_transform, "Geometry")
    link(ng, ext_pos, "Vector", pullout_transform, "Translation")

    # ============ TOE KICK ============
    tk_size = create_combine_xyz(ng, name="TK Size", location=(-1000, -1400))
    link(ng, group_in, "Width", tk_size, "X")
    link(ng, group_in, "Toe Kick Depth", tk_size, "Y")
    link(ng, group_in, "Toe Kick Height", tk_size, "Z")

    toe_kick = create_cube(ng, name="Toe Kick", location=(-900, -1400))
    link(ng, tk_size, "Vector", toe_kick, "Size")

    tk_y = create_math(ng, 'DIVIDE', name="TK Y", location=(-900, -1450))
    link(ng, group_in, "Toe Kick Depth", tk_y, 0)
    set_default(tk_y, 1, -2.0)

    tk_z = create_math(ng, 'DIVIDE', name="TK Z", location=(-900, -1500))
    link(ng, group_in, "Toe Kick Height", tk_z, 0)
    set_default(tk_z, 1, -2.0)

    tk_pos = create_combine_xyz(ng, name="TK Pos", location=(-800, -1400))
    set_default(tk_pos, "X", 0.0)
    link(ng, tk_y, 0, tk_pos, "Y")
    link(ng, tk_z, 0, tk_pos, "Z")

    tk_transform = create_transform(ng, name="TK Transform", location=(-700, -1400))
    link(ng, toe_kick, "Mesh", tk_transform, "Geometry")
    link(ng, tk_pos, "Vector", tk_transform, "Translation")

    tk_mat = create_set_material(ng, name="TK Material", location=(-550, -1400))
    link(ng, tk_transform, "Geometry", tk_mat, "Geometry")
    link(ng, group_in, "Carcass Material", tk_mat, "Material")

    switch_tk = create_switch(ng, 'GEOMETRY', name="TK Switch", location=(-400, -1400))
    link(ng, group_in, "Has Toe Kick", switch_tk, "Switch")
    link(ng, tk_mat, "Geometry", switch_tk, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(500, 0))
    link(ng, carcass_mat, "Geometry", join_all, "Geometry")
    link(ng, pullout_transform, "Geometry", join_all, "Geometry")
    link(ng, switch_tk, "Output", join_all, "Geometry")

    # ============ BEVEL ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(700, 0))
    if bevel is not None:
        link(ng, join_all, "Geometry", bevel, "Mesh")
        link(ng, group_in, "Bevel Width", bevel, "Width")
        link(ng, group_in, "Bevel Segments", bevel, "Segments")
        final_geo = bevel
        final_socket = "Mesh"
    else:
        final_geo = join_all
        final_socket = "Geometry"

    # ============ OUTPUT ============
    link(ng, final_geo, final_socket, group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/systems/pullout_pantry.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the PulloutPantry node group applied."""
    if nodegroup is None:
        nodegroup = create_pullout_pantry_nodegroup()

    mesh = bpy.data.meshes.new("PulloutPantry_Test")
    obj = bpy.data.objects.new("PulloutPantry_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_pullout_pantry_nodegroup()
    print(f"Created node group: {ng.name}")
