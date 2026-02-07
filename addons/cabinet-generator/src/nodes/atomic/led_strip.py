# LED Light Strip node group generator
# Atomic component: Under-cabinet and in-cabinet LED lighting
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


def create_led_strip_nodegroup():
    """Generate the LEDStrip node group.

    Creates LED light strip geometry for cabinet lighting:
    - Under-cabinet mounting (below wall cabinets)
    - In-cabinet mounting (inside cabinets)
    - Configurable length and positioning

    The strip is represented as a thin rectangular profile with
    an emissive material slot for the LEDs and a housing material slot.

    Inputs:
        Length: Strip length
        Width: Strip width (typically 8-12mm)
        Height: Strip height/thickness (typically 3-5mm)
        Mount Type: 0=Surface (bottom), 1=Recessed, 2=Angled (45 deg)
        Has Diffuser: Whether strip has frosted diffuser cover
        Housing Material: Material for aluminum channel
        LED Material: Emissive material for LED elements

    Outputs:
        Geometry: LED strip mesh
    """
    ng = create_node_group("LEDStrip")

    # Create interface
    dims_panel = create_panel(ng, "Dimensions")
    style_panel = create_panel(ng, "Style")
    materials_panel = create_panel(ng, "Materials")

    add_float_socket(ng, "Length", default=0.6, min_val=0.1, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Width", default=0.012, min_val=0.008, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.005, min_val=0.003, max_val=0.015,
                     subtype='DISTANCE', panel=dims_panel)

    add_int_socket(ng, "Mount Type", default=0, min_val=0, max_val=2, panel=style_panel)
    add_bool_socket(ng, "Has Diffuser", default=True, panel=style_panel)

    add_material_socket(ng, "Housing Material", panel=materials_panel)
    add_material_socket(ng, "LED Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ ALUMINUM CHANNEL HOUSING ============
    # U-shaped channel profile (simplified as cube)
    channel_size = create_combine_xyz(ng, name="Channel Size", location=(-500, 200))
    link(ng, group_in, "Length", channel_size, "X")
    link(ng, group_in, "Width", channel_size, "Y")
    link(ng, group_in, "Height", channel_size, "Z")

    channel = create_cube(ng, name="Channel", location=(-400, 200))
    link(ng, channel_size, "Vector", channel, "Size")

    channel_mat = create_set_material(ng, name="Channel Mat", location=(-300, 200))
    link(ng, channel, "Mesh", channel_mat, "Geometry")
    link(ng, group_in, "Housing Material", channel_mat, "Material")

    # ============ LED STRIP ELEMENT ============
    # Thin glowing strip inside the channel
    led_width = create_math(ng, 'MULTIPLY', name="LED Width", location=(-600, 0))
    link(ng, group_in, "Width", led_width, 0)
    set_default(led_width, 1, 0.7)  # LED strip is 70% of channel width

    led_height = create_math(ng, 'MULTIPLY', name="LED Height", location=(-600, -50))
    link(ng, group_in, "Height", led_height, 0)
    set_default(led_height, 1, 0.3)  # LED strip is 30% of channel height

    led_size = create_combine_xyz(ng, name="LED Size", location=(-500, -20))
    link(ng, group_in, "Length", led_size, "X")
    link(ng, led_width, 0, led_size, "Y")
    link(ng, led_height, 0, led_size, "Z")

    led_strip = create_cube(ng, name="LED Strip", location=(-400, 0))
    link(ng, led_size, "Vector", led_strip, "Size")

    # Position LED strip at bottom of channel
    led_z_offset = create_math(ng, 'DIVIDE', name="LED Z Offset", location=(-500, -100))
    link(ng, group_in, "Height", led_z_offset, 0)
    set_default(led_z_offset, 1, -4.0)  # Offset down

    led_pos = create_combine_xyz(ng, name="LED Pos", location=(-400, -100))
    link(ng, led_z_offset, 0, led_pos, "Z")

    led_transform = create_transform(ng, name="LED Transform", location=(-300, 0))
    link(ng, led_strip, "Mesh", led_transform, "Geometry")
    link(ng, led_pos, "Vector", led_transform, "Translation")

    led_mat = create_set_material(ng, name="LED Mat", location=(-200, 0))
    link(ng, led_transform, "Geometry", led_mat, "Geometry")
    link(ng, group_in, "LED Material", led_mat, "Material")

    # ============ DIFFUSER COVER ============
    diffuser_height = create_math(ng, 'MULTIPLY', name="Diffuser Height", location=(-600, -200))
    link(ng, group_in, "Height", diffuser_height, 0)
    set_default(diffuser_height, 1, 0.15)  # Thin diffuser

    diffuser_size = create_combine_xyz(ng, name="Diffuser Size", location=(-500, -200))
    link(ng, group_in, "Length", diffuser_size, "X")
    link(ng, group_in, "Width", diffuser_size, "Y")
    link(ng, diffuser_height, 0, diffuser_size, "Z")

    diffuser = create_cube(ng, name="Diffuser", location=(-400, -200))
    link(ng, diffuser_size, "Vector", diffuser, "Size")

    # Position diffuser at top of channel
    diffuser_z = create_math(ng, 'DIVIDE', name="Diffuser Z", location=(-500, -280))
    link(ng, group_in, "Height", diffuser_z, 0)
    set_default(diffuser_z, 1, 2.5)  # Slight offset up

    diffuser_pos = create_combine_xyz(ng, name="Diffuser Pos", location=(-400, -280))
    link(ng, diffuser_z, 0, diffuser_pos, "Z")

    diffuser_transform = create_transform(ng, name="Diffuser Transform", location=(-300, -200))
    link(ng, diffuser, "Mesh", diffuser_transform, "Geometry")
    link(ng, diffuser_pos, "Vector", diffuser_transform, "Translation")

    # Diffuser uses a translucent version of LED material (or separate)
    diffuser_mat = create_set_material(ng, name="Diffuser Mat", location=(-200, -200))
    link(ng, diffuser_transform, "Geometry", diffuser_mat, "Geometry")
    link(ng, group_in, "LED Material", diffuser_mat, "Material")

    # Switch diffuser on/off
    switch_diffuser = create_switch(ng, 'GEOMETRY', name="Diffuser Switch", location=(0, -200))
    link(ng, group_in, "Has Diffuser", switch_diffuser, "Switch")
    link(ng, diffuser_mat, "Geometry", switch_diffuser, "True")

    # ============ JOIN COMPONENTS ============
    join_all = create_join_geometry(ng, name="Join All", location=(200, 0))
    link(ng, channel_mat, "Geometry", join_all, "Geometry")
    link(ng, led_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_diffuser, "Output", join_all, "Geometry")

    # ============ MOUNT TYPE ROTATION ============
    # Type 0: Surface mount (no rotation)
    # Type 1: Recessed (no rotation, just different position - handled by parent)
    # Type 2: Angled 45 degrees

    # Create angled version
    angled_rotation = create_combine_xyz(ng, name="Angled Rotation", location=(200, -150))
    set_default(angled_rotation, "X", 0.785398)  # 45 degrees in radians

    angled_transform = create_transform(ng, name="Angled Transform", location=(300, -100))
    link(ng, join_all, "Geometry", angled_transform, "Geometry")
    link(ng, angled_rotation, "Vector", angled_transform, "Rotation")

    # Switch based on mount type
    is_angled = create_compare(ng, 'EQUAL', 'INT', name="Is Angled", location=(300, -200))
    link(ng, group_in, "Mount Type", is_angled, 2)
    set_default(is_angled, 3, 2)

    switch_mount = create_switch(ng, 'GEOMETRY', name="Mount Switch", location=(400, 0))
    link(ng, is_angled, "Result", switch_mount, "Switch")
    link(ng, join_all, "Geometry", switch_mount, "False")
    link(ng, angled_transform, "Geometry", switch_mount, "True")

    # ============ OUTPUT ============
    link(ng, switch_mount, "Output", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/led_strip.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the LEDStrip node group applied."""
    if nodegroup is None:
        nodegroup = create_led_strip_nodegroup()

    mesh = bpy.data.meshes.new("LEDStrip_Test")
    obj = bpy.data.objects.new("LEDStrip_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_led_strip_nodegroup()
    print(f"Created node group: {ng.name}")
