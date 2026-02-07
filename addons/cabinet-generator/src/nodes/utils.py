# Node generation utility functions
# Reusable helpers extracted from GN_Carcass reference patterns

import bpy


def create_node_group(name, remove_existing=True):
    """Create a new geometry node group.

    Args:
        name: Name for the node group
        remove_existing: If True, removes existing node group with same name

    Returns:
        The new node group
    """
    if remove_existing and name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])

    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    return ng


def add_geometry_output(ng, name="Geometry"):
    """Add geometry output socket to node group."""
    ng.interface.new_socket(
        name=name,
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )


def add_geometry_input(ng, name="Geometry"):
    """Add geometry input socket to node group."""
    ng.interface.new_socket(
        name=name,
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )


def add_float_socket(ng, name, default=0.0, min_val=None, max_val=None,
                     subtype='NONE', panel=None):
    """Add float input socket to node group.

    Args:
        ng: Node group
        name: Socket name
        default: Default value
        min_val: Minimum value (optional)
        max_val: Maximum value (optional)
        subtype: Socket subtype ('NONE', 'DISTANCE', 'ANGLE', 'FACTOR', etc.)
        panel: Panel to add socket to (optional)

    Returns:
        The new socket
    """
    socket = ng.interface.new_socket(
        name=name,
        in_out='INPUT',
        socket_type='NodeSocketFloat',
        parent=panel
    )
    socket.default_value = default
    socket.subtype = subtype
    if min_val is not None:
        socket.min_value = min_val
    if max_val is not None:
        socket.max_value = max_val
    return socket


def add_int_socket(ng, name, default=0, min_val=None, max_val=None, panel=None):
    """Add integer input socket to node group."""
    socket = ng.interface.new_socket(
        name=name,
        in_out='INPUT',
        socket_type='NodeSocketInt',
        parent=panel
    )
    socket.default_value = default
    if min_val is not None:
        socket.min_value = min_val
    if max_val is not None:
        socket.max_value = max_val
    return socket


def add_bool_socket(ng, name, default=False, panel=None):
    """Add boolean input socket to node group."""
    socket = ng.interface.new_socket(
        name=name,
        in_out='INPUT',
        socket_type='NodeSocketBool',
        parent=panel
    )
    socket.default_value = default
    return socket


def add_material_socket(ng, name="Material", panel=None):
    """Add material input socket to node group."""
    return ng.interface.new_socket(
        name=name,
        in_out='INPUT',
        socket_type='NodeSocketMaterial',
        parent=panel
    )


def add_vector_socket(ng, name, default=(0.0, 0.0, 0.0), panel=None):
    """Add vector input socket to node group."""
    socket = ng.interface.new_socket(
        name=name,
        in_out='INPUT',
        socket_type='NodeSocketVector',
        parent=panel
    )
    socket.default_value = default
    return socket


def create_panel(ng, name, default_closed=False):
    """Create an interface panel for organizing sockets.

    Args:
        ng: Node group
        name: Panel name
        default_closed: Whether panel starts collapsed

    Returns:
        The new panel
    """
    panel = ng.interface.new_panel(name, default_closed=default_closed)
    return panel


# Node creation helpers

def create_group_input(ng, location=(-400, 0)):
    """Create group input node."""
    node = ng.nodes.new('NodeGroupInput')
    node.location = location
    return node


def create_group_output(ng, location=(400, 0)):
    """Create group output node."""
    node = ng.nodes.new('NodeGroupOutput')
    node.location = location
    return node


