# Open Shelving Unit node group generator
# System component: Open cabinet with exposed shelves (no doors)
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
    create_bevel,
    link,
    set_default,
    add_metadata,
)


def create_open_shelving_nodegroup():
    """Generate the OpenShelving node group.

    Open shelving unit with:
    - Exposed shelves (no doors or drawer fronts)
    - Optional side panels (can be bracket-mounted)
    - Optional back panel
    - Adjustable shelf count

    Ideal for:
    - Display cabinets
    - Floating shelves
    - Pantry organization
    - Laundry room storage

    Coordinate system:
    - X = width (left-right)
    - Y = depth (front-back, negative Y is front)
    - Z = height (floor to ceiling)
    - Origin at front-bottom-center (floor level)
    """
    ng = create_node_group("OpenShelving")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    shelves_panel = create_panel(ng, "Shelves")
    options_panel = create_panel(ng, "Options")
    bevel_panel = create_panel(ng, "Bevel")
    materials_panel = create_panel(ng, "Materials")

    # Dimensions
    add_float_socket(ng, "Width", default=0.8, min_val=0.3, max_val=1.5,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Height", default=1.2, min_val=0.4, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.3, min_val=0.15, max_val=0.5,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.025, min_val=0.018, max_val=0.04,
                     subtype='DISTANCE', panel=dims_panel)

    # Shelves
    add_int_socket(ng, "Shelf Count", default=4, min_val=2, max_val=10, panel=shelves_panel)
    add_bool_socket(ng, "Include Top", default=True, panel=shelves_panel)
    add_bool_socket(ng, "Include Bottom", default=True, panel=shelves_panel)

    # Options
    add_bool_socket(ng, "Has Sides", default=True, panel=options_panel)
    add_bool_socket(ng, "Has Back", default=False, panel=options_panel)
    add_bool_socket(ng, "Front Lip", default=False, panel=options_panel)
    add_float_socket(ng, "Lip Height", default=0.025, min_val=0.015, max_val=0.05,
                     subtype='DISTANCE', panel=options_panel)

    # Bevel
    add_float_socket(ng, "Bevel Width", default=0.002, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=bevel_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=bevel_panel)

    # Materials
    add_material_socket(ng, "Shelf Material", panel=materials_panel)
    add_material_socket(ng, "Side Material", panel=materials_panel)
    add_material_socket(ng, "Back Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1200, 0))
    group_out = create_group_output(ng, location=(1200, 0))

    # ============ CALCULATE DIMENSIONS ============
    panel_x2 = create_math(ng, 'MULTIPLY', name="Panel x2", location=(-1000, -400))
    link(ng, group_in, "Panel Thickness", panel_x2, 0)
    set_default(panel_x2, 1, 2.0)

    # Interior width (between sides if sides exist)
    interior_width = create_math(ng, 'SUBTRACT', name="Interior Width", location=(-900, -400))
    link(ng, group_in, "Width", interior_width, 0)
    link(ng, panel_x2, 0, interior_width, 1)

    depth_half = create_math(ng, 'DIVIDE', name="Depth Half", location=(-1000, -500))
    link(ng, group_in, "Depth", depth_half, 0)
    set_default(depth_half, 1, -2.0)

    height_half = create_math(ng, 'DIVIDE', name="Height Half", location=(-1000, -550))
    link(ng, group_in, "Height", height_half, 0)
    set_default(height_half, 1, 2.0)

    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-1000, -600))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)

    # ============ CALCULATE SHELF SPACING ============
    # Available height for shelves
    available_height = create_math(ng, 'SUBTRACT', name="Available Height", location=(-900, -700))
    link(ng, group_in, "Height", available_height, 0)
    link(ng, panel_x2, 0, available_height, 1)  # Subtract top and bottom thickness

    # Spacing between shelves = available_height / (shelf_count - 1)
    shelf_count_minus_1 = create_math(ng, 'SUBTRACT', name="Shelf Count - 1", location=(-800, -750))
    link(ng, group_in, "Shelf Count", shelf_count_minus_1, 0)
    set_default(shelf_count_minus_1, 1, 1.0)

    shelf_spacing = create_math(ng, 'DIVIDE', name="Shelf Spacing", location=(-700, -750))
    link(ng, available_height, 0, shelf_spacing, 0)
    link(ng, shelf_count_minus_1, 0, shelf_spacing, 1)

    # ============ LEFT SIDE PANEL ============
    left_size = create_combine_xyz(ng, name="Left Size", location=(-800, 400))
    link(ng, group_in, "Panel Thickness", left_size, "X")
    link(ng, group_in, "Depth", left_size, "Y")
    link(ng, group_in, "Height", left_size, "Z")

    left_side = create_cube(ng, name="Left Side", location=(-700, 400))
    link(ng, left_size, "Vector", left_side, "Size")

    left_x = create_math(ng, 'SUBTRACT', name="Left X Sub", location=(-800, 350))
    link(ng, group_in, "Width", left_x, 0)
    link(ng, group_in, "Panel Thickness", left_x, 1)
    left_x_div = create_math(ng, 'DIVIDE', name="Left X Div", location=(-700, 350))
    link(ng, left_x, 0, left_x_div, 0)
    set_default(left_x_div, 1, 2.0)
    left_x_neg = create_math(ng, 'MULTIPLY', name="Left X Neg", location=(-600, 350))
    link(ng, left_x_div, 0, left_x_neg, 0)
    set_default(left_x_neg, 1, -1.0)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-600, 400))
    link(ng, left_x_neg, 0, left_pos, "X")
    link(ng, depth_half, 0, left_pos, "Y")
    link(ng, height_half, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Transform", location=(-500, 400))
    link(ng, left_side, "Mesh", left_transform, "Geometry")
    link(ng, left_pos, "Vector", left_transform, "Translation")

    left_mat = create_set_material(ng, name="Left Material", location=(-350, 400))
    link(ng, left_transform, "Geometry", left_mat, "Geometry")
    link(ng, group_in, "Side Material", left_mat, "Material")

    # ============ RIGHT SIDE PANEL ============
    right_side = create_cube(ng, name="Right Side", location=(-700, 250))
    link(ng, left_size, "Vector", right_side, "Size")

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-600, 250))
    link(ng, left_x_div, 0, right_pos, "X")
    link(ng, depth_half, 0, right_pos, "Y")
    link(ng, height_half, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Transform", location=(-500, 250))
    link(ng, right_side, "Mesh", right_transform, "Geometry")
    link(ng, right_pos, "Vector", right_transform, "Translation")

    right_mat = create_set_material(ng, name="Right Material", location=(-350, 250))
    link(ng, right_transform, "Geometry", right_mat, "Geometry")
    link(ng, group_in, "Side Material", right_mat, "Material")

    # Join sides
    join_sides = create_join_geometry(ng, name="Join Sides", location=(-200, 325))
    link(ng, left_mat, "Geometry", join_sides, "Geometry")
    link(ng, right_mat, "Geometry", join_sides, "Geometry")

    switch_sides = create_switch(ng, 'GEOMETRY', name="Sides Switch", location=(-50, 325))
    link(ng, group_in, "Has Sides", switch_sides, "Switch")
    link(ng, join_sides, "Geometry", switch_sides, "True")

    # ============ SHELVES ============
    # Use interior width if has sides, full width otherwise
    shelf_width_with_sides = interior_width  # Already calculated
    shelf_width_no_sides = group_in  # Width directly

    # Create shelf size
    shelf_size = create_combine_xyz(ng, name="Shelf Size", location=(-800, 0))
    link(ng, interior_width, 0, shelf_size, "X")
    link(ng, group_in, "Depth", shelf_size, "Y")
    link(ng, group_in, "Panel Thickness", shelf_size, "Z")

    shelf_cube = create_cube(ng, name="Shelf Cube", location=(-700, 0))
    link(ng, shelf_size, "Vector", shelf_cube, "Size")

    # Bottom shelf (at panel_half Z)
    shelf_0_pos = create_combine_xyz(ng, name="Shelf 0 Pos", location=(-500, 0))
    set_default(shelf_0_pos, "X", 0.0)
    link(ng, depth_half, 0, shelf_0_pos, "Y")
    link(ng, panel_half, 0, shelf_0_pos, "Z")

    shelf_0 = create_transform(ng, name="Shelf 0", location=(-400, 0))
    link(ng, shelf_cube, "Mesh", shelf_0, "Geometry")
    link(ng, shelf_0_pos, "Vector", shelf_0, "Translation")

    # Shelf 1 (at panel_half + shelf_spacing)
    shelf_1_z = create_math(ng, 'ADD', name="Shelf 1 Z", location=(-600, -100))
    link(ng, panel_half, 0, shelf_1_z, 0)
    link(ng, shelf_spacing, 0, shelf_1_z, 1)

    shelf_1_pos = create_combine_xyz(ng, name="Shelf 1 Pos", location=(-500, -100))
    set_default(shelf_1_pos, "X", 0.0)
    link(ng, depth_half, 0, shelf_1_pos, "Y")
    link(ng, shelf_1_z, 0, shelf_1_pos, "Z")

    shelf_1 = create_transform(ng, name="Shelf 1", location=(-400, -100))
    link(ng, shelf_cube, "Mesh", shelf_1, "Geometry")
    link(ng, shelf_1_pos, "Vector", shelf_1, "Translation")

    # Shelf 2
    shelf_spacing_x2 = create_math(ng, 'MULTIPLY', name="Spacing x2", location=(-700, -200))
    link(ng, shelf_spacing, 0, shelf_spacing_x2, 0)
    set_default(shelf_spacing_x2, 1, 2.0)
    shelf_2_z = create_math(ng, 'ADD', name="Shelf 2 Z", location=(-600, -200))
    link(ng, panel_half, 0, shelf_2_z, 0)
    link(ng, shelf_spacing_x2, 0, shelf_2_z, 1)

    shelf_2_pos = create_combine_xyz(ng, name="Shelf 2 Pos", location=(-500, -200))
    set_default(shelf_2_pos, "X", 0.0)
    link(ng, depth_half, 0, shelf_2_pos, "Y")
    link(ng, shelf_2_z, 0, shelf_2_pos, "Z")

    shelf_2 = create_transform(ng, name="Shelf 2", location=(-400, -200))
    link(ng, shelf_cube, "Mesh", shelf_2, "Geometry")
    link(ng, shelf_2_pos, "Vector", shelf_2, "Translation")

    # Shelf 3
    shelf_spacing_x3 = create_math(ng, 'MULTIPLY', name="Spacing x3", location=(-700, -300))
    link(ng, shelf_spacing, 0, shelf_spacing_x3, 0)
    set_default(shelf_spacing_x3, 1, 3.0)
    shelf_3_z = create_math(ng, 'ADD', name="Shelf 3 Z", location=(-600, -300))
    link(ng, panel_half, 0, shelf_3_z, 0)
    link(ng, shelf_spacing_x3, 0, shelf_3_z, 1)

    shelf_3_pos = create_combine_xyz(ng, name="Shelf 3 Pos", location=(-500, -300))
    set_default(shelf_3_pos, "X", 0.0)
    link(ng, depth_half, 0, shelf_3_pos, "Y")
    link(ng, shelf_3_z, 0, shelf_3_pos, "Z")

    shelf_3 = create_transform(ng, name="Shelf 3", location=(-400, -300))
    link(ng, shelf_cube, "Mesh", shelf_3, "Geometry")
    link(ng, shelf_3_pos, "Vector", shelf_3, "Translation")

    # Top shelf (at height - panel_half)
    top_z = create_math(ng, 'SUBTRACT', name="Top Z", location=(-600, -400))
    link(ng, group_in, "Height", top_z, 0)
    link(ng, panel_half, 0, top_z, 1)

    shelf_top_pos = create_combine_xyz(ng, name="Shelf Top Pos", location=(-500, -400))
    set_default(shelf_top_pos, "X", 0.0)
    link(ng, depth_half, 0, shelf_top_pos, "Y")
    link(ng, top_z, 0, shelf_top_pos, "Z")

    shelf_top = create_transform(ng, name="Shelf Top", location=(-400, -400))
    link(ng, shelf_cube, "Mesh", shelf_top, "Geometry")
    link(ng, shelf_top_pos, "Vector", shelf_top, "Translation")

    # Join shelves
    join_shelves = create_join_geometry(ng, name="Join Shelves", location=(-200, -150))
    link(ng, shelf_0, "Geometry", join_shelves, "Geometry")
    link(ng, shelf_1, "Geometry", join_shelves, "Geometry")
    link(ng, shelf_2, "Geometry", join_shelves, "Geometry")
    link(ng, shelf_3, "Geometry", join_shelves, "Geometry")
    link(ng, shelf_top, "Geometry", join_shelves, "Geometry")

    shelf_mat = create_set_material(ng, name="Shelf Material", location=(-50, -150))
    link(ng, join_shelves, "Geometry", shelf_mat, "Geometry")
    link(ng, group_in, "Shelf Material", shelf_mat, "Material")

    # ============ BACK PANEL ============
    interior_height = create_math(ng, 'SUBTRACT', name="Interior Height", location=(-900, -600))
    link(ng, group_in, "Height", interior_height, 0)
    link(ng, panel_x2, 0, interior_height, 1)

    back_size = create_combine_xyz(ng, name="Back Size", location=(-800, -600))
    link(ng, interior_width, 0, back_size, "X")
    set_default(back_size, "Y", 0.006)
    link(ng, interior_height, 0, back_size, "Z")

    back = create_cube(ng, name="Back", location=(-700, -600))
    link(ng, back_size, "Vector", back, "Size")

    back_y = create_math(ng, 'MULTIPLY', name="Back Y Neg", location=(-800, -650))
    link(ng, group_in, "Depth", back_y, 0)
    set_default(back_y, 1, -1.0)
    back_y_offset = create_math(ng, 'ADD', name="Back Y Offset", location=(-700, -650))
    link(ng, back_y, 0, back_y_offset, 0)
    set_default(back_y_offset, 1, 0.003)

    back_pos = create_combine_xyz(ng, name="Back Pos", location=(-600, -600))
    set_default(back_pos, "X", 0.0)
    link(ng, back_y_offset, 0, back_pos, "Y")
    link(ng, height_half, 0, back_pos, "Z")

    back_transform = create_transform(ng, name="Back Transform", location=(-500, -600))
    link(ng, back, "Mesh", back_transform, "Geometry")
    link(ng, back_pos, "Vector", back_transform, "Translation")

    back_mat = create_set_material(ng, name="Back Material", location=(-350, -600))
    link(ng, back_transform, "Geometry", back_mat, "Geometry")
    link(ng, group_in, "Back Material", back_mat, "Material")

    switch_back = create_switch(ng, 'GEOMETRY', name="Back Switch", location=(-200, -600))
    link(ng, group_in, "Has Back", switch_back, "Switch")
    link(ng, back_mat, "Geometry", switch_back, "True")

    # ============ JOIN ALL ============
    join_all = create_join_geometry(ng, name="Join All", location=(200, 0))
    link(ng, switch_sides, "Output", join_all, "Geometry")
    link(ng, shelf_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_back, "Output", join_all, "Geometry")

    # ============ BEVEL ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(400, 0))
    if bevel is not None:
        link(ng, join_all, "Geometry", bevel, "Mesh")
        link(ng, group_in, "Bevel Width", bevel, "Width")
        link(ng, group_in, "Bevel Segments", bevel, "Segments")
        final_geo = bevel
        final_socket = "Mesh"
    else:
        final_geo = join_all
        final_socket = "Geometry"

    # ============ OUTPUT ============
    link(ng, final_geo, final_socket, group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/systems/open_shelving.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the OpenShelving node group applied."""
    if nodegroup is None:
        nodegroup = create_open_shelving_nodegroup()

    mesh = bpy.data.meshes.new("OpenShelving_Test")
    obj = bpy.data.objects.new("OpenShelving_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_open_shelving_nodegroup()
    print(f"Created node group: {ng.name}")
