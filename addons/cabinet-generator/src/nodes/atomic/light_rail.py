# Light Rail Molding node group generator
# Atomic component: Under-cabinet light rail to hide LED strips
# Coordinate system: X=width, Y=depth, Z=height (Z-up)

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


def create_light_rail_nodegroup():
    """Generate the LightRail node group.

    Creates light rail molding that attaches to bottom of wall cabinets
    to hide under-cabinet lighting and provide a finished look.

    Light rail is typically a small (1.5" to 2") trim piece that runs
    along the bottom front edge of wall cabinets.

    Inputs:
        Width: Cabinet width (rail spans this)
        Rail Height: Vertical height of rail (typically 38-50mm)
        Rail Thickness: Depth/thickness of rail (typically 18mm)
        Has End Caps: Whether to include finished end pieces
        Material: Rail material

    Outputs:
        Geometry: Light rail mesh
    """
    ng = create_node_group("LightRail")

    # Create interface
    dims_panel = create_panel(ng, "Dimensions")
    style_panel = create_panel(ng, "Style")
    materials_panel = create_panel(ng, "Materials")

    add_float_socket(ng, "Width", default=0.6, min_val=0.2, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Rail Height", default=0.045, min_val=0.025, max_val=0.075,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Rail Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    add_bool_socket(ng, "Has End Caps", default=True, panel=style_panel)

    add_material_socket(ng, "Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-600, 0))
    group_out = create_group_output(ng, location=(600, 0))

    # ============ MAIN RAIL ============
    rail_size = create_combine_xyz(ng, name="Rail Size", location=(-400, 100))
    link(ng, group_in, "Width", rail_size, "X")
    link(ng, group_in, "Rail Thickness", rail_size, "Y")
    link(ng, group_in, "Rail Height", rail_size, "Z")

    rail = create_cube(ng, name="Rail", location=(-300, 100))
    link(ng, rail_size, "Vector", rail, "Size")

    # Position rail (front edge, hanging down)
    thickness_half = create_math(ng, 'DIVIDE', name="Thick Half", location=(-400, 0))
    link(ng, group_in, "Rail Thickness", thickness_half, 0)
    set_default(thickness_half, 1, 2.0)

    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-400, -50))
    link(ng, group_in, "Rail Height", height_half, 0)
    set_default(height_half, 1, -2.0)  # Negative to hang down

    rail_pos = create_combine_xyz(ng, name="Rail Pos", location=(-300, 0))
    set_default(rail_pos, "X", 0.0)
    link(ng, thickness_half, 0, rail_pos, "Y")
    link(ng, height_half, 0, rail_pos, "Z")

    rail_transform = create_transform(ng, name="Rail Transform", location=(-200, 100))
    link(ng, rail, "Mesh", rail_transform, "Geometry")
    link(ng, rail_pos, "Vector", rail_transform, "Translation")

    # ============ LEFT END CAP ============
    cap_size = create_combine_xyz(ng, name="Cap Size", location=(-400, -150))
    link(ng, group_in, "Rail Thickness", cap_size, "X")
    link(ng, group_in, "Rail Thickness", cap_size, "Y")
    link(ng, group_in, "Rail Height", cap_size, "Z")

    left_cap = create_cube(ng, name="Left Cap", location=(-300, -150))
    link(ng, cap_size, "Vector", left_cap, "Size")

    # Position left cap
    left_x = create_math(ng, 'DIVIDE', name="Left X", location=(-400, -250))
    link(ng, group_in, "Width", left_x, 0)
    set_default(left_x, 1, -2.0)

    left_x_offset = create_math(ng, 'SUBTRACT', name="Left X Offset", location=(-300, -250))
    link(ng, left_x, 0, left_x_offset, 0)
    link(ng, thickness_half, 0, left_x_offset, 1)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-200, -200))
    link(ng, left_x_offset, 0, left_pos, "X")
    link(ng, thickness_half, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Transform", location=(-100, -150))
    link(ng, left_cap, "Mesh", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    # ============ RIGHT END CAP ============
    right_cap = create_cube(ng, name="Right Cap", location=(-300, -350))
    link(ng, cap_size, "Vector", right_cap, "Size")

    # Position right cap (mirror of left)
    right_x = create_math(ng, 'DIVIDE', name="Right X", location=(-400, -400))
    link(ng, group_in, "Width", right_x, 0)
    set_default(right_x, 1, 2.0)

    right_x_offset = create_math(ng, 'ADD', name="Right X Offset", location=(-300, -400))
    link(ng, right_x, 0, right_x_offset, 0)
    link(ng, thickness_half, 0, right_x_offset, 1)

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-200, -380))
    link(ng, right_x_offset, 0, right_pos, "X")
    link(ng, thickness_half, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Transform", location=(-100, -350))
    link(ng, right_cap, "Mesh", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    # ============ JOIN END CAPS ============
    join_caps = create_join_geometry(ng, name="Join Caps", location=(0, -250))
    link(ng, left_transform, "Geometry", join_caps, "Geometry")
    link(ng, right_transform, "Geometry", join_caps, "Geometry")

    # Switch end caps on/off
    switch_caps = create_switch(ng, 'GEOMETRY', name="Caps Switch", location=(100, -250))
    link(ng, group_in, "Has End Caps", switch_caps, "Switch")
    link(ng, join_caps, "Geometry", switch_caps, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(200, 0))
    link(ng, rail_transform, "Geometry", join_all, "Geometry")
    link(ng, switch_caps, "Output", join_all, "Geometry")

    # ============ MATERIAL ============
    mat_node = create_set_material(ng, name="Set Material", location=(400, 0))
    link(ng, join_all, "Geometry", mat_node, "Geometry")
    link(ng, group_in, "Material", mat_node, "Material")

    # ============ OUTPUT ============
    link(ng, mat_node, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/light_rail.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the LightRail node group applied."""
    if nodegroup is None:
        nodegroup = create_light_rail_nodegroup()

    mesh = bpy.data.meshes.new("LightRail_Test")
    obj = bpy.data.objects.new("LightRail_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_light_rail_nodegroup()
    print(f"Created node group: {ng.name}")
