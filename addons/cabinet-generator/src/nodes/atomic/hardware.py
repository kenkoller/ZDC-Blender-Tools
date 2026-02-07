# Hardware node group generator
# Atomic component: Handles, knobs, and pulls

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
    create_transform,
    create_join_geometry,
    create_switch,
    create_compare,
    link,
    set_default,
    add_metadata,
)


def create_handle_nodegroup():
    """Generate the Handle node group.

    A cabinet handle/pull with selectable styles:
    - Style 0: Bar Pull (simple rectangular bar)
    - Style 1: Wire Pull (thin wire-style handle)
    - Style 2: Knob (single point knob)
    - Style 3: Cup Pull (bin-style pull)
    - Style 4: Edge Pull (modern edge grip)

    Inputs:
        Length (float): Handle length (for bar/wire)
        Width (float): Handle width/diameter
        Projection (float): How far handle projects from surface
        Post Spacing (float): Distance between mounting posts
        Post Diameter (float): Diameter of mounting posts
        Style (int): 0=Bar, 1=Wire, 2=Knob, 3=Cup, 4=Edge
        Material (material): Handle material

    Outputs:
        Geometry: The handle mesh

    Returns:
        The created node group
    """
    ng = create_node_group("Handle")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    style_panel = create_panel(ng, "Style")

    # Dimension sockets
    add_float_socket(ng, "Length", default=0.128, min_val=0.05, max_val=0.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Width", default=0.012, min_val=0.006, max_val=0.03,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Projection", default=0.03, min_val=0.015, max_val=0.06,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Post Spacing", default=0.096, min_val=0.05, max_val=0.3,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Post Diameter", default=0.008, min_val=0.004, max_val=0.015,
                     subtype='DISTANCE', panel=dims_panel)

    # Style
    add_int_socket(ng, "Style", default=0, min_val=0, max_val=4, panel=style_panel)

    # Material
    add_material_socket(ng, "Material")

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(700, 0))

    # ============ BAR PULL (Style 0) ============
    # Horizontal bar with two vertical posts

    # Bar (horizontal grip)
    bar = create_cube(ng, name="Bar Grip", location=(-400, 300))
    bar_size = create_combine_xyz(ng, name="Bar Size", location=(-550, 350))
    bar_pos = create_combine_xyz(ng, name="Bar Pos", location=(-550, 250))
    bar_transform = create_transform(ng, name="Bar Transform", location=(-250, 300))

    link(ng, group_in, "Length", bar_size, "X")
    link(ng, group_in, "Width", bar_size, "Y")
    link(ng, group_in, "Width", bar_size, "Z")
    link(ng, bar_size, "Vector", bar, "Size")

    # Bar Z position = projection - width/2
    bar_z = create_math(ng, 'SUBTRACT', name="Bar Z", location=(-650, 200))
    width_half = create_math(ng, 'DIVIDE', name="Width Half", location=(-750, 200))
    link(ng, group_in, "Width", width_half, 0)
    set_default(width_half, 1, 2.0)
    link(ng, group_in, "Projection", bar_z, 0)
    link(ng, width_half, 0, bar_z, 1)
    link(ng, bar_z, 0, bar_pos, "Z")
    link(ng, bar_pos, "Vector", bar_transform, "Translation")
    link(ng, bar, "Mesh", bar_transform, "Geometry")

    # Left post
    left_post = create_cube(ng, name="Left Post", location=(-400, 100))
    post_size = create_combine_xyz(ng, name="Post Size", location=(-550, 150))
    left_post_pos = create_combine_xyz(ng, name="Left Post Pos", location=(-550, 50))
    left_post_transform = create_transform(ng, name="Left Post Transform", location=(-250, 100))

    link(ng, group_in, "Post Diameter", post_size, "X")
    link(ng, group_in, "Post Diameter", post_size, "Y")
    link(ng, group_in, "Projection", post_size, "Z")
    link(ng, post_size, "Vector", left_post, "Size")

    # Left post X = -post_spacing/2
    post_x = create_math(ng, 'DIVIDE', name="Post X", location=(-650, 0))
    post_x_neg = create_math(ng, 'MULTIPLY', name="Post X Neg", location=(-550, 0))
    link(ng, group_in, "Post Spacing", post_x, 0)
    set_default(post_x, 1, 2.0)
    link(ng, post_x, 0, post_x_neg, 0)
    set_default(post_x_neg, 1, -1.0)
    link(ng, post_x_neg, 0, left_post_pos, "X")

    # Post Z = projection/2
    post_z = create_math(ng, 'DIVIDE', name="Post Z", location=(-650, -100))
    link(ng, group_in, "Projection", post_z, 0)
    set_default(post_z, 1, 2.0)
    link(ng, post_z, 0, left_post_pos, "Z")

    link(ng, left_post_pos, "Vector", left_post_transform, "Translation")
    link(ng, left_post, "Mesh", left_post_transform, "Geometry")

    # Right post
    right_post = create_cube(ng, name="Right Post", location=(-400, -100))
    right_post_pos = create_combine_xyz(ng, name="Right Post Pos", location=(-550, -150))
    right_post_transform = create_transform(ng, name="Right Post Transform", location=(-250, -100))

    link(ng, post_size, "Vector", right_post, "Size")
    link(ng, post_x, 0, right_post_pos, "X")  # Positive X
    link(ng, post_z, 0, right_post_pos, "Z")
    link(ng, right_post_pos, "Vector", right_post_transform, "Translation")
    link(ng, right_post, "Mesh", right_post_transform, "Geometry")

    # Join bar pull
    join_bar = create_join_geometry(ng, name="Join Bar", location=(-50, 200))
    link(ng, bar_transform, "Geometry", join_bar, "Geometry")
    link(ng, left_post_transform, "Geometry", join_bar, "Geometry")
    link(ng, right_post_transform, "Geometry", join_bar, "Geometry")

    # ============ WIRE PULL (Style 1) ============
    # Thinner version - use same geometry but scale down width
    wire_width = create_math(ng, 'MULTIPLY', name="Wire Width", location=(-650, -300))
    link(ng, group_in, "Width", wire_width, 0)
    set_default(wire_width, 1, 0.5)  # Half width for wire style

    # Wire bar
    wire_bar = create_cube(ng, name="Wire Bar", location=(-400, -300))
    wire_bar_size = create_combine_xyz(ng, name="Wire Bar Size", location=(-550, -250))
    wire_bar_pos = create_combine_xyz(ng, name="Wire Bar Pos", location=(-550, -350))
    wire_bar_transform = create_transform(ng, name="Wire Bar Transform", location=(-250, -300))

    link(ng, group_in, "Length", wire_bar_size, "X")
    link(ng, wire_width, 0, wire_bar_size, "Y")
    link(ng, wire_width, 0, wire_bar_size, "Z")
    link(ng, wire_bar_size, "Vector", wire_bar, "Size")

    # Wire bar Z position
    wire_z = create_math(ng, 'SUBTRACT', name="Wire Z", location=(-650, -400))
    wire_half = create_math(ng, 'DIVIDE', name="Wire Half", location=(-750, -400))
    link(ng, wire_width, 0, wire_half, 0)
    set_default(wire_half, 1, 2.0)
    link(ng, group_in, "Projection", wire_z, 0)
    link(ng, wire_half, 0, wire_z, 1)
    link(ng, wire_z, 0, wire_bar_pos, "Z")
    link(ng, wire_bar_pos, "Vector", wire_bar_transform, "Translation")
    link(ng, wire_bar, "Mesh", wire_bar_transform, "Geometry")

    # Wire posts (same position as bar posts)
    wire_left = create_cube(ng, name="Wire Left", location=(-400, -500))
    wire_post_size = create_combine_xyz(ng, name="Wire Post Size", location=(-550, -450))
    wire_left_transform = create_transform(ng, name="Wire Left Transform", location=(-250, -500))

    wire_post_diam = create_math(ng, 'MULTIPLY', name="Wire Post Diam", location=(-750, -500))
    link(ng, group_in, "Post Diameter", wire_post_diam, 0)
    set_default(wire_post_diam, 1, 0.6)

    link(ng, wire_post_diam, 0, wire_post_size, "X")
    link(ng, wire_post_diam, 0, wire_post_size, "Y")
    link(ng, group_in, "Projection", wire_post_size, "Z")
    link(ng, wire_post_size, "Vector", wire_left, "Size")
    link(ng, left_post_pos, "Vector", wire_left_transform, "Translation")
    link(ng, wire_left, "Mesh", wire_left_transform, "Geometry")

    wire_right = create_cube(ng, name="Wire Right", location=(-400, -600))
    wire_right_transform = create_transform(ng, name="Wire Right Transform", location=(-250, -600))
    link(ng, wire_post_size, "Vector", wire_right, "Size")
    link(ng, right_post_pos, "Vector", wire_right_transform, "Translation")
    link(ng, wire_right, "Mesh", wire_right_transform, "Geometry")

    # Join wire pull
    join_wire = create_join_geometry(ng, name="Join Wire", location=(-50, -400))
    link(ng, wire_bar_transform, "Geometry", join_wire, "Geometry")
    link(ng, wire_left_transform, "Geometry", join_wire, "Geometry")
    link(ng, wire_right_transform, "Geometry", join_wire, "Geometry")

    # ============ KNOB (Style 2) ============
    # Single cylindrical/cube knob
    knob = create_cube(ng, name="Knob", location=(-400, -800))
    knob_size = create_combine_xyz(ng, name="Knob Size", location=(-550, -750))
    knob_pos = create_combine_xyz(ng, name="Knob Pos", location=(-550, -850))
    knob_transform = create_transform(ng, name="Knob Transform", location=(-250, -800))

    knob_diam = create_math(ng, 'MULTIPLY', name="Knob Diam", location=(-700, -750))
    link(ng, group_in, "Width", knob_diam, 0)
    set_default(knob_diam, 1, 2.5)  # Knob is 2.5x the width

    link(ng, knob_diam, 0, knob_size, "X")
    link(ng, knob_diam, 0, knob_size, "Y")
    link(ng, group_in, "Projection", knob_size, "Z")
    link(ng, knob_size, "Vector", knob, "Size")

    link(ng, post_z, 0, knob_pos, "Z")
    link(ng, knob_pos, "Vector", knob_transform, "Translation")
    link(ng, knob, "Mesh", knob_transform, "Geometry")

    # ============ CUP PULL (Style 3) ============
    # U-shaped bin pull - base plate + curved recess
    cup_base = create_cube(ng, name="Cup Base", location=(-400, -1000))
    cup_base_size = create_combine_xyz(ng, name="Cup Base Size", location=(-550, -950))
    cup_base_pos = create_combine_xyz(ng, name="Cup Base Pos", location=(-550, -1050))
    cup_base_transform = create_transform(ng, name="Cup Base Transform", location=(-250, -1000))

    cup_width = create_math(ng, 'MULTIPLY', name="Cup Width", location=(-700, -950))
    link(ng, group_in, "Width", cup_width, 0)
    set_default(cup_width, 1, 3.0)  # Cup is wider

    link(ng, group_in, "Length", cup_base_size, "X")
    link(ng, cup_width, 0, cup_base_size, "Y")
    cup_thickness = create_math(ng, 'MULTIPLY', name="Cup Thick", location=(-700, -1000))
    link(ng, group_in, "Width", cup_thickness, 0)
    set_default(cup_thickness, 1, 0.3)
    link(ng, cup_thickness, 0, cup_base_size, "Z")
    link(ng, cup_base_size, "Vector", cup_base, "Size")

    # Cup Z position
    cup_z = create_math(ng, 'DIVIDE', name="Cup Z", location=(-650, -1100))
    link(ng, cup_thickness, 0, cup_z, 0)
    set_default(cup_z, 1, 2.0)
    link(ng, cup_z, 0, cup_base_pos, "Z")
    link(ng, cup_base_pos, "Vector", cup_base_transform, "Translation")
    link(ng, cup_base, "Mesh", cup_base_transform, "Geometry")

    # Cup lip (front edge)
    cup_lip = create_cube(ng, name="Cup Lip", location=(-400, -1150))
    cup_lip_size = create_combine_xyz(ng, name="Cup Lip Size", location=(-550, -1100))
    cup_lip_pos = create_combine_xyz(ng, name="Cup Lip Pos", location=(-550, -1200))
    cup_lip_transform = create_transform(ng, name="Cup Lip Transform", location=(-250, -1150))

    link(ng, group_in, "Length", cup_lip_size, "X")
    link(ng, cup_thickness, 0, cup_lip_size, "Y")
    link(ng, group_in, "Projection", cup_lip_size, "Z")
    link(ng, cup_lip_size, "Vector", cup_lip, "Size")

    cup_lip_y = create_math(ng, 'SUBTRACT', name="Cup Lip Y", location=(-700, -1150))
    cup_half = create_math(ng, 'DIVIDE', name="Cup Half", location=(-800, -1150))
    link(ng, cup_width, 0, cup_half, 0)
    set_default(cup_half, 1, 2.0)
    link(ng, cup_half, 0, cup_lip_y, 0)
    link(ng, cup_z, 0, cup_lip_y, 1)
    link(ng, cup_lip_y, 0, cup_lip_pos, "Y")
    link(ng, post_z, 0, cup_lip_pos, "Z")
    link(ng, cup_lip_pos, "Vector", cup_lip_transform, "Translation")
    link(ng, cup_lip, "Mesh", cup_lip_transform, "Geometry")

    # Join cup
    join_cup = create_join_geometry(ng, name="Join Cup", location=(-50, -1050))
    link(ng, cup_base_transform, "Geometry", join_cup, "Geometry")
    link(ng, cup_lip_transform, "Geometry", join_cup, "Geometry")

    # ============ EDGE PULL (Style 4) ============
    # Modern edge grip - mounts on edge of door/drawer
    edge_grip = create_cube(ng, name="Edge Grip", location=(-400, -1350))
    edge_size = create_combine_xyz(ng, name="Edge Size", location=(-550, -1300))
    edge_pos = create_combine_xyz(ng, name="Edge Pos", location=(-550, -1400))
    edge_transform = create_transform(ng, name="Edge Transform", location=(-250, -1350))

    edge_depth = create_math(ng, 'MULTIPLY', name="Edge Depth", location=(-700, -1300))
    link(ng, group_in, "Projection", edge_depth, 0)
    set_default(edge_depth, 1, 1.5)

    link(ng, group_in, "Length", edge_size, "X")
    link(ng, edge_depth, 0, edge_size, "Y")
    link(ng, group_in, "Width", edge_size, "Z")
    link(ng, edge_size, "Vector", edge_grip, "Size")

    edge_y = create_math(ng, 'DIVIDE', name="Edge Y", location=(-650, -1400))
    link(ng, edge_depth, 0, edge_y, 0)
    set_default(edge_y, 1, -2.0)  # Recess into surface
    link(ng, edge_y, 0, edge_pos, "Y")
    link(ng, width_half, 0, edge_pos, "Z")
    link(ng, edge_pos, "Vector", edge_transform, "Translation")
    link(ng, edge_grip, "Mesh", edge_transform, "Geometry")

    # ============ STYLE SWITCHING ============
    # Using cascading switches for 5 styles
    # Compare: Style == 0 (Bar)
    is_bar = create_compare(ng, 'EQUAL', 'INT', name="Is Bar", location=(150, 200))
    link(ng, group_in, "Style", is_bar, 2)
    set_default(is_bar, 3, 0)

    # Compare: Style == 1 (Wire)
    is_wire = create_compare(ng, 'EQUAL', 'INT', name="Is Wire", location=(150, 100))
    link(ng, group_in, "Style", is_wire, 2)
    set_default(is_wire, 3, 1)

    # Compare: Style == 2 (Knob)
    is_knob = create_compare(ng, 'EQUAL', 'INT', name="Is Knob", location=(150, 0))
    link(ng, group_in, "Style", is_knob, 2)
    set_default(is_knob, 3, 2)

    # Compare: Style == 3 (Cup)
    is_cup = create_compare(ng, 'EQUAL', 'INT', name="Is Cup", location=(150, -100))
    link(ng, group_in, "Style", is_cup, 2)
    set_default(is_cup, 3, 3)

    # Compare: Style == 4 (Edge) - default if none match

    # Cascade switches from most specific to least
    # Edge vs Cup
    switch_cup_edge = create_switch(ng, 'GEOMETRY', name="Cup/Edge", location=(300, -150))
    link(ng, is_cup, "Result", switch_cup_edge, "Switch")
    link(ng, edge_transform, "Geometry", switch_cup_edge, "False")
    link(ng, join_cup, "Geometry", switch_cup_edge, "True")

    # Knob vs (Cup/Edge)
    switch_knob = create_switch(ng, 'GEOMETRY', name="Knob Switch", location=(350, -50))
    link(ng, is_knob, "Result", switch_knob, "Switch")
    link(ng, switch_cup_edge, "Output", switch_knob, "False")
    link(ng, knob_transform, "Geometry", switch_knob, "True")

    # Wire vs (Knob/Cup/Edge)
    switch_wire = create_switch(ng, 'GEOMETRY', name="Wire Switch", location=(400, 50))
    link(ng, is_wire, "Result", switch_wire, "Switch")
    link(ng, switch_knob, "Output", switch_wire, "False")
    link(ng, join_wire, "Geometry", switch_wire, "True")

    # Bar vs (Wire/Knob/Cup/Edge)
    switch_bar = create_switch(ng, 'GEOMETRY', name="Style Switch", location=(450, 150))
    link(ng, is_bar, "Result", switch_bar, "Switch")
    link(ng, switch_wire, "Output", switch_bar, "False")
    link(ng, join_bar, "Geometry", switch_bar, "True")

    # Set material
    set_mat = create_set_material(ng, name="Set Material", location=(550, 0))
    link(ng, switch_bar, "Output", set_mat, "Geometry")
    link(ng, group_in, "Material", set_mat, "Material")

    # Output
    link(ng, set_mat, "Geometry", group_out, "Geometry")

    # Add metadata
    add_metadata(ng, version="1.1.0",
                 script_path="src/nodes/atomic/hardware.py")

    return ng


def create_test_object(handle_nodegroup=None):
    """Create a test object with the Handle node group applied."""
    if handle_nodegroup is None:
        handle_nodegroup = create_handle_nodegroup()

    mesh = bpy.data.meshes.new("Handle_Test")
    obj = bpy.data.objects.new("Handle_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = handle_nodegroup

    return obj


if __name__ == "__main__":
    ng = create_handle_nodegroup()
    print(f"Created node group: {ng.name}")
