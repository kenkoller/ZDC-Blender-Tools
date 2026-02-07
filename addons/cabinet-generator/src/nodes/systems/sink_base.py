# Sink Base Cabinet node group generator
# System component: Base cabinet with open front for sink plumbing
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


def create_sink_base_nodegroup():
    """Generate the SinkBase node group.

    Sink base cabinet with:
    - Open interior (no shelf) for plumbing access
    - False front panels (non-functional drawer faces)
    - Optional floor panel (some sinks need full floor, others partial)
    - Cutout in back for plumbing (optional)

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back, negative Y is front)
    - Z = height (floor to ceiling)
    - Origin at front-bottom-center (floor level)

    Inputs:
        Width, Height, Depth: Cabinet dimensions
        Panel Thickness: Panel material thickness
        Has Floor: Include bottom panel
        False Front Count: Number of false drawer fronts
        Has Plumbing Cutout: Cutout in back panel
        Door Style: Style for doors (if any)
        Materials: Carcass, Front, Handle

    Outputs:
        Geometry: Complete sink base cabinet
    """
    ng = create_node_group("SinkBase")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    options_panel = create_panel(ng, "Options")
    front_panel = create_panel(ng, "Front")
    toekick_panel = create_panel(ng, "Toe Kick")
    bevel_panel = create_panel(ng, "Bevel")
    materials_panel = create_panel(ng, "Materials")

    # Dimensions
    add_float_socket(ng, "Width", default=0.9, min_val=0.6, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.72, min_val=0.6, max_val=0.9,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.6, min_val=0.5, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Options
    add_bool_socket(ng, "Has Floor", default=True, panel=options_panel)
    add_bool_socket(ng, "Has Back", default=True, panel=options_panel)
    add_bool_socket(ng, "Has Plumbing Cutout", default=True, panel=options_panel)
    add_float_socket(ng, "Cutout Width", default=0.3, min_val=0.1, max_val=0.5,
                     subtype='DISTANCE', panel=options_panel)
    add_float_socket(ng, "Cutout Height", default=0.2, min_val=0.1, max_val=0.3,
                     subtype='DISTANCE', panel=options_panel)

    # Front
    add_int_socket(ng, "False Front Count", default=2, min_val=0, max_val=3, panel=front_panel)
    add_float_socket(ng, "False Front Height", default=0.1, min_val=0.05, max_val=0.15,
                     subtype='DISTANCE', panel=front_panel)
    add_bool_socket(ng, "Double Doors", default=True, panel=front_panel)
    add_int_socket(ng, "Door Style", default=1, min_val=0, max_val=4, panel=front_panel)
    add_int_socket(ng, "Handle Style", default=0, min_val=0, max_val=4, panel=front_panel)

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
    add_material_socket(ng, "Handle Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1200, 0))
    group_out = create_group_output(ng, location=(1200, 0))

    # ============ CALCULATE DIMENSIONS ============
    # Interior width = width - 2 * panel_thickness
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-1000, -400))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)

    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-900, -400))
    link(ng, group_in, "Width", interior_width, 0)
    link(ng, panel_x2, 0, interior_width, 1)

    # Common positioning values
    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-1000, -500))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-1000, -550))
    link(ng, group_in, "Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-1000, -600))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)

    # ============ LEFT SIDE PANEL ============
    left_size = create_combine_xyz(ng, name="Left Size", location=(-800, 400))
    link(ng, group_in, "Panel Thickness", left_size, "X")
    link(ng, group_in, "Depth", left_size, "Y")
    link(ng, group_in, "Height", left_size, "Z")

    left_side = create_cube(ng, name="Left Side", location=(-700, 400))
    link(ng, left_size, "Vector", left_side, "Size")

    # Left X position
    left_x = create_math(ng, 'SUBTRACT', name="Left X Sub", location=(-800, 350))
    link(ng, group_in, "Width", left_x, 0)
    link(ng, group_in, "Panel Thickness", left_x, 1)
    left_x_div = create_math(ng, 'DIVIDE', name="Left X Div", location=(-700, 350))
    link(ng, left_x, 0, left_x_div, 0)
    set_default(left_x_div, 1, 2.0)
    left_x_neg = create_math(ng, 'MULTIPLY', name="Left X Neg", location=(-600, 350))
    link(ng, left_x_div, 0, left_x_neg, 0)
    set_default(left_x_neg, 1, -1.0)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-600, 400))
    link(ng, left_x_neg, 0, left_pos, "X")
    link(ng, depth_half, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Transform", location=(-500, 400))
    link(ng, left_side, "Mesh", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    # ============ RIGHT SIDE PANEL ============
    right_side = create_cube(ng, name="Right Side", location=(-700, 250))
    link(ng, left_size, "Vector", right_side, "Size")

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-600, 250))
    link(ng, left_x_div, 0, right_pos, "X")  # Positive X
    link(ng, depth_half, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Transform", location=(-500, 250))
    link(ng, right_side, "Mesh", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    # ============ TOP PANEL ============
    top_size = create_combine_xyz(ng, name="Top Size", location=(-800, 100))
    link(ng, interior_width, 0, top_size, "X")
    link(ng, group_in, "Depth", top_size, "Y")
    link(ng, group_in, "Panel Thickness", top_size, "Z")

    top = create_cube(ng, name="Top", location=(-700, 100))
    link(ng, top_size, "Vector", top, "Size")

    top_z = create_math(ng, 'SUBTRACT', name="Top Z", location=(-800, 50))
    link(ng, group_in, "Height", top_z, 0)
    link(ng, panel_half, 0, top_z, 1)

    top_pos = create_combine_xyz(ng, name="Top Pos", location=(-600, 100))
    set_default(top_pos, "X", 0.0)
    link(ng, depth_half, 0, top_pos, "Y")
    link(ng, top_z, 0, top_pos, "Z")

    top_transform = create_transform(ng, name="Top Transform", location=(-500, 100))
    link(ng, top, "Mesh", top_transform, "Geometry")
    link(ng, top_pos, "Vector", top_transform, "Translation")

    # ============ BOTTOM PANEL (OPTIONAL) ============
    bottom_size = create_combine_xyz(ng, name="Bottom Size", location=(-800, -50))
    link(ng, interior_width, 0, bottom_size, "X")
    link(ng, group_in, "Depth", bottom_size, "Y")
    link(ng, group_in, "Panel Thickness", bottom_size, "Z")

    bottom = create_cube(ng, name="Bottom", location=(-700, -50))
    link(ng, bottom_size, "Vector", bottom, "Size")

    bottom_pos = create_combine_xyz(ng, name="Bottom Pos", location=(-600, -50))
    set_default(bottom_pos, "X", 0.0)
    link(ng, depth_half, 0, bottom_pos, "Y")
    link(ng, panel_half, 0, bottom_pos, "Z")

    bottom_transform = create_transform(ng, name="Bottom Transform", location=(-500, -50))
    link(ng, bottom, "Mesh", bottom_transform, "Geometry")
    link(ng, bottom_pos, "Vector", bottom_transform, "Translation")

    # Switch for floor
    switch_floor = create_switch(ng, 'GEOMETRY', name="Floor Switch", location=(-350, -50))
    link(ng, group_in, "Has Floor", switch_floor, "Switch")
    link(ng, bottom_transform, "Geometry", switch_floor, "True")

    # ============ BACK PANEL ============
    interior_height = create_math(ng, 'SUBTRACT', name="Interior Height", location=(-900, -200))
    link(ng, group_in, "Height", interior_height, 0)
    link(ng, panel_x2, 0, interior_height, 1)

    back_size = create_combine_xyz(ng, name="Back Size", location=(-800, -200))
    link(ng, interior_width, 0, back_size, "X")
    set_default(back_size, "Y", 0.006)  # Thin back
    link(ng, interior_height, 0, back_size, "Z")

    back = create_cube(ng, name="Back", location=(-700, -200))
    link(ng, back_size, "Vector", back, "Size")

    back_y = create_math(ng, 'MULTIPLY', name="Back Y Neg", location=(-800, -250))
    link(ng, group_in, "Depth", back_y, 0)
    set_default(back_y, 1, -1.0)
    back_y_offset = create_math(ng, 'ADD', name="Back Y Offset", location=(-700, -250))
    link(ng, back_y, 0, back_y_offset, 0)
    set_default(back_y_offset, 1, 0.003)  # Half back thickness

    back_pos = create_combine_xyz(ng, name="Back Pos", location=(-600, -200))
    set_default(back_pos, "X", 0.0)
    link(ng, back_y_offset, 0, back_pos, "Y")
    link(ng, height_half, 0, back_pos, "Z")

    back_transform = create_transform(ng, name="Back Transform", location=(-500, -200))
    link(ng, back, "Mesh", back_transform, "Geometry")
    link(ng, back_pos, "Vector", back_transform, "Translation")

    # Switch for back
    switch_back = create_switch(ng, 'GEOMETRY', name="Back Switch", location=(-350, -200))
    link(ng, group_in, "Has Back", switch_back, "Switch")
    link(ng, back_transform, "Geometry", switch_back, "True")

    # ============ JOIN CARCASS ============
    join_carcass = create_join_geometry(ng, name="Join Carcass", location=(-200, 200))
    link(ng, left_transform, "Geometry", join_carcass, "Geometry")
    link(ng, right_transform, "Geometry", join_carcass, "Geometry")
    link(ng, top_transform, "Geometry", join_carcass, "Geometry")
    link(ng, switch_floor, "Output", join_carcass, "Geometry")
    link(ng, switch_back, "Output", join_carcass, "Geometry")

    # Set carcass material
    carcass_mat = create_set_material(ng, name="Carcass Material", location=(-50, 200))
    link(ng, join_carcass, "Geometry", carcass_mat, "Geometry")
    link(ng, group_in, "Carcass Material", carcass_mat, "Material")

    # ============ FALSE FRONT PANELS ============
    # Simple false drawer fronts at top (non-functional)
    false_front_width = create_math(ng, 'SUBTRACT', name="FF Width", location=(-800, -400))
    link(ng, group_in, "Width", false_front_width, 0)
    set_default(false_front_width, 1, 0.006)  # Gap for reveal

    ff_size = create_combine_xyz(ng, name="FF Size", location=(-700, -400))
    link(ng, false_front_width, 0, ff_size, "X")
    link(ng, group_in, "Panel Thickness", ff_size, "Y")
    link(ng, group_in, "False Front Height", ff_size, "Z")

    false_front = create_cube(ng, name="False Front", location=(-600, -400))
    link(ng, ff_size, "Vector", false_front, "Size")

    ff_z = create_math(ng, 'SUBTRACT', name="FF Z", location=(-700, -450))
    link(ng, group_in, "Height", ff_z, 0)
    ff_height_half = create_math(ng, 'DIVIDE', name="FF Height Half", location=(-600, -450))
    link(ng, group_in, "False Front Height", ff_height_half, 0)
    set_default(ff_height_half, 1, 2.0)
    ff_z_final = create_math(ng, 'SUBTRACT', name="FF Z Final", location=(-500, -450))
    link(ng, ff_z, 0, ff_z_final, 0)
    link(ng, ff_height_half, 0, ff_z_final, 1)

    ff_pos = create_combine_xyz(ng, name="FF Pos", location=(-500, -400))
    set_default(ff_pos, "X", 0.0)
    set_default(ff_pos, "Y", 0.009)  # Panel thickness / 2
    link(ng, ff_z_final, 0, ff_pos, "Z")

    ff_transform = create_transform(ng, name="FF Transform", location=(-400, -400))
    link(ng, false_front, "Mesh", ff_transform, "Geometry")
    link(ng, ff_pos, "Vector", ff_transform, "Translation")

    ff_mat = create_set_material(ng, name="FF Material", location=(-250, -400))
    link(ng, ff_transform, "Geometry", ff_mat, "Geometry")
    link(ng, group_in, "Front Material", ff_mat, "Material")

    # ============ DOORS ============
    # Using DoorAssembly would be ideal, but for self-contained, create simple doors
    # Door height = cabinet height - false front height - gap
    door_height = create_math(ng, 'SUBTRACT', name="Door Height", location=(-800, -600))
    link(ng, group_in, "Height", door_height, 0)
    link(ng, group_in, "False Front Height", door_height, 1)
    door_height_gap = create_math(ng, 'SUBTRACT', name="Door Height Gap", location=(-700, -600))
    link(ng, door_height, 0, door_height_gap, 0)
    set_default(door_height_gap, 1, 0.006)  # Gaps

    # Single door width (for double doors)
    door_width_half = create_math(ng, 'DIVIDE', name="Door Width Half", location=(-800, -650))
    link(ng, false_front_width, 0, door_width_half, 0)
    set_default(door_width_half, 1, 2.0)
    door_width_gap = create_math(ng, 'SUBTRACT', name="Door Width Gap", location=(-700, -650))
    link(ng, door_width_half, 0, door_width_gap, 0)
    set_default(door_width_gap, 1, 0.003)

    door_size = create_combine_xyz(ng, name="Door Size", location=(-600, -600))
    link(ng, door_width_gap, 0, door_size, "X")
    link(ng, group_in, "Panel Thickness", door_size, "Y")
    link(ng, door_height_gap, 0, door_size, "Z")

    door_l = create_cube(ng, name="Door Left", location=(-500, -600))
    link(ng, door_size, "Vector", door_l, "Size")

    # Left door position
    door_x_offset = create_math(ng, 'DIVIDE', name="Door X Offset", location=(-600, -700))
    link(ng, door_width_gap, 0, door_x_offset, 0)
    set_default(door_x_offset, 1, -2.0)
    door_x_left = create_math(ng, 'SUBTRACT', name="Door X Left", location=(-500, -700))
    link(ng, door_x_offset, 0, door_x_left, 0)
    set_default(door_x_left, 1, 0.0015)

    door_z = create_math(ng, 'DIVIDE', name="Door Z", location=(-600, -750))
    link(ng, door_height_gap, 0, door_z, 0)
    set_default(door_z, 1, 2.0)
    door_z_offset = create_math(ng, 'ADD', name="Door Z Offset", location=(-500, -750))
    link(ng, door_z, 0, door_z_offset, 0)
    link(ng, group_in, "Panel Thickness", door_z_offset, 1)

    door_l_pos = create_combine_xyz(ng, name="Door L Pos", location=(-400, -600))
    link(ng, door_x_left, 0, door_l_pos, "X")
    set_default(door_l_pos, "Y", 0.009)
    link(ng, door_z_offset, 0, door_l_pos, "Z")

    door_l_transform = create_transform(ng, name="Door L Transform", location=(-300, -600))
    link(ng, door_l, "Mesh", door_l_transform, "Geometry")
    link(ng, door_l_pos, "Vector", door_l_transform, "Translation")

    # Right door
    door_r = create_cube(ng, name="Door Right", location=(-500, -800))
    link(ng, door_size, "Vector", door_r, "Size")

    door_x_right = create_math(ng, 'ADD', name="Door X Right", location=(-500, -850))
    link(ng, door_x_offset, 0, door_x_right, 0)
    door_x_right_neg = create_math(ng, 'MULTIPLY', name="Door X Right Neg", location=(-400, -850))
    link(ng, door_x_right, 0, door_x_right_neg, 0)
    set_default(door_x_right_neg, 1, -1.0)
    door_x_right_offset = create_math(ng, 'ADD', name="Door X Right Offset", location=(-300, -850))
    link(ng, door_x_right_neg, 0, door_x_right_offset, 0)
    set_default(door_x_right_offset, 1, 0.0015)

    door_r_pos = create_combine_xyz(ng, name="Door R Pos", location=(-400, -800))
    link(ng, door_x_right_offset, 0, door_r_pos, "X")
    set_default(door_r_pos, "Y", 0.009)
    link(ng, door_z_offset, 0, door_r_pos, "Z")

    door_r_transform = create_transform(ng, name="Door R Transform", location=(-300, -800))
    link(ng, door_r, "Mesh", door_r_transform, "Geometry")
    link(ng, door_r_pos, "Vector", door_r_transform, "Translation")

    # Join doors
    join_doors = create_join_geometry(ng, name="Join Doors", location=(-100, -700))
    link(ng, door_l_transform, "Geometry", join_doors, "Geometry")
    link(ng, door_r_transform, "Geometry", join_doors, "Geometry")

    door_mat = create_set_material(ng, name="Door Material", location=(50, -700))
    link(ng, join_doors, "Geometry", door_mat, "Geometry")
    link(ng, group_in, "Front Material", door_mat, "Material")

    # ============ TOE KICK ============
    tk_size = create_combine_xyz(ng, name="TK Size", location=(-800, -1000))
    link(ng, group_in, "Width", tk_size, "X")
    link(ng, group_in, "Toe Kick Depth", tk_size, "Y")
    link(ng, group_in, "Toe Kick Height", tk_size, "Z")

    toe_kick = create_cube(ng, name="Toe Kick", location=(-700, -1000))
    link(ng, tk_size, "Vector", toe_kick, "Size")

    tk_y = create_math(ng, 'DIVIDE', name="TK Y", location=(-700, -1050))
    link(ng, group_in, "Toe Kick Depth", tk_y, 0)
    set_default(tk_y, 1, -2.0)

    tk_z = create_math(ng, 'DIVIDE', name="TK Z", location=(-700, -1100))
    link(ng, group_in, "Toe Kick Height", tk_z, 0)
    set_default(tk_z, 1, -2.0)

    tk_pos = create_combine_xyz(ng, name="TK Pos", location=(-600, -1000))
    set_default(tk_pos, "X", 0.0)
    link(ng, tk_y, 0, tk_pos, "Y")
    link(ng, tk_z, 0, tk_pos, "Z")

    tk_transform = create_transform(ng, name="TK Transform", location=(-500, -1000))
    link(ng, toe_kick, "Mesh", tk_transform, "Geometry")
    link(ng, tk_pos, "Vector", tk_transform, "Translation")

    tk_mat = create_set_material(ng, name="TK Material", location=(-350, -1000))
    link(ng, tk_transform, "Geometry", tk_mat, "Geometry")
    link(ng, group_in, "Carcass Material", tk_mat, "Material")

    switch_tk = create_switch(ng, 'GEOMETRY', name="TK Switch", location=(-200, -1000))
    link(ng, group_in, "Has Toe Kick", switch_tk, "Switch")
    link(ng, tk_mat, "Geometry", switch_tk, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(200, 0))
    link(ng, carcass_mat, "Geometry", join_all, "Geometry")
    link(ng, ff_mat, "Geometry", join_all, "Geometry")
    link(ng, door_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_tk, "Output", join_all, "Geometry")

    # ============ BEVEL ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(400, 0))
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

    add_metadata(ng, version="1.0.0", script_path="src/nodes/systems/sink_base.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the SinkBase node group applied."""
    if nodegroup is None:
        nodegroup = create_sink_base_nodegroup()

    mesh = bpy.data.meshes.new("SinkBase_Test")
    obj = bpy.data.objects.new("SinkBase_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_sink_base_nodegroup()
    print(f"Created node group: {ng.name}")
