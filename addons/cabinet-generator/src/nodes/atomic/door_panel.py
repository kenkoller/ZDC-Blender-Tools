# Door panel node group generator
# Atomic component: Door panel with style variants (Flat, Shaker, Raised)

import bpy
from ..utils import (
    create_node_group,
    add_geometry_output,
    add_float_socket,
    add_int_socket,
    add_material_socket,
    create_panel,
    create_group_input,
    create_group_output,
    create_cube,
    create_math,
    create_combine_xyz,
    create_set_material,
    create_set_position,
    create_join_geometry,
    create_switch,
    create_transform,
    create_boolean_math,
    create_compare,
    link,
    set_default,
    add_metadata,
)


def create_door_panel_nodegroup():
    """Generate the DoorPanel node group.

    A door panel with selectable style variants:
    - Style 0: Flat (simple slab)
    - Style 1: Shaker (recessed center panel with frame)
    - Style 2: Raised (raised center panel with frame)
    - Style 3: Recessed Flat (flat with frame detail)
    - Style 4: Double Shaker (nested shaker frames)

    Inputs:
        Width (float): Door width
        Height (float): Door height
        Thickness (float): Door thickness
        Style (int): 0=Flat, 1=Shaker, 2=Raised, 3=Recessed, 4=Double Shaker
        Frame Width (float): Width of frame border (Shaker/Raised)
        Panel Inset (float): How much center panel is recessed/raised
        Material (material): Optional material assignment

    Outputs:
        Geometry: The door panel mesh

    Returns:
        The created node group
    """
    ng = create_node_group("DoorPanel")

    # Create interface panels for organization
    dims_panel = create_panel(ng, "Dimensions")
    style_panel = create_panel(ng, "Style")

    # Add interface sockets
    add_float_socket(ng, "Width", default=0.4, min_val=0.1, max_val=1.5,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.6, min_val=0.1, max_val=2.5,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Thickness", default=0.018, min_val=0.01, max_val=0.05,
                     subtype='DISTANCE', panel=dims_panel)

    add_int_socket(ng, "Style", default=1, min_val=0, max_val=4, panel=style_panel)
    add_float_socket(ng, "Frame Width", default=0.05, min_val=0.02, max_val=0.15,
                     subtype='DISTANCE', panel=style_panel)
    add_float_socket(ng, "Panel Inset", default=0.006, min_val=0.0, max_val=0.02,
                     subtype='DISTANCE', panel=style_panel)

    add_material_socket(ng, "Material")
    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ FLAT STYLE (Style 0) ============
    # Simple cube sized to width x height x thickness
    flat_cube = create_cube(ng, name="Flat Panel", location=(-400, 300))
    flat_size = create_combine_xyz(ng, name="Flat Size", location=(-550, 300))

    link(ng, group_in, "Width", flat_size, "X")
    link(ng, group_in, "Height", flat_size, "Y")
    link(ng, group_in, "Thickness", flat_size, "Z")
    link(ng, flat_size, "Vector", flat_cube, "Size")

    # ============ SHAKER STYLE (Style 1) ============
    # Frame (outer border) + recessed center panel

    # Frame dimensions: full size but we'll boolean subtract the center
    # For simplicity, build frame from 4 pieces + center panel

    # Top rail
    shaker_top = create_cube(ng, name="Shaker Top Rail", location=(-400, 0))
    shaker_top_size = create_combine_xyz(ng, name="Top Rail Size", location=(-550, 50))
    shaker_top_pos = create_combine_xyz(ng, name="Top Rail Pos", location=(-550, -50))
    shaker_top_transform = create_transform(ng, name="Top Rail Transform", location=(-250, 0))

    # Top rail: width = full width, height = frame width, thickness = full
    link(ng, group_in, "Width", shaker_top_size, "X")
    link(ng, group_in, "Frame Width", shaker_top_size, "Y")
    link(ng, group_in, "Thickness", shaker_top_size, "Z")
    link(ng, shaker_top_size, "Vector", shaker_top, "Size")

    # Position: Y = (height - frame_width) / 2
    top_y_math = create_math(ng, 'SUBTRACT', name="Top Y Sub", location=(-700, -100))
    top_y_div = create_math(ng, 'DIVIDE', name="Top Y Div", location=(-600, -100))
    link(ng, group_in, "Height", top_y_math, 0)
    link(ng, group_in, "Frame Width", top_y_math, 1)
    link(ng, top_y_math, 0, top_y_div, 0)
    set_default(top_y_div, 1, 2.0)
    link(ng, top_y_div, 0, shaker_top_pos, "Y")
    link(ng, shaker_top_pos, "Vector", shaker_top_transform, "Translation")
    link(ng, shaker_top, "Mesh", shaker_top_transform, "Geometry")

    # Bottom rail (mirror of top)
    shaker_bottom = create_cube(ng, name="Shaker Bottom Rail", location=(-400, -200))
    shaker_bottom_size = create_combine_xyz(ng, name="Bottom Rail Size", location=(-550, -150))
    shaker_bottom_pos = create_combine_xyz(ng, name="Bottom Rail Pos", location=(-550, -250))
    shaker_bottom_transform = create_transform(ng, name="Bottom Rail Transform", location=(-250, -200))

    link(ng, group_in, "Width", shaker_bottom_size, "X")
    link(ng, group_in, "Frame Width", shaker_bottom_size, "Y")
    link(ng, group_in, "Thickness", shaker_bottom_size, "Z")
    link(ng, shaker_bottom_size, "Vector", shaker_bottom, "Size")

    # Position: Y = -(height - frame_width) / 2
    bottom_y_neg = create_math(ng, 'MULTIPLY', name="Bottom Y Neg", location=(-500, -300))
    link(ng, top_y_div, 0, bottom_y_neg, 0)
    set_default(bottom_y_neg, 1, -1.0)
    link(ng, bottom_y_neg, 0, shaker_bottom_pos, "Y")
    link(ng, shaker_bottom_pos, "Vector", shaker_bottom_transform, "Translation")
    link(ng, shaker_bottom, "Mesh", shaker_bottom_transform, "Geometry")

    # Left stile
    shaker_left = create_cube(ng, name="Shaker Left Stile", location=(-400, -400))
    shaker_left_size = create_combine_xyz(ng, name="Left Stile Size", location=(-550, -350))
    shaker_left_pos = create_combine_xyz(ng, name="Left Stile Pos", location=(-550, -450))
    shaker_left_transform = create_transform(ng, name="Left Stile Transform", location=(-250, -400))

    # Left stile: width = frame_width, height = height - 2*frame_width
    inner_height = create_math(ng, 'SUBTRACT', name="Inner Height", location=(-700, -400))
    frame_x2 = create_math(ng, 'MULTIPLY', name="Frame x2", location=(-800, -400))
    link(ng, group_in, "Frame Width", frame_x2, 0)
    set_default(frame_x2, 1, 2.0)
    link(ng, group_in, "Height", inner_height, 0)
    link(ng, frame_x2, 0, inner_height, 1)

    link(ng, group_in, "Frame Width", shaker_left_size, "X")
    link(ng, inner_height, 0, shaker_left_size, "Y")
    link(ng, group_in, "Thickness", shaker_left_size, "Z")
    link(ng, shaker_left_size, "Vector", shaker_left, "Size")

    # Position: X = -(width - frame_width) / 2
    left_x_sub = create_math(ng, 'SUBTRACT', name="Left X Sub", location=(-700, -500))
    left_x_div = create_math(ng, 'DIVIDE', name="Left X Div", location=(-600, -500))
    left_x_neg = create_math(ng, 'MULTIPLY', name="Left X Neg", location=(-500, -500))
    link(ng, group_in, "Width", left_x_sub, 0)
    link(ng, group_in, "Frame Width", left_x_sub, 1)
    link(ng, left_x_sub, 0, left_x_div, 0)
    set_default(left_x_div, 1, 2.0)
    link(ng, left_x_div, 0, left_x_neg, 0)
    set_default(left_x_neg, 1, -1.0)
    link(ng, left_x_neg, 0, shaker_left_pos, "X")
    link(ng, shaker_left_pos, "Vector", shaker_left_transform, "Translation")
    link(ng, shaker_left, "Mesh", shaker_left_transform, "Geometry")

    # Right stile (mirror of left)
    shaker_right = create_cube(ng, name="Shaker Right Stile", location=(-400, -600))
    shaker_right_size = create_combine_xyz(ng, name="Right Stile Size", location=(-550, -550))
    shaker_right_pos = create_combine_xyz(ng, name="Right Stile Pos", location=(-550, -650))
    shaker_right_transform = create_transform(ng, name="Right Stile Transform", location=(-250, -600))

    link(ng, group_in, "Frame Width", shaker_right_size, "X")
    link(ng, inner_height, 0, shaker_right_size, "Y")
    link(ng, group_in, "Thickness", shaker_right_size, "Z")
    link(ng, shaker_right_size, "Vector", shaker_right, "Size")

    link(ng, left_x_div, 0, shaker_right_pos, "X")  # Positive X (no negation)
    link(ng, shaker_right_pos, "Vector", shaker_right_transform, "Translation")
    link(ng, shaker_right, "Mesh", shaker_right_transform, "Geometry")

    # Center panel (recessed for Shaker)
    shaker_center = create_cube(ng, name="Shaker Center", location=(-400, -800))
    shaker_center_size = create_combine_xyz(ng, name="Center Size", location=(-550, -750))
    shaker_center_pos = create_combine_xyz(ng, name="Center Pos", location=(-550, -850))
    shaker_center_transform = create_transform(ng, name="Center Transform", location=(-250, -800))

    # Center: width = width - 2*frame, height = height - 2*frame, thickness = thickness - inset
    inner_width = create_math(ng, 'SUBTRACT', name="Inner Width", location=(-700, -750))
    link(ng, group_in, "Width", inner_width, 0)
    link(ng, frame_x2, 0, inner_width, 1)

    center_thick = create_math(ng, 'SUBTRACT', name="Center Thick", location=(-700, -850))
    link(ng, group_in, "Thickness", center_thick, 0)
    link(ng, group_in, "Panel Inset", center_thick, 1)

    link(ng, inner_width, 0, shaker_center_size, "X")
    link(ng, inner_height, 0, shaker_center_size, "Y")
    link(ng, center_thick, 0, shaker_center_size, "Z")
    link(ng, shaker_center_size, "Vector", shaker_center, "Size")

    # Center position: Z = -inset/2 (recessed back)
    center_z = create_math(ng, 'DIVIDE', name="Center Z", location=(-700, -900))
    center_z_neg = create_math(ng, 'MULTIPLY', name="Center Z Neg", location=(-600, -900))
    link(ng, group_in, "Panel Inset", center_z, 0)
    set_default(center_z, 1, 2.0)
    link(ng, center_z, 0, center_z_neg, 0)
    set_default(center_z_neg, 1, -1.0)
    link(ng, center_z_neg, 0, shaker_center_pos, "Z")
    link(ng, shaker_center_pos, "Vector", shaker_center_transform, "Translation")
    link(ng, shaker_center, "Mesh", shaker_center_transform, "Geometry")

    # Join all shaker pieces
    shaker_join = create_join_geometry(ng, name="Join Shaker", location=(0, -300))
    link(ng, shaker_top_transform, "Geometry", shaker_join, "Geometry")
    link(ng, shaker_bottom_transform, "Geometry", shaker_join, "Geometry")
    link(ng, shaker_left_transform, "Geometry", shaker_join, "Geometry")
    link(ng, shaker_right_transform, "Geometry", shaker_join, "Geometry")
    link(ng, shaker_center_transform, "Geometry", shaker_join, "Geometry")

    # ============ RAISED STYLE (Style 2) ============
    # Same as shaker but center panel is raised (positive Z offset)
    raised_center = create_cube(ng, name="Raised Center", location=(-400, -1000))
    raised_center_size = create_combine_xyz(ng, name="Raised Center Size", location=(-550, -950))
    raised_center_pos = create_combine_xyz(ng, name="Raised Center Pos", location=(-550, -1050))
    raised_center_transform = create_transform(ng, name="Raised Center Transform", location=(-250, -1000))

    # Same dimensions as shaker center
    link(ng, inner_width, 0, raised_center_size, "X")
    link(ng, inner_height, 0, raised_center_size, "Y")
    link(ng, center_thick, 0, raised_center_size, "Z")
    link(ng, raised_center_size, "Vector", raised_center, "Size")

    # Position: Z = +inset/2 (raised forward)
    link(ng, center_z, 0, raised_center_pos, "Z")  # Positive (no negation)
    link(ng, raised_center_pos, "Vector", raised_center_transform, "Translation")
    link(ng, raised_center, "Mesh", raised_center_transform, "Geometry")

    # Join raised style (frame + raised center)
    raised_join = create_join_geometry(ng, name="Join Raised", location=(0, -600))
    link(ng, shaker_top_transform, "Geometry", raised_join, "Geometry")
    link(ng, shaker_bottom_transform, "Geometry", raised_join, "Geometry")
    link(ng, shaker_left_transform, "Geometry", raised_join, "Geometry")
    link(ng, shaker_right_transform, "Geometry", raised_join, "Geometry")
    link(ng, raised_center_transform, "Geometry", raised_join, "Geometry")

    # ============ RECESSED FLAT (Style 3) ============
    # Flat panel with recessed edge detail (like a picture frame)
    recessed_outer = create_cube(ng, name="Recessed Outer", location=(-400, -1200))
    recessed_inner = create_cube(ng, name="Recessed Inner", location=(-400, -1350))
    recessed_outer_size = create_combine_xyz(ng, name="Recessed Outer Size", location=(-550, -1150))
    recessed_inner_size = create_combine_xyz(ng, name="Recessed Inner Size", location=(-550, -1300))
    recessed_inner_pos = create_combine_xyz(ng, name="Recessed Inner Pos", location=(-550, -1400))
    recessed_inner_transform = create_transform(ng, name="Recessed Inner Transform", location=(-250, -1350))

    # Outer layer: full size, thinner
    outer_thick = create_math(ng, 'MULTIPLY', name="Outer Thick", location=(-700, -1200))
    link(ng, group_in, "Thickness", outer_thick, 0)
    set_default(outer_thick, 1, 0.3)

    link(ng, group_in, "Width", recessed_outer_size, "X")
    link(ng, group_in, "Height", recessed_outer_size, "Y")
    link(ng, outer_thick, 0, recessed_outer_size, "Z")
    link(ng, recessed_outer_size, "Vector", recessed_outer, "Size")

    # Inner layer: smaller, full thickness, raised
    inner_inset = create_math(ng, 'MULTIPLY', name="Inner Inset", location=(-700, -1300))
    link(ng, group_in, "Frame Width", inner_inset, 0)
    set_default(inner_inset, 1, 1.5)

    inner_inset_x2 = create_math(ng, 'MULTIPLY', name="Inner Inset x2", location=(-600, -1300))
    link(ng, inner_inset, 0, inner_inset_x2, 0)
    set_default(inner_inset_x2, 1, 2.0)

    recessed_w = create_math(ng, 'SUBTRACT', name="Recessed W", location=(-500, -1250))
    link(ng, group_in, "Width", recessed_w, 0)
    link(ng, inner_inset_x2, 0, recessed_w, 1)

    recessed_h = create_math(ng, 'SUBTRACT', name="Recessed H", location=(-500, -1300))
    link(ng, group_in, "Height", recessed_h, 0)
    link(ng, inner_inset_x2, 0, recessed_h, 1)

    link(ng, recessed_w, 0, recessed_inner_size, "X")
    link(ng, recessed_h, 0, recessed_inner_size, "Y")
    link(ng, group_in, "Thickness", recessed_inner_size, "Z")
    link(ng, recessed_inner_size, "Vector", recessed_inner, "Size")

    # Inner Z position
    inner_z = create_math(ng, 'SUBTRACT', name="Inner Z", location=(-550, -1450))
    thick_half = create_math(ng, 'DIVIDE', name="Thick Half", location=(-650, -1450))
    link(ng, group_in, "Thickness", thick_half, 0)
    set_default(thick_half, 1, 2.0)
    link(ng, thick_half, 0, inner_z, 0)
    outer_half = create_math(ng, 'DIVIDE', name="Outer Half", location=(-650, -1500))
    link(ng, outer_thick, 0, outer_half, 0)
    set_default(outer_half, 1, 2.0)
    link(ng, outer_half, 0, inner_z, 1)

    link(ng, inner_z, 0, recessed_inner_pos, "Z")
    link(ng, recessed_inner_pos, "Vector", recessed_inner_transform, "Translation")
    link(ng, recessed_inner, "Mesh", recessed_inner_transform, "Geometry")

    recessed_join = create_join_geometry(ng, name="Join Recessed", location=(0, -1300))
    link(ng, recessed_outer, "Mesh", recessed_join, "Geometry")
    link(ng, recessed_inner_transform, "Geometry", recessed_join, "Geometry")

    # ============ DOUBLE SHAKER (Style 4) ============
    # Shaker with additional inner frame detail
    # Use shaker frame + a smaller inner shaker frame
    double_inner_frame = create_math(ng, 'MULTIPLY', name="Double Inner Frame", location=(-700, -1600))
    link(ng, group_in, "Frame Width", double_inner_frame, 0)
    set_default(double_inner_frame, 1, 0.6)

    double_center_w = create_math(ng, 'SUBTRACT', name="Double Center W", location=(-500, -1600))
    double_frame_total = create_math(ng, 'MULTIPLY', name="Double Frame Total", location=(-600, -1600))
    link(ng, group_in, "Frame Width", double_frame_total, 0)
    # Calculate: inner_width - 2*double_inner_frame
    double_inset_x2 = create_math(ng, 'MULTIPLY', name="Double Inset x2", location=(-600, -1650))
    link(ng, double_inner_frame, 0, double_inset_x2, 0)
    set_default(double_inset_x2, 1, 2.0)

    link(ng, inner_width, 0, double_center_w, 0)
    link(ng, double_inset_x2, 0, double_center_w, 1)

    double_center_h = create_math(ng, 'SUBTRACT', name="Double Center H", location=(-500, -1700))
    link(ng, inner_height, 0, double_center_h, 0)
    link(ng, double_inset_x2, 0, double_center_h, 1)

    double_center = create_cube(ng, name="Double Center", location=(-400, -1700))
    double_center_size = create_combine_xyz(ng, name="Double Center Size", location=(-550, -1650))
    double_center_pos = create_combine_xyz(ng, name="Double Center Pos", location=(-550, -1750))
    double_center_transform = create_transform(ng, name="Double Center Transform", location=(-250, -1700))

    # Double center thickness is less (more recessed)
    double_thick = create_math(ng, 'SUBTRACT', name="Double Thick", location=(-700, -1700))
    inset_x2 = create_math(ng, 'MULTIPLY', name="Inset x2", location=(-800, -1700))
    link(ng, group_in, "Panel Inset", inset_x2, 0)
    set_default(inset_x2, 1, 2.0)
    link(ng, group_in, "Thickness", double_thick, 0)
    link(ng, inset_x2, 0, double_thick, 1)

    link(ng, double_center_w, 0, double_center_size, "X")
    link(ng, double_center_h, 0, double_center_size, "Y")
    link(ng, double_thick, 0, double_center_size, "Z")
    link(ng, double_center_size, "Vector", double_center, "Size")

    # Position Z same as shaker center (recessed)
    link(ng, center_z_neg, 0, double_center_pos, "Z")
    link(ng, double_center_pos, "Vector", double_center_transform, "Translation")
    link(ng, double_center, "Mesh", double_center_transform, "Geometry")

    double_join = create_join_geometry(ng, name="Join Double", location=(0, -1600))
    link(ng, shaker_top_transform, "Geometry", double_join, "Geometry")
    link(ng, shaker_bottom_transform, "Geometry", double_join, "Geometry")
    link(ng, shaker_left_transform, "Geometry", double_join, "Geometry")
    link(ng, shaker_right_transform, "Geometry", double_join, "Geometry")
    link(ng, shaker_center_transform, "Geometry", double_join, "Geometry")
    link(ng, double_center_transform, "Geometry", double_join, "Geometry")

    # ============ STYLE SWITCHING ============
    # Switch between Flat (0), Shaker (1), Raised (2), Recessed (3), Double (4)

    # Compare: Style == 0 (Flat)
    is_flat = create_compare(ng, 'EQUAL', 'INT', name="Is Flat", location=(200, 300))
    link(ng, group_in, "Style", is_flat, 2)
    set_default(is_flat, 3, 0)

    # Compare: Style == 1 (Shaker)
    is_shaker = create_compare(ng, 'EQUAL', 'INT', name="Is Shaker", location=(200, 200))
    link(ng, group_in, "Style", is_shaker, 2)
    set_default(is_shaker, 3, 1)

    # Compare: Style == 2 (Raised)
    is_raised = create_compare(ng, 'EQUAL', 'INT', name="Is Raised", location=(200, 100))
    link(ng, group_in, "Style", is_raised, 2)
    set_default(is_raised, 3, 2)

    # Compare: Style == 3 (Recessed)
    is_recessed = create_compare(ng, 'EQUAL', 'INT', name="Is Recessed", location=(200, 0))
    link(ng, group_in, "Style", is_recessed, 2)
    set_default(is_recessed, 3, 3)

    # Compare: Style == 4 (Double) - default

    # Cascade switches
    # Recessed vs Double
    switch_rec_double = create_switch(ng, 'GEOMETRY', name="Rec/Double", location=(350, -100))
    link(ng, is_recessed, "Result", switch_rec_double, "Switch")
    link(ng, double_join, "Geometry", switch_rec_double, "False")
    link(ng, recessed_join, "Geometry", switch_rec_double, "True")

    # Raised vs (Recessed/Double)
    switch_raised = create_switch(ng, 'GEOMETRY', name="Raised Switch", location=(400, 0))
    link(ng, is_raised, "Result", switch_raised, "Switch")
    link(ng, switch_rec_double, "Output", switch_raised, "False")
    link(ng, raised_join, "Geometry", switch_raised, "True")

    # Shaker vs (Raised/Recessed/Double)
    switch_shaker = create_switch(ng, 'GEOMETRY', name="Shaker Switch", location=(450, 100))
    link(ng, is_shaker, "Result", switch_shaker, "Switch")
    link(ng, switch_raised, "Output", switch_shaker, "False")
    link(ng, shaker_join, "Geometry", switch_shaker, "True")

    # Flat vs (Shaker/Raised/Recessed/Double)
    switch_flat = create_switch(ng, 'GEOMETRY', name="Style Switch", location=(500, 200))
    link(ng, is_flat, "Result", switch_flat, "Switch")
    link(ng, switch_shaker, "Output", switch_flat, "False")
    link(ng, flat_cube, "Mesh", switch_flat, "True")

    # Set material
    set_mat = create_set_material(ng, name="Set Material", location=(650, 0))
    link(ng, switch_flat, "Output", set_mat, "Geometry")
    link(ng, group_in, "Material", set_mat, "Material")

    # Output
    link(ng, set_mat, "Geometry", group_out, "Geometry")

    # Add metadata
    add_metadata(ng, version="1.1.0",
                 script_path="src/nodes/atomic/door_panel.py")

    return ng


def create_test_object(door_nodegroup=None):
    """Create a test object with the DoorPanel node group applied."""
    if door_nodegroup is None:
        door_nodegroup = create_door_panel_nodegroup()

    mesh = bpy.data.meshes.new("DoorPanel_Test")
    obj = bpy.data.objects.new("DoorPanel_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = door_nodegroup

    return obj


if __name__ == "__main__":
    ng = create_door_panel_nodegroup()
    print(f"Created node group: {ng.name}")
