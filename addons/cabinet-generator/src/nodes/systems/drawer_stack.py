# Drawer Stack node group generator
# System component: Creates a stack of drawers for cabinet front
# Coordinate system: X=width, Y=depth, Z=height (Z-up, front at Y=0)

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
    create_bevel,
    link,
    set_default,
    add_metadata,
)


def create_drawer_stack_nodegroup():
    """Generate the DrawerStack node group.

    Creates a vertical stack of drawer fronts with handles.
    Drawers stack vertically along Z axis.

    Coordinate system:
    - Drawer fronts face positive Y
    - Origin at cabinet front-bottom-center
    """
    ng = create_node_group("DrawerStack")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    options_panel = create_panel(ng, "Options")
    handle_panel = create_panel(ng, "Handle")
    anim_panel = create_panel(ng, "Animation")
    materials_panel = create_panel(ng, "Materials")

    # Dimension inputs
    add_float_socket(ng, "Opening Width", default=0.564, min_val=0.1, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Opening Height", default=0.684, min_val=0.1, max_val=1.0,
                     subtype='DISTANCE', panel=dims_panel)
    add_int_socket(ng, "Drawer Count", default=3, min_val=1, max_val=6, panel=dims_panel)
    add_float_socket(ng, "Front Thickness", default=0.018, min_val=0.015, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Drawer Gap", default=0.003, min_val=0.001, max_val=0.01,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Overlay", default=0.018, min_val=0.0, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    # Handle options
    add_float_socket(ng, "Handle Length", default=0.128, min_val=0.03, max_val=0.3,
                     subtype='DISTANCE', panel=handle_panel)
    add_float_socket(ng, "Handle Width", default=0.012, min_val=0.006, max_val=0.025,
                     subtype='DISTANCE', panel=handle_panel)
    add_float_socket(ng, "Handle Projection", default=0.03, min_val=0.015, max_val=0.06,
                     subtype='DISTANCE', panel=handle_panel)
    add_float_socket(ng, "Handle Offset Z", default=0.0, min_val=-0.1, max_val=0.1,
                     subtype='DISTANCE', panel=handle_panel)

    # Animation
    add_float_socket(ng, "Drawer Open", default=0.0, min_val=0.0, max_val=1.0,
                     subtype='FACTOR', panel=anim_panel)
    add_float_socket(ng, "Drawer Depth", default=0.4, min_val=0.1, max_val=0.6,
                     subtype='DISTANCE', panel=anim_panel)

    # Bevel options
    bevel_panel = create_panel(ng, "Bevel")
    add_float_socket(ng, "Bevel Width", default=0.001, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=bevel_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=bevel_panel)

    # Materials
    add_material_socket(ng, "Front Material", panel=materials_panel)
    add_material_socket(ng, "Handle Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1000, 0))
    group_out = create_group_output(ng, location=(800, 0))

    # ============ CALCULATE DRAWER DIMENSIONS ============
    # Drawer width = opening_width + 2*overlay - gap
    overlay_x2 = create_math(ng, 'MULTIPLY', name="Overlay x2", location=(-800, 300))
    link(ng, group_in, "Overlay", overlay_x2, 0)
    set_default(overlay_x2, 1, 2.0)

    drawer_width_base = create_math(ng, 'ADD', name="Drawer Width Base", location=(-700, 300))
    link(ng, group_in, "Opening Width", drawer_width_base, 0)
    link(ng, overlay_x2, 0, drawer_width_base, 1)

    drawer_width = create_math(ng, 'SUBTRACT', name="Drawer Width", location=(-600, 300))
    link(ng, drawer_width_base, 0, drawer_width, 0)
    link(ng, group_in, "Drawer Gap", drawer_width, 1)

    # Total available height = opening_height + 2*overlay
    total_height = create_math(ng, 'ADD', name="Total Height", location=(-700, 200))
    link(ng, group_in, "Opening Height", total_height, 0)
    link(ng, overlay_x2, 0, total_height, 1)

    # Gap space = (drawer_count + 1) * gap
    count_plus1 = create_math(ng, 'ADD', name="Count+1", location=(-700, 100))
    link(ng, group_in, "Drawer Count", count_plus1, 0)
    set_default(count_plus1, 1, 1.0)

    gap_space = create_math(ng, 'MULTIPLY', name="Gap Space", location=(-600, 100))
    link(ng, count_plus1, 0, gap_space, 0)
    link(ng, group_in, "Drawer Gap", gap_space, 1)

    # Usable height = total_height - gap_space
    usable_height = create_math(ng, 'SUBTRACT', name="Usable Height", location=(-500, 150))
    link(ng, total_height, 0, usable_height, 0)
    link(ng, gap_space, 0, usable_height, 1)

    # Single drawer height = usable_height / drawer_count
    single_height = create_math(ng, 'DIVIDE', name="Single Height", location=(-400, 150))
    link(ng, usable_height, 0, single_height, 0)
    link(ng, group_in, "Drawer Count", single_height, 1)

    # ============ USE MESH LINE + INSTANCE FOR DRAWERS ============
    # Create points for drawer positions along Z
    mesh_line = ng.nodes.new('GeometryNodeMeshLine')
    mesh_line.name = "Drawer Positions"
    mesh_line.location = (-200, 0)
    mesh_line.mode = 'END_POINTS'

    link(ng, group_in, "Drawer Count", mesh_line, "Count")

    # Spacing = single_height + gap
    spacing = create_math(ng, 'ADD', name="Spacing", location=(-300, -100))
    link(ng, single_height, 0, spacing, 0)
    link(ng, group_in, "Drawer Gap", spacing, 1)

    # Start Z = panel_thickness + gap + single_height/2
    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-400, -200))
    link(ng, single_height, 0, height_half, 0)
    set_default(height_half, 1, 2.0)

    start_z = create_math(ng, 'ADD', name="Start Z 1", location=(-300, -200))
    link(ng, group_in, "Panel Thickness", start_z, 0)
    link(ng, group_in, "Drawer Gap", start_z, 1)

    start_z_final = create_math(ng, 'ADD', name="Start Z Final", location=(-200, -200))
    link(ng, start_z, 0, start_z_final, 0)
    link(ng, height_half, 0, start_z_final, 1)

    # End Z offset = spacing * (drawer_count - 1)
    count_minus1 = create_math(ng, 'SUBTRACT', name="Count-1", location=(-400, -300))
    link(ng, group_in, "Drawer Count", count_minus1, 0)
    set_default(count_minus1, 1, 1.0)

    end_z_offset = create_math(ng, 'MULTIPLY', name="End Z Offset", location=(-300, -300))
    link(ng, spacing, 0, end_z_offset, 0)
    link(ng, count_minus1, 0, end_z_offset, 1)

    # Y position = front_thickness/2 (front face at Y=0)
    front_y = create_math(ng, 'DIVIDE', name="Front Y", location=(-400, -400))
    link(ng, group_in, "Front Thickness", front_y, 0)
    set_default(front_y, 1, 2.0)

    start_pos = create_combine_xyz(ng, name="Start Pos", location=(-100, -150))
    link(ng, front_y, 0, start_pos, "Y")
    link(ng, start_z_final, 0, start_pos, "Z")

    end_offset = create_combine_xyz(ng, name="End Offset", location=(-100, -300))
    link(ng, end_z_offset, 0, end_offset, "Z")

    link(ng, start_pos, "Vector", mesh_line, "Start Location")
    link(ng, end_offset, "Vector", mesh_line, "Offset")

    # ============ DRAWER FRONT TEMPLATE ============
    # Size: width (X) x thickness (Y) x height (Z)
    drawer_front = create_cube(ng, name="Drawer Front", location=(50, 300))
    front_size = create_combine_xyz(ng, name="Front Size", location=(-100, 350))

    link(ng, drawer_width, 0, front_size, "X")
    link(ng, group_in, "Front Thickness", front_size, "Y")
    link(ng, single_height, 0, front_size, "Z")
    link(ng, front_size, "Vector", drawer_front, "Size")

    # ============ HANDLE TEMPLATE ============
    handle = create_cube(ng, name="Handle", location=(50, 150))
    handle_size = create_combine_xyz(ng, name="Handle Size", location=(-100, 180))

    link(ng, group_in, "Handle Length", handle_size, "X")
    link(ng, group_in, "Handle Width", handle_size, "Y")
    link(ng, group_in, "Handle Projection", handle_size, "Z")
    link(ng, handle_size, "Vector", handle, "Size")

    # Handle position relative to drawer front (centered, on front face)
    handle_y = create_math(ng, 'ADD', name="Handle Y", location=(-100, 100))
    proj_half = create_math(ng, 'DIVIDE', name="Proj Half", location=(-200, 100))
    link(ng, group_in, "Handle Projection", proj_half, 0)
    set_default(proj_half, 1, 2.0)
    link(ng, group_in, "Front Thickness", handle_y, 0)
    link(ng, proj_half, 0, handle_y, 1)

    handle_pos = create_combine_xyz(ng, name="Handle Pos", location=(50, 80))
    link(ng, handle_y, 0, handle_pos, "Y")
    link(ng, group_in, "Handle Offset Z", handle_pos, "Z")

    handle_transform = create_transform(ng, name="Handle Transform", location=(200, 150))
    link(ng, handle_pos, "Vector", handle_transform, "Translation")
    link(ng, handle, "Mesh", handle_transform, "Geometry")

    # Join front + handle as single instance
    join_drawer = create_join_geometry(ng, name="Join Drawer", location=(300, 250))

    # Set materials
    front_mat = create_set_material(ng, name="Front Mat", location=(200, 350))
    link(ng, drawer_front, "Mesh", front_mat, "Geometry")
    link(ng, group_in, "Front Material", front_mat, "Material")

    handle_mat = create_set_material(ng, name="Handle Mat", location=(300, 150))
    link(ng, handle_transform, "Geometry", handle_mat, "Geometry")
    link(ng, group_in, "Handle Material", handle_mat, "Material")

    link(ng, front_mat, "Geometry", join_drawer, "Geometry")
    link(ng, handle_mat, "Geometry", join_drawer, "Geometry")

    # Instance drawers on points
    instance_on_points = ng.nodes.new('GeometryNodeInstanceOnPoints')
    instance_on_points.name = "Instance Drawers"
    instance_on_points.location = (450, 0)

    link(ng, mesh_line, "Mesh", instance_on_points, "Points")
    link(ng, join_drawer, "Geometry", instance_on_points, "Instance")

    # Realize instances
    realize = ng.nodes.new('GeometryNodeRealizeInstances')
    realize.name = "Realize"
    realize.location = (600, 0)
    link(ng, instance_on_points, "Instances", realize, "Geometry")

    # ============ DRAWER OPEN ANIMATION ============
    # Calculate Y offset: drawer_open * drawer_depth (positive Y to pull toward front)
    open_offset = create_math(ng, 'MULTIPLY', name="Open Offset", location=(700, -100))
    link(ng, group_in, "Drawer Open", open_offset, 0)
    link(ng, group_in, "Drawer Depth", open_offset, 1)

    open_pos = create_combine_xyz(ng, name="Open Pos", location=(800, -100))
    link(ng, open_offset, 0, open_pos, "Y")

    open_transform = create_transform(ng, name="Open Transform", location=(900, 0))
    link(ng, realize, "Geometry", open_transform, "Geometry")
    link(ng, open_pos, "Vector", open_transform, "Translation")

    # ============ BEVEL EDGES ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(1000, 0))
    if bevel is not None:
        link(ng, open_transform, "Geometry", bevel, "Mesh")
        link(ng, group_in, "Bevel Width", bevel, "Width")
        link(ng, group_in, "Bevel Segments", bevel, "Segments")
        final_geo = bevel
        final_socket = "Mesh"
    else:
        final_geo = open_transform
        final_socket = "Geometry"

    # Output
    link(ng, final_geo, final_socket, group_out, "Geometry")

    add_metadata(ng, version="1.4.0", script_path="src/nodes/systems/drawer_stack.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the DrawerStack node group applied."""
    if nodegroup is None:
        nodegroup = create_drawer_stack_nodegroup()

    mesh = bpy.data.meshes.new("DrawerStack_Test")
    obj = bpy.data.objects.new("DrawerStack_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_drawer_stack_nodegroup()
    print(f"Created node group: {ng.name}")
