# Spice Rack node group generator
# Atomic component: Pull-out spice rack insert
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
    link,
    set_default,
    add_metadata,
)


def create_spice_rack_nodegroup():
    """Generate the SpiceRack node group.

    Creates a pull-out spice rack insert with:
    - Multiple shelves/tiers
    - Front lip to hold bottles
    - Narrow form factor for door or cabinet mount

    Inputs:
        Width: Rack width
        Depth: Rack depth
        Height: Total rack height
        Tier Count: Number of shelf tiers
        Extension: 0-1 (how far pulled out)
        Frame Material: Frame/shelf material
        Lip Material: Front lip material

    Outputs:
        Geometry: Spice rack mesh
    """
    ng = create_node_group("SpiceRack")

    # Create interface
    dims_panel = create_panel(ng, "Dimensions")
    options_panel = create_panel(ng, "Options")
    anim_panel = create_panel(ng, "Animation")
    materials_panel = create_panel(ng, "Materials")

    add_float_socket(ng, "Width", default=0.1, min_val=0.06, max_val=0.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.5, min_val=0.3, max_val=0.6,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=0.6, min_val=0.3, max_val=0.9,
                     subtype='DISTANCE', panel=dims_panel)
    add_int_socket(ng, "Tier Count", default=4, min_val=2, max_val=8, panel=options_panel)
    add_float_socket(ng, "Extension", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='FACTOR', panel=anim_panel)
    add_material_socket(ng, "Frame Material", panel=materials_panel)
    add_material_socket(ng, "Lip Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1000, 0))
    group_out = create_group_output(ng, location=(1000, 0))

    # ============ FRAME DIMENSIONS ============
    frame_thick = 0.008  # Frame thickness
    lip_height = 0.025   # Front lip to hold bottles

    # ============ SIDE PANELS ============
    side_size = create_combine_xyz(ng, name="Side Size", location=(-700, 300))
    set_default(side_size, "X", frame_thick)
    link(ng, group_in, "Depth", side_size, "Y")
    link(ng, group_in, "Height", side_size, "Z")

    side_panel = create_cube(ng, name="Side Panel", location=(-600, 300))
    link(ng, side_size, "Vector", side_panel, "Size")

    # Left side position
    left_x = create_math(ng, 'DIVIDE', name="Left X", location=(-700, 200))
    link(ng, group_in, "Width", left_x, 0)
    set_default(left_x, 1, -2.0)
    left_x_offset = create_math(ng, 'ADD', name="Left X Offset", location=(-600, 200))
    link(ng, left_x, 0, left_x_offset, 0)
    set_default(left_x_offset, 1, frame_thick / 2)

    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-700, 150))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-700, 100))
    link(ng, group_in, "Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-500, 200))
    link(ng, left_x_offset, 0, left_pos, "X")
    link(ng, depth_half, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Side", location=(-400, 300))
    link(ng, side_panel, "Mesh", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    # Right side position
    right_x = create_math(ng, 'DIVIDE', name="Right X", location=(-700, 50))
    link(ng, group_in, "Width", right_x, 0)
    set_default(right_x, 1, 2.0)
    right_x_offset = create_math(ng, 'SUBTRACT', name="Right X Offset", location=(-600, 50))
    link(ng, right_x, 0, right_x_offset, 0)
    set_default(right_x_offset, 1, frame_thick / 2)

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-500, 50))
    link(ng, right_x_offset, 0, right_pos, "X")
    link(ng, depth_half, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Side", location=(-400, 100))
    link(ng, side_panel, "Mesh", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    # ============ SHELVES (TIERS) ============
    # Calculate interior width
    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-700, -100))
    link(ng, group_in, "Width", interior_width, 0)
    set_default(interior_width, 1, frame_thick * 2)

    shelf_size = create_combine_xyz(ng, name="Shelf Size", location=(-600, -150))
    link(ng, interior_width, 0, shelf_size, "X")
    link(ng, group_in, "Depth", shelf_size, "Y")
    set_default(shelf_size, "Z", frame_thick)

    shelf_cube = create_cube(ng, name="Shelf Cube", location=(-500, -150))
    link(ng, shelf_size, "Vector", shelf_cube, "Size")

    # Dynamic tier placement using Instance on Points
    # Tier spacing = Height / Tier Count
    tier_spacing = create_math(ng, 'DIVIDE', name="Tier Spacing", location=(-700, -250))
    link(ng, group_in, "Height", tier_spacing, 0)
    link(ng, group_in, "Tier Count", tier_spacing, 1)

    # Ensure at least 1 point for the mesh line
    tier_count_max = create_math(ng, 'MAXIMUM', name="Tier Count Max", location=(-600, -300))
    link(ng, group_in, "Tier Count", tier_count_max, 0)
    set_default(tier_count_max, 1, 1)

    # Create mesh line for shelf positions (vertical along Z)
    shelf_line = ng.nodes.new('GeometryNodeMeshLine')
    shelf_line.name = "Shelf Positions"
    shelf_line.location = (-400, -250)
    shelf_line.mode = 'END_POINTS'

    link(ng, tier_count_max, 0, shelf_line, "Count")

    # Start position: bottom shelf at Z = frame_thick/2, Y = depth_half
    start_z = create_math(ng, 'ADD', name="Start Z", location=(-600, -400))
    set_default(start_z, 0, 0.0)
    set_default(start_z, 1, frame_thick / 2)

    shelf_start = create_combine_xyz(ng, name="Shelf Start", location=(-500, -350))
    set_default(shelf_start, "X", 0.0)
    link(ng, depth_half, 0, shelf_start, "Y")
    link(ng, start_z, 0, shelf_start, "Z")

    # End offset: (tier_count - 1) * tier_spacing along Z
    tier_count_minus1 = create_math(ng, 'SUBTRACT', name="Count-1", location=(-600, -500))
    link(ng, group_in, "Tier Count", tier_count_minus1, 0)
    set_default(tier_count_minus1, 1, 1.0)

    end_z_offset = create_math(ng, 'MULTIPLY', name="End Z Offset", location=(-500, -500))
    link(ng, tier_spacing, 0, end_z_offset, 0)
    link(ng, tier_count_minus1, 0, end_z_offset, 1)

    shelf_end_offset = create_combine_xyz(ng, name="Shelf End Offset", location=(-400, -450))
    set_default(shelf_end_offset, "X", 0.0)
    set_default(shelf_end_offset, "Y", 0.0)
    link(ng, end_z_offset, 0, shelf_end_offset, "Z")

    link(ng, shelf_start, "Vector", shelf_line, "Start Location")
    link(ng, shelf_end_offset, "Vector", shelf_line, "Offset")

    # Instance shelves on points
    shelf_instance = ng.nodes.new('GeometryNodeInstanceOnPoints')
    shelf_instance.name = "Instance Shelves"
    shelf_instance.location = (-200, -200)

    link(ng, shelf_line, "Mesh", shelf_instance, "Points")
    link(ng, shelf_cube, "Mesh", shelf_instance, "Instance")

    shelf_realize = ng.nodes.new('GeometryNodeRealizeInstances')
    shelf_realize.name = "Realize Shelves"
    shelf_realize.location = (-50, -200)
    link(ng, shelf_instance, "Instances", shelf_realize, "Geometry")

    join_shelves = create_join_geometry(ng, name="Join Shelves", location=(-100, -300))
    link(ng, shelf_realize, "Geometry", join_shelves, "Geometry")

    # ============ FRONT LIPS ============
    lip_size = create_combine_xyz(ng, name="Lip Size", location=(-600, -650))
    link(ng, interior_width, 0, lip_size, "X")
    set_default(lip_size, "Y", frame_thick)
    set_default(lip_size, "Z", lip_height)

    lip_cube = create_cube(ng, name="Lip Cube", location=(-500, -650))
    link(ng, lip_size, "Vector", lip_cube, "Size")

    # Lip positions: same Z as shelves but shifted Y to front and Z up by lip_height/2
    lip_y_pos = create_math(ng, 'ADD', name="Lip Y", location=(-500, -700))
    set_default(lip_y_pos, 0, -frame_thick / 2)
    set_default(lip_y_pos, 1, 0.0)

    lip_z_add = create_math(ng, 'ADD', name="Lip Z Offset", location=(-500, -750))
    set_default(lip_z_add, 0, frame_thick / 2)
    set_default(lip_z_add, 1, lip_height / 2)

    lip_start = create_combine_xyz(ng, name="Lip Start", location=(-400, -700))
    set_default(lip_start, "X", 0.0)
    link(ng, lip_y_pos, 0, lip_start, "Y")
    link(ng, lip_z_add, 0, lip_start, "Z")

    # Lip line uses same count and Z offsets as shelves
    lip_line = ng.nodes.new('GeometryNodeMeshLine')
    lip_line.name = "Lip Positions"
    lip_line.location = (-300, -700)
    lip_line.mode = 'END_POINTS'

    link(ng, tier_count_max, 0, lip_line, "Count")
    link(ng, lip_start, "Vector", lip_line, "Start Location")
    link(ng, shelf_end_offset, "Vector", lip_line, "Offset")

    # Instance lips on points
    lip_instance = ng.nodes.new('GeometryNodeInstanceOnPoints')
    lip_instance.name = "Instance Lips"
    lip_instance.location = (-100, -700)

    link(ng, lip_line, "Mesh", lip_instance, "Points")
    link(ng, lip_cube, "Mesh", lip_instance, "Instance")

    lip_realize = ng.nodes.new('GeometryNodeRealizeInstances')
    lip_realize.name = "Realize Lips"
    lip_realize.location = (50, -700)
    link(ng, lip_instance, "Instances", lip_realize, "Geometry")

    # Set lip material
    lip_mat = create_set_material(ng, name="Lip Material", location=(150, -800))
    link(ng, lip_realize, "Geometry", lip_mat, "Geometry")
    link(ng, group_in, "Lip Material", lip_mat, "Material")

    # ============ JOIN ALL FRAME PARTS ============
    join_frame = create_join_geometry(ng, name="Join Frame", location=(100, 0))
    link(ng, left_transform, "Geometry", join_frame, "Geometry")
    link(ng, right_transform, "Geometry", join_frame, "Geometry")
    link(ng, join_shelves, "Geometry", join_frame, "Geometry")

    # Set frame material
    frame_mat = create_set_material(ng, name="Frame Material", location=(250, 0))
    link(ng, join_frame, "Geometry", frame_mat, "Geometry")
    link(ng, group_in, "Frame Material", frame_mat, "Material")

    # Join frame and lips
    join_all = create_join_geometry(ng, name="Join All", location=(400, 0))
    link(ng, frame_mat, "Geometry", join_all, "Geometry")
    link(ng, lip_mat, "Geometry", join_all, "Geometry")

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

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/spice_rack.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the SpiceRack node group applied."""
    if nodegroup is None:
        nodegroup = create_spice_rack_nodegroup()

    mesh = bpy.data.meshes.new("SpiceRack_Test")
    obj = bpy.data.objects.new("SpiceRack_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_spice_rack_nodegroup()
    print(f"Created node group: {ng.name}")
