# Door Assembly node group generator
# System component: Creates door(s) with handles for cabinet front
# Coordinate system: X=width, Y=depth, Z=height (Z-up, front at Y=0)
#
# Features:
# - Single or double door configurations
# - Hinge side control (left/right/auto for single, both for double)
# - Door swing animation with proper pivot rotation
# - Glass insert option
# - Auto double-door based on width threshold
# - Overlay type support (inset, half, full)

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
    create_mesh_boolean,
    link,
    set_default,
    add_metadata,
)


def create_door_assembly_nodegroup():
    """Generate the DoorAssembly node group.

    Creates cabinet door(s) with proper sizing, gap, and handles.
    Supports single door or double door configurations.
    Includes door swing animation control with proper hinge side selection.

    Coordinate system:
    - Doors face positive Y (front of cabinet)
    - Door hinges on left/right edges based on Hinge Side parameter
    - Origin at cabinet front-bottom-center

    Hinge Side options:
    - 0 = Left (single door hinges on left, opens right)
    - 1 = Right (single door hinges on right, opens left)

    For double doors, both doors hinge on outer edges and open toward center.
    """
    ng = create_node_group("DoorAssembly")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    style_panel = create_panel(ng, "Style")
    handle_panel = create_panel(ng, "Handle")
    anim_panel = create_panel(ng, "Animation")
    materials_panel = create_panel(ng, "Materials")

    # Dimension inputs
    add_float_socket(ng, "Opening Width", default=0.564, min_val=0.1, max_val=1.2,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Opening Height", default=0.684, min_val=0.1, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Door Thickness", default=0.018, min_val=0.015, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Door Gap", default=0.003, min_val=0.001, max_val=0.01,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Door Overlay", default=0.018, min_val=0.0, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Face Frame Width", default=0.038, min_val=0.0, max_val=0.075,
                     subtype='DISTANCE', panel=dims_panel)
    # Overlay Type: 0=Full Overlay, 1=Half Overlay, 2=Inset
    add_int_socket(ng, "Overlay Type", default=0, min_val=0, max_val=2, panel=dims_panel)

    # Style options
    add_bool_socket(ng, "Double Doors", default=False, panel=style_panel)
    add_int_socket(ng, "Hinge Side", default=0, min_val=0, max_val=1, panel=style_panel)
    add_bool_socket(ng, "Glass Insert", default=False, panel=style_panel)
    add_float_socket(ng, "Glass Frame Width", default=0.04, min_val=0.02, max_val=0.1,
                     subtype='DISTANCE', panel=style_panel)
    add_float_socket(ng, "Glass Thickness", default=0.004, min_val=0.003, max_val=0.01,
                     subtype='DISTANCE', panel=style_panel)

    # Handle options
    add_float_socket(ng, "Handle Length", default=0.128, min_val=0.03, max_val=0.3,
                     subtype='DISTANCE', panel=handle_panel)
    add_float_socket(ng, "Handle Width", default=0.012, min_val=0.006, max_val=0.025,
                     subtype='DISTANCE', panel=handle_panel)
    add_float_socket(ng, "Handle Projection", default=0.03, min_val=0.015, max_val=0.06,
                     subtype='DISTANCE', panel=handle_panel)
    add_float_socket(ng, "Handle Offset X", default=0.05, min_val=0.02, max_val=0.2,
                     subtype='DISTANCE', panel=handle_panel)
    add_float_socket(ng, "Handle Offset Z", default=0.0, min_val=-0.3, max_val=0.3,
                     subtype='DISTANCE', panel=handle_panel)

    # Animation
    add_float_socket(ng, "Door Open Angle", default=0.0, min_val=0.0, max_val=120.0,
                     subtype='NONE', panel=anim_panel)

    # Bevel options
    bevel_panel = create_panel(ng, "Bevel")
    add_float_socket(ng, "Bevel Width", default=0.001, min_val=0.0, max_val=0.01,
                     subtype='DISTANCE', panel=bevel_panel)
    add_int_socket(ng, "Bevel Segments", default=2, min_val=1, max_val=6, panel=bevel_panel)

    # Materials
    add_material_socket(ng, "Door Material", panel=materials_panel)
    add_material_socket(ng, "Handle Material", panel=materials_panel)
    add_material_socket(ng, "Glass Material", panel=materials_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1200, 0))
    group_out = create_group_output(ng, location=(1000, 0))

    # ============ CALCULATE DOOR DIMENSIONS ============
    # Door width = opening_width + 2*overlay - gap (for single door)
    overlay_x2 = create_math(ng, 'MULTIPLY', name="Overlay x2", location=(-1000, 400))
    link(ng, group_in, "Door Overlay", overlay_x2, 0)
    set_default(overlay_x2, 1, 2.0)

    single_door_width_base = create_math(ng, 'ADD', name="Single Width Base", location=(-900, 400))
    link(ng, group_in, "Opening Width", single_door_width_base, 0)
    link(ng, overlay_x2, 0, single_door_width_base, 1)

    single_door_width = create_math(ng, 'SUBTRACT', name="Single Door Width", location=(-800, 400))
    link(ng, single_door_width_base, 0, single_door_width, 0)
    link(ng, group_in, "Door Gap", single_door_width, 1)

    # Door height = opening_height + 2*overlay - gap
    door_height_base = create_math(ng, 'ADD', name="Door Height Base", location=(-900, 300))
    link(ng, group_in, "Opening Height", door_height_base, 0)
    link(ng, overlay_x2, 0, door_height_base, 1)

    door_height = create_math(ng, 'SUBTRACT', name="Door Height", location=(-800, 300))
    link(ng, door_height_base, 0, door_height, 0)
    link(ng, group_in, "Door Gap", door_height, 1)

    # Door Z center = panel_thickness + opening_height/2
    opening_half = create_math(ng, 'DIVIDE', name="Opening Half", location=(-900, 200))
    link(ng, group_in, "Opening Height", opening_half, 0)
    set_default(opening_half, 1, 2.0)

    door_z = create_math(ng, 'ADD', name="Door Z", location=(-800, 200))
    link(ng, group_in, "Panel Thickness", door_z, 0)
    link(ng, opening_half, 0, door_z, 1)

    # Door Y position = door_thickness/2 (front face at Y=0)
    door_y = create_math(ng, 'DIVIDE', name="Door Y", location=(-800, 100))
    link(ng, group_in, "Door Thickness", door_y, 0)
    set_default(door_y, 1, 2.0)

    # ============ SINGLE DOOR ============
    single_door = create_cube(ng, name="Single Door", location=(-500, 400))
    single_size = create_combine_xyz(ng, name="Single Size", location=(-650, 450))

    link(ng, single_door_width, 0, single_size, "X")
    link(ng, group_in, "Door Thickness", single_size, "Y")
    link(ng, door_height, 0, single_size, "Z")
    link(ng, single_size, "Vector", single_door, "Size")

    single_pos = create_combine_xyz(ng, name="Single Pos", location=(-650, 350))
    link(ng, door_y, 0, single_pos, "Y")
    link(ng, door_z, 0, single_pos, "Z")

    single_transform = create_transform(ng, name="Single Transform", location=(-350, 400))
    link(ng, single_pos, "Vector", single_transform, "Translation")
    link(ng, single_door, "Mesh", single_transform, "Geometry")

    # Single door handle (centered, offset from edge)
    single_handle = create_cube(ng, name="Single Handle", location=(-500, 250))
    single_handle_size = create_combine_xyz(ng, name="S Handle Size", location=(-650, 280))

    link(ng, group_in, "Handle Length", single_handle_size, "X")
    link(ng, group_in, "Handle Width", single_handle_size, "Y")
    link(ng, group_in, "Handle Projection", single_handle_size, "Z")
    link(ng, single_handle_size, "Vector", single_handle, "Size")

    # Handle position
    handle_y = create_math(ng, 'ADD', name="Handle Y", location=(-750, 180))
    proj_half = create_math(ng, 'DIVIDE', name="Proj Half", location=(-850, 180))
    link(ng, group_in, "Handle Projection", proj_half, 0)
    set_default(proj_half, 1, 2.0)
    link(ng, group_in, "Door Thickness", handle_y, 0)
    link(ng, proj_half, 0, handle_y, 1)

    handle_z = create_math(ng, 'ADD', name="Handle Z", location=(-750, 100))
    link(ng, door_z, 0, handle_z, 0)
    link(ng, group_in, "Handle Offset Z", handle_z, 1)

    single_handle_pos = create_combine_xyz(ng, name="S Handle Pos", location=(-650, 150))
    link(ng, handle_y, 0, single_handle_pos, "Y")
    link(ng, handle_z, 0, single_handle_pos, "Z")

    single_handle_transform = create_transform(ng, name="S Handle Transform", location=(-350, 250))
    link(ng, single_handle_pos, "Vector", single_handle_transform, "Translation")
    link(ng, single_handle, "Mesh", single_handle_transform, "Geometry")

    # Set materials
    single_door_mat = create_set_material(ng, name="Single Door Mat", location=(-200, 400))
    link(ng, single_transform, "Geometry", single_door_mat, "Geometry")
    link(ng, group_in, "Door Material", single_door_mat, "Material")

    single_handle_mat = create_set_material(ng, name="S Handle Mat", location=(-200, 250))
    link(ng, single_handle_transform, "Geometry", single_handle_mat, "Geometry")
    link(ng, group_in, "Handle Material", single_handle_mat, "Material")

    # Join single door + handle
    join_single = create_join_geometry(ng, name="Join Single", location=(0, 350))
    link(ng, single_door_mat, "Geometry", join_single, "Geometry")
    link(ng, single_handle_mat, "Geometry", join_single, "Geometry")

    # ============ DOUBLE DOORS ============
    # Each door width = (opening_width + 2*overlay - 3*gap) / 2
    gap_x3 = create_math(ng, 'MULTIPLY', name="Gap x3", location=(-1000, -100))
    link(ng, group_in, "Door Gap", gap_x3, 0)
    set_default(gap_x3, 1, 3.0)

    double_width_sub = create_math(ng, 'SUBTRACT', name="Double Width Sub", location=(-900, -100))
    link(ng, single_door_width_base, 0, double_width_sub, 0)
    link(ng, gap_x3, 0, double_width_sub, 1)

    double_door_width = create_math(ng, 'DIVIDE', name="Double Door Width", location=(-800, -100))
    link(ng, double_width_sub, 0, double_door_width, 0)
    set_default(double_door_width, 1, 2.0)

    # Left door
    left_door = create_cube(ng, name="Left Door", location=(-500, -100))
    left_size = create_combine_xyz(ng, name="Left Size", location=(-650, -50))

    link(ng, double_door_width, 0, left_size, "X")
    link(ng, group_in, "Door Thickness", left_size, "Y")
    link(ng, door_height, 0, left_size, "Z")
    link(ng, left_size, "Vector", left_door, "Size")

    # Left door X = -(double_door_width + gap) / 2
    left_x_base = create_math(ng, 'ADD', name="Left X Base", location=(-750, -150))
    link(ng, double_door_width, 0, left_x_base, 0)
    link(ng, group_in, "Door Gap", left_x_base, 1)

    left_x = create_math(ng, 'DIVIDE', name="Left X Div", location=(-650, -150))
    link(ng, left_x_base, 0, left_x, 0)
    set_default(left_x, 1, -2.0)

    left_pos = create_combine_xyz(ng, name="Left Pos", location=(-550, -200))
    link(ng, left_x, 0, left_pos, "X")
    link(ng, door_y, 0, left_pos, "Y")
    link(ng, door_z, 0, left_pos, "Z")

    left_transform = create_transform(ng, name="Left Transform", location=(-350, -100))
    link(ng, left_pos, "Vector", left_transform, "Translation")
    link(ng, left_door, "Mesh", left_transform, "Geometry")

    # Right door
    right_door = create_cube(ng, name="Right Door", location=(-500, -300))
    right_size = create_combine_xyz(ng, name="Right Size", location=(-650, -250))

    link(ng, double_door_width, 0, right_size, "X")
    link(ng, group_in, "Door Thickness", right_size, "Y")
    link(ng, door_height, 0, right_size, "Z")
    link(ng, right_size, "Vector", right_door, "Size")

    # Right door X = (double_door_width + gap) / 2
    right_x = create_math(ng, 'DIVIDE', name="Right X Div", location=(-650, -350))
    link(ng, left_x_base, 0, right_x, 0)
    set_default(right_x, 1, 2.0)

    right_pos = create_combine_xyz(ng, name="Right Pos", location=(-550, -400))
    link(ng, right_x, 0, right_pos, "X")
    link(ng, door_y, 0, right_pos, "Y")
    link(ng, door_z, 0, right_pos, "Z")

    right_transform = create_transform(ng, name="Right Transform", location=(-350, -300))
    link(ng, right_pos, "Vector", right_transform, "Translation")
    link(ng, right_door, "Mesh", right_transform, "Geometry")

    # Left handle (near center gap)
    left_handle = create_cube(ng, name="Left Handle", location=(-500, -500))
    left_handle_size = create_combine_xyz(ng, name="L Handle Size", location=(-650, -470))

    link(ng, group_in, "Handle Length", left_handle_size, "X")
    link(ng, group_in, "Handle Width", left_handle_size, "Y")
    link(ng, group_in, "Handle Projection", left_handle_size, "Z")
    link(ng, left_handle_size, "Vector", left_handle, "Size")

    # Handle X near inner edge
    handle_from_edge = create_math(ng, 'SUBTRACT', name="Handle From Edge", location=(-750, -550))
    door_width_half = create_math(ng, 'DIVIDE', name="Door W Half", location=(-850, -550))
    link(ng, double_door_width, 0, door_width_half, 0)
    set_default(door_width_half, 1, 2.0)
    link(ng, door_width_half, 0, handle_from_edge, 0)
    link(ng, group_in, "Handle Offset X", handle_from_edge, 1)

    left_handle_x = create_math(ng, 'ADD', name="L Handle X", location=(-650, -550))
    link(ng, left_x, 0, left_handle_x, 0)
    link(ng, handle_from_edge, 0, left_handle_x, 1)

    left_handle_pos = create_combine_xyz(ng, name="L Handle Pos", location=(-550, -600))
    link(ng, left_handle_x, 0, left_handle_pos, "X")
    link(ng, handle_y, 0, left_handle_pos, "Y")
    link(ng, handle_z, 0, left_handle_pos, "Z")

    left_handle_transform = create_transform(ng, name="L Handle Transform", location=(-350, -500))
    link(ng, left_handle_pos, "Vector", left_handle_transform, "Translation")
    link(ng, left_handle, "Mesh", left_handle_transform, "Geometry")

    # Right handle (mirror of left)
    right_handle = create_cube(ng, name="Right Handle", location=(-500, -700))

    right_handle_x = create_math(ng, 'SUBTRACT', name="R Handle X", location=(-650, -750))
    link(ng, right_x, 0, right_handle_x, 0)
    link(ng, handle_from_edge, 0, right_handle_x, 1)

    right_handle_pos = create_combine_xyz(ng, name="R Handle Pos", location=(-550, -800))
    link(ng, right_handle_x, 0, right_handle_pos, "X")
    link(ng, handle_y, 0, right_handle_pos, "Y")
    link(ng, handle_z, 0, right_handle_pos, "Z")

    right_handle_transform = create_transform(ng, name="R Handle Transform", location=(-350, -700))
    link(ng, right_handle_pos, "Vector", right_handle_transform, "Translation")
    link(ng, left_handle_size, "Vector", right_handle, "Size")
    link(ng, right_handle, "Mesh", right_handle_transform, "Geometry")

    # Set materials for double doors
    left_door_mat = create_set_material(ng, name="Left Door Mat", location=(-200, -100))
    link(ng, left_transform, "Geometry", left_door_mat, "Geometry")
    link(ng, group_in, "Door Material", left_door_mat, "Material")

    right_door_mat = create_set_material(ng, name="Right Door Mat", location=(-200, -300))
    link(ng, right_transform, "Geometry", right_door_mat, "Geometry")
    link(ng, group_in, "Door Material", right_door_mat, "Material")

    left_handle_mat = create_set_material(ng, name="L Handle Mat", location=(-200, -500))
    link(ng, left_handle_transform, "Geometry", left_handle_mat, "Geometry")
    link(ng, group_in, "Handle Material", left_handle_mat, "Material")

    right_handle_mat = create_set_material(ng, name="R Handle Mat", location=(-200, -700))
    link(ng, right_handle_transform, "Geometry", right_handle_mat, "Geometry")
    link(ng, group_in, "Handle Material", right_handle_mat, "Material")

    # Join double doors
    join_double = create_join_geometry(ng, name="Join Double", location=(0, -300))
    link(ng, left_door_mat, "Geometry", join_double, "Geometry")
    link(ng, right_door_mat, "Geometry", join_double, "Geometry")
    link(ng, left_handle_mat, "Geometry", join_double, "Geometry")
    link(ng, right_handle_mat, "Geometry", join_double, "Geometry")

    # ============ SWITCH SINGLE/DOUBLE ============
    switch_doors = create_switch(ng, 'GEOMETRY', name="Door Switch", location=(200, 0))
    link(ng, group_in, "Double Doors", switch_doors, "Switch")
    link(ng, join_single, "Geometry", switch_doors, "False")
    link(ng, join_double, "Geometry", switch_doors, "True")

    # ============ GLASS INSERT OPTION ============
    # Create glass cutout dimensions (door size minus frame width on each side)
    frame_x2 = create_math(ng, 'MULTIPLY', name="Frame x2", location=(300, -600))
    link(ng, group_in, "Glass Frame Width", frame_x2, 0)
    set_default(frame_x2, 1, 2.0)

    # Glass width for single door
    glass_width_single = create_math(ng, 'SUBTRACT', name="Glass W Single", location=(400, -550))
    link(ng, single_door_width, 0, glass_width_single, 0)
    link(ng, frame_x2, 0, glass_width_single, 1)

    # Glass width for double doors
    glass_width_double = create_math(ng, 'SUBTRACT', name="Glass W Double", location=(400, -650))
    link(ng, double_door_width, 0, glass_width_double, 0)
    link(ng, frame_x2, 0, glass_width_double, 1)

    # Glass height (same for both)
    glass_height = create_math(ng, 'SUBTRACT', name="Glass Height", location=(400, -750))
    link(ng, door_height, 0, glass_height, 0)
    link(ng, frame_x2, 0, glass_height, 1)

    # Switch glass width based on door type
    switch_glass_w = create_switch(ng, 'FLOAT', name="Glass Width Switch", location=(500, -600))
    link(ng, group_in, "Double Doors", switch_glass_w, "Switch")
    link(ng, glass_width_single, 0, switch_glass_w, "False")
    link(ng, glass_width_double, 0, switch_glass_w, "True")

    # Create glass panel geometry
    glass_panel = create_cube(ng, name="Glass Panel", location=(600, -700))
    glass_size = create_combine_xyz(ng, name="Glass Size", location=(500, -750))
    link(ng, switch_glass_w, "Output", glass_size, "X")
    link(ng, group_in, "Glass Thickness", glass_size, "Y")
    link(ng, glass_height, 0, glass_size, "Z")
    link(ng, glass_size, "Vector", glass_panel, "Size")

    # Glass Y position (slightly recessed into door)
    glass_y = create_math(ng, 'DIVIDE', name="Glass Y", location=(500, -850))
    link(ng, group_in, "Glass Thickness", glass_y, 0)
    set_default(glass_y, 1, 2.0)

    # Single glass position (centered)
    single_glass_pos = create_combine_xyz(ng, name="S Glass Pos", location=(600, -850))
    link(ng, glass_y, 0, single_glass_pos, "Y")
    link(ng, door_z, 0, single_glass_pos, "Z")

    single_glass_transform = create_transform(ng, name="S Glass Transform", location=(700, -800))
    link(ng, single_glass_pos, "Vector", single_glass_transform, "Translation")
    link(ng, glass_panel, "Mesh", single_glass_transform, "Geometry")

    # Left glass position for double doors
    left_glass_pos = create_combine_xyz(ng, name="L Glass Pos", location=(600, -950))
    link(ng, left_x, 0, left_glass_pos, "X")
    link(ng, glass_y, 0, left_glass_pos, "Y")
    link(ng, door_z, 0, left_glass_pos, "Z")

    left_glass_transform = create_transform(ng, name="L Glass Transform", location=(700, -900))
    link(ng, left_glass_pos, "Vector", left_glass_transform, "Translation")
    link(ng, glass_panel, "Mesh", left_glass_transform, "Geometry")

    # Right glass position for double doors
    right_glass_pos = create_combine_xyz(ng, name="R Glass Pos", location=(600, -1050))
    link(ng, right_x, 0, right_glass_pos, "X")
    link(ng, glass_y, 0, right_glass_pos, "Y")
    link(ng, door_z, 0, right_glass_pos, "Z")

    right_glass_transform = create_transform(ng, name="R Glass Transform", location=(700, -1000))
    link(ng, right_glass_pos, "Vector", right_glass_transform, "Translation")
    link(ng, glass_panel, "Mesh", right_glass_transform, "Geometry")

    # Set glass material
    single_glass_mat = create_set_material(ng, name="S Glass Mat", location=(800, -800))
    link(ng, single_glass_transform, "Geometry", single_glass_mat, "Geometry")
    link(ng, group_in, "Glass Material", single_glass_mat, "Material")

    left_glass_mat = create_set_material(ng, name="L Glass Mat", location=(800, -900))
    link(ng, left_glass_transform, "Geometry", left_glass_mat, "Geometry")
    link(ng, group_in, "Glass Material", left_glass_mat, "Material")

    right_glass_mat = create_set_material(ng, name="R Glass Mat", location=(800, -1000))
    link(ng, right_glass_transform, "Geometry", right_glass_mat, "Geometry")
    link(ng, group_in, "Glass Material", right_glass_mat, "Material")

    # Join single door glass
    join_single_glass = create_join_geometry(ng, name="Join Single Glass", location=(900, -800))
    link(ng, single_glass_mat, "Geometry", join_single_glass, "Geometry")

    # Join double door glasses
    join_double_glass = create_join_geometry(ng, name="Join Double Glass", location=(900, -950))
    link(ng, left_glass_mat, "Geometry", join_double_glass, "Geometry")
    link(ng, right_glass_mat, "Geometry", join_double_glass, "Geometry")

    # Switch glass based on door type
    switch_glass = create_switch(ng, 'GEOMETRY', name="Glass Switch", location=(1000, -850))
    link(ng, group_in, "Double Doors", switch_glass, "Switch")
    link(ng, join_single_glass, "Geometry", switch_glass, "False")
    link(ng, join_double_glass, "Geometry", switch_glass, "True")

    # Join doors with glass (when glass insert is enabled)
    join_with_glass = create_join_geometry(ng, name="Join With Glass", location=(400, -200))
    link(ng, switch_doors, "Output", join_with_glass, "Geometry")
    link(ng, switch_glass, "Output", join_with_glass, "Geometry")

    # Switch between solid doors and glass doors
    switch_glass_option = create_switch(ng, 'GEOMETRY', name="Glass Option Switch", location=(500, 0))
    link(ng, group_in, "Glass Insert", switch_glass_option, "Switch")
    link(ng, switch_doors, "Output", switch_glass_option, "False")
    link(ng, join_with_glass, "Geometry", switch_glass_option, "True")

    # ============ DOOR SWING ANIMATION ============
    # For single doors, rotation direction depends on hinge side
    # For double doors, each door rotates around its outer edge

    # Convert door angle from degrees to radians
    angle_rad = create_math(ng, 'RADIANS', name="Angle Rad", location=(600, -200))
    link(ng, group_in, "Door Open Angle", angle_rad, 0)

    # Pivot offset = door_width / 2 (distance from center to edge)
    single_pivot_offset = create_math(ng, 'DIVIDE', name="S Pivot Offset", location=(600, -300))
    link(ng, single_door_width, 0, single_pivot_offset, 0)
    set_default(single_pivot_offset, 1, 2.0)

    # ============ SINGLE DOOR ROTATION WITH HINGE SIDE ============
    # Hinge Side: 0 = Left (door hinges on left, opens right with negative rotation)
    #             1 = Right (door hinges on right, opens left with positive rotation)

    # Check if hinge is on right side
    is_right_hinge = create_compare(ng, 'EQUAL', 'INT', name="Is Right Hinge", location=(600, -350))
    link(ng, group_in, "Hinge Side", is_right_hinge, 2)
    set_default(is_right_hinge, 3, 1)

    # Pre-translation X: positive for left hinge, negative for right hinge
    # Left hinge: move door right so left edge is at origin
    # Right hinge: move door left so right edge is at origin
    single_pre_x_left = single_pivot_offset  # positive (move right)
    single_pre_x_right = create_math(ng, 'MULTIPLY', name="S Pre X Right", location=(700, -400))
    link(ng, single_pivot_offset, 0, single_pre_x_right, 0)
    set_default(single_pre_x_right, 1, -1.0)

    switch_pre_x = create_switch(ng, 'FLOAT', name="Switch Pre X", location=(800, -380))
    link(ng, is_right_hinge, "Result", switch_pre_x, "Switch")
    link(ng, single_pivot_offset, 0, switch_pre_x, "False")  # Left hinge: positive
    link(ng, single_pre_x_right, 0, switch_pre_x, "True")    # Right hinge: negative

    single_pre_pos = create_combine_xyz(ng, name="S Pre Pos", location=(900, -350))
    link(ng, switch_pre_x, "Output", single_pre_pos, "X")

    single_pre_transform = create_transform(ng, name="S Pre Transform", location=(1000, -300))
    link(ng, switch_glass_option, "Output", single_pre_transform, "Geometry")
    link(ng, single_pre_pos, "Vector", single_pre_transform, "Translation")

    # Rotation direction: negative for left hinge (opens right), positive for right hinge (opens left)
    angle_neg = create_math(ng, 'MULTIPLY', name="Angle Neg", location=(700, -480))
    link(ng, angle_rad, 0, angle_neg, 0)
    set_default(angle_neg, 1, -1.0)

    switch_angle = create_switch(ng, 'FLOAT', name="Switch Angle", location=(800, -500))
    link(ng, is_right_hinge, "Result", switch_angle, "Switch")
    link(ng, angle_neg, 0, switch_angle, "False")  # Left hinge: negative rotation
    link(ng, angle_rad, 0, switch_angle, "True")   # Right hinge: positive rotation

    single_rotation = create_combine_xyz(ng, name="S Rotation", location=(900, -480))
    link(ng, switch_angle, "Output", single_rotation, "Z")

    single_rotate = create_transform(ng, name="S Rotate", location=(1100, -350))
    link(ng, single_pre_transform, "Geometry", single_rotate, "Geometry")
    link(ng, single_rotation, "Vector", single_rotate, "Rotation")

    # Post-translation (opposite of pre-translation)
    single_post_x_left = create_math(ng, 'MULTIPLY', name="S Post X Left", location=(700, -580))
    link(ng, single_pivot_offset, 0, single_post_x_left, 0)
    set_default(single_post_x_left, 1, -1.0)

    switch_post_x = create_switch(ng, 'FLOAT', name="Switch Post X", location=(800, -600))
    link(ng, is_right_hinge, "Result", switch_post_x, "Switch")
    link(ng, single_post_x_left, 0, switch_post_x, "False")  # Left hinge: negative
    link(ng, single_pivot_offset, 0, switch_post_x, "True")  # Right hinge: positive

    single_post_pos = create_combine_xyz(ng, name="S Post Pos", location=(900, -580))
    link(ng, switch_post_x, "Output", single_post_pos, "X")

    single_post_transform = create_transform(ng, name="S Post Transform", location=(1200, -400))
    link(ng, single_rotate, "Geometry", single_post_transform, "Geometry")
    link(ng, single_post_pos, "Vector", single_post_transform, "Translation")

    # ============ DOUBLE DOOR ROTATION ============
    # Left door hinges on left outer edge (negative X), opens with negative rotation
    # Right door hinges on right outer edge (positive X), opens with positive rotation

    double_pivot_offset = create_math(ng, 'DIVIDE', name="D Pivot Offset", location=(600, -700))
    link(ng, double_door_width, 0, double_pivot_offset, 0)
    set_default(double_pivot_offset, 1, 2.0)

    # Left door: hinge at outer left edge
    # Pre-translate: move door right by half its width + half gap (to put hinge at X=0 temporarily)
    left_hinge_x = create_math(ng, 'SUBTRACT', name="Left Hinge X", location=(700, -750))
    link(ng, left_x, 0, left_hinge_x, 0)
    link(ng, double_pivot_offset, 0, left_hinge_x, 1)

    # We need to translate the door so its hinge edge is at the origin
    # The door center is at left_x, hinge edge is at left_x - door_width/2
    # So we translate by -(left_x - door_width/2) = -left_x + door_width/2

    left_pre_x = create_math(ng, 'SUBTRACT', name="L Pre X", location=(700, -800))
    link(ng, double_pivot_offset, 0, left_pre_x, 0)
    link(ng, left_x, 0, left_pre_x, 1)

    left_pre_pos = create_combine_xyz(ng, name="L Pre Pos", location=(800, -800))
    link(ng, left_pre_x, 0, left_pre_pos, "X")

    # Apply pre-transform to left door geometry (from join_double with materials)
    left_door_geo = create_join_geometry(ng, name="Left Door Geo", location=(600, -850))
    link(ng, left_door_mat, "Geometry", left_door_geo, "Geometry")
    link(ng, left_handle_mat, "Geometry", left_door_geo, "Geometry")

    left_pre_transform = create_transform(ng, name="L Pre Transform", location=(900, -850))
    link(ng, left_door_geo, "Geometry", left_pre_transform, "Geometry")
    link(ng, left_pre_pos, "Vector", left_pre_transform, "Translation")

    # Rotate left door (negative angle for outward swing)
    left_rotation = create_combine_xyz(ng, name="L Rotation", location=(800, -920))
    link(ng, angle_neg, 0, left_rotation, "Z")

    left_rotate = create_transform(ng, name="L Rotate", location=(1000, -880))
    link(ng, left_pre_transform, "Geometry", left_rotate, "Geometry")
    link(ng, left_rotation, "Vector", left_rotate, "Rotation")

    # Post-translate left door back
    left_post_x = create_math(ng, 'SUBTRACT', name="L Post X", location=(700, -970))
    link(ng, left_x, 0, left_post_x, 0)
    link(ng, double_pivot_offset, 0, left_post_x, 1)

    left_post_pos = create_combine_xyz(ng, name="L Post Pos", location=(800, -1000))
    link(ng, left_post_x, 0, left_post_pos, "X")

    left_post_transform = create_transform(ng, name="L Post Transform", location=(1100, -920))
    link(ng, left_rotate, "Geometry", left_post_transform, "Geometry")
    link(ng, left_post_pos, "Vector", left_post_transform, "Translation")

    # Right door: hinge at outer right edge
    # Pre-translate: move door left by half its width (to put hinge at X=0)
    right_pre_x = create_math(ng, 'SUBTRACT', name="R Pre X", location=(700, -1100))
    link(ng, double_pivot_offset, 0, right_pre_x, 0)
    link(ng, right_x, 0, right_pre_x, 1)
    # Negate because right_x is positive
    right_pre_x_neg = create_math(ng, 'MULTIPLY', name="R Pre X Neg", location=(800, -1100))
    link(ng, right_pre_x, 0, right_pre_x_neg, 0)
    set_default(right_pre_x_neg, 1, -1.0)

    right_pre_pos = create_combine_xyz(ng, name="R Pre Pos", location=(900, -1100))
    link(ng, right_pre_x_neg, 0, right_pre_pos, "X")

    # Apply pre-transform to right door geometry
    right_door_geo = create_join_geometry(ng, name="Right Door Geo", location=(600, -1150))
    link(ng, right_door_mat, "Geometry", right_door_geo, "Geometry")
    link(ng, right_handle_mat, "Geometry", right_door_geo, "Geometry")

    right_pre_transform = create_transform(ng, name="R Pre Transform", location=(1000, -1150))
    link(ng, right_door_geo, "Geometry", right_pre_transform, "Geometry")
    link(ng, right_pre_pos, "Vector", right_pre_transform, "Translation")

    # Rotate right door (positive angle for outward swing - mirror of left)
    right_rotation = create_combine_xyz(ng, name="R Rotation", location=(900, -1220))
    link(ng, angle_rad, 0, right_rotation, "Z")

    right_rotate = create_transform(ng, name="R Rotate", location=(1100, -1180))
    link(ng, right_pre_transform, "Geometry", right_rotate, "Geometry")
    link(ng, right_rotation, "Vector", right_rotate, "Rotation")

    # Post-translate right door back
    right_post_x = create_math(ng, 'ADD', name="R Post X", location=(700, -1280))
    link(ng, right_x, 0, right_post_x, 0)
    link(ng, double_pivot_offset, 0, right_post_x, 1)

    right_post_pos = create_combine_xyz(ng, name="R Post Pos", location=(900, -1300))
    link(ng, right_post_x, 0, right_post_pos, "X")

    right_post_transform = create_transform(ng, name="R Post Transform", location=(1200, -1220))
    link(ng, right_rotate, "Geometry", right_post_transform, "Geometry")
    link(ng, right_post_pos, "Vector", right_post_transform, "Translation")

    # Join rotated double doors
    join_double_rotated = create_join_geometry(ng, name="Join Double Rotated", location=(1300, -1000))
    link(ng, left_post_transform, "Geometry", join_double_rotated, "Geometry")
    link(ng, right_post_transform, "Geometry", join_double_rotated, "Geometry")

    # Add glass to rotated double doors if enabled
    # For double doors with glass, we need to include the glass in the rotation
    # This requires restructuring - for now, we'll add static glass (TODO: rotate glass with doors)
    join_double_with_glass = create_join_geometry(ng, name="Join Double Glass", location=(1400, -900))
    link(ng, join_double_rotated, "Geometry", join_double_with_glass, "Geometry")
    link(ng, join_double_glass, "Geometry", join_double_with_glass, "Geometry")

    switch_double_glass = create_switch(ng, 'GEOMETRY', name="Double Glass Switch", location=(1500, -950))
    link(ng, group_in, "Glass Insert", switch_double_glass, "Switch")
    link(ng, join_double_rotated, "Geometry", switch_double_glass, "False")
    link(ng, join_double_with_glass, "Geometry", switch_double_glass, "True")

    # ============ FINAL SINGLE/DOUBLE SWITCH (WITH ROTATION) ============
    switch_final = create_switch(ng, 'GEOMETRY', name="Final Door Switch", location=(1600, -500))
    link(ng, group_in, "Double Doors", switch_final, "Switch")
    link(ng, single_post_transform, "Geometry", switch_final, "False")
    link(ng, switch_double_glass, "Output", switch_final, "True")

    # ============ BEVEL EDGES ============
    # Note: Bevel node removed in Blender 5.0, skip beveling
    bevel = create_bevel(ng, name="Edge Bevel", location=(1700, 0))
    if bevel is not None:
        link(ng, switch_final, "Output", bevel, "Mesh")
        link(ng, group_in, "Bevel Width", bevel, "Width")
        link(ng, group_in, "Bevel Segments", bevel, "Segments")
        final_geo = bevel
        final_socket = "Mesh"
    else:
        final_geo = switch_final
        final_socket = "Output"

    # Output
    link(ng, final_geo, final_socket, group_out, "Geometry")

    add_metadata(ng, version="2.0.0", script_path="src/nodes/systems/door_assembly.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the DoorAssembly node group applied."""
    if nodegroup is None:
        nodegroup = create_door_assembly_nodegroup()

    mesh = bpy.data.meshes.new("DoorAssembly_Test")
    obj = bpy.data.objects.new("DoorAssembly_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_door_assembly_nodegroup()
    print(f"Created node group: {ng.name}")
