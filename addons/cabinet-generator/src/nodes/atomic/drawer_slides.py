# Drawer Slides node group generator
# Atomic component: Side-mount and undermount drawer slide rails
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


def create_drawer_slides_nodegroup():
    """Generate the DrawerSlides node group.

    Creates drawer slide hardware with multiple styles:
    - Style 0: Side Mount (ball bearing)
    - Style 1: Undermount (concealed)
    - Style 2: Center Mount (single rail)

    Slides are generated as a pair (left and right).

    Inputs:
        Style: Slide style (0-2)
        Depth: Slide length (travel distance)
        Drawer Width: Width between slides
        Extension: 0-1 (how far drawer is extended)
        Material: Slide material

    Outputs:
        Geometry: Slide pair mesh
    """
    ng = create_node_group("DrawerSlides")

    # Create interface
    style_panel = create_panel(ng, "Style")
    dims_panel = create_panel(ng, "Dimensions")
    anim_panel = create_panel(ng, "Animation")
    materials_panel = create_panel(ng, "Materials")

    add_int_socket(ng, "Style", default=0, min_val=0, max_val=2, panel=style_panel)
    add_float_socket(ng, "Depth", default=0.45, min_val=0.2, max_val=0.6,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Drawer Width", default=0.5, min_val=0.2, max_val=1.0,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height Offset", default=0.05, min_val=0.0, max_val=0.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Extension", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='FACTOR', panel=anim_panel)
    add_material_socket(ng, "Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1000, 0))
    group_out = create_group_output(ng, location=(1000, 0))

    # ============ STYLE 0: SIDE MOUNT SLIDES ============
    # Cabinet-mounted rail (outer)
    outer_rail_size = create_combine_xyz(ng, name="Outer Rail Size", location=(-600, 300))
    set_default(outer_rail_size, "X", 0.012)  # Rail width
    link(ng, group_in, "Depth", outer_rail_size, "Y")
    set_default(outer_rail_size, "Z", 0.035)  # Rail height

    outer_rail = create_cube(ng, name="Outer Rail", location=(-500, 300))
    link(ng, outer_rail_size, "Vector", outer_rail, "Size")

    # Inner rail (drawer-mounted, moves with extension)
    inner_rail_size = create_combine_xyz(ng, name="Inner Rail Size", location=(-600, 150))
    set_default(inner_rail_size, "X", 0.008)
    link(ng, group_in, "Depth", inner_rail_size, "Y")
    set_default(inner_rail_size, "Z", 0.025)

    inner_rail = create_cube(ng, name="Inner Rail", location=(-500, 150))
    link(ng, inner_rail_size, "Vector", inner_rail, "Size")

    # Calculate extension offset
    ext_offset = create_math(ng, 'MULTIPLY', name="Ext Offset", location=(-700, 0))
    link(ng, group_in, "Extension", ext_offset, 0)
    link(ng, group_in, "Depth", ext_offset, 1)

    # Inner rail position (moves forward with extension)
    inner_pos = create_combine_xyz(ng, name="Inner Pos", location=(-500, 50))
    set_default(inner_pos, "X", 0.0)
    link(ng, ext_offset, 0, inner_pos, "Y")
    set_default(inner_pos, "Z", 0.0)

    inner_transform = create_transform(ng, name="Inner Transform", location=(-350, 150))
    link(ng, inner_rail, "Mesh", inner_transform, "Geometry")
    link(ng, inner_pos, "Vector", inner_transform, "Translation")

    # Join single slide
    join_slide = create_join_geometry(ng, name="Join Slide", location=(-200, 200))
    link(ng, outer_rail, "Mesh", join_slide, "Geometry")
    link(ng, inner_transform, "Geometry", join_slide, "Geometry")

    # ============ CREATE LEFT AND RIGHT SLIDES ============
    # Left slide X position
    left_x = create_math(ng, 'DIVIDE', name="Left X", location=(-300, -100))
    link(ng, group_in, "Drawer Width", left_x, 0)
    set_default(left_x, 1, -2.0)

    # Right slide X position
    right_x = create_math(ng, 'DIVIDE', name="Right X", location=(-300, -200))
    link(ng, group_in, "Drawer Width", right_x, 0)
    set_default(right_x, 1, 2.0)

    # Y position (centered on depth)
    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-300, -300))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    # Left slide position
    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-100, -100))
    link(ng, left_x, 0, left_pos, "X")
    link(ng, depth_half, 0, left_pos, "Y")
    link(ng, group_in, "Height Offset", left_pos, "Z")

    left_transform = create_transform(ng, name="Left Slide", location=(0, 100))
    link(ng, join_slide, "Geometry", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    # Right slide position
    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-100, -200))
    link(ng, right_x, 0, right_pos, "X")
    link(ng, depth_half, 0, right_pos, "Y")
    link(ng, group_in, "Height Offset", right_pos, "Z")

    right_transform = create_transform(ng, name="Right Slide", location=(0, -100))
    link(ng, join_slide, "Geometry", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    # Join left and right (side mount)
    join_side_mount = create_join_geometry(ng, name="Join Side Mount", location=(200, 0))
    link(ng, left_transform, "Geometry", join_side_mount, "Geometry")
    link(ng, right_transform, "Geometry", join_side_mount, "Geometry")

    # ============ STYLE 1: UNDERMOUNT SLIDES ============
    # Lower profile, mounted under drawer
    under_rail_size = create_combine_xyz(ng, name="Under Rail Size", location=(-600, -400))
    set_default(under_rail_size, "X", 0.025)  # Wider
    link(ng, group_in, "Depth", under_rail_size, "Y")
    set_default(under_rail_size, "Z", 0.015)  # Lower profile

    under_rail = create_cube(ng, name="Under Rail", location=(-500, -400))
    link(ng, under_rail_size, "Vector", under_rail, "Size")

    # Left undermount
    left_under_pos = create_combine_xyz(ng, name="Left Under Pos", location=(-100, -400))
    link(ng, left_x, 0, left_under_pos, "X")
    link(ng, depth_half, 0, left_under_pos, "Y")
    set_default(left_under_pos, "Z", 0.0075)

    left_under = create_transform(ng, name="Left Undermount", location=(0, -350))
    link(ng, under_rail, "Mesh", left_under, "Geometry")
    link(ng, left_under_pos, "Vector", left_under, "Translation")

    # Right undermount
    right_under_pos = create_combine_xyz(ng, name="Right Under Pos", location=(-100, -500))
    link(ng, right_x, 0, right_under_pos, "X")
    link(ng, depth_half, 0, right_under_pos, "Y")
    set_default(right_under_pos, "Z", 0.0075)

    right_under = create_transform(ng, name="Right Undermount", location=(0, -450))
    link(ng, under_rail, "Mesh", right_under, "Geometry")
    link(ng, right_under_pos, "Vector", right_under, "Translation")

    join_undermount = create_join_geometry(ng, name="Join Undermount", location=(200, -400))
    link(ng, left_under, "Geometry", join_undermount, "Geometry")
    link(ng, right_under, "Geometry", join_undermount, "Geometry")

    # ============ STYLE 2: CENTER MOUNT ============
    center_rail_size = create_combine_xyz(ng, name="Center Rail Size", location=(-600, -600))
    set_default(center_rail_size, "X", 0.02)
    link(ng, group_in, "Depth", center_rail_size, "Y")
    set_default(center_rail_size, "Z", 0.025)

    center_rail = create_cube(ng, name="Center Rail", location=(-500, -600))
    link(ng, center_rail_size, "Vector", center_rail, "Size")

    center_pos = create_combine_xyz(ng, name="Center Pos", location=(-100, -600))
    set_default(center_pos, "X", 0.0)
    link(ng, depth_half, 0, center_pos, "Y")
    set_default(center_pos, "Z", 0.0125)

    center_transform = create_transform(ng, name="Center Mount", location=(0, -600))
    link(ng, center_rail, "Mesh", center_transform, "Geometry")
    link(ng, center_pos, "Vector", center_transform, "Translation")

    # ============ STYLE SWITCHING ============
    style_is_1 = create_compare(ng, 'EQUAL', 'INT', name="Style=1", location=(300, -200))
    link(ng, group_in, "Style", style_is_1, 2)
    set_default(style_is_1, 3, 1)

    switch_01 = create_switch(ng, 'GEOMETRY', name="Switch 0-1", location=(400, -100))
    link(ng, style_is_1, "Result", switch_01, "Switch")
    link(ng, join_side_mount, "Geometry", switch_01, "False")
    link(ng, join_undermount, "Geometry", switch_01, "True")

    style_is_2 = create_compare(ng, 'EQUAL', 'INT', name="Style=2", location=(400, -300))
    link(ng, group_in, "Style", style_is_2, 2)
    set_default(style_is_2, 3, 2)

    switch_final = create_switch(ng, 'GEOMETRY', name="Switch Final", location=(500, 0))
    link(ng, style_is_2, "Result", switch_final, "Switch")
    link(ng, switch_01, "Output", switch_final, "False")
    link(ng, center_transform, "Geometry", switch_final, "True")

    # ============ MATERIAL ============
    mat_node = create_set_material(ng, name="Set Material", location=(700, 0))
    link(ng, switch_final, "Output", mat_node, "Geometry")
    link(ng, group_in, "Material", mat_node, "Material")

    # ============ OUTPUT ============
    link(ng, mat_node, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/drawer_slides.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the DrawerSlides node group applied."""
    if nodegroup is None:
        nodegroup = create_drawer_slides_nodegroup()

    mesh = bpy.data.meshes.new("DrawerSlides_Test")
    obj = bpy.data.objects.new("DrawerSlides_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_drawer_slides_nodegroup()
    print(f"Created node group: {ng.name}")
