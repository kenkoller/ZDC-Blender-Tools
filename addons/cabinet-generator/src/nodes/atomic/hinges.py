# Hinge node group generator
# Atomic component: European cup hinge and exposed hinge styles
# Coordinate system: X=width, Y=depth, Z=height (Z-up)

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


def create_hinge_nodegroup():
    """Generate the Hinge node group.

    Creates hinge hardware with multiple styles:
    - Style 0: European Cup Hinge (concealed)
    - Style 1: Exposed Barrel Hinge
    - Style 2: Piano Hinge (continuous)

    Inputs:
        Style: Hinge style (0-2)
        Height: Hinge height (for sizing)
        Material: Hinge material

    Outputs:
        Geometry: Hinge mesh
    """
    ng = create_node_group("Hinge")

    # Create interface
    style_panel = create_panel(ng, "Style")
    dims_panel = create_panel(ng, "Dimensions")
    materials_panel = create_panel(ng, "Materials")

    add_int_socket(ng, "Style", default=0, min_val=0, max_val=2, panel=style_panel)
    add_float_socket(ng, "Door Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.08, min_val=0.04, max_val=0.15,
                     subtype='DISTANCE', panel=dims_panel)
    add_material_socket(ng, "Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ STYLE 0: EUROPEAN CUP HINGE ============
    # Cup part (cylindrical, simplified as cube)
    cup_size = create_combine_xyz(ng, name="Cup Size", location=(-400, 300))
    set_default(cup_size, "X", 0.035)  # 35mm cup diameter
    set_default(cup_size, "Y", 0.012)  # Cup depth
    set_default(cup_size, "Z", 0.035)  # Cup height

    cup = create_cube(ng, name="Cup", location=(-300, 300))
    link(ng, cup_size, "Vector", cup, "Size")

    cup_pos = create_combine_xyz(ng, name="Cup Pos", location=(-400, 250))
    set_default(cup_pos, "X", 0.0)
    set_default(cup_pos, "Y", -0.006)
    set_default(cup_pos, "Z", 0.0)

    cup_transform = create_transform(ng, name="Cup Transform", location=(-200, 300))
    link(ng, cup, "Mesh", cup_transform, "Geometry")
    link(ng, cup_pos, "Vector", cup_transform, "Translation")

    # Arm part
    arm_size = create_combine_xyz(ng, name="Arm Size", location=(-400, 150))
    set_default(arm_size, "X", 0.012)
    set_default(arm_size, "Y", 0.05)
    set_default(arm_size, "Z", 0.008)

    arm = create_cube(ng, name="Arm", location=(-300, 150))
    link(ng, arm_size, "Vector", arm, "Size")

    arm_pos = create_combine_xyz(ng, name="Arm Pos", location=(-400, 100))
    set_default(arm_pos, "X", 0.0)
    set_default(arm_pos, "Y", 0.025)
    set_default(arm_pos, "Z", 0.0)

    arm_transform = create_transform(ng, name="Arm Transform", location=(-200, 150))
    link(ng, arm, "Mesh", arm_transform, "Geometry")
    link(ng, arm_pos, "Vector", arm_transform, "Translation")

    # Mounting plate
    plate_size = create_combine_xyz(ng, name="Plate Size", location=(-400, 0))
    set_default(plate_size, "X", 0.032)
    set_default(plate_size, "Y", 0.012)
    set_default(plate_size, "Z", 0.08)

    plate = create_cube(ng, name="Plate", location=(-300, 0))
    link(ng, plate_size, "Vector", plate, "Size")

    plate_y = create_math(ng, 'ADD', name="Plate Y", location=(-400, -50))
    link(ng, group_in, "Door Thickness", plate_y, 0)
    set_default(plate_y, 1, 0.05)

    plate_pos = create_combine_xyz(ng, name="Plate Pos", location=(-300, -50))
    set_default(plate_pos, "X", 0.0)
    link(ng, plate_y, 0, plate_pos, "Y")
    set_default(plate_pos, "Z", 0.0)

    plate_transform = create_transform(ng, name="Plate Transform", location=(-200, 0))
    link(ng, plate, "Mesh", plate_transform, "Geometry")
    link(ng, plate_pos, "Vector", plate_transform, "Translation")

    # Join European hinge
    join_euro = create_join_geometry(ng, name="Join Euro", location=(0, 200))
    link(ng, cup_transform, "Geometry", join_euro, "Geometry")
    link(ng, arm_transform, "Geometry", join_euro, "Geometry")
    link(ng, plate_transform, "Geometry", join_euro, "Geometry")

    # ============ STYLE 1: EXPOSED BARREL HINGE ============
    # Barrel
    barrel_size = create_combine_xyz(ng, name="Barrel Size", location=(-400, -200))
    set_default(barrel_size, "X", 0.012)
    set_default(barrel_size, "Y", 0.012)
    link(ng, group_in, "Height", barrel_size, "Z")

    barrel = create_cube(ng, name="Barrel", location=(-300, -200))
    link(ng, barrel_size, "Vector", barrel, "Size")

    barrel_transform = create_transform(ng, name="Barrel Transform", location=(-200, -200))
    link(ng, barrel, "Mesh", barrel_transform, "Geometry")

    # Leaf 1 (door side)
    leaf1_size = create_combine_xyz(ng, name="Leaf1 Size", location=(-400, -300))
    set_default(leaf1_size, "X", 0.025)
    set_default(leaf1_size, "Y", 0.002)
    link(ng, group_in, "Height", leaf1_size, "Z")

    leaf1 = create_cube(ng, name="Leaf1", location=(-300, -300))
    link(ng, leaf1_size, "Vector", leaf1, "Size")

    leaf1_pos = create_combine_xyz(ng, name="Leaf1 Pos", location=(-400, -350))
    set_default(leaf1_pos, "X", -0.0185)
    set_default(leaf1_pos, "Y", -0.006)
    set_default(leaf1_pos, "Z", 0.0)

    leaf1_transform = create_transform(ng, name="Leaf1 Transform", location=(-200, -300))
    link(ng, leaf1, "Mesh", leaf1_transform, "Geometry")
    link(ng, leaf1_pos, "Vector", leaf1_transform, "Translation")

    # Leaf 2 (cabinet side)
    leaf2 = create_cube(ng, name="Leaf2", location=(-300, -400))
    link(ng, leaf1_size, "Vector", leaf2, "Size")

    leaf2_pos = create_combine_xyz(ng, name="Leaf2 Pos", location=(-400, -450))
    set_default(leaf2_pos, "X", -0.0185)
    set_default(leaf2_pos, "Y", 0.006)
    set_default(leaf2_pos, "Z", 0.0)

    leaf2_transform = create_transform(ng, name="Leaf2 Transform", location=(-200, -400))
    link(ng, leaf2, "Mesh", leaf2_transform, "Geometry")
    link(ng, leaf2_pos, "Vector", leaf2_transform, "Translation")

    # Join exposed hinge
    join_exposed = create_join_geometry(ng, name="Join Exposed", location=(0, -300))
    link(ng, barrel_transform, "Geometry", join_exposed, "Geometry")
    link(ng, leaf1_transform, "Geometry", join_exposed, "Geometry")
    link(ng, leaf2_transform, "Geometry", join_exposed, "Geometry")

    # ============ STYLE 2: PIANO HINGE ============
    # Continuous hinge (simplified)
    piano_size = create_combine_xyz(ng, name="Piano Size", location=(-400, -550))
    set_default(piano_size, "X", 0.025)
    set_default(piano_size, "Y", 0.003)
    link(ng, group_in, "Height", piano_size, "Z")

    piano = create_cube(ng, name="Piano", location=(-300, -550))
    link(ng, piano_size, "Vector", piano, "Size")

    piano_transform = create_transform(ng, name="Piano Transform", location=(-200, -550))
    link(ng, piano, "Mesh", piano_transform, "Geometry")

    # ============ STYLE SWITCHING ============
    # Switch between Euro (0), Exposed (1), Piano (2)
    switch_01 = create_switch(ng, 'GEOMETRY', name="Switch 0-1", location=(200, 0))

    style_compare_1 = create_compare(ng, 'EQUAL', 'INT', name="Style=1", location=(100, -50))
    link(ng, group_in, "Style", style_compare_1, 2)
    set_default(style_compare_1, 3, 1)

    link(ng, style_compare_1, "Result", switch_01, "Switch")
    link(ng, join_euro, "Geometry", switch_01, "False")
    link(ng, join_exposed, "Geometry", switch_01, "True")

    # Switch to Piano
    style_compare_2 = create_compare(ng, 'EQUAL', 'INT', name="Style=2", location=(300, -100))
    link(ng, group_in, "Style", style_compare_2, 2)
    set_default(style_compare_2, 3, 2)

    switch_final = create_switch(ng, 'GEOMETRY', name="Switch Final", location=(400, 0))
    link(ng, style_compare_2, "Result", switch_final, "Switch")
    link(ng, switch_01, "Output", switch_final, "False")
    link(ng, piano_transform, "Geometry", switch_final, "True")

    # ============ MATERIAL ============
    mat_node = create_set_material(ng, name="Set Material", location=(600, 0))
    link(ng, switch_final, "Output", mat_node, "Geometry")
    link(ng, group_in, "Material", mat_node, "Material")

    # ============ OUTPUT ============
    link(ng, mat_node, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/hinges.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the Hinge node group applied."""
    if nodegroup is None:
        nodegroup = create_hinge_nodegroup()

    mesh = bpy.data.meshes.new("Hinge_Test")
    obj = bpy.data.objects.new("Hinge_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_hinge_nodegroup()
    print(f"Created node group: {ng.name}")
