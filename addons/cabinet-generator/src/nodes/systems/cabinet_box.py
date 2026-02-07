# Cabinet Box (Carcass) node group generator
# System component: Cabinet shell with sides, top, bottom, back
# Coordinate system: X=width, Y=depth, Z=height (Z-up, origin at floor)

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


def create_cabinet_box_nodegroup():
    """Generate the CabinetBox node group.

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back, negative Y is front)
    - Z = height (floor to ceiling)
    - Origin at front-bottom-center (floor level)

    A cabinet carcass/box consisting of:
    - Left side panel
    - Right side panel
    - Top panel
    - Bottom panel
    - Back panel (optional)
    """
    ng = create_node_group("CabinetBox")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    thickness_panel = create_panel(ng, "Thickness")
    options_panel = create_panel(ng, "Options")
    materials_panel = create_panel(ng, "Materials")

    # Dimension inputs
    add_float_socket(ng, "Width", default=0.6, min_val=0.2, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.72, min_val=0.3, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.55, min_val=0.3, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)

    # Thickness inputs
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=thickness_panel)
    add_float_socket(ng, "Back Thickness", default=0.006, min_val=0.003, max_val=0.012,
                     subtype='DISTANCE', panel=thickness_panel)

    # Options
    add_bool_socket(ng, "Has Back", default=True, panel=options_panel)
    add_bool_socket(ng, "Has Face Frame", default=False, panel=options_panel)
    add_float_socket(ng, "Face Frame Width", default=0.038, min_val=0.025, max_val=0.075,
                     subtype='DISTANCE', panel=options_panel)
    add_float_socket(ng, "Bevel Width", default=0.001, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=options_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=options_panel)

    # Materials
    add_material_socket(ng, "Carcass Material", panel=materials_panel)
    add_material_socket(ng, "Back Material", panel=materials_panel)

    # Outputs
    add_geometry_output(ng)
    ng.interface.new_socket(name="Interior Width", in_out='OUTPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket(name="Interior Height", in_out='OUTPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket(name="Interior Depth", in_out='OUTPUT', socket_type='NodeSocketFloat')

    # Create nodes
    group_in = create_group_input(ng, location=(-1000, 0))
    group_out = create_group_output(ng, location=(1000, 0))

    # ============ CALCULATE INTERIOR DIMENSIONS ============
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-900, -400))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)

    # Interior width = width - 2 * panel_thickness
    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-800, -400))
    link(ng, group_in, "Width", interior_width, 0)
    link(ng, panel_x2, 0, interior_width, 1)

    # Interior height = height - 2 * panel_thickness
    interior_height = create_math(ng, 'SUBTRACT', name="Interior Height", location=(-800, -500))
    link(ng, group_in, "Height", interior_height, 0)
    link(ng, panel_x2, 0, interior_height, 1)

    # Interior depth = depth - back_thickness
    interior_depth = create_math(ng, 'SUBTRACT', name="Interior Depth", location=(-800, -600))
    link(ng, group_in, "Depth", interior_depth, 0)
    link(ng, group_in, "Back Thickness", interior_depth, 1)

    # ============ LEFT SIDE PANEL ============
    # Size: panel_thickness (X) x depth (Y) x height (Z)
    left_side = create_cube(ng, name="Left Side", location=(-500, 400))
    left_size = create_combine_xyz(ng, name="Left Size", location=(-650, 450))
    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-650, 350))
    left_transform = create_transform(ng, name="Left Transform", location=(-350, 400))

    link(ng, group_in, "Panel Thickness", left_size, "X")
    link(ng, group_in, "Depth", left_size, "Y")
    link(ng, group_in, "Height", left_size, "Z")
    link(ng, left_size, "Vector", left_side, "Size")

    # Left X = -(width - panel_thickness) / 2
    left_x = create_math(ng, 'SUBTRACT', name="Left X Sub", location=(-750, 300))
    left_x_div = create_math(ng, 'DIVIDE', name="Left X Div", location=(-650, 300))
    left_x_neg = create_math(ng, 'MULTIPLY', name="Left X Neg", location=(-550, 300))
    link(ng, group_in, "Width", left_x, 0)
    link(ng, group_in, "Panel Thickness", left_x, 1)
    link(ng, left_x, 0, left_x_div, 0)
    set_default(left_x_div, 1, 2.0)
    link(ng, left_x_div, 0, left_x_neg, 0)
    set_default(left_x_neg, 1, -1.0)

    # Y position = -depth/2 (centered on depth, front at Y=0)
    depth_half_neg = create_math(ng, 'DIVIDE', name="Depth Half", location=(-750, 250))
    link(ng, group_in, "Depth", depth_half_neg, 0)
    set_default(depth_half_neg, 1, -2.0)

    # Z position = height/2 (bottom at Z=0)
    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-750, 200))
    link(ng, group_in, "Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    link(ng, left_x_neg, 0, left_pos, "X")
    link(ng, depth_half_neg, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")
    link(ng, left_pos, "Vector", left_transform, "Translation")
    link(ng, left_side, "Mesh", left_transform, "Geometry")

    # ============ RIGHT SIDE PANEL ============
    right_side = create_cube(ng, name="Right Side", location=(-500, 200))
    right_size = create_combine_xyz(ng, name="Right Size", location=(-650, 250))
    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-650, 150))
    right_transform = create_transform(ng, name="Right Transform", location=(-350, 200))

    link(ng, group_in, "Panel Thickness", right_size, "X")
    link(ng, group_in, "Depth", right_size, "Y")
    link(ng, group_in, "Height", right_size, "Z")
    link(ng, right_size, "Vector", right_side, "Size")

    link(ng, left_x_div, 0, right_pos, "X")  # Positive X
    link(ng, depth_half_neg, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")
    link(ng, right_pos, "Vector", right_transform, "Translation")
    link(ng, right_side, "Mesh", right_transform, "Geometry")

    # ============ TOP PANEL ============
    # Size: interior_width (X) x depth (Y) x panel_thickness (Z)
    top = create_cube(ng, name="Top", location=(-500, 0))
    top_size = create_combine_xyz(ng, name="Top Size", location=(-650, 50))
    top_pos = create_combine_xyz(ng, name="Top Pos", location=(-650, -50))
    top_transform = create_transform(ng, name="Top Transform", location=(-350, 0))

    link(ng, interior_width, 0, top_size, "X")
    link(ng, group_in, "Depth", top_size, "Y")
    link(ng, group_in, "Panel Thickness", top_size, "Z")
    link(ng, top_size, "Vector", top, "Size")

    # Top Z = height - panel_thickness/2
    top_z = create_math(ng, 'SUBTRACT', name="Top Z Sub", location=(-750, -100))
    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-850, -100))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)
    link(ng, group_in, "Height", top_z, 0)
    link(ng, panel_half, 0, top_z, 1)

    link(ng, depth_half_neg, 0, top_pos, "Y")
    link(ng, top_z, 0, top_pos, "Z")
    link(ng, top_pos, "Vector", top_transform, "Translation")
    link(ng, top, "Mesh", top_transform, "Geometry")

    # ============ BOTTOM PANEL ============
    bottom = create_cube(ng, name="Bottom", location=(-500, -200))
    bottom_size = create_combine_xyz(ng, name="Bottom Size", location=(-650, -150))
    bottom_pos = create_combine_xyz(ng, name="Bottom Pos", location=(-650, -250))
    bottom_transform = create_transform(ng, name="Bottom Transform", location=(-350, -200))

    link(ng, interior_width, 0, bottom_size, "X")
    link(ng, group_in, "Depth", bottom_size, "Y")
    link(ng, group_in, "Panel Thickness", bottom_size, "Z")
    link(ng, bottom_size, "Vector", bottom, "Size")

    # Bottom Z = panel_thickness/2
    link(ng, depth_half_neg, 0, bottom_pos, "Y")
    link(ng, panel_half, 0, bottom_pos, "Z")
    link(ng, bottom_pos, "Vector", bottom_transform, "Translation")
    link(ng, bottom, "Mesh", bottom_transform, "Geometry")

    # ============ BACK PANEL ============
    # Size: interior_width (X) x back_thickness (Y) x interior_height (Z)
    back = create_cube(ng, name="Back", location=(-500, -400))
    back_size = create_combine_xyz(ng, name="Back Size", location=(-650, -350))
    back_pos = create_combine_xyz(ng, name="Back Pos", location=(-650, -450))
    back_transform = create_transform(ng, name="Back Transform", location=(-350, -400))

    link(ng, interior_width, 0, back_size, "X")
    link(ng, group_in, "Back Thickness", back_size, "Y")
    link(ng, interior_height, 0, back_size, "Z")
    link(ng, back_size, "Vector", back, "Size")

    # Back Y = -depth + back_thickness/2
    back_thick_half = create_math(ng, 'DIVIDE', name="Back Thick Half", location=(-850, -450))
    link(ng, group_in, "Back Thickness", back_thick_half, 0)
    set_default(back_thick_half, 1, 2.0)
    back_y = create_math(ng, 'MULTIPLY', name="Back Y Neg", location=(-750, -450))
    link(ng, group_in, "Depth", back_y, 0)
    set_default(back_y, 1, -1.0)
    back_y_offset = create_math(ng, 'ADD', name="Back Y Offset", location=(-650, -450))
    link(ng, back_y, 0, back_y_offset, 0)
    link(ng, back_thick_half, 0, back_y_offset, 1)

    link(ng, back_y_offset, 0, back_pos, "Y")
    link(ng, height_half, 0, back_pos, "Z")
    link(ng, back_pos, "Vector", back_transform, "Translation")
    link(ng, back, "Mesh", back_transform, "Geometry")

    # Set back material
    back_mat = create_set_material(ng, name="Back Material", location=(-200, -400))
    link(ng, back_transform, "Geometry", back_mat, "Geometry")
    link(ng, group_in, "Back Material", back_mat, "Material")

    # Switch for back panel
    switch_back = create_switch(ng, 'GEOMETRY', name="Has Back Switch", location=(0, -400))
    link(ng, group_in, "Has Back", switch_back, "Switch")
    link(ng, back_mat, "Geometry", switch_back, "True")

    # ============ FACE FRAME ============
    # Face frame consists of:
    # - Left stile (vertical)
    # - Right stile (vertical)
    # - Top rail (horizontal)
    # - Bottom rail (horizontal)
    # All at the front face of the cabinet (Y=0)

    # Left stile: Face Frame Width (X) x Panel Thickness (Y) x Height (Z)
    left_stile = create_cube(ng, name="Left Stile", location=(-500, -550))
    left_stile_size = create_combine_xyz(ng, name="Left Stile Size", location=(-650, -500))
    left_stile_pos = create_combine_xyz(ng, name="Left Stile Pos", location=(-650, -600))
    left_stile_transform = create_transform(ng, name="Left Stile Transform", location=(-350, -550))

    link(ng, group_in, "Face Frame Width", left_stile_size, "X")
    link(ng, group_in, "Panel Thickness", left_stile_size, "Y")
    link(ng, group_in, "Height", left_stile_size, "Z")
    link(ng, left_stile_size, "Vector", left_stile, "Size")

    # Left stile X = -(width/2 - frame_width/2)
    frame_half = create_math(ng, 'DIVIDE', name="Frame Half", location=(-850, -550))
    link(ng, group_in, "Face Frame Width", frame_half, 0)
    set_default(frame_half, 1, 2.0)

    width_half = create_math(ng, 'DIVIDE', name="Width Half", location=(-850, -600))
    link(ng, group_in, "Width", width_half, 0)
    set_default(width_half, 1, 2.0)

    left_stile_x = create_math(ng, 'SUBTRACT', name="Left Stile X", location=(-750, -550))
    link(ng, frame_half, 0, left_stile_x, 0)
    link(ng, width_half, 0, left_stile_x, 1)

    # Y position = -panel_thickness/2 (at front)
    stile_y = create_math(ng, 'DIVIDE', name="Stile Y", location=(-850, -650))
    link(ng, group_in, "Panel Thickness", stile_y, 0)
    set_default(stile_y, 1, -2.0)

    link(ng, left_stile_x, 0, left_stile_pos, "X")
    link(ng, stile_y, 0, left_stile_pos, "Y")
    link(ng, height_half, 0, left_stile_pos, "Z")
    link(ng, left_stile_pos, "Vector", left_stile_transform, "Translation")
    link(ng, left_stile, "Mesh", left_stile_transform, "Geometry")

    # Right stile
    right_stile = create_cube(ng, name="Right Stile", location=(-500, -700))
    right_stile_size = create_combine_xyz(ng, name="Right Stile Size", location=(-650, -650))
    right_stile_pos = create_combine_xyz(ng, name="Right Stile Pos", location=(-650, -750))
    right_stile_transform = create_transform(ng, name="Right Stile Transform", location=(-350, -700))

    link(ng, group_in, "Face Frame Width", right_stile_size, "X")
    link(ng, group_in, "Panel Thickness", right_stile_size, "Y")
    link(ng, group_in, "Height", right_stile_size, "Z")
    link(ng, right_stile_size, "Vector", right_stile, "Size")

    right_stile_x = create_math(ng, 'SUBTRACT', name="Right Stile X", location=(-750, -700))
    link(ng, width_half, 0, right_stile_x, 0)
    link(ng, frame_half, 0, right_stile_x, 1)

    link(ng, right_stile_x, 0, right_stile_pos, "X")
    link(ng, stile_y, 0, right_stile_pos, "Y")
    link(ng, height_half, 0, right_stile_pos, "Z")
    link(ng, right_stile_pos, "Vector", right_stile_transform, "Translation")
    link(ng, right_stile, "Mesh", right_stile_transform, "Geometry")

    # Top rail: (width - 2*frame_width) (X) x Panel Thickness (Y) x Face Frame Width (Z)
    top_rail = create_cube(ng, name="Top Rail", location=(-500, -850))
    top_rail_size = create_combine_xyz(ng, name="Top Rail Size", location=(-650, -800))
    top_rail_pos = create_combine_xyz(ng, name="Top Rail Pos", location=(-650, -900))
    top_rail_transform = create_transform(ng, name="Top Rail Transform", location=(-350, -850))

    # Rail width = width - 2*frame_width
    frame_x2 = create_math(ng, 'MULTIPLY', name="Frame x2", location=(-850, -800))
    link(ng, group_in, "Face Frame Width", frame_x2, 0)
    set_default(frame_x2, 1, 2.0)
    rail_width = create_math(ng, 'SUBTRACT', name="Rail Width", location=(-750, -800))
    link(ng, group_in, "Width", rail_width, 0)
    link(ng, frame_x2, 0, rail_width, 1)

    link(ng, rail_width, 0, top_rail_size, "X")
    link(ng, group_in, "Panel Thickness", top_rail_size, "Y")
    link(ng, group_in, "Face Frame Width", top_rail_size, "Z")
    link(ng, top_rail_size, "Vector", top_rail, "Size")

    # Top rail Z = height - frame_width/2
    top_rail_z = create_math(ng, 'SUBTRACT', name="Top Rail Z", location=(-750, -850))
    link(ng, group_in, "Height", top_rail_z, 0)
    link(ng, frame_half, 0, top_rail_z, 1)

    link(ng, stile_y, 0, top_rail_pos, "Y")
    link(ng, top_rail_z, 0, top_rail_pos, "Z")
    link(ng, top_rail_pos, "Vector", top_rail_transform, "Translation")
    link(ng, top_rail, "Mesh", top_rail_transform, "Geometry")

    # Bottom rail
    bottom_rail = create_cube(ng, name="Bottom Rail", location=(-500, -1000))
    bottom_rail_size = create_combine_xyz(ng, name="Bottom Rail Size", location=(-650, -950))
    bottom_rail_pos = create_combine_xyz(ng, name="Bottom Rail Pos", location=(-650, -1050))
    bottom_rail_transform = create_transform(ng, name="Bottom Rail Transform", location=(-350, -1000))

    link(ng, rail_width, 0, bottom_rail_size, "X")
    link(ng, group_in, "Panel Thickness", bottom_rail_size, "Y")
    link(ng, group_in, "Face Frame Width", bottom_rail_size, "Z")
    link(ng, bottom_rail_size, "Vector", bottom_rail, "Size")

    # Bottom rail Z = frame_width/2
    link(ng, stile_y, 0, bottom_rail_pos, "Y")
    link(ng, frame_half, 0, bottom_rail_pos, "Z")
    link(ng, bottom_rail_pos, "Vector", bottom_rail_transform, "Translation")
    link(ng, bottom_rail, "Mesh", bottom_rail_transform, "Geometry")

    # Join face frame parts
    join_face_frame = create_join_geometry(ng, name="Join Face Frame", location=(-150, -700))
    link(ng, left_stile_transform, "Geometry", join_face_frame, "Geometry")
    link(ng, right_stile_transform, "Geometry", join_face_frame, "Geometry")
    link(ng, top_rail_transform, "Geometry", join_face_frame, "Geometry")
    link(ng, bottom_rail_transform, "Geometry", join_face_frame, "Geometry")

    # Switch for face frame
    switch_face_frame = create_switch(ng, 'GEOMETRY', name="Has Face Frame Switch", location=(0, -700))
    link(ng, group_in, "Has Face Frame", switch_face_frame, "Switch")
    link(ng, join_face_frame, "Geometry", switch_face_frame, "True")

    # ============ JOIN CARCASS ============
    join_carcass = create_join_geometry(ng, name="Join Carcass", location=(0, 200))
    link(ng, left_transform, "Geometry", join_carcass, "Geometry")
    link(ng, right_transform, "Geometry", join_carcass, "Geometry")
    link(ng, top_transform, "Geometry", join_carcass, "Geometry")
    link(ng, bottom_transform, "Geometry", join_carcass, "Geometry")

    # Set carcass material
    carcass_mat = create_set_material(ng, name="Carcass Material", location=(200, 200))
    link(ng, join_carcass, "Geometry", carcass_mat, "Geometry")
    link(ng, group_in, "Carcass Material", carcass_mat, "Material")

    # Join with back and face frame
    join_all = create_join_geometry(ng, name="Join All", location=(400, 0))
    link(ng, carcass_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_back, "Output", join_all, "Geometry")
    link(ng, switch_face_frame, "Output", join_all, "Geometry")

    # ============ BEVEL EDGES ============
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

    # ============ OUTPUTS ============
    link(ng, final_geo, final_socket, group_out, "Geometry")
    link(ng, interior_width, 0, group_out, "Interior Width")
    link(ng, interior_height, 0, group_out, "Interior Height")
    link(ng, interior_depth, 0, group_out, "Interior Depth")

    add_metadata(ng, version="1.3.0", script_path="src/nodes/systems/cabinet_box.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the CabinetBox node group applied."""
    if nodegroup is None:
        nodegroup = create_cabinet_box_nodegroup()

    mesh = bpy.data.meshes.new("CabinetBox_Test")
    obj = bpy.data.objects.new("CabinetBox_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_cabinet_box_nodegroup()
    print(f"Created node group: {ng.name}")
