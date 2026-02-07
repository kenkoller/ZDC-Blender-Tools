# Shelf Array node group generator
# System component: Distributes multiple shelves within cabinet interior
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
    create_math,
    create_combine_xyz,
    create_set_material,
    create_switch,
    create_compare,
    link,
    set_default,
    add_metadata,
)


def create_shelf_array_nodegroup():
    """Generate the ShelfArray node group.

    Distributes shelves evenly within a cabinet interior space.
    Uses Geometry Nodes instancing for efficiency.
    Z-up coordinate system with shelves horizontal.
    """
    ng = create_node_group("ShelfArray")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    options_panel = create_panel(ng, "Options")

    # Dimension inputs (typically passed from CabinetBox)
    add_float_socket(ng, "Interior Width", default=0.564, min_val=0.1, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Interior Height", default=0.684, min_val=0.1, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Interior Depth", default=0.544, min_val=0.1, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Shelf options
    add_int_socket(ng, "Shelf Count", default=2, min_val=0, max_val=10, panel=options_panel)
    add_float_socket(ng, "Shelf Thickness", default=0.018, min_val=0.01, max_val=0.025,
                     subtype='DISTANCE', panel=options_panel)
    add_float_socket(ng, "Shelf Inset", default=0.02, min_val=0.0, max_val=0.1,
                     subtype='DISTANCE', panel=options_panel)

    # Material
    add_material_socket(ng, "Material")

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(600, 0))

    # Shelf dimensions
    # Width slightly smaller for fit
    shelf_width = create_math(ng, 'SUBTRACT', name="Shelf Width", location=(-600, 200))
    link(ng, group_in, "Interior Width", shelf_width, 0)
    set_default(shelf_width, 1, 0.002)

    # Depth with inset from front
    shelf_depth = create_math(ng, 'SUBTRACT', name="Shelf Depth", location=(-600, 100))
    link(ng, group_in, "Interior Depth", shelf_depth, 0)
    link(ng, group_in, "Shelf Inset", shelf_depth, 1)

    # Create a mesh line for shelf positions (vertical line along Z)
    mesh_line = ng.nodes.new('GeometryNodeMeshLine')
    mesh_line.name = "Shelf Positions"
    mesh_line.location = (-400, 0)
    mesh_line.mode = 'END_POINTS'

    # Count = shelf_count (need at least 1 point)
    count_max = create_math(ng, 'MAXIMUM', name="Count Max", location=(-550, -100))
    link(ng, group_in, "Shelf Count", count_max, 0)
    set_default(count_max, 1, 1)
    link(ng, count_max, 0, mesh_line, "Count")

    # Calculate spacing along Z axis
    # Available height for shelves = interior_height - shelf_thickness
    avail_height = create_math(ng, 'SUBTRACT', name="Avail Height", location=(-600, -200))
    link(ng, group_in, "Interior Height", avail_height, 0)
    link(ng, group_in, "Shelf Thickness", avail_height, 1)

    # Spacing = avail_height / (shelf_count + 1)
    count_plus1 = create_math(ng, 'ADD', name="Count+1", location=(-550, -300))
    link(ng, group_in, "Shelf Count", count_plus1, 0)
    set_default(count_plus1, 1, 1.0)

    spacing = create_math(ng, 'DIVIDE', name="Spacing", location=(-450, -300))
    link(ng, avail_height, 0, spacing, 0)
    link(ng, count_plus1, 0, spacing, 1)

    # Start Z = panel_thickness + spacing (first shelf position from bottom)
    start_z = create_math(ng, 'ADD', name="Start Z", location=(-450, -400))
    link(ng, group_in, "Panel Thickness", start_z, 0)
    link(ng, spacing, 0, start_z, 1)

    # End Z offset = spacing * (shelf_count - 1)
    count_minus1 = create_math(ng, 'SUBTRACT', name="Count-1", location=(-550, -500))
    link(ng, group_in, "Shelf Count", count_minus1, 0)
    set_default(count_minus1, 1, 1.0)

    end_z_offset = create_math(ng, 'MULTIPLY', name="End Z Offset", location=(-450, -500))
    link(ng, spacing, 0, end_z_offset, 0)
    link(ng, count_minus1, 0, end_z_offset, 1)

    # Y position = -depth/2 - panel_thickness/2 - inset/2 (centered in interior, front at Y=0)
    depth_half_neg = create_math(ng, 'DIVIDE', name="Depth Half Neg", location=(-600, -600))
    link(ng, group_in, "Interior Depth", depth_half_neg, 0)
    set_default(depth_half_neg, 1, -2.0)

    inset_half = create_math(ng, 'DIVIDE', name="Inset Half", location=(-600, -700))
    link(ng, group_in, "Shelf Inset", inset_half, 0)
    set_default(inset_half, 1, -2.0)

    shelf_y = create_math(ng, 'ADD', name="Shelf Y", location=(-500, -650))
    link(ng, depth_half_neg, 0, shelf_y, 0)
    link(ng, inset_half, 0, shelf_y, 1)

    # Set line start and end points (vertical line)
    start_pos = create_combine_xyz(ng, name="Start Pos", location=(-300, -200))
    link(ng, shelf_y, 0, start_pos, "Y")
    link(ng, start_z, 0, start_pos, "Z")

    end_offset = create_combine_xyz(ng, name="End Offset", location=(-300, -400))
    link(ng, end_z_offset, 0, end_offset, "Z")

    link(ng, start_pos, "Vector", mesh_line, "Start Location")
    link(ng, end_offset, "Vector", mesh_line, "Offset")

    # Create single shelf geometry (cube)
    # Size: width (X) x depth (Y) x thickness (Z)
    shelf_cube = ng.nodes.new('GeometryNodeMeshCube')
    shelf_cube.name = "Shelf Template"
    shelf_cube.location = (-200, 200)

    shelf_size = create_combine_xyz(ng, name="Shelf Size", location=(-350, 250))
    link(ng, shelf_width, 0, shelf_size, "X")
    link(ng, shelf_depth, 0, shelf_size, "Y")
    link(ng, group_in, "Shelf Thickness", shelf_size, "Z")
    link(ng, shelf_size, "Vector", shelf_cube, "Size")

    # Instance shelves on points
    instance_on_points = ng.nodes.new('GeometryNodeInstanceOnPoints')
    instance_on_points.name = "Instance Shelves"
    instance_on_points.location = (0, 0)

    link(ng, mesh_line, "Mesh", instance_on_points, "Points")
    link(ng, shelf_cube, "Mesh", instance_on_points, "Instance")

    # Realize instances
    realize = ng.nodes.new('GeometryNodeRealizeInstances')
    realize.name = "Realize"
    realize.location = (200, 0)
    link(ng, instance_on_points, "Instances", realize, "Geometry")

    # Set material
    set_mat = create_set_material(ng, name="Set Material", location=(400, 0))
    link(ng, realize, "Geometry", set_mat, "Geometry")
    link(ng, group_in, "Material", set_mat, "Material")

    # Handle zero shelves case with switch
    switch_zero = create_switch(ng, 'GEOMETRY', name="Zero Check", location=(500, 100))

    # Compare shelf count > 0
    count_gt_zero = create_compare(ng, 'GREATER_THAN', 'INT', name="Count > 0", location=(300, 200))
    link(ng, group_in, "Shelf Count", count_gt_zero, 2)
    set_default(count_gt_zero, 3, 0)

    link(ng, count_gt_zero, "Result", switch_zero, "Switch")
    link(ng, set_mat, "Geometry", switch_zero, "True")

    # Output
    link(ng, switch_zero, "Output", group_out, "Geometry")

    add_metadata(ng, version="1.1.0", script_path="src/nodes/systems/shelf_array.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the ShelfArray node group applied."""
    if nodegroup is None:
        nodegroup = create_shelf_array_nodegroup()

    mesh = bpy.data.meshes.new("ShelfArray_Test")
    obj = bpy.data.objects.new("ShelfArray_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_shelf_array_nodegroup()
    print(f"Created node group: {ng.name}")
