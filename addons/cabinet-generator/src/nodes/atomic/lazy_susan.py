# Lazy Susan node group generator
# Atomic component: Rotating circular shelf for corner cabinets

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


def create_lazy_susan_nodegroup():
    """Generate the LazySusan node group.

    Creates a rotating circular shelf (lazy susan) for corner cabinets.
    Supports 5 tray shapes matching Rev-A-Shelf product lines.

    Standard lazy susan sizes:
    - Full round: 16", 18", 20", 22", 24", 28", 32" diameter
    - Kidney: 18", 24", 28", 32"
    - Pie-cut: 18", 24", 28", 31"
    - D-shape: 20", 22", 28", 31", 32"
    - Half-moon: 32", 35", 38" (for BC42/45/48 cabinets)

    Coordinate system:
    - Origin at center of rotation
    - Z = height (shelf surface)
    - Rotation around Z axis

    Inputs:
        Diameter (float): Overall diameter of lazy susan
        Thickness (float): Shelf thickness
        Rim Height (float): Height of raised rim/lip
        Rim Width (float): Width of rim
        Style (int): 0=Full Round, 1=Kidney (270°), 2=Pie Cut (180°),
                     3=D-Shape, 4=Half-Moon
        Mounting Type (int): 0=Cabinet Floor (post), 1=Door-Mounted, 2=Pivot & Slide
        Has Rim (bool): Include raised rim around edge
        Rotation (float): Current rotation angle (for animation)
        Material (material): Shelf material
        Rim Material (material): Rim material (if different)

    Outputs:
        Geometry: The lazy susan mesh

    Returns:
        The created node group
    """
    ng = create_node_group("LazySusan")

    # Create interface panels
    dims_panel = create_panel(ng, "Dimensions")
    style_panel = create_panel(ng, "Style")
    anim_panel = create_panel(ng, "Animation")

    # Dimension inputs
    add_float_socket(ng, "Diameter", default=0.5, min_val=0.3, max_val=0.8,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Thickness", default=0.018, min_val=0.01, max_val=0.03,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Rim Height", default=0.025, min_val=0.01, max_val=0.05,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Rim Width", default=0.02, min_val=0.01, max_val=0.04,
                     subtype='DISTANCE', panel=dims_panel)

    # Style options
    # 0=Full Round, 1=Kidney, 2=Pie Cut, 3=D-Shape, 4=Half-Moon
    add_int_socket(ng, "Style", default=0, min_val=0, max_val=4, panel=style_panel)
    # Mounting: 0=Cabinet Floor (post), 1=Door-Mounted, 2=Pivot & Slide
    add_int_socket(ng, "Mounting Type", default=0, min_val=0, max_val=2, panel=style_panel)
    add_bool_socket(ng, "Has Rim", default=True, panel=style_panel)

    # Animation
    add_float_socket(ng, "Rotation", default=0.0, min_val=0.0, max_val=360.0,
                     subtype='NONE', panel=anim_panel)

    # Materials
    add_material_socket(ng, "Material")
    add_material_socket(ng, "Rim Material")

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-800, 0))
    group_out = create_group_output(ng, location=(1200, 0))

    # ============ FULL ROUND SHELF (Style 0) ============
    # Create cylinder for the base shelf
    cylinder = ng.nodes.new('GeometryNodeMeshCylinder')
    cylinder.name = "Full Round Shelf"
    cylinder.location = (-400, 300)
    cylinder.fill_type = 'NGON'

    # Radius = diameter / 2
    radius = create_math(ng, 'DIVIDE', name="Radius", location=(-550, 350))
    link(ng, group_in, "Diameter", radius, 0)
    set_default(radius, 1, 2.0)

    link(ng, radius, 0, cylinder, "Radius")
    link(ng, group_in, "Thickness", cylinder, "Depth")
    set_default(cylinder, "Vertices", 32)

    # ============ KIDNEY SHELF (Style 1) - 270° ============
    # Use a cylinder with part cut out via boolean
    kidney_base = ng.nodes.new('GeometryNodeMeshCylinder')
    kidney_base.name = "Kidney Base"
    kidney_base.location = (-400, 0)
    kidney_base.fill_type = 'NGON'

    link(ng, radius, 0, kidney_base, "Radius")
    link(ng, group_in, "Thickness", kidney_base, "Depth")
    set_default(kidney_base, "Vertices", 32)

    # Create cutout cube for the 90° removed section
    cutout = ng.nodes.new('GeometryNodeMeshCube')
    cutout.name = "Kidney Cutout"
    cutout.location = (-400, -150)

    cutout_size = create_combine_xyz(ng, name="Cutout Size", location=(-550, -150))
    link(ng, radius, 0, cutout_size, "X")
    link(ng, radius, 0, cutout_size, "Y")

    # Cutout thickness slightly larger than shelf
    cutout_thick = create_math(ng, 'MULTIPLY', name="Cutout Thick", location=(-650, -200))
    link(ng, group_in, "Thickness", cutout_thick, 0)
    set_default(cutout_thick, 1, 2.0)
    link(ng, cutout_thick, 0, cutout_size, "Z")
    link(ng, cutout_size, "Vector", cutout, "Size")

    # Position cutout at corner
    cutout_pos = create_combine_xyz(ng, name="Cutout Pos", location=(-550, -250))
    radius_half = create_math(ng, 'DIVIDE', name="Radius Half", location=(-650, -250))
    link(ng, radius, 0, radius_half, 0)
    set_default(radius_half, 1, 2.0)
    link(ng, radius_half, 0, cutout_pos, "X")
    link(ng, radius_half, 0, cutout_pos, "Y")

    cutout_transform = create_transform(ng, name="Cutout Transform", location=(-300, -150))
    link(ng, cutout_pos, "Vector", cutout_transform, "Translation")
    link(ng, cutout, "Mesh", cutout_transform, "Geometry")

    # Boolean difference
    kidney_boolean = ng.nodes.new('GeometryNodeMeshBoolean')
    kidney_boolean.name = "Kidney Boolean"
    kidney_boolean.location = (-100, -50)
    kidney_boolean.operation = 'DIFFERENCE'

    link(ng, kidney_base, "Mesh", kidney_boolean, "Mesh 1")
    link(ng, cutout_transform, "Geometry", kidney_boolean, "Mesh 2")

    # ============ PIE CUT SHELF (Style 2) - 180° ============
    pie_base = ng.nodes.new('GeometryNodeMeshCylinder')
    pie_base.name = "Pie Base"
    pie_base.location = (-400, -400)
    pie_base.fill_type = 'NGON'

    link(ng, radius, 0, pie_base, "Radius")
    link(ng, group_in, "Thickness", pie_base, "Depth")
    set_default(pie_base, "Vertices", 32)

    # Create half-circle cutout
    pie_cutout = ng.nodes.new('GeometryNodeMeshCube')
    pie_cutout.name = "Pie Cutout"
    pie_cutout.location = (-400, -550)

    pie_cutout_size = create_combine_xyz(ng, name="Pie Cutout Size", location=(-550, -500))
    link(ng, group_in, "Diameter", pie_cutout_size, "X")  # Full diameter width
    link(ng, radius, 0, pie_cutout_size, "Y")  # Half depth
    link(ng, cutout_thick, 0, pie_cutout_size, "Z")
    link(ng, pie_cutout_size, "Vector", pie_cutout, "Size")

    pie_cutout_pos = create_combine_xyz(ng, name="Pie Cutout Pos", location=(-550, -600))
    radius_half_neg = create_math(ng, 'MULTIPLY', name="Radius Half Neg", location=(-650, -550))
    link(ng, radius_half, 0, radius_half_neg, 0)
    set_default(radius_half_neg, 1, -1.0)
    link(ng, radius_half_neg, 0, pie_cutout_pos, "Y")

    pie_cutout_transform = create_transform(ng, name="Pie Cutout Transform", location=(-300, -550))
    link(ng, pie_cutout_pos, "Vector", pie_cutout_transform, "Translation")
    link(ng, pie_cutout, "Mesh", pie_cutout_transform, "Geometry")

    pie_boolean = ng.nodes.new('GeometryNodeMeshBoolean')
    pie_boolean.name = "Pie Boolean"
    pie_boolean.location = (-100, -450)
    pie_boolean.operation = 'DIFFERENCE'

    link(ng, pie_base, "Mesh", pie_boolean, "Mesh 1")
    link(ng, pie_cutout_transform, "Geometry", pie_boolean, "Mesh 2")

    # ============ D-SHAPE SHELF (Style 3) ============
    # Half-circle with flat back: cylinder minus rear half
    dshape_base = ng.nodes.new('GeometryNodeMeshCylinder')
    dshape_base.name = "D-Shape Base"
    dshape_base.location = (-400, -800)
    dshape_base.fill_type = 'NGON'

    link(ng, radius, 0, dshape_base, "Radius")
    link(ng, group_in, "Thickness", dshape_base, "Depth")
    set_default(dshape_base, "Vertices", 32)

    # Cutout removes the rear ~40% (flat back at ~0.1*radius from center)
    dshape_cutout = ng.nodes.new('GeometryNodeMeshCube')
    dshape_cutout.name = "D-Shape Cutout"
    dshape_cutout.location = (-400, -950)

    dshape_cutout_size = create_combine_xyz(ng, name="D Cutout Size", location=(-550, -900))
    link(ng, group_in, "Diameter", dshape_cutout_size, "X")  # Full width
    link(ng, radius, 0, dshape_cutout_size, "Y")  # Half depth
    link(ng, cutout_thick, 0, dshape_cutout_size, "Z")
    link(ng, dshape_cutout_size, "Vector", dshape_cutout, "Size")

    # Position cutout at rear of circle
    dshape_cutout_pos = create_combine_xyz(ng, name="D Cutout Pos", location=(-550, -1000))
    # Offset: -(radius - radius*0.3) = place cut so flat back is ~30% from rear
    dshape_back_offset = create_math(ng, 'MULTIPLY', name="D Back Offset", location=(-650, -950))
    link(ng, radius, 0, dshape_back_offset, 0)
    set_default(dshape_back_offset, 1, -0.8)
    link(ng, dshape_back_offset, 0, dshape_cutout_pos, "Y")

    dshape_cutout_transform = create_transform(ng, name="D Cutout Xform", location=(-300, -950))
    link(ng, dshape_cutout_pos, "Vector", dshape_cutout_transform, "Translation")
    link(ng, dshape_cutout, "Mesh", dshape_cutout_transform, "Geometry")

    dshape_boolean = ng.nodes.new('GeometryNodeMeshBoolean')
    dshape_boolean.name = "D-Shape Boolean"
    dshape_boolean.location = (-100, -850)
    dshape_boolean.operation = 'DIFFERENCE'

    link(ng, dshape_base, "Mesh", dshape_boolean, "Mesh 1")
    link(ng, dshape_cutout_transform, "Geometry", dshape_boolean, "Mesh 2")

    # ============ HALF-MOON SHELF (Style 4) ============
    # Semicircle: cylinder minus one full half
    halfmoon_base = ng.nodes.new('GeometryNodeMeshCylinder')
    halfmoon_base.name = "Half-Moon Base"
    halfmoon_base.location = (-400, -1200)
    halfmoon_base.fill_type = 'NGON'

    link(ng, radius, 0, halfmoon_base, "Radius")
    link(ng, group_in, "Thickness", halfmoon_base, "Depth")
    set_default(halfmoon_base, "Vertices", 32)

    # Cutout removes exactly one half
    halfmoon_cutout = ng.nodes.new('GeometryNodeMeshCube')
    halfmoon_cutout.name = "Half-Moon Cutout"
    halfmoon_cutout.location = (-400, -1350)

    halfmoon_cutout_size = create_combine_xyz(ng, name="HM Cutout Size", location=(-550, -1300))
    link(ng, group_in, "Diameter", halfmoon_cutout_size, "X")
    link(ng, group_in, "Diameter", halfmoon_cutout_size, "Y")
    link(ng, cutout_thick, 0, halfmoon_cutout_size, "Z")
    link(ng, halfmoon_cutout_size, "Vector", halfmoon_cutout, "Size")

    halfmoon_cutout_pos = create_combine_xyz(ng, name="HM Cutout Pos", location=(-550, -1400))
    link(ng, radius_half_neg, 0, halfmoon_cutout_pos, "X")

    halfmoon_cutout_transform = create_transform(ng, name="HM Cutout Xform", location=(-300, -1350))
    link(ng, halfmoon_cutout_pos, "Vector", halfmoon_cutout_transform, "Translation")
    link(ng, halfmoon_cutout, "Mesh", halfmoon_cutout_transform, "Geometry")

    halfmoon_boolean = ng.nodes.new('GeometryNodeMeshBoolean')
    halfmoon_boolean.name = "Half-Moon Boolean"
    halfmoon_boolean.location = (-100, -1250)
    halfmoon_boolean.operation = 'DIFFERENCE'

    link(ng, halfmoon_base, "Mesh", halfmoon_boolean, "Mesh 1")
    link(ng, halfmoon_cutout_transform, "Geometry", halfmoon_boolean, "Mesh 2")

    # ============ STYLE SWITCHING (5 styles) ============
    # Cascading switch pattern: check each style from highest to lowest,
    # chain switches so the final output is the correct geometry.

    # Compare: Style == 4 (Half-Moon)
    is_halfmoon = create_compare(ng, 'EQUAL', 'INT', name="Is Half-Moon", location=(100, -400))
    link(ng, group_in, "Style", is_halfmoon, 2)
    set_default(is_halfmoon, 3, 4)

    # Compare: Style == 3 (D-Shape)
    is_dshape = create_compare(ng, 'EQUAL', 'INT', name="Is D-Shape", location=(100, -250))
    link(ng, group_in, "Style", is_dshape, 2)
    set_default(is_dshape, 3, 3)

    # Compare: Style == 2 (Pie Cut)
    is_pie = create_compare(ng, 'EQUAL', 'INT', name="Is Pie Cut", location=(100, -100))
    link(ng, group_in, "Style", is_pie, 2)
    set_default(is_pie, 3, 2)

    # Compare: Style == 1 (Kidney)
    is_kidney = create_compare(ng, 'EQUAL', 'INT', name="Is Kidney", location=(100, 50))
    link(ng, group_in, "Style", is_kidney, 2)
    set_default(is_kidney, 3, 1)

    # Build switch chain from bottom up:
    # Default = Full Circle (style 0), override with each match

    # Switch: Half-Moon vs D-Shape
    switch_hm_d = create_switch(ng, 'GEOMETRY', name="HM/D Switch", location=(250, -350))
    link(ng, is_halfmoon, "Result", switch_hm_d, "Switch")
    link(ng, dshape_boolean, "Mesh", switch_hm_d, "False")
    link(ng, halfmoon_boolean, "Mesh", switch_hm_d, "True")

    # Switch: D-Shape vs Pie
    switch_d_pie = create_switch(ng, 'GEOMETRY', name="D/Pie Switch", location=(350, -200))
    link(ng, is_dshape, "Result", switch_d_pie, "Switch")
    link(ng, pie_boolean, "Mesh", switch_d_pie, "False")
    link(ng, dshape_boolean, "Mesh", switch_d_pie, "True")

    # Switch: Pie vs Kidney
    switch_pie_kidney = create_switch(ng, 'GEOMETRY', name="Pie/Kidney", location=(250, -50))
    link(ng, is_pie, "Result", switch_pie_kidney, "Switch")
    link(ng, kidney_boolean, "Mesh", switch_pie_kidney, "False")
    link(ng, pie_boolean, "Mesh", switch_pie_kidney, "True")

    # Switch: Kidney vs Full
    switch_kidney_full = create_switch(ng, 'GEOMETRY', name="Kidney/Full", location=(350, 50))
    link(ng, is_kidney, "Result", switch_kidney_full, "Switch")
    link(ng, cylinder, "Mesh", switch_kidney_full, "False")
    link(ng, kidney_boolean, "Mesh", switch_kidney_full, "True")

    # Final cascading switch: select correct geometry by style
    # Style 0 (Full) → kidney_full false path
    # Style 1 (Kidney) → kidney_full true path
    # Style 2 (Pie) → override
    # Style 3 (D-Shape) → override
    # Style 4 (Half-Moon) → override

    # Chain: start with kidney/full, override with pie, d-shape, half-moon
    switch_s2 = create_switch(ng, 'GEOMETRY', name="Style>=2", location=(450, -50))
    link(ng, is_pie, "Result", switch_s2, "Switch")
    link(ng, switch_kidney_full, "Output", switch_s2, "False")
    link(ng, pie_boolean, "Mesh", switch_s2, "True")

    switch_s3 = create_switch(ng, 'GEOMETRY', name="Style>=3", location=(550, -150))
    link(ng, is_dshape, "Result", switch_s3, "Switch")
    link(ng, switch_s2, "Output", switch_s3, "False")
    link(ng, dshape_boolean, "Mesh", switch_s3, "True")

    switch_style = create_switch(ng, 'GEOMETRY', name="Style Final", location=(650, -250))
    link(ng, is_halfmoon, "Result", switch_style, "Switch")
    link(ng, switch_s3, "Output", switch_style, "False")
    link(ng, halfmoon_boolean, "Mesh", switch_style, "True")

    # ============ RIM (optional) ============
    # Create torus for rim
    rim = ng.nodes.new('GeometryNodeMeshCylinder')
    rim.name = "Rim"
    rim.location = (-400, -750)
    rim.fill_type = 'NONE'  # Hollow cylinder for rim

    # Rim inner radius
    rim_inner = create_math(ng, 'SUBTRACT', name="Rim Inner", location=(-600, -750))
    link(ng, radius, 0, rim_inner, 0)
    link(ng, group_in, "Rim Width", rim_inner, 1)

    link(ng, radius, 0, rim, "Radius")
    link(ng, group_in, "Rim Height", rim, "Depth")
    set_default(rim, "Vertices", 32)

    # Position rim on top of shelf
    rim_pos = create_combine_xyz(ng, name="Rim Pos", location=(-550, -850))
    rim_z = create_math(ng, 'DIVIDE', name="Rim Z", location=(-650, -850))
    thick_half = create_math(ng, 'DIVIDE', name="Thick Half", location=(-750, -850))
    link(ng, group_in, "Thickness", thick_half, 0)
    set_default(thick_half, 1, 2.0)

    rim_h_half = create_math(ng, 'DIVIDE', name="Rim H Half", location=(-750, -900))
    link(ng, group_in, "Rim Height", rim_h_half, 0)
    set_default(rim_h_half, 1, 2.0)

    rim_z_add = create_math(ng, 'ADD', name="Rim Z Add", location=(-650, -900))
    link(ng, thick_half, 0, rim_z_add, 0)
    link(ng, rim_h_half, 0, rim_z_add, 1)

    link(ng, rim_z_add, 0, rim_pos, "Z")

    rim_transform = create_transform(ng, name="Rim Transform", location=(-250, -800))
    link(ng, rim_pos, "Vector", rim_transform, "Translation")
    link(ng, rim, "Mesh", rim_transform, "Geometry")

    # Rim material
    rim_mat = create_set_material(ng, name="Rim Material", location=(-100, -800))
    link(ng, rim_transform, "Geometry", rim_mat, "Geometry")
    link(ng, group_in, "Rim Material", rim_mat, "Material")

    # Switch for rim
    switch_rim = create_switch(ng, 'GEOMETRY', name="Rim Switch", location=(100, -700))
    link(ng, group_in, "Has Rim", switch_rim, "Switch")
    link(ng, rim_mat, "Geometry", switch_rim, "True")

    # ============ SET SHELF MATERIAL ============
    shelf_mat = create_set_material(ng, name="Shelf Material", location=(800, 100))
    link(ng, switch_style, "Output", shelf_mat, "Geometry")
    link(ng, group_in, "Material", shelf_mat, "Material")

    # ============ JOIN SHELF + RIM ============
    join_all = create_join_geometry(ng, name="Join All", location=(900, 0))
    link(ng, shelf_mat, "Geometry", join_all, "Geometry")
    link(ng, switch_rim, "Output", join_all, "Geometry")

    # ============ ROTATION ANIMATION ============
    # Convert degrees to radians
    rotation_rad = create_math(ng, 'RADIANS', name="Rotation Rad", location=(900, -200))
    link(ng, group_in, "Rotation", rotation_rad, 0)

    rotation_vec = create_combine_xyz(ng, name="Rotation Vec", location=(1000, -200))
    link(ng, rotation_rad, 0, rotation_vec, "Z")

    final_transform = create_transform(ng, name="Final Transform", location=(1050, 0))
    link(ng, join_all, "Geometry", final_transform, "Geometry")
    link(ng, rotation_vec, "Vector", final_transform, "Rotation")

    # Output
    link(ng, final_transform, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="2.0.0", script_path="src/nodes/atomic/lazy_susan.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the LazySusan node group applied."""
    if nodegroup is None:
        nodegroup = create_lazy_susan_nodegroup()

    mesh = bpy.data.meshes.new("LazySusan_Test")
    obj = bpy.data.objects.new("LazySusan_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_lazy_susan_nodegroup()
    print(f"Created node group: {ng.name}")
