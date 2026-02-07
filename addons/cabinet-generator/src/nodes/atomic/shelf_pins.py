# Shelf Pins node group generator
# Atomic component: Adjustable shelf pin holes pattern
# Coordinate system: X=width, Y=depth, Z=height (Z-up)

import bpy
from ..utils import (
    create_node_group,
    add_geometry_output,
    add_float_socket,
    add_int_socket,
    add_bool_socket,
    create_panel,
    create_group_input,
    create_group_output,
    create_math,
    create_combine_xyz,
    create_transform,
    create_join_geometry,
    link,
    set_default,
    add_metadata,
)


def create_shelf_pins_nodegroup():
    """Generate the ShelfPins node group.

    Creates a pattern of shelf pin holes on cabinet side panels.
    Standard 32mm system (European) or 1.25" system (American).

    Inputs:
        Height: Panel height to cover
        Depth: Panel depth (for positioning)
        Hole Diameter: Pin hole diameter
        Vertical Spacing: Distance between holes
        Rows Front: Number of rows from front
        Rows Back: Number of rows from back
        Start Height: Distance from bottom to first hole
        End Height: Distance from top to last hole
        Side: 0=Left, 1=Right (affects X offset direction)

    Outputs:
        Geometry: Cylinder holes for boolean subtraction
    """
    ng = create_node_group("ShelfPins")

    # Create interface
    dims_panel = create_panel(ng, "Dimensions")
    spacing_panel = create_panel(ng, "Spacing")
    options_panel = create_panel(ng, "Options")

    add_float_socket(ng, "Height", default=0.7, min_val=0.3, max_val=2.4,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Depth", default=0.5, min_val=0.3, max_val=0.7,
                     subtype='DISTANCE', panel=dims_panel)
    add_float_socket(ng, "Panel Thickness", default=0.018, min_val=0.012, max_val=0.025,
                     subtype='DISTANCE', panel=dims_panel)

    add_float_socket(ng, "Hole Diameter", default=0.005, min_val=0.003, max_val=0.008,
                     subtype='DISTANCE', panel=spacing_panel)
    add_float_socket(ng, "Vertical Spacing", default=0.032, min_val=0.025, max_val=0.05,
                     subtype='DISTANCE', panel=spacing_panel)
    add_float_socket(ng, "Front Offset", default=0.037, min_val=0.02, max_val=0.1,
                     subtype='DISTANCE', panel=spacing_panel)
    add_float_socket(ng, "Back Offset", default=0.037, min_val=0.02, max_val=0.1,
                     subtype='DISTANCE', panel=spacing_panel)
    add_float_socket(ng, "Start Height", default=0.1, min_val=0.05, max_val=0.2,
                     subtype='DISTANCE', panel=spacing_panel)
    add_float_socket(ng, "End Height", default=0.1, min_val=0.05, max_val=0.2,
                     subtype='DISTANCE', panel=spacing_panel)

    add_int_socket(ng, "Side", default=0, min_val=0, max_val=1, panel=options_panel)
    add_bool_socket(ng, "Double Row", default=True, panel=options_panel)

    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-1000, 0))
    group_out = create_group_output(ng, location=(1000, 0))

    # ============ CALCULATE NUMBER OF HOLES ============
    # Available height = Height - Start Height - End Height
    avail_height = create_math(ng, 'SUBTRACT', name="Avail Height 1", location=(-800, 200))
    link(ng, group_in, "Height", avail_height, 0)
    link(ng, group_in, "Start Height", avail_height, 1)

    avail_height_2 = create_math(ng, 'SUBTRACT', name="Avail Height 2", location=(-700, 200))
    link(ng, avail_height, 0, avail_height_2, 0)
    link(ng, group_in, "End Height", avail_height_2, 1)

    # Number of holes = floor(avail_height / spacing) + 1
    num_holes_raw = create_math(ng, 'DIVIDE', name="Num Holes Raw", location=(-600, 200))
    link(ng, avail_height_2, 0, num_holes_raw, 0)
    link(ng, group_in, "Vertical Spacing", num_holes_raw, 1)

    num_holes = create_math(ng, 'FLOOR', name="Num Holes Floor", location=(-500, 200))
    link(ng, num_holes_raw, 0, num_holes, 0)

    # ============ CREATE SINGLE HOLE (CYLINDER) ============
    # Using a cube as simplified representation (proper would use cylinder mesh)
    hole_node = ng.nodes.new('GeometryNodeMeshCylinder')
    hole_node.name = "Hole Cylinder"
    hole_node.label = "Hole Cylinder"
    hole_node.location = (-600, 0)

    # Hole radius
    hole_radius = create_math(ng, 'DIVIDE', name="Hole Radius", location=(-700, -50))
    link(ng, group_in, "Hole Diameter", hole_radius, 0)
    set_default(hole_radius, 1, 2.0)

    link(ng, hole_radius, 0, hole_node, "Radius")
    link(ng, group_in, "Panel Thickness", hole_node, "Depth")
    set_default(hole_node, "Vertices", 8)  # Low poly cylinder

    # ============ CALCULATE X POSITION ============
    # For left side (Side=0): X is positive (holes face inward)
    # For right side (Side=1): X is negative
    panel_half = create_math(ng, 'DIVIDE', name="Panel Half", location=(-800, -200))
    link(ng, group_in, "Panel Thickness", panel_half, 0)
    set_default(panel_half, 1, 2.0)

    # ============ FRONT ROW Y POSITION ============
    front_y = create_math(ng, 'MULTIPLY', name="Front Y Neg", location=(-700, -300))
    link(ng, group_in, "Front Offset", front_y, 0)
    set_default(front_y, 1, -1.0)

    # ============ BACK ROW Y POSITION ============
    back_y = create_math(ng, 'MULTIPLY', name="Back Y", location=(-700, -400))
    link(ng, group_in, "Depth", back_y, 0)
    set_default(back_y, 1, -1.0)
    back_y_offset = create_math(ng, 'ADD', name="Back Y Offset", location=(-600, -400))
    link(ng, back_y, 0, back_y_offset, 0)
    link(ng, group_in, "Back Offset", back_y_offset, 1)

    # ============ CREATE HOLE INSTANCES (DYNAMIC) ============
    # Use Instance on Points with Mesh Line for parametric hole count

    # Ensure at least 1 point for mesh line
    num_holes_plus1 = create_math(ng, 'ADD', name="Num Holes+1", location=(-400, 200))
    link(ng, num_holes, 0, num_holes_plus1, 0)
    set_default(num_holes_plus1, 1, 1.0)

    hole_count_max = create_math(ng, 'MAXIMUM', name="Hole Count Max", location=(-300, 200))
    link(ng, num_holes_plus1, 0, hole_count_max, 0)
    set_default(hole_count_max, 1, 1)

    # End Z offset = (hole_count - 1) * spacing
    hole_count_minus1 = create_math(ng, 'SUBTRACT', name="Count-1", location=(-400, 150))
    link(ng, num_holes_plus1, 0, hole_count_minus1, 0)
    set_default(hole_count_minus1, 1, 1.0)

    end_z_offset = create_math(ng, 'MULTIPLY', name="End Z Offset", location=(-300, 150))
    link(ng, group_in, "Vertical Spacing", end_z_offset, 0)
    link(ng, hole_count_minus1, 0, end_z_offset, 1)

    z_end_offset = create_combine_xyz(ng, name="Z End Offset", location=(-200, 150))
    set_default(z_end_offset, "X", 0.0)
    set_default(z_end_offset, "Y", 0.0)
    link(ng, end_z_offset, 0, z_end_offset, "Z")

    # ============ FRONT ROW ============
    front_start = create_combine_xyz(ng, name="Front Start", location=(-300, 0))
    link(ng, panel_half, 0, front_start, "X")
    link(ng, front_y, 0, front_start, "Y")
    link(ng, group_in, "Start Height", front_start, "Z")

    front_line = ng.nodes.new('GeometryNodeMeshLine')
    front_line.name = "Front Row Line"
    front_line.location = (-150, 0)
    front_line.mode = 'END_POINTS'

    link(ng, hole_count_max, 0, front_line, "Count")
    link(ng, front_start, "Vector", front_line, "Start Location")
    link(ng, z_end_offset, "Vector", front_line, "Offset")

    front_instance = ng.nodes.new('GeometryNodeInstanceOnPoints')
    front_instance.name = "Instance Front"
    front_instance.location = (0, 0)

    link(ng, front_line, "Mesh", front_instance, "Points")
    link(ng, hole_node, "Mesh", front_instance, "Instance")

    front_realize = ng.nodes.new('GeometryNodeRealizeInstances')
    front_realize.name = "Realize Front"
    front_realize.location = (150, 0)
    link(ng, front_instance, "Instances", front_realize, "Geometry")

    # ============ BACK ROW ============
    back_start = create_combine_xyz(ng, name="Back Start", location=(-300, -400))
    link(ng, panel_half, 0, back_start, "X")
    link(ng, back_y_offset, 0, back_start, "Y")
    link(ng, group_in, "Start Height", back_start, "Z")

    back_line = ng.nodes.new('GeometryNodeMeshLine')
    back_line.name = "Back Row Line"
    back_line.location = (-150, -400)
    back_line.mode = 'END_POINTS'

    link(ng, hole_count_max, 0, back_line, "Count")
    link(ng, back_start, "Vector", back_line, "Start Location")
    link(ng, z_end_offset, "Vector", back_line, "Offset")

    back_instance = ng.nodes.new('GeometryNodeInstanceOnPoints')
    back_instance.name = "Instance Back"
    back_instance.location = (0, -400)

    link(ng, back_line, "Mesh", back_instance, "Points")
    link(ng, hole_node, "Mesh", back_instance, "Instance")

    back_realize = ng.nodes.new('GeometryNodeRealizeInstances')
    back_realize.name = "Realize Back"
    back_realize.location = (150, -400)
    link(ng, back_instance, "Instances", back_realize, "Geometry")

    # ============ JOIN ALL ROWS ============
    join_all = create_join_geometry(ng, name="Join All Holes", location=(300, 0))
    link(ng, front_realize, "Geometry", join_all, "Geometry")
    link(ng, back_realize, "Geometry", join_all, "Geometry")

    # ============ OUTPUT ============
    link(ng, join_all, "Geometry", group_out, "Geometry")

    add_metadata(ng, version="1.0.0", script_path="src/nodes/atomic/shelf_pins.py")

    return ng


def create_test_object(nodegroup=None):
    """Create a test object with the ShelfPins node group applied."""
    if nodegroup is None:
        nodegroup = create_shelf_pins_nodegroup()

    mesh = bpy.data.meshes.new("ShelfPins_Test")
    obj = bpy.data.objects.new("ShelfPins_Test", mesh)
    bpy.context.collection.objects.link(obj)

    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup

    return obj


if __name__ == "__main__":
    ng = create_shelf_pins_nodegroup()
    print(f"Created node group: {ng.name}")
