# Drawer node group generator
# Atomic component: Single drawer box with front panel

import bpy
from ..utils import (
    create_node_group,
    add_geometry_output,
    add_float_socket,
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
    link,
    set_default,
    add_metadata,
)


def create_drawer_nodegroup():
    """Generate the Drawer node group.

    A drawer box consisting of:
    - Front panel (visible drawer face)
    - Two side panels
    - Back panel
    - Bottom panel

    Inputs:
        Width (float): Drawer width (exterior)
        Height (float): Drawer front height
        Depth (float): Drawer depth
        Front Thickness (float): Thickness of drawer front
        Side Thickness (float): Thickness of sides/back
        Bottom Thickness (float): Thickness of bottom panel
        Bottom Inset (float): How far bottom is inset from edges
        Include Box (bool): Whether to include the box or just the front
        Front Material (material): Material for drawer front
        Box Material (material): Material for drawer box

    Outputs:
        Geometry: The drawer mesh

    Returns:
        The created node group
    """
    ng = create_node_group("Drawer")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    thickness_panel = create_panel(ng, "Thickness")
    materials_panel = create_panel(ng, "Materials")

    # Dimension sockets
    add_float_socket(ng, "Width", default=0.4, min_val=0.1, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.15, min_val=0.05, max_val=0.5,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.45, min_val=0.1, max_val=0.8,
                     subtype='DISTANCE', panel=dims_panel)

    # Thickness sockets
    add_float_socket(ng, "Front Thickness", default=0.018, min_val=0.01, max_val=0.03,
                     subtype='DISTANCE', panel=thickness_panel)
    add_float_socket(ng, "Side Thickness", default=0.012, min_val=0.006, max_val=0.02,
                     subtype='DISTANCE', panel=thickness_panel)
    add_float_socket(ng, "Bottom Thickness", default=0.006, min_val=0.003, max_val=0.012,
                     subtype='DISTANCE', panel=thickness_panel)
    add_float_socket(ng, "Bottom Inset", default=0.01, min_val=0.0, max_val=0.03,
                     subtype='DISTANCE', panel=thickness_panel)

    # Options
    add_bool_socket(ng, "Include Box", default=True, panel=dims_panel)

    # Material sockets
    add_material_socket(ng, "Front Material", panel=materials_panel)
    add_material_socket(ng, "Box Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-900, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ DRAWER FRONT ============
    front = create_cube(ng, name="Drawer Front", location=(-500, 400))
    front_size = create_combine_xyz(ng, name="Front Size", location=(-650, 450))
    front_pos = create_combine_xyz(ng, name="Front Pos", location=(-650, 350))
    front_transform = create_transform(ng, name="Front Transform", location=(-350, 400))

    link(ng, group_in, "Width", front_size, "X")
    link(ng, group_in, "Height", front_size, "Y")
    link(ng, group_in, "Front Thickness", front_size, "Z")
    link(ng, front_size, "Vector", front, "Size")

    # Front position: Z = depth/2 (front face of drawer)
    front_z = create_math(ng, 'DIVIDE', name="Front Z", location=(-750, 300))
    link(ng, group_in, "Depth", front_z, 0)
    set_default(front_z, 1, 2.0)
    link(ng, front_z, 0, front_pos, "Z")
    link(ng, front_pos, "Vector", front_transform, "Translation")
    link(ng, front, "Mesh", front_transform, "Geometry")

    # Set front material
    front_mat = create_set_material(ng, name="Front Material", location=(-200, 400))
    link(ng, front_transform, "Geometry", front_mat, "Geometry")
    link(ng, group_in, "Front Material", front_mat, "Material")

    # ============ DRAWER BOX ============
    # Calculate interior dimensions
    # Interior width = width - 2*side_thickness - small gap for front overlay
    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-750, 100))
    side_x2 = create_math(ng, 'MULTIPLY', name="Side x2", location=(-850, 100))
    link(ng, group_in, "Side Thickness", side_x2, 0)
    set_default(side_x2, 1, 2.0)
    link(ng, group_in, "Width", interior_width, 0)
    link(ng, side_x2, 0, interior_width, 1)

    # Box depth = depth - front_thickness
    box_depth = create_math(ng, 'SUBTRACT', name="Box Depth", location=(-750, 0))
    link(ng, group_in, "Depth", box_depth, 0)
    link(ng, group_in, "Front Thickness", box_depth, 1)

    # Box height = height - small gap
    box_height = create_math(ng, 'SUBTRACT', name="Box Height", location=(-750, -100))
    link(ng, group_in, "Height", box_height, 0)
    set_default(box_height, 1, 0.01)  # 10mm gap below front

    # ============ LEFT SIDE ============
    left_side = create_cube(ng, name="Left Side", location=(-500, 100))
    left_size = create_combine_xyz(ng, name="Left Size", location=(-650, 150))
    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-650, 50))
    left_transform = create_transform(ng, name="Left Transform", location=(-350, 100))

    link(ng, group_in, "Side Thickness", left_size, "X")
    link(ng, box_height, 0, left_size, "Y")
    link(ng, box_depth, 0, left_size, "Z")
    link(ng, left_size, "Vector", left_side, "Size")

    # Left X position = -(interior_width + side_thickness) / 2
    left_x_add = create_math(ng, 'ADD', name="Left X Add", location=(-750, -200))
    left_x_div = create_math(ng, 'DIVIDE', name="Left X Div", location=(-650, -200))
    left_x_neg = create_math(ng, 'MULTIPLY', name="Left X Neg", location=(-550, -200))
    link(ng, interior_width, 0, left_x_add, 0)
    link(ng, group_in, "Side Thickness", left_x_add, 1)
    link(ng, left_x_add, 0, left_x_div, 0)
    set_default(left_x_div, 1, 2.0)
    link(ng, left_x_div, 0, left_x_neg, 0)
    set_default(left_x_neg, 1, -1.0)
    link(ng, left_x_neg, 0, left_pos, "X")

    # Y position (centered on box height, offset down from front)
    box_y_offset = create_math(ng, 'SUBTRACT', name="Box Y Offset", location=(-750, -300))
    box_y_div = create_math(ng, 'DIVIDE', name="Box Y Div", location=(-650, -300))
    box_y_neg = create_math(ng, 'MULTIPLY', name="Box Y Neg", location=(-550, -300))
    link(ng, group_in, "Height", box_y_offset, 0)
    link(ng, box_height, 0, box_y_offset, 1)
    link(ng, box_y_offset, 0, box_y_div, 0)
    set_default(box_y_div, 1, 2.0)
    link(ng, box_y_div, 0, box_y_neg, 0)
    set_default(box_y_neg, 1, -1.0)
    link(ng, box_y_neg, 0, left_pos, "Y")

    # Z position (centered behind front)
    box_z = create_math(ng, 'SUBTRACT', name="Box Z", location=(-750, -400))
    box_z_div = create_math(ng, 'DIVIDE', name="Box Z Div", location=(-650, -400))
    link(ng, front_z, 0, box_z, 0)
    link(ng, group_in, "Front Thickness", box_z, 1)
    link(ng, box_depth, 0, box_z_div, 0)
    set_default(box_z_div, 1, 2.0)
    box_z_final = create_math(ng, 'SUBTRACT', name="Box Z Final", location=(-550, -400))
    link(ng, box_z, 0, box_z_final, 0)
    link(ng, box_z_div, 0, box_z_final, 1)
    link(ng, box_z_final, 0, left_pos, "Z")

    link(ng, left_pos, "Vector", left_transform, "Translation")
    link(ng, left_side, "Mesh", left_transform, "Geometry")

    # ============ RIGHT SIDE ============
    right_side = create_cube(ng, name="Right Side", location=(-500, -100))
    right_size = create_combine_xyz(ng, name="Right Size", location=(-650, -50))
    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-650, -150))
    right_transform = create_transform(ng, name="Right Transform", location=(-350, -100))

    link(ng, group_in, "Side Thickness", right_size, "X")
    link(ng, box_height, 0, right_size, "Y")
    link(ng, box_depth, 0, right_size, "Z")
    link(ng, right_size, "Vector", right_side, "Size")

    link(ng, left_x_div, 0, right_pos, "X")  # Positive X
    link(ng, box_y_neg, 0, right_pos, "Y")
    link(ng, box_z_final, 0, right_pos, "Z")
    link(ng, right_pos, "Vector", right_transform, "Translation")
    link(ng, right_side, "Mesh", right_transform, "Geometry")

    # ============ BACK ============
    back = create_cube(ng, name="Back", location=(-500, -300))
    back_size = create_combine_xyz(ng, name="Back Size", location=(-650, -250))
    back_pos = create_combine_xyz(ng, name="Back Pos", location=(-650, -350))
    back_transform = create_transform(ng, name="Back Transform", location=(-350, -300))

    link(ng, interior_width, 0, back_size, "X")
    link(ng, box_height, 0, back_size, "Y")
    link(ng, group_in, "Side Thickness", back_size, "Z")
    link(ng, back_size, "Vector", back, "Size")

    # Back Z position
    back_z = create_math(ng, 'SUBTRACT', name="Back Z", location=(-750, -500))
    back_z_offset = create_math(ng, 'DIVIDE', name="Back Z Offset", location=(-650, -500))
    link(ng, box_z_final, 0, back_z, 0)
    link(ng, box_depth, 0, back_z_offset, 0)
    set_default(back_z_offset, 1, 2.0)
    back_z_add = create_math(ng, 'ADD', name="Back Z Add", location=(-550, -500))
    link(ng, back_z, 0, back_z_add, 0)
    link(ng, group_in, "Side Thickness", back_z_add, 1)
    back_z_sub = create_math(ng, 'SUBTRACT', name="Back Z Sub", location=(-450, -500))
    link(ng, back_z_add, 0, back_z_sub, 0)
    link(ng, back_z_offset, 0, back_z_sub, 1)

    link(ng, box_y_neg, 0, back_pos, "Y")
    link(ng, back_z_sub, 0, back_pos, "Z")
    link(ng, back_pos, "Vector", back_transform, "Translation")
    link(ng, back, "Mesh", back_transform, "Geometry")

    # ============ BOTTOM ============
    bottom = create_cube(ng, name="Bottom", location=(-500, -500))
    bottom_size = create_combine_xyz(ng, name="Bottom Size", location=(-650, -450))
    bottom_pos = create_combine_xyz(ng, name="Bottom Pos", location=(-650, -550))
    bottom_transform = create_transform(ng, name="Bottom Transform", location=(-350, -500))

    # Bottom dimensions (inset from sides)
    bottom_width = create_math(ng, 'SUBTRACT', name="Bottom Width", location=(-750, -600))
    inset_x2 = create_math(ng, 'MULTIPLY', name="Inset x2", location=(-850, -600))
    link(ng, group_in, "Bottom Inset", inset_x2, 0)
    set_default(inset_x2, 1, 2.0)
    link(ng, interior_width, 0, bottom_width, 0)
    link(ng, inset_x2, 0, bottom_width, 1)

    bottom_depth = create_math(ng, 'SUBTRACT', name="Bottom Depth", location=(-750, -700))
    link(ng, box_depth, 0, bottom_depth, 0)
    link(ng, inset_x2, 0, bottom_depth, 1)

    link(ng, bottom_width, 0, bottom_size, "X")
    link(ng, group_in, "Bottom Thickness", bottom_size, "Y")
    link(ng, bottom_depth, 0, bottom_size, "Z")
    link(ng, bottom_size, "Vector", bottom, "Size")

    # Bottom Y position (at bottom of box)
    bottom_y = create_math(ng, 'SUBTRACT', name="Bottom Y", location=(-750, -800))
    bottom_y_div = create_math(ng, 'DIVIDE', name="Bottom Y Div", location=(-650, -800))
    link(ng, box_height, 0, bottom_y, 0)
    link(ng, group_in, "Bottom Thickness", bottom_y, 1)
    link(ng, bottom_y, 0, bottom_y_div, 0)
    set_default(bottom_y_div, 1, 2.0)
    bottom_y_neg = create_math(ng, 'MULTIPLY', name="Bottom Y Neg", location=(-550, -800))
    bottom_y_add = create_math(ng, 'ADD', name="Bottom Y Add", location=(-450, -800))
    link(ng, bottom_y_div, 0, bottom_y_neg, 0)
    set_default(bottom_y_neg, 1, -1.0)
    link(ng, box_y_neg, 0, bottom_y_add, 0)
    link(ng, bottom_y_neg, 0, bottom_y_add, 1)

    link(ng, bottom_y_add, 0, bottom_pos, "Y")
    link(ng, box_z_final, 0, bottom_pos, "Z")
    link(ng, bottom_pos, "Vector", bottom_transform, "Translation")
    link(ng, bottom, "Mesh", bottom_transform, "Geometry")

    # ============ JOIN BOX PARTS ============
    join_box = create_join_geometry(ng, name="Join Box", location=(-100, -200))
    link(ng, left_transform, "Geometry", join_box, "Geometry")
    link(ng, right_transform, "Geometry", join_box, "Geometry")
    link(ng, back_transform, "Geometry", join_box, "Geometry")
    link(ng, bottom_transform, "Geometry", join_box, "Geometry")

    # Set box material
    box_mat = create_set_material(ng, name="Box Material", location=(50, -200))
    link(ng, join_box, "Geometry", box_mat, "Geometry")
    link(ng, group_in, "Box Material", box_mat, "Material")

    # ============ SWITCH: Include Box ============
    switch_box = create_switch(ng, 'GEOMETRY', name="Include Box Switch", location=(200, 0))
    link(ng, group_in, "Include Box", switch_box, "Switch")

    # Join front + box when box is included
    join_all = create_join_geometry(ng, name="Join All", location=(350, -100))
    link(ng, front_mat, "Geometry", join_all, "Geometry")
    link(ng, box_mat, "Geometry", join_all, "Geometry")

    link(ng, front_mat, "Geometry", switch_box, "False")  # Front only
    link(ng, join_all, "Geometry", switch_box, "True")    # Front + Box

    # Output
    link(ng, switch_box, "Output", group_out, "Geometry")

    # Add metadata
    add_metadata(ng, version="1.0.0",
                 script_path="src/nodes/atomic/drawer.py")

    return ng


def create_test_object(drawer_nodegroup=None):
    """Create a test object with the Drawer node group applied."""
    if drawer_nodegroup is None:
        drawer_nodegroup = create_drawer_nodegroup()

    mesh = bpy.data.meshes.new("Drawer_Test")
    obj = bpy.data.objects.new("Drawer_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = drawer_nodegroup

    return obj


if __name__ == "__main__":
    ng = create_drawer_nodegroup()
    print(f"Created node group: {ng.name}")
