# Toe kick node group generator
# Atomic component: Recessed base for floor-standing cabinets

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


def create_toe_kick_nodegroup():
    """Generate the ToeKick node group.

    Creates a recessed toe kick base for floor-standing cabinets.
    The toe kick consists of:
    - Front panel (the visible recessed face)
    - Left/right side panels (returns to the cabinet sides)
    - Optional end caps for exposed sides

    Standard toe kick dimensions:
    - Height: 100-150mm (4-6 inches)
    - Depth: 50-75mm (2-3 inches) recessed from cabinet front

    Coordinate system:
    - X = width (matches cabinet width)
    - Y = depth (extends back from front face)
    - Z = height (from floor)
    - Origin at front-bottom-center

    Inputs:
        Width (float): Cabinet width (exterior)
        Height (float): Toe kick height (typically 100-150mm)
        Depth (float): Toe kick recess depth from front
        Cabinet Depth (float): Full cabinet depth
        Panel Thickness (float): Thickness of toe kick panels
        Left End Cap (bool): Include left end panel
        Right End Cap (bool): Include right end panel
        Material (material): Optional material assignment

    Outputs:
        Geometry: The toe kick mesh

    Returns:
        The created node group
    """
    ng = create_node_group("ToeKick")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    options_panel = create_panel(ng, "Options")

    # Dimension inputs
    add_float_socket(ng, "Width", default=0.6, min_val=0.2, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.1, min_val=0.05, max_val=0.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.06, min_val=0.03, max_val=0.1,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Cabinet Depth", default=0.55, min_val=0.3, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Options
    add_bool_socket(ng, "Left End Cap", default=False, panel=options_panel)
    add_bool_socket(ng, "Right End Cap", default=False, panel=options_panel)

    # Material
    add_material_socket(ng, "Material")

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ FRONT PANEL ============
    # The visible recessed front face
    front = create_cube(ng, name="Front Panel", location=(-400, 300))
    front_size = create_combine_xyz(ng, name="Front Size", location=(-550, 350))
    front_pos = create_combine_xyz(ng, name="Front Pos", location=(-550, 250))
    front_transform = create_transform(ng, name="Front Transform", location=(-250, 300))

    # Front width = cabinet width - 2*panel_thickness (fits between sides)
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-700, 200))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)

    front_width = create_math(ng, 'SUBTRACT', name="Front Width", location=(-600, 300))
    link(ng, group_in, "Width", front_width, 0)
    link(ng, panel_x2, 0, front_width, 1)

    link(ng, front_width, 0, front_size, "X")
    link(ng, group_in, "Panel Thickness", front_size, "Y")
    link(ng, group_in, "Height", front_size, "Z")
    link(ng, front_size, "Vector", front, "Size")

    # Front Y position = -depth + panel_thickness/2 (recessed from front)
    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-700, 100))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)

    front_y = create_math(ng, 'SUBTRACT', name="Front Y", location=(-600, 100))
    link(ng, panel_half, 0, front_y, 0)
    link(ng, group_in, "Depth", front_y, 1)

    # Front Z position = height/2 (bottom at Z=0)
    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-700, 0))
    link(ng, group_in, "Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    link(ng, front_y, 0, front_pos, "Y")
    link(ng, height_half, 0, front_pos, "Z")
    link(ng, front_pos, "Vector", front_transform, "Translation")
    link(ng, front, "Mesh", front_transform, "Geometry")

    # ============ LEFT SIDE PANEL (return) ============
    left_side = create_cube(ng, name="Left Side", location=(-400, 0))
    left_size = create_combine_xyz(ng, name="Left Size", location=(-550, 50))
    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-550, -50))
    left_transform = create_transform(ng, name="Left Transform", location=(-250, 0))

    # Side depth = toe kick depth - panel_thickness (connects to front)
    side_depth = create_math(ng, 'SUBTRACT', name="Side Depth", location=(-700, -100))
    link(ng, group_in, "Depth", side_depth, 0)
    link(ng, group_in, "Panel Thickness", side_depth, 1)

    link(ng, group_in, "Panel Thickness", left_size, "X")
    link(ng, side_depth, 0, left_size, "Y")
    link(ng, group_in, "Height", left_size, "Z")
    link(ng, left_size, "Vector", left_side, "Size")

    # Left X position = -(width - panel_thickness) / 2
    left_x_sub = create_math(ng, 'SUBTRACT', name="Left X Sub", location=(-700, -200))
    link(ng, group_in, "Width", left_x_sub, 0)
    link(ng, group_in, "Panel Thickness", left_x_sub, 1)

    left_x = create_math(ng, 'DIVIDE', name="Left X Div", location=(-600, -200))
    link(ng, left_x_sub, 0, left_x, 0)
    set_default(left_x, 1, -2.0)

    # Left Y position = -(depth - panel_thickness) / 2 - panel_thickness (behind front panel)
    side_y = create_math(ng, 'DIVIDE', name="Side Y", location=(-600, -300))
    link(ng, side_depth, 0, side_y, 0)
    set_default(side_y, 1, -2.0)

    link(ng, left_x, 0, left_pos, "X")
    link(ng, side_y, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")
    link(ng, left_pos, "Vector", left_transform, "Translation")
    link(ng, left_side, "Mesh", left_transform, "Geometry")

    # ============ RIGHT SIDE PANEL (return) ============
    right_side = create_cube(ng, name="Right Side", location=(-400, -200))
    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-550, -250))
    right_transform = create_transform(ng, name="Right Transform", location=(-250, -200))

    # Right X = positive version of left X
    right_x = create_math(ng, 'MULTIPLY', name="Right X", location=(-600, -400))
    link(ng, left_x, 0, right_x, 0)
    set_default(right_x, 1, -1.0)

    link(ng, left_size, "Vector", right_side, "Size")
    link(ng, right_x, 0, right_pos, "X")
    link(ng, side_y, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")
    link(ng, right_pos, "Vector", right_transform, "Translation")
    link(ng, right_side, "Mesh", right_transform, "Geometry")

    # ============ LEFT END CAP (optional) ============
    left_cap = create_cube(ng, name="Left Cap", location=(-400, -400))
    left_cap_size = create_combine_xyz(ng, name="L Cap Size", location=(-550, -350))
    left_cap_pos = create_combine_xyz(ng, name="L Cap Pos", location=(-550, -450))
    left_cap_transform = create_transform(ng, name="L Cap Transform", location=(-250, -400))

    # Cap extends from toe kick back to cabinet back
    cap_depth = create_math(ng, 'SUBTRACT', name="Cap Depth", location=(-700, -500))
    link(ng, group_in, "Cabinet Depth", cap_depth, 0)
    link(ng, group_in, "Depth", cap_depth, 1)

    link(ng, group_in, "Panel Thickness", left_cap_size, "X")
    link(ng, cap_depth, 0, left_cap_size, "Y")
    link(ng, group_in, "Height", left_cap_size, "Z")
    link(ng, left_cap_size, "Vector", left_cap, "Size")

    # Cap Y position
    cap_y_base = create_math(ng, 'DIVIDE', name="Cap Y Base", location=(-700, -600))
    link(ng, cap_depth, 0, cap_y_base, 0)
    set_default(cap_y_base, 1, 2.0)

    cap_y = create_math(ng, 'SUBTRACT', name="Cap Y", location=(-600, -600))
    link(ng, group_in, "Depth", cap_y, 0)
    link(ng, cap_y_base, 0, cap_y, 1)

    cap_y_neg = create_math(ng, 'MULTIPLY', name="Cap Y Neg", location=(-500, -600))
    link(ng, cap_y, 0, cap_y_neg, 0)
    set_default(cap_y_neg, 1, -1.0)

    link(ng, left_x, 0, left_cap_pos, "X")
    link(ng, cap_y_neg, 0, left_cap_pos, "Y")
    link(ng, height_half, 0, left_cap_pos, "Z")
    link(ng, left_cap_pos, "Vector", left_cap_transform, "Translation")
    link(ng, left_cap, "Mesh", left_cap_transform, "Geometry")

    # ============ RIGHT END CAP (optional) ============
    right_cap = create_cube(ng, name="Right Cap", location=(-400, -600))
    right_cap_pos = create_combine_xyz(ng, name="R Cap Pos", location=(-550, -650))
    right_cap_transform = create_transform(ng, name="R Cap Transform", location=(-250, -600))

    link(ng, left_cap_size, "Vector", right_cap, "Size")
    link(ng, right_x, 0, right_cap_pos, "X")
    link(ng, cap_y_neg, 0, right_cap_pos, "Y")
    link(ng, height_half, 0, right_cap_pos, "Z")
    link(ng, right_cap_pos, "Vector", right_cap_transform, "Translation")
    link(ng, right_cap, "Mesh", right_cap_transform, "Geometry")

    # ============ JOIN BASE COMPONENTS ============
    join_base = create_join_geometry(ng, name="Join Base", location=(0, 100))
    link(ng, front_transform, "Geometry", join_base, "Geometry")
    link(ng, left_transform, "Geometry", join_base, "Geometry")
    link(ng, right_transform, "Geometry", join_base, "Geometry")

    # ============ SWITCHES FOR END CAPS ============
    switch_left_cap = create_switch(ng, 'GEOMETRY', name="Left Cap Switch", location=(0, -400))
    link(ng, group_in, "Left End Cap", switch_left_cap, "Switch")
    link(ng, left_cap_transform, "Geometry", switch_left_cap, "True")

    switch_right_cap = create_switch(ng, 'GEOMETRY', name="Right Cap Switch", location=(0, -600))
    link(ng, group_in, "Right End Cap", switch_right_cap, "Switch")
    link(ng, right_cap_transform, "Geometry", switch_right_cap, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(200, 0))
    link(ng, join_base, "Geometry", join_all, "Geometry")
    link(ng, switch_left_cap, "Output", join_all, "Geometry")
    link(ng, switch_right_cap, "Output", join_all, "Geometry")

    # Set material
    set_mat = create_set_material(ng, name="Set Material", location=(400, 0))
    link(ng, join_all, "Geometry", set_mat, "Geometry")
    link(ng, group_in, "Material", set_mat, "Material")

    # Output
    link(ng, set_mat, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/toe_kick.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the ToeKick node group applied."""
    if nodegroup is None:
        nodegroup = create_toe_kick_nodegroup()

    mesh = bpy.data.meshes.new("ToeKick_Test")
    obj = bpy.data.objects.new("ToeKick_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_toe_kick_nodegroup()
    print(f"Created node group: {ng.name}")
