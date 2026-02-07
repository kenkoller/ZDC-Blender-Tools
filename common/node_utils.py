"""Shared node tree manipulation helpers for ZDC addons.

This module provides common utilities for creating and managing Blender
node groups programmatically. Extracted patterns shared between
cabinet-generator and metallic-flake-shader.

Note: cabinet-generator has extensive node helpers in its own
src/nodes/utils.py — this module is for cross-addon utilities.
Addon-specific helpers should stay in their respective addons.
"""

import bpy
from typing import Optional


def get_or_create_node_group(name: str) -> bpy.types.NodeTree:
    """Get an existing node group by name, or create a new empty one.

    Args:
        name: Node group name (should use ZDC_ prefix per convention)

    Returns:
        The node group (existing or newly created).
    """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    return bpy.data.node_groups.new(name, 'GeometryNodeTree')


def ensure_group_input(
    node_group: bpy.types.NodeTree,
    name: str,
    socket_type: str,
    default: Optional[object] = None,
) -> None:
    """Ensure a node group has an input socket with the given name and type.

    Uses the Blender 5.0+ interface API (ng.interface.new_socket).

    Args:
        node_group: Target node group
        name: Socket display name
        socket_type: Socket type string (e.g. 'NodeSocketFloat')
        default: Optional default value
    """
    for item in node_group.interface.items_tree:
        if (item.item_type == 'SOCKET'
                and item.in_out == 'INPUT'
                and item.name == name):
            return  # Already exists

    socket = node_group.interface.new_socket(
        name=name,
        in_out='INPUT',
        socket_type=socket_type,
    )
    if default is not None and hasattr(socket, 'default_value'):
        socket.default_value = default


def ensure_group_output(
    node_group: bpy.types.NodeTree,
    name: str,
    socket_type: str,
) -> None:
    """Ensure a node group has an output socket with the given name and type.

    Args:
        node_group: Target node group
        name: Socket display name
        socket_type: Socket type string
    """
    for item in node_group.interface.items_tree:
        if (item.item_type == 'SOCKET'
                and item.in_out == 'OUTPUT'
                and item.name == name):
            return

    node_group.interface.new_socket(
        name=name,
        in_out='OUTPUT',
        socket_type=socket_type,
    )