def create_cube(ng, name=None, location=(0, 0)):
    """Create mesh cube node."""
    node = ng.nodes.new('GeometryNodeMeshCube')
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_math(ng, operation='ADD', name=None, location=(0, 0)):
    """Create math node with specified operation.

    Common operations: ADD, SUBTRACT, MULTIPLY, DIVIDE, MULTIPLY_ADD,
    MINIMUM, MAXIMUM, ABSOLUTE, SNAP, FLOOR, CEIL, ROUND
    """
    node = ng.nodes.new('ShaderNodeMath')
    node.operation = operation
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_vector_math(ng, operation='ADD', name=None, location=(0, 0)):
    """Create vector math node."""
    node = ng.nodes.new('ShaderNodeVectorMath')
    node.operation = operation
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_combine_xyz(ng, name=None, location=(0, 0)):
    """Create combine XYZ node."""
    node = ng.nodes.new('ShaderNodeCombineXYZ')
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_separate_xyz(ng, name=None, location=(0, 0)):
    """Create separate XYZ node."""
    node = ng.nodes.new('ShaderNodeSeparateXYZ')
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_set_position(ng, name=None, location=(0, 0)):
    """Create set position node."""
    node = ng.nodes.new('GeometryNodeSetPosition')
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_transform(ng, name=None, location=(0, 0)):
    """Create transform geometry node."""
    node = ng.nodes.new('GeometryNodeTransform')
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_join_geometry(ng, name=None, location=(0, 0)):
    """Create join geometry node."""
    node = ng.nodes.new('GeometryNodeJoinGeometry')
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_set_material(ng, name=None, location=(0, 0)):
    """Create set material node."""
    node = ng.nodes.new('GeometryNodeSetMaterial')
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_switch(ng, input_type='GEOMETRY', name=None, location=(0, 0)):
    """Create switch node.

    Args:
        input_type: Type of switch (GEOMETRY, FLOAT, INT, BOOLEAN, VECTOR, etc.)
    """
    node = ng.nodes.new('GeometryNodeSwitch')
    node.input_type = input_type
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_boolean_math(ng, operation='AND', name=None, location=(0, 0)):
    """Create boolean math node.

    Operations: AND, OR, NOT, NAND, NOR, XNOR, XOR, IMPLY, NIMPLY
    """
    node = ng.nodes.new('FunctionNodeBooleanMath')
    node.operation = operation
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_compare(ng, operation='GREATER_THAN', data_type='FLOAT',
                   name=None, location=(0, 0)):
    """Create compare node."""
    node = ng.nodes.new('FunctionNodeCompare')
    node.operation = operation
    node.data_type = data_type
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_mesh_boolean(ng, operation='DIFFERENCE', name=None, location=(0, 0)):
    """Create mesh boolean node.

    Operations: INTERSECT, UNION, DIFFERENCE
    """
    node = ng.nodes.new('GeometryNodeMeshBoolean')
    node.operation = operation
    if name:
        node.name = name
        node.label = name
    node.location = location
    return node


def create_frame(ng, name, location=(0, 0), width=200, height=100):
    """Create a frame node for organization."""
    frame = ng.nodes.new('NodeFrame')
    frame.name = name
    frame.label = name
    frame.location = location
    frame.width = width
    frame.height = height
    return frame


def create_reroute(ng, location=(0, 0)):
    """Create a reroute node for cleaner wiring."""
    node = ng.nodes.new('NodeReroute')
    node.location = location
    return node


# Linking helper

def link(ng, from_node, from_socket, to_node, to_socket):
    """Create a link between two node sockets.

    Args:
        ng: Node group
        from_node: Source node
        from_socket: Source socket name or index
        to_node: Destination node
        to_socket: Destination socket name or index

    Returns:
        The new link
    """
    # Handle socket by name or index
    if isinstance(from_socket, str):
        out_socket = from_node.outputs[from_socket]
    else:
        out_socket = from_node.outputs[from_socket]

    if isinstance(to_socket, str):
        in_socket = to_node.inputs[to_socket]
    else:
        in_socket = to_node.inputs[to_socket]

    return ng.links.new(out_socket, in_socket)


def set_default(node, socket, value):
    """Set default value for a node input socket.

    Args:
        node: The node
        socket: Socket name or index
        value: Value to set
    """
    if isinstance(socket, str):
        node.inputs[socket].default_value = value
    else:
        node.inputs[socket].default_value = value


def add_metadata(ng, version="1.0.0", script_path=None):
    """Add version and generator metadata to node group."""
    ng["version"] = version
    if script_path:
        ng["generator_script"] = script_path


def create_bevel(ng, name=None, location=(0, 0)):
    """Create mesh bevel node for edge beveling.

    Note: In Blender 5.0, GeometryNodeBevel was removed.
    This function now returns None and bevel should be skipped
    or handled via modifiers instead.

    Inputs:
        Mesh: Geometry to bevel
        Width: Bevel width/offset
        Segments: Number of segments (default 1)
        Angle: Maximum angle for auto-weight (radians)

    Returns:
        None (bevel node unavailable in Blender 5.0)
    """
    # GeometryNodeBevel was removed in Blender 5.0
    # Return None so calling code can skip bevel operations
    # Beveling can be applied via modifier on the final object instead
    return None
