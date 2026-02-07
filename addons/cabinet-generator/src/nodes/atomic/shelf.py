# Shelf node group generator
# Atomic component: Single parametric shelf panel

import bpy
from ..utils import (
    create_node_group,
    add_geometry_output,
    add_float_socket,
    add_material_socket,
    create_group_input,
    create_group_output,
    create_cube,
    create_set_material,
    create_combine_xyz,
    link,
    add_metadata,
)


def create_shelf_nodegroup():
    """Generate the Shelf node group.

    A simple parametric shelf panel defined by width, depth, and thickness.
    The shelf is centered on X and Y, with bottom face at Z=0.

    Inputs:
        Width (float): Shelf width (X dimension)
        Depth (float): Shelf depth (Y dimension)
        Thickness (float): Shelf thickness (Z dimension)
        Material (material): Optional material assignment

    Outputs:
        Geometry: The shelf mesh

    Returns:
        The created node group
    """
    # Create node group
    ng = create_node_group("Shelf")

    # Add interface sockets
    add_float_socket(ng, "Width", default=0.6, min_val=0.1, max_val=3.0,
                     subtype='DISTANCE')
    add_float_socket(ng, "Depth", default=0.5, min_val=0.1, max_val=2.0,
                     subtype='DISTANCE')
    add_float_socket(ng, "Thickness", default=0.018, min_val=0.005, max_val=0.1,
                     subtype='DISTANCE')
    add_material_socket(ng, "Material")
    add_geometry_output(ng)

    # Create nodes
    group_in = create_group_input(ng, location=(-400, 0))
    group_out = create_group_output(ng, location=(400, 0))

    # Cube node - base shelf geometry
    cube = create_cube(ng, name="Shelf Cube", location=(-100, 100))

    # Combine XYZ for cube size (width, depth, thickness)
    size_combine = create_combine_xyz(ng, name="Size", location=(-250, 100))

    # Set material node
    set_mat = create_set_material(ng, name="Set Material", location=(100, 0))

    # Wire connections
    # Size inputs -> Combine XYZ
    link(ng, group_in, "Width", size_combine, "X")
    link(ng, group_in, "Depth", size_combine, "Y")
    link(ng, group_in, "Thickness", size_combine, "Z")

    # Combine XYZ -> Cube size
    link(ng, size_combine, "Vector", cube, "Size")

    # Cube -> Set Material -> Output
    link(ng, cube, "Mesh", set_mat, "Geometry")
    link(ng, group_in, "Material", set_mat, "Material")
    link(ng, set_mat, "Geometry", group_out, "Geometry")

    # Add metadata
    add_metadata(ng, version="1.0.0",
                 script_path="src/nodes/atomic/shelf.py")

    return ng


def create_test_object(shelf_nodegroup=None):
    """Create a test object with the Shelf node group applied.

    Useful for quick testing in Blender.

    Args:
        shelf_nodegroup: Existing node group to use, or None to create new

    Returns:
        The created mesh object with geometry nodes modifier
    """
    if shelf_nodegroup is None:
        shelf_nodegroup = create_shelf_nodegroup()

    # Create empty mesh
    mesh = bpy.data.meshes.new("Shelf_Test")
    obj = bpy.data.objects.new("Shelf_Test", mesh)

    # Link to active collection
    bpy.context.collection.objects.link(obj)

    # Add geometry nodes modifier
    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = shelf_nodegroup

    return obj


# Allow running directly in Blender
if __name__ == "__main__":
    ng = create_shelf_nodegroup()
    print(f"Created node group: {ng.name}")
