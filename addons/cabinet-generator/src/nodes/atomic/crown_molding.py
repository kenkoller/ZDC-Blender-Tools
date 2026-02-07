# Crown Molding node group generator
# Atomic component: Decorative crown molding for cabinet tops
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


def create_crown_molding_nodegroup():
    """Generate the CrownMolding node group.

    Creates decorative crown molding for cabinet tops:
    - Configurable profile height and projection
    - Runs along front and optionally sides
    - Position at top of cabinet

    The molding profile is simplified as angled geometry.
    A more detailed version would use curves or mesh profiles.

    Inputs:
        Width: Cabinet width (molding spans this)
        Depth: Cabinet depth (for side returns)
        Profile Height: Vertical height of molding profile
        Profile Projection: How far molding projects from cabinet face
        Has Side Returns: Whether molding wraps around sides
        Material: Molding material

    Outputs:
        Geometry: Crown molding mesh
    """
    ng = create_node_group("CrownMolding")

    # Create interface
    dims_panel = create_panel(ng, "Dimensions")
    style_panel = create_panel(ng, "Style")
    materials_panel = create_panel(ng, "Materials")

    add_float_socket(ng, "Width", default=0.6, min_val=0.2, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.55, min_val=0.2, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Profile Height", default=0.075, min_val=0.03, max_val=0.15,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Profile Projection", default=0.03, min_val=0.01, max_val=0.06,
                     subtype='DISTANCE', panel=dims_panel)

    add_bool_socket(ng, "Has Side Returns", default=True, panel=style_panel)

    add_material_socket(ng, "Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ FRONT MOLDING PIECE ============
    # Simplified as angled rectangular profile
    # In production, this would be a proper profile curve

    # Main body of front molding
    front_width = create_math(ng, 'ADD', name="Front Width", location=(-600, 200))
    link(ng, group_in, "Width", front_width, 0)
    link(ng, group_in, "Profile Projection", front_width, 1)  # Extend for miters

    front_size = create_combine_xyz(ng, name="Front Size", location=(-500, 200))
    link(ng, front_width, 0, front_size, "X")
    link(ng, group_in, "Profile Projection", front_size, "Y")
    link(ng, group_in, "Profile Height", front_size, "Z")

    front_body = create_cube(ng, name="Front Body", location=(-400, 200))
    link(ng, front_size, "Vector", front_body, "Size")

    # Position front molding (front edge, projecting forward)
    proj_half = create_math(ng, 'DIVIDE', name="Proj Half", location=(-600, 100))
    link(ng, group_in, "Profile Projection", proj_half, 0)
    set_default(proj_half, 1, 2.0)

    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-600, 50))
    link(ng, group_in, "Profile Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    front_pos = create_combine_xyz(ng, name="Front Pos", location=(-500, 100))
    set_default(front_pos, "X", 0.0)
    link(ng, proj_half, 0, front_pos, "Y")  # Project forward
    link(ng, height_half, 0, front_pos, "Z")  # Offset for pivot

    front_transform = create_transform(ng, name="Front Transform", location=(-300, 200))
    link(ng, front_body, "Mesh", front_transform, "Geometry")
    link(ng, front_pos, "Vector", front_transform, "Translation")

    # ============ LEFT SIDE RETURN ============
    # Side piece runs along depth
    side_length = create_math(ng, 'ADD', name="Side Length", location=(-600, -100))
    link(ng, group_in, "Depth", side_length, 0)
    link(ng, group_in, "Profile Projection", side_length, 1)

    side_size = create_combine_xyz(ng, name="Side Size", location=(-500, -100))
    link(ng, group_in, "Profile Projection", side_size, "X")
    link(ng, side_length, 0, side_size, "Y")
    link(ng, group_in, "Profile Height", side_size, "Z")

    left_side = create_cube(ng, name="Left Side", location=(-400, -100))
    link(ng, side_size, "Vector", left_side, "Size")

    # Position left side
    left_x = create_math(ng, 'DIVIDE', name="Left X", location=(-600, -200))
    link(ng, group_in, "Width", left_x, 0)
    set_default(left_x, 1, -2.0)  # Negative for left side

    left_x_offset = create_math(ng, 'SUBTRACT', name="Left X Offset", location=(-500, -200))
    link(ng, left_x, 0, left_x_offset, 0)
    link(ng, proj_half, 0, left_x_offset, 1)

    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-600, -250))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-400, -200))
    link(ng, left_x_offset, 0, left_pos, "X")
    link(ng, depth_half, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Transform", location=(-300, -100))
    link(ng, left_side, "Mesh", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    # ============ RIGHT SIDE RETURN ============
    right_side = create_cube(ng, name="Right Side", location=(-400, -350))
    link(ng, side_size, "Vector", right_side, "Size")

    # Position right side (mirror of left)
    right_x = create_math(ng, 'DIVIDE', name="Right X", location=(-600, -400))
    link(ng, group_in, "Width", right_x, 0)
    set_default(right_x, 1, 2.0)  # Positive for right side

    right_x_offset = create_math(ng, 'ADD', name="Right X Offset", location=(-500, -400))
    link(ng, right_x, 0, right_x_offset, 0)
    link(ng, proj_half, 0, right_x_offset, 1)

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-400, -400))
    link(ng, right_x_offset, 0, right_pos, "X")
    link(ng, depth_half, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Transform", location=(-300, -350))
    link(ng, right_side, "Mesh", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    # ============ JOIN SIDE RETURNS ============
    join_sides = create_join_geometry(ng, name="Join Sides", location=(-100, -200))
    link(ng, left_transform, "Geometry", join_sides, "Geometry")
    link(ng, right_transform, "Geometry", join_sides, "Geometry")

    # Switch sides on/off
    switch_sides = create_switch(ng, 'GEOMETRY', name="Sides Switch", location=(0, -200))
    link(ng, group_in, "Has Side Returns", switch_sides, "Switch")
    link(ng, join_sides, "Geometry", switch_sides, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(200, 0))
    link(ng, front_transform, "Geometry", join_all, "Geometry")
    link(ng, switch_sides, "Output", join_all, "Geometry")

    # ============ MATERIAL ============
    mat_node = create_set_material(ng, name="Set Material", location=(400, 0))
    link(ng, join_all, "Geometry", mat_node, "Geometry")
    link(ng, group_in, "Material", mat_node, "Material")

    # ============ OUTPUT ============
    link(ng, mat_node, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/crown_molding.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the CrownMolding node group applied."""
    if nodegroup is None:
        nodegroup = create_crown_molding_nodegroup()

    mesh = bpy.data.meshes.new("CrownMolding_Test")
    obj = bpy.data.objects.new("CrownMolding_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_crown_molding_nodegroup()
    print(f"Created node group: {ng.name}")
