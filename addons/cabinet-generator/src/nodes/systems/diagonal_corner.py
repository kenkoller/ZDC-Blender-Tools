# Diagonal Corner Cabinet node group generator
# System component: 45-degree angled front corner cabinet
# Coordinate system: X=width, Y=depth, Z=height (Z-up)

import bpy
import math
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


def create_diagonal_corner_nodegroup():
    """Generate the DiagonalCorner node group.

    Diagonal corner cabinet with:
    - 45-degree angled front
    - Single door on diagonal face
    - Interior access for corner storage
    - Optional lazy susan

    Better space utilization than blind corner for smaller kitchens.

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back, negative Y is front)
    - Z = height (floor to ceiling)
    - Origin at front corner of diagonal face
    """
    ng = create_node_group("DiagonalCorner")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    front_panel = create_panel(ng, "Front")
    options_panel = create_panel(ng, "Options")
    toekick_panel = create_panel(ng, "Toe Kick")
    bevel_panel = create_panel(ng, "Bevel")
    materials_panel = create_panel(ng, "Materials")

    # Dimensions - diagonal corner is typically square in plan
    add_float_socket(ng, "Width", default=0.6, min_val=0.45, max_val=0.9,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.72, min_val=0.6, max_val=0.9,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.6, min_val=0.45, max_val=0.9,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Diagonal Width", default=0.4, min_val=0.3, max_val=0.6,
                     subtype='DISTANCE', panel=dims_panel)

    # Front options
    add_int_socket(ng, "Door Style", default=1, min_val=0, max_val=4, panel=front_panel)
    add_int_socket(ng, "Handle Style", default=0, min_val=0, max_val=4, panel=front_panel)

    # Options
    add_bool_socket(ng, "Has Back", default=True, panel=options_panel)
    add_bool_socket(ng, "Has Lazy Susan", default=False, panel=options_panel)
    add_int_socket(ng, "Lazy Susan Count", default=2, min_val=1, max_val=4, panel=options_panel)
    # 0=Full Round, 1=Kidney, 2=Pie Cut, 3=D-Shape, 4=Half-Moon
    add_int_socket(ng, "Lazy Susan Style", default=0, min_val=0, max_val=4, panel=options_panel)
    # Override diameter (0 = auto-calculate from interior dimensions)
    add_float_socket(ng, "Lazy Susan Diameter", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='DISTANCE', panel=options_panel)
    add_int_socket(ng, "Corner Type", default=0, min_val=0, max_val=1, panel=options_panel)

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
    add_material_socket(ng, "Door Material", panel=materials_panel)
    add_material_socket(ng, "Handle Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1400, 0))
    group_out = create_group_output(ng, location=(1400, 0))

    # ============ CALCULATE KEY DIMENSIONS ============
    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-1200, -400))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)

    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-1200, -450))
    link(ng, group_in, "Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    # Diagonal calculation: diagonal_width is the face width
    # The cabinet extends back at 45 degrees

    # ============ LEFT SIDE PANEL ============
    # Runs along Y axis from front to corner
    left_size = create_combine_xyz(ng, name="Left Size", location=(-1000, 400))
    link(ng, group_in, "Panel Thickness", left_size, "X")
    link(ng, group_in, "Depth", left_size, "Y")
    link(ng, group_in, "Height", left_size, "Z")

    left_side = create_cube(ng, name="Left Side", location=(-900, 400))
    link(ng, left_size, "Vector", left_side, "Size")

    # Left side X position at -width/2 + panel_thickness/2
    width_half = create_math(ng, 'DIVIDE', name="Width Half", location=(-1100, 350))
    link(ng, group_in, "Width", width_half, 0)
    set_default(width_half, 1, 2.0)
    left_x = create_math(ng, 'MULTIPLY', name="Left X Neg", location=(-1000, 350))
    link(ng, width_half, 0, left_x, 0)
    set_default(left_x, 1, -1.0)
    left_x_offset = create_math(ng, 'ADD', name="Left X Offset", location=(-900, 350))
    link(ng, left_x, 0, left_x_offset, 0)
    link(ng, panel_half, 0, left_x_offset, 1)

    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-1100, 300))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-800, 400))
    link(ng, left_x_offset, 0, left_pos, "X")
    link(ng, depth_half, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Transform", location=(-700, 400))
    link(ng, left_side, "Mesh", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    # ============ RIGHT SIDE PANEL ============
    # Runs along X axis from front to corner
    right_size = create_combine_xyz(ng, name="Right Size", location=(-1000, 200))
    link(ng, group_in, "Width", right_size, "X")
    link(ng, group_in, "Panel Thickness", right_size, "Y")
    link(ng, group_in, "Height", right_size, "Z")

    right_side = create_cube(ng, name="Right Side", location=(-900, 200))
    link(ng, right_size, "Vector", right_side, "Size")

    # Right side Y position at -depth + panel_thickness/2
    depth_neg = create_math(ng, 'MULTIPLY', name="Depth Neg", location=(-1000, 150))
    link(ng, group_in, "Depth", depth_neg, 0)
    set_default(depth_neg, 1, -1.0)
    right_y = create_math(ng, 'ADD', name="Right Y Offset", location=(-900, 150))
    link(ng, depth_neg, 0, right_y, 0)
    link(ng, panel_half, 0, right_y, 1)

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-800, 200))
    set_default(right_pos, "X", 0.0)
    link(ng, right_y, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Transform", location=(-700, 200))
    link(ng, right_side, "Mesh", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    # ============ TOP PANEL ============
    # Simplified as full rectangle (in reality would be L-shaped minus diagonal)
    top_size = create_combine_xyz(ng, name="Top Size", location=(-1000, 0))
    link(ng, group_in, "Width", top_size, "X")
    link(ng, group_in, "Depth", top_size, "Y")
    link(ng, group_in, "Panel Thickness", top_size, "Z")

    top = create_cube(ng, name="Top", location=(-900, 0))
    link(ng, top_size, "Vector", top, "Size")

    top_z = create_math(ng, 'SUBTRACT', name="Top Z", location=(-1000, -50))
    link(ng, group_in, "Height", top_z, 0)
    link(ng, panel_half, 0, top_z, 1)

    top_pos = create_combine_xyz(ng, name="Top Pos", location=(-800, 0))
    set_default(top_pos, "X", 0.0)
    link(ng, depth_half, 0, top_pos, "Y")
    link(ng, top_z, 0, top_pos, "Z")

    top_transform = create_transform(ng, name="Top Transform", location=(-700, 0))
    link(ng, top, "Mesh", top_transform, "Geometry")
    link(ng, top_pos, "Vector", top_transform, "Translation")

    # ============ BOTTOM PANEL ============
    bottom = create_cube(ng, name="Bottom", location=(-900, -100))
    link(ng, top_size, "Vector", bottom, "Size")

    bottom_pos = create_combine_xyz(ng, name="Bottom Pos", location=(-800, -100))
    set_default(bottom_pos, "X", 0.0)
    link(ng, depth_half, 0, bottom_pos, "Y")
    link(ng, panel_half, 0, bottom_pos, "Z")

    bottom_transform = create_transform(ng, name="Bottom Transform", location=(-700, -100))
    link(ng, bottom, "Mesh", bottom_transform, "Geometry")
    link(ng, bottom_pos, "Vector", bottom_transform, "Translation")

    # ============ DIAGONAL DOOR PANEL ============
    # The angled front door
    door_height = create_math(ng, 'SUBTRACT', name="Door Height", location=(-1000, -300))
    link(ng, group_in, "Height", door_height, 0)
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-1100, -350))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)
    door_height_final = create_math(ng, 'SUBTRACT', name="Door Height Final", location=(-900, -300))
    link(ng, door_height, 0, door_height_final, 0)
    set_default(door_height_final, 1, 0.006)  # Gap

    door_size = create_combine_xyz(ng, name="Door Size", location=(-800, -300))
    link(ng, group_in, "Diagonal Width", door_size, "X")
    link(ng, group_in, "Panel Thickness", door_size, "Y")
    link(ng, door_height_final, 0, door_size, "Z")

    door = create_cube(ng, name="Door", location=(-700, -300))
    link(ng, door_size, "Vector", door, "Size")

    # Door position and rotation (45 degrees)
    # Position at front corner, rotated 45 degrees around Z
    diag_half = create_math(ng, 'DIVIDE', name="Diag Half", location=(-900, -400))
    link(ng, group_in, "Diagonal Width", diag_half, 0)
    set_default(diag_half, 1, 2.0)

    # The door center in local space before rotation
    # For a 45-degree cabinet, the door sits at the corner clipped area
    door_z = create_math(ng, 'ADD', name="Door Z", location=(-800, -400))
    link(ng, group_in, "Panel Thickness", door_z, 0)
    door_z_half = create_math(ng, 'DIVIDE', name="Door Z Half", location=(-700, -400))
    link(ng, door_height_final, 0, door_z_half, 0)
    set_default(door_z_half, 1, 2.0)
    door_z_final = create_math(ng, 'ADD', name="Door Z Final", location=(-600, -400))
    link(ng, door_z, 0, door_z_final, 0)
    link(ng, door_z_half, 0, door_z_final, 1)

    door_pos = create_combine_xyz(ng, name="Door Pos", location=(-600, -300))
    link(ng, left_x, 0, door_pos, "X")  # At front-left
    set_default(door_pos, "Y", 0.0)
    link(ng, door_z_final, 0, door_pos, "Z")

    # Rotation: 45 degrees = pi/4 radians
    door_rot = create_combine_xyz(ng, name="Door Rot", location=(-600, -350))
    set_default(door_rot, "X", 0.0)
    set_default(door_rot, "Y", 0.0)
    set_default(door_rot, "Z", math.pi / 4)  # 45 degrees

    door_transform = create_transform(ng, name="Door Transform", location=(-500, -300))
    link(ng, door, "Mesh", door_transform, "Geometry")
    link(ng, door_pos, "Vector", door_transform, "Translation")
    link(ng, door_rot, "Vector", door_transform, "Rotation")

    door_mat = create_set_material(ng, name="Door Material", location=(-350, -300))
    link(ng, door_transform, "Geometry", door_mat, "Geometry")
    link(ng, group_in, "Door Material", door_mat, "Material")

    # ============ JOIN CARCASS ============
    join_carcass = create_join_geometry(ng, name="Join Carcass", location=(-400, 200))
    link(ng, left_transform, "Geometry", join_carcass, "Geometry")
    link(ng, right_transform, "Geometry", join_carcass, "Geometry")
    link(ng, top_transform, "Geometry", join_carcass, "Geometry")
    link(ng, bottom_transform, "Geometry", join_carcass, "Geometry")

    carcass_mat = create_set_material(ng, name="Carcass Material", location=(-250, 200))
    link(ng, join_carcass, "Geometry", carcass_mat, "Geometry")
    link(ng, group_in, "Carcass Material", carcass_mat, "Material")

    # ============ TOE KICK ============
    tk_size = create_combine_xyz(ng, name="TK Size", location=(-1000, -600))
    link(ng, group_in, "Diagonal Width", tk_size, "X")
    link(ng, group_in, "Toe Kick Depth", tk_size, "Y")
    link(ng, group_in, "Toe Kick Height", tk_size, "Z")

    toe_kick = create_cube(ng, name="Toe Kick", location=(-900, -600))
    link(ng, tk_size, "Vector", toe_kick, "Size")

    tk_z = create_math(ng, 'DIVIDE', name="TK Z", location=(-900, -650))
    link(ng, group_in, "Toe Kick Height", tk_z, 0)
    set_default(tk_z, 1, -2.0)

    tk_y = create_math(ng, 'DIVIDE', name="TK Y", location=(-900, -700))
    link(ng, group_in, "Toe Kick Depth", tk_y, 0)
    set_default(tk_y, 1, -2.0)

    tk_pos = create_combine_xyz(ng, name="TK Pos", location=(-800, -600))
    link(ng, left_x, 0, tk_pos, "X")
    link(ng, tk_y, 0, tk_pos, "Y")
    link(ng, tk_z, 0, tk_pos, "Z")

    tk_transform = create_transform(ng, name="TK Transform", location=(-700, -600))
    link(ng, toe_kick, "Mesh", tk_transform, "Geometry")
    link(ng, tk_pos, "Vector", tk_transform, "Translation")
    link(ng, door_rot, "Vector", tk_transform, "Rotation")  # Same 45-degree rotation

    tk_mat = create_set_material(ng, name="TK Material", location=(-550, -600))
    link(ng, tk_transform, "Geometry", tk_mat, "Geometry")
    link(ng, group_in, "Carcass Material", tk_mat, "Material")

    switch_tk = create_switch(ng, 'GEOMETRY', name="TK Switch", location=(-400, -600))
    link(ng, group_in, "Has Toe Kick", switch_tk, "Switch")
    link(ng, tk_mat, "Geometry", switch_tk, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(0, 0))
    link(ng, carcass_mat, "Geometry", join_all, "Geometry")
    link(ng, door_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_tk, "Output", join_all, "Geometry")

    # ============ BEVEL ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(200, 0))
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

    add_metadata(ng, version="1.0.0", script_path="src/nodes/systems/diagonal_corner.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the DiagonalCorner node group applied."""
    if nodegroup is None:
        nodegroup = create_diagonal_corner_nodegroup()

    mesh = bpy.data.meshes.new("DiagonalCorner_Test")
    obj = bpy.data.objects.new("DiagonalCorner_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_diagonal_corner_nodegroup()
    print(f"Created node group: {ng.name}")
