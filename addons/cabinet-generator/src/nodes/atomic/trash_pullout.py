# Trash Pull-out node group generator
# Atomic component: Pull-out trash/recycling bin insert
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
    link,
    set_default,
    add_metadata,
)


def create_trash_pullout_nodegroup():
    """Generate the TrashPullout node group.

    Creates a pull-out trash/recycling bin insert with:
    - Frame/cage structure
    - Single or double bin configuration
    - Pull-out extension animation

    Inputs:
        Width: Insert width
        Depth: Insert depth
        Height: Insert height
        Double Bin: Use two bins side by side
        Extension: 0-1 (how far pulled out)
        Frame Material: Metal frame material
        Bin Material: Bin material (optional)

    Outputs:
        Geometry: Trash insert mesh
    """
    ng = create_node_group("TrashPullout")

    # Create interface
    dims_panel = create_panel(ng, "Dimensions")
    options_panel = create_panel(ng, "Options")
    anim_panel = create_panel(ng, "Animation")
    materials_panel = create_panel(ng, "Materials")

    add_float_socket(ng, "Width", default=0.35, min_val=0.2, max_val=0.6,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.45, min_val=0.3, max_val=0.55,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.5, min_val=0.3, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_bool_socket(ng, "Double Bin", default=False, panel=options_panel)
    add_float_socket(ng, "Extension", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='FACTOR', panel=anim_panel)
    add_material_socket(ng, "Frame Material", panel=materials_panel)
    add_material_socket(ng, "Bin Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1000, 0))
    group_out = create_group_output(ng, location=(1000, 0))

    # ============ FRAME RAILS ============
    rail_thickness = 0.015

    # Bottom frame - front rail
    front_rail_size = create_combine_xyz(ng, name="Front Rail Size", location=(-700, 400))
    link(ng, group_in, "Width", front_rail_size, "X")
    set_default(front_rail_size, "Y", rail_thickness)
    set_default(front_rail_size, "Z", rail_thickness)

    front_rail = create_cube(ng, name="Front Rail", location=(-600, 400))
    link(ng, front_rail_size, "Vector", front_rail, "Size")

    front_rail_pos = create_combine_xyz(ng, name="Front Rail Pos", location=(-700, 350))
    set_default(front_rail_pos, "X", 0.0)
    set_default(front_rail_pos, "Y", -rail_thickness / 2)
    set_default(front_rail_pos, "Z", rail_thickness / 2)

    front_rail_transform = create_transform(ng, name="Front Rail Transform", location=(-500, 400))
    link(ng, front_rail, "Mesh", front_rail_transform, "Geometry")
    link(ng, front_rail_pos, "Vector", front_rail_transform, "Translation")

    # Bottom frame - back rail
    back_rail = create_cube(ng, name="Back Rail", location=(-600, 300))
    link(ng, front_rail_size, "Vector", back_rail, "Size")

    back_y = create_math(ng, 'MULTIPLY', name="Back Y", location=(-700, 250))
    link(ng, group_in, "Depth", back_y, 0)
    set_default(back_y, 1, -1.0)
    back_y_offset = create_math(ng, 'ADD', name="Back Y Offset", location=(-600, 250))
    link(ng, back_y, 0, back_y_offset, 0)
    set_default(back_y_offset, 1, rail_thickness / 2)

    back_rail_pos = create_combine_xyz(ng, name="Back Rail Pos", location=(-500, 250))
    set_default(back_rail_pos, "X", 0.0)
    link(ng, back_y_offset, 0, back_rail_pos, "Y")
    set_default(back_rail_pos, "Z", rail_thickness / 2)

    back_rail_transform = create_transform(ng, name="Back Rail Transform", location=(-400, 300))
    link(ng, back_rail, "Mesh", back_rail_transform, "Geometry")
    link(ng, back_rail_pos, "Vector", back_rail_transform, "Translation")

    # Side rails (left and right)
    side_rail_size = create_combine_xyz(ng, name="Side Rail Size", location=(-700, 100))
    set_default(side_rail_size, "X", rail_thickness)
    link(ng, group_in, "Depth", side_rail_size, "Y")
    set_default(side_rail_size, "Z", rail_thickness)

    side_rail = create_cube(ng, name="Side Rail", location=(-600, 100))
    link(ng, side_rail_size, "Vector", side_rail, "Size")

    # Left side rail
    left_x = create_math(ng, 'DIVIDE', name="Left X", location=(-700, 50))
    link(ng, group_in, "Width", left_x, 0)
    set_default(left_x, 1, -2.0)
    left_x_offset = create_math(ng, 'ADD', name="Left X Offset", location=(-600, 50))
    link(ng, left_x, 0, left_x_offset, 0)
    set_default(left_x_offset, 1, rail_thickness / 2)

    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-700, 0))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    left_rail_pos = create_combine_xyz(ng, name="Left Rail Pos", location=(-500, 50))
    link(ng, left_x_offset, 0, left_rail_pos, "X")
    link(ng, depth_half, 0, left_rail_pos, "Y")
    set_default(left_rail_pos, "Z", rail_thickness / 2)

    left_rail_transform = create_transform(ng, name="Left Rail Transform", location=(-400, 100))
    link(ng, side_rail, "Mesh", left_rail_transform, "Geometry")
    link(ng, left_rail_pos, "Vector", left_rail_transform, "Translation")

    # Right side rail
    right_x = create_math(ng, 'DIVIDE', name="Right X", location=(-700, -50))
    link(ng, group_in, "Width", right_x, 0)
    set_default(right_x, 1, 2.0)
    right_x_offset = create_math(ng, 'SUBTRACT', name="Right X Offset", location=(-600, -50))
    link(ng, right_x, 0, right_x_offset, 0)
    set_default(right_x_offset, 1, rail_thickness / 2)

    right_rail_pos = create_combine_xyz(ng, name="Right Rail Pos", location=(-500, -50))
    link(ng, right_x_offset, 0, right_rail_pos, "X")
    link(ng, depth_half, 0, right_rail_pos, "Y")
    set_default(right_rail_pos, "Z", rail_thickness / 2)

    right_rail_transform = create_transform(ng, name="Right Rail Transform", location=(-400, -50))
    link(ng, side_rail, "Mesh", right_rail_transform, "Geometry")
    link(ng, right_rail_pos, "Vector", right_rail_transform, "Translation")

    # Join bottom frame
    join_frame = create_join_geometry(ng, name="Join Frame", location=(-200, 200))
    link(ng, front_rail_transform, "Geometry", join_frame, "Geometry")
    link(ng, back_rail_transform, "Geometry", join_frame, "Geometry")
    link(ng, left_rail_transform, "Geometry", join_frame, "Geometry")
    link(ng, right_rail_transform, "Geometry", join_frame, "Geometry")

    # Set frame material
    frame_mat = create_set_material(ng, name="Frame Material", location=(-50, 200))
    link(ng, join_frame, "Geometry", frame_mat, "Geometry")
    link(ng, group_in, "Frame Material", frame_mat, "Material")

    # ============ SINGLE BIN ============
    bin_wall = 0.003  # Thin bin walls

    # Bin dimensions (slightly smaller than frame)
    bin_width = create_math(ng, 'SUBTRACT', name="Bin Width", location=(-700, -200))
    link(ng, group_in, "Width", bin_width, 0)
    set_default(bin_width, 1, rail_thickness * 2 + 0.01)

    bin_depth = create_math(ng, 'SUBTRACT', name="Bin Depth", location=(-700, -250))
    link(ng, group_in, "Depth", bin_depth, 0)
    set_default(bin_depth, 1, rail_thickness * 2 + 0.01)

    bin_height = create_math(ng, 'SUBTRACT', name="Bin Height", location=(-700, -300))
    link(ng, group_in, "Height", bin_height, 0)
    set_default(bin_height, 1, rail_thickness + 0.02)

    # Outer bin (hollow - using difference would be complex, so simplified solid)
    bin_size = create_combine_xyz(ng, name="Bin Size", location=(-500, -250))
    link(ng, bin_width, 0, bin_size, "X")
    link(ng, bin_depth, 0, bin_size, "Y")
    link(ng, bin_height, 0, bin_size, "Z")

    bin_cube = create_cube(ng, name="Bin", location=(-400, -250))
    link(ng, bin_size, "Vector", bin_cube, "Size")

    # Bin position (centered, sitting on frame)
    bin_z = create_math(ng, 'DIVIDE', name="Bin Z", location=(-500, -350))
    link(ng, bin_height, 0, bin_z, 0)
    set_default(bin_z, 1, 2.0)
    bin_z_offset = create_math(ng, 'ADD', name="Bin Z Offset", location=(-400, -350))
    link(ng, bin_z, 0, bin_z_offset, 0)
    set_default(bin_z_offset, 1, rail_thickness)

    bin_pos = create_combine_xyz(ng, name="Bin Pos", location=(-300, -300))
    set_default(bin_pos, "X", 0.0)
    link(ng, depth_half, 0, bin_pos, "Y")
    link(ng, bin_z_offset, 0, bin_pos, "Z")

    bin_transform = create_transform(ng, name="Bin Transform", location=(-200, -250))
    link(ng, bin_cube, "Mesh", bin_transform, "Geometry")
    link(ng, bin_pos, "Vector", bin_transform, "Translation")

    # Set bin material
    bin_mat = create_set_material(ng, name="Bin Material", location=(-50, -250))
    link(ng, bin_transform, "Geometry", bin_mat, "Geometry")
    link(ng, group_in, "Bin Material", bin_mat, "Material")

    # ============ DOUBLE BIN ============
    # Two smaller bins side by side
    double_bin_width = create_math(ng, 'DIVIDE', name="Double Bin Width", location=(-700, -450))
    link(ng, bin_width, 0, double_bin_width, 0)
    set_default(double_bin_width, 1, 2.1)  # Slightly less than half for gap

    double_bin_size = create_combine_xyz(ng, name="Double Bin Size", location=(-500, -450))
    link(ng, double_bin_width, 0, double_bin_size, "X")
    link(ng, bin_depth, 0, double_bin_size, "Y")
    link(ng, bin_height, 0, double_bin_size, "Z")

    double_bin = create_cube(ng, name="Double Bin", location=(-400, -450))
    link(ng, double_bin_size, "Vector", double_bin, "Size")

    # Left bin position
    left_bin_x = create_math(ng, 'DIVIDE', name="Left Bin X", location=(-500, -500))
    link(ng, double_bin_width, 0, left_bin_x, 0)
    set_default(left_bin_x, 1, -2.0)
    left_bin_x_offset = create_math(ng, 'SUBTRACT', name="Left Bin X Offset", location=(-400, -500))
    link(ng, left_bin_x, 0, left_bin_x_offset, 0)
    set_default(left_bin_x_offset, 1, 0.005)

    left_bin_pos = create_combine_xyz(ng, name="Left Bin Pos", location=(-300, -500))
    link(ng, left_bin_x_offset, 0, left_bin_pos, "X")
    link(ng, depth_half, 0, left_bin_pos, "Y")
    link(ng, bin_z_offset, 0, left_bin_pos, "Z")

    left_bin_transform = create_transform(ng, name="Left Bin Transform", location=(-200, -450))
    link(ng, double_bin, "Mesh", left_bin_transform, "Geometry")
    link(ng, left_bin_pos, "Vector", left_bin_transform, "Translation")

    # Right bin position
    right_bin_x = create_math(ng, 'DIVIDE', name="Right Bin X", location=(-500, -600))
    link(ng, double_bin_width, 0, right_bin_x, 0)
    set_default(right_bin_x, 1, 2.0)
    right_bin_x_offset = create_math(ng, 'ADD', name="Right Bin X Offset", location=(-400, -600))
    link(ng, right_bin_x, 0, right_bin_x_offset, 0)
    set_default(right_bin_x_offset, 1, 0.005)

    right_bin_pos = create_combine_xyz(ng, name="Right Bin Pos", location=(-300, -600))
    link(ng, right_bin_x_offset, 0, right_bin_pos, "X")
    link(ng, depth_half, 0, right_bin_pos, "Y")
    link(ng, bin_z_offset, 0, right_bin_pos, "Z")

    right_bin_transform = create_transform(ng, name="Right Bin Transform", location=(-200, -550))
    link(ng, double_bin, "Mesh", right_bin_transform, "Geometry")
    link(ng, right_bin_pos, "Vector", right_bin_transform, "Translation")

    # Join double bins
    join_double = create_join_geometry(ng, name="Join Double Bins", location=(-50, -500))
    link(ng, left_bin_transform, "Geometry", join_double, "Geometry")
    link(ng, right_bin_transform, "Geometry", join_double, "Geometry")

    double_bin_mat = create_set_material(ng, name="Double Bin Material", location=(100, -500))
    link(ng, join_double, "Geometry", double_bin_mat, "Geometry")
    link(ng, group_in, "Bin Material", double_bin_mat, "Material")

    # ============ SWITCH SINGLE/DOUBLE ============
    switch_bins = create_switch(ng, 'GEOMETRY', name="Bin Switch", location=(250, -350))
    link(ng, group_in, "Double Bin", switch_bins, "Switch")
    link(ng, bin_mat, "Geometry", switch_bins, "False")
    link(ng, double_bin_mat, "Geometry", switch_bins, "True")

    # ============ JOIN FRAME AND BINS ============
    join_all = create_join_geometry(ng, name="Join All", location=(400, 0))
    link(ng, frame_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_bins, "Output", join_all, "Geometry")

    # ============ APPLY EXTENSION ============
    ext_offset = create_math(ng, 'MULTIPLY', name="Extension Offset", location=(500, -100))
    link(ng, group_in, "Extension", ext_offset, 0)
    link(ng, group_in, "Depth", ext_offset, 1)

    ext_pos = create_combine_xyz(ng, name="Extension Pos", location=(600, -100))
    set_default(ext_pos, "X", 0.0)
    link(ng, ext_offset, 0, ext_pos, "Y")
    set_default(ext_pos, "Z", 0.0)

    final_transform = create_transform(ng, name="Final Transform", location=(700, 0))
    link(ng, join_all, "Geometry", final_transform, "Geometry")
    link(ng, ext_pos, "Vector", final_transform, "Translation")

    # ============ OUTPUT ============
    link(ng, final_transform, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/trash_pullout.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the TrashPullout node group applied."""
    if nodegroup is None:
        nodegroup = create_trash_pullout_nodegroup()

    mesh = bpy.data.meshes.new("TrashPullout_Test")
    obj = bpy.data.objects.new("TrashPullout_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_trash_pullout_nodegroup()
    print(f"Created node group: {ng.name}")
