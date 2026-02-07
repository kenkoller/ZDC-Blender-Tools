# Appliance Cabinet node group generator
# System component: Cabinet for microwave/oven housing
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
    create_compare,
    create_bevel,
    link,
    set_default,
    add_metadata,
)


def create_appliance_cabinet_nodegroup():
    """Generate the ApplianceCabinet node group.

    Appliance cabinet with:
    - Open front cavity for appliance (microwave, oven)
    - Optional trim frame around opening
    - Ventilation space at back
    - Support for different appliance types

    Appliance Types:
    - 0: Microwave (standard opening)
    - 1: Wall Oven (tall opening)
    - 2: Built-in Refrigerator (full height)

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back, negative Y is front)
    - Z = height (floor to ceiling)
    - Origin at front-bottom-center (floor level)
    """
    ng = create_node_group("ApplianceCabinet")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    appliance_panel = create_panel(ng, "Appliance")
    options_panel = create_panel(ng, "Options")
    bevel_panel = create_panel(ng, "Bevel")
    materials_panel = create_panel(ng, "Materials")

    # Dimensions
    add_float_socket(ng, "Width", default=0.6, min_val=0.45, max_val=0.9,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.72, min_val=0.4, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.6, min_val=0.5, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Appliance opening
    add_int_socket(ng, "Appliance Type", default=0, min_val=0, max_val=2, panel=appliance_panel)
    add_float_socket(ng, "Opening Width", default=0.55, min_val=0.3, max_val=0.85,
                     subtype='DISTANCE', panel=appliance_panel)
    add_float_socket(ng, "Opening Height", default=0.4, min_val=0.25, max_val=0.8,
                     subtype='DISTANCE', panel=appliance_panel)
    add_float_socket(ng, "Opening Bottom", default=0.15, min_val=0.0, max_val=0.5,
                     subtype='DISTANCE', panel=appliance_panel)

    # Options
    add_bool_socket(ng, "Has Trim", default=True, panel=options_panel)
    add_float_socket(ng, "Trim Width", default=0.025, min_val=0.015, max_val=0.05,
                     subtype='DISTANCE', panel=options_panel)
    add_bool_socket(ng, "Has Back", default=True, panel=options_panel)
    add_bool_socket(ng, "Ventilation Gap", default=True, panel=options_panel)

    # Bevel
    add_float_socket(ng, "Bevel Width", default=0.001, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=bevel_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=bevel_panel)

    # Materials
    add_material_socket(ng, "Carcass Material", panel=materials_panel)
    add_material_socket(ng, "Trim Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1200, 0))
    group_out = create_group_output(ng, location=(1200, 0))

    # ============ CALCULATE DIMENSIONS ============
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-1000, -400))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)

    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-900, -400))
    link(ng, group_in, "Width", interior_width, 0)
    link(ng, panel_x2, 0, interior_width, 1)

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
    link(ng, left_x_div, 0, right_pos, "X")
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

    # ============ BOTTOM PANEL ============
    bottom = create_cube(ng, name="Bottom", location=(-700, -50))
    link(ng, top_size, "Vector", bottom, "Size")

    bottom_pos = create_combine_xyz(ng, name="Bottom Pos", location=(-600, -50))
    set_default(bottom_pos, "X", 0.0)
    link(ng, depth_half, 0, bottom_pos, "Y")
    link(ng, panel_half, 0, bottom_pos, "Z")

    bottom_transform = create_transform(ng, name="Bottom Transform", location=(-500, -50))
    link(ng, bottom, "Mesh", bottom_transform, "Geometry")
    link(ng, bottom_pos, "Vector", bottom_transform, "Translation")

    # ============ BACK PANEL ============
    interior_height = create_math(ng, 'SUBTRACT', name="Interior Height", location=(-900, -200))
    link(ng, group_in, "Height", interior_height, 0)
    link(ng, panel_x2, 0, interior_height, 1)

    back_size = create_combine_xyz(ng, name="Back Size", location=(-800, -200))
    link(ng, interior_width, 0, back_size, "X")
    set_default(back_size, "Y", 0.006)
    link(ng, interior_height, 0, back_size, "Z")

    back = create_cube(ng, name="Back", location=(-700, -200))
    link(ng, back_size, "Vector", back, "Size")

    back_y = create_math(ng, 'MULTIPLY', name="Back Y Neg", location=(-800, -250))
    link(ng, group_in, "Depth", back_y, 0)
    set_default(back_y, 1, -1.0)
    back_y_offset = create_math(ng, 'ADD', name="Back Y Offset", location=(-700, -250))
    link(ng, back_y, 0, back_y_offset, 0)
    set_default(back_y_offset, 1, 0.003)

    back_pos = create_combine_xyz(ng, name="Back Pos", location=(-600, -200))
    set_default(back_pos, "X", 0.0)
    link(ng, back_y_offset, 0, back_pos, "Y")
    link(ng, height_half, 0, back_pos, "Z")

    back_transform = create_transform(ng, name="Back Transform", location=(-500, -200))
    link(ng, back, "Mesh", back_transform, "Geometry")
    link(ng, back_pos, "Vector", back_transform, "Translation")

    switch_back = create_switch(ng, 'GEOMETRY', name="Back Switch", location=(-350, -200))
    link(ng, group_in, "Has Back", switch_back, "Switch")
    link(ng, back_transform, "Geometry", switch_back, "True")

    # ============ JOIN CARCASS ============
    join_carcass = create_join_geometry(ng, name="Join Carcass", location=(-200, 200))
    link(ng, left_transform, "Geometry", join_carcass, "Geometry")
    link(ng, right_transform, "Geometry", join_carcass, "Geometry")
    link(ng, top_transform, "Geometry", join_carcass, "Geometry")
    link(ng, bottom_transform, "Geometry", join_carcass, "Geometry")
    link(ng, switch_back, "Output", join_carcass, "Geometry")

    carcass_mat = create_set_material(ng, name="Carcass Material", location=(-50, 200))
    link(ng, join_carcass, "Geometry", carcass_mat, "Geometry")
    link(ng, group_in, "Carcass Material", carcass_mat, "Material")

    # ============ TRIM FRAME ============
    # Top trim piece
    trim_h_size = create_combine_xyz(ng, name="Trim H Size", location=(-800, -400))
    link(ng, group_in, "Opening Width", trim_h_size, "X")
    link(ng, group_in, "Trim Width", trim_h_size, "Y")
    link(ng, group_in, "Trim Width", trim_h_size, "Z")

    trim_top = create_cube(ng, name="Trim Top", location=(-700, -400))
    link(ng, trim_h_size, "Vector", trim_top, "Size")

    # Trim top Z = Opening Bottom + Opening Height + Trim Width/2
    trim_top_z = create_math(ng, 'ADD', name="Trim Top Z 1", location=(-700, -450))
    link(ng, group_in, "Opening Bottom", trim_top_z, 0)
    link(ng, group_in, "Opening Height", trim_top_z, 1)
    trim_w_half = create_math(ng, 'DIVIDE', name="Trim W Half", location=(-600, -450))
    link(ng, group_in, "Trim Width", trim_w_half, 0)
    set_default(trim_w_half, 1, 2.0)
    trim_top_z_final = create_math(ng, 'ADD', name="Trim Top Z Final", location=(-500, -450))
    link(ng, trim_top_z, 0, trim_top_z_final, 0)
    link(ng, trim_w_half, 0, trim_top_z_final, 1)

    trim_top_pos = create_combine_xyz(ng, name="Trim Top Pos", location=(-500, -400))
    set_default(trim_top_pos, "X", 0.0)
    link(ng, trim_w_half, 0, trim_top_pos, "Y")
    link(ng, trim_top_z_final, 0, trim_top_pos, "Z")

    trim_top_transform = create_transform(ng, name="Trim Top Transform", location=(-400, -400))
    link(ng, trim_top, "Mesh", trim_top_transform, "Geometry")
    link(ng, trim_top_pos, "Vector", trim_top_transform, "Translation")

    # Bottom trim piece
    trim_bottom = create_cube(ng, name="Trim Bottom", location=(-700, -550))
    link(ng, trim_h_size, "Vector", trim_bottom, "Size")

    trim_bottom_z = create_math(ng, 'ADD', name="Trim Bottom Z", location=(-600, -550))
    link(ng, group_in, "Opening Bottom", trim_bottom_z, 0)
    trim_bottom_z_neg = create_math(ng, 'SUBTRACT', name="Trim Bottom Z Neg", location=(-500, -550))
    link(ng, trim_bottom_z, 0, trim_bottom_z_neg, 0)
    link(ng, trim_w_half, 0, trim_bottom_z_neg, 1)

    trim_bottom_pos = create_combine_xyz(ng, name="Trim Bottom Pos", location=(-500, -550))
    set_default(trim_bottom_pos, "X", 0.0)
    link(ng, trim_w_half, 0, trim_bottom_pos, "Y")
    link(ng, trim_bottom_z_neg, 0, trim_bottom_pos, "Z")

    trim_bottom_transform = create_transform(ng, name="Trim Bottom Transform", location=(-400, -550))
    link(ng, trim_bottom, "Mesh", trim_bottom_transform, "Geometry")
    link(ng, trim_bottom_pos, "Vector", trim_bottom_transform, "Translation")

    # Side trim pieces
    trim_v_height = create_math(ng, 'ADD', name="Trim V Height", location=(-800, -700))
    link(ng, group_in, "Opening Height", trim_v_height, 0)
    link(ng, group_in, "Trim Width", trim_v_height, 1)

    trim_v_size = create_combine_xyz(ng, name="Trim V Size", location=(-700, -700))
    link(ng, group_in, "Trim Width", trim_v_size, "X")
    link(ng, group_in, "Trim Width", trim_v_size, "Y")
    link(ng, trim_v_height, 0, trim_v_size, "Z")

    trim_left = create_cube(ng, name="Trim Left", location=(-600, -700))
    link(ng, trim_v_size, "Vector", trim_left, "Size")

    trim_x_offset = create_math(ng, 'DIVIDE', name="Trim X Offset", location=(-700, -750))
    link(ng, group_in, "Opening Width", trim_x_offset, 0)
    set_default(trim_x_offset, 1, -2.0)
    trim_x_left = create_math(ng, 'SUBTRACT', name="Trim X Left", location=(-600, -750))
    link(ng, trim_x_offset, 0, trim_x_left, 0)
    link(ng, trim_w_half, 0, trim_x_left, 1)

    trim_v_z = create_math(ng, 'ADD', name="Trim V Z", location=(-600, -800))
    link(ng, group_in, "Opening Bottom", trim_v_z, 0)
    trim_v_z_offset = create_math(ng, 'DIVIDE', name="Trim V Z Offset", location=(-500, -800))
    link(ng, group_in, "Opening Height", trim_v_z_offset, 0)
    set_default(trim_v_z_offset, 1, 2.0)
    trim_v_z_final = create_math(ng, 'ADD', name="Trim V Z Final", location=(-400, -800))
    link(ng, trim_v_z, 0, trim_v_z_final, 0)
    link(ng, trim_v_z_offset, 0, trim_v_z_final, 1)

    trim_left_pos = create_combine_xyz(ng, name="Trim Left Pos", location=(-400, -700))
    link(ng, trim_x_left, 0, trim_left_pos, "X")
    link(ng, trim_w_half, 0, trim_left_pos, "Y")
    link(ng, trim_v_z_final, 0, trim_left_pos, "Z")

    trim_left_transform = create_transform(ng, name="Trim Left Transform", location=(-300, -700))
    link(ng, trim_left, "Mesh", trim_left_transform, "Geometry")
    link(ng, trim_left_pos, "Vector", trim_left_transform, "Translation")

    # Right trim
    trim_right = create_cube(ng, name="Trim Right", location=(-600, -900))
    link(ng, trim_v_size, "Vector", trim_right, "Size")

    trim_x_right = create_math(ng, 'MULTIPLY', name="Trim X Right", location=(-500, -900))
    link(ng, trim_x_left, 0, trim_x_right, 0)
    set_default(trim_x_right, 1, -1.0)

    trim_right_pos = create_combine_xyz(ng, name="Trim Right Pos", location=(-400, -900))
    link(ng, trim_x_right, 0, trim_right_pos, "X")
    link(ng, trim_w_half, 0, trim_right_pos, "Y")
    link(ng, trim_v_z_final, 0, trim_right_pos, "Z")

    trim_right_transform = create_transform(ng, name="Trim Right Transform", location=(-300, -900))
    link(ng, trim_right, "Mesh", trim_right_transform, "Geometry")
    link(ng, trim_right_pos, "Vector", trim_right_transform, "Translation")

    # Join trim
    join_trim = create_join_geometry(ng, name="Join Trim", location=(-100, -600))
    link(ng, trim_top_transform, "Geometry", join_trim, "Geometry")
    link(ng, trim_bottom_transform, "Geometry", join_trim, "Geometry")
    link(ng, trim_left_transform, "Geometry", join_trim, "Geometry")
    link(ng, trim_right_transform, "Geometry", join_trim, "Geometry")

    trim_mat = create_set_material(ng, name="Trim Material", location=(50, -600))
    link(ng, join_trim, "Geometry", trim_mat, "Geometry")
    link(ng, group_in, "Trim Material", trim_mat, "Material")

    switch_trim = create_switch(ng, 'GEOMETRY', name="Trim Switch", location=(200, -600))
    link(ng, group_in, "Has Trim", switch_trim, "Switch")
    link(ng, trim_mat, "Geometry", switch_trim, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(400, 0))
    link(ng, carcass_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_trim, "Output", join_all, "Geometry")

    # ============ BEVEL ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(600, 0))
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

    add_metadata(ng, version="1.0.0", script_path="src/nodes/systems/appliance_cabinet.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the ApplianceCabinet node group applied."""
    if nodegroup is None:
        nodegroup = create_appliance_cabinet_nodegroup()

    mesh = bpy.data.meshes.new("ApplianceCabinet_Test")
    obj = bpy.data.objects.new("ApplianceCabinet_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_appliance_cabinet_nodegroup()
    print(f"Created node group: {ng.name}")
