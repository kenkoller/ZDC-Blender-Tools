# Batch Generation for Cabinet Generator
# Create multiple cabinets in sequence or from a layout

import bpy
import json
from mathutils import Vector
from typing import List, Dict, Optional


def create_cabinet_from_settings(context, settings, location: Vector = None) -> Optional[bpy.types.Object]:
    """Create a single cabinet using current settings.

    Args:
        context: Blender context
        settings: CABINET_PG_Settings property group
        location: Optional location for the cabinet

    Returns:
        Created cabinet object or None
    """
    # Import here to avoid circular imports
    from src.nodes import master

    # Generate node groups if needed
    if "CabinetMaster" not in bpy.data.node_groups:
        master.generate_all_nodegroups()

    # Create the cabinet
    nodegroup = bpy.data.node_groups["CabinetMaster"]
    obj = master.create_test_object(nodegroup)

    if location:
        obj.location = location

    # Apply settings (simplified version - full implementation in operators.py)
    return obj


class CabinetSpec:
    """Specification for a single cabinet in a batch."""

    def __init__(
        self,
        cabinet_type: str = "BASE",
        width: float = 0.6,
        height: float = 0.72,
        depth: float = 0.55,
        position: tuple = (0, 0, 0),
        **kwargs
    ):
        self.cabinet_type = cabinet_type
        self.width = width
        self.height = height
        self.depth = depth
        self.position = Vector(position)
        self.extra_settings = kwargs

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "cabinet_type": self.cabinet_type,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "position": list(self.position),
            **self.extra_settings
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CabinetSpec':
        """Create from dictionary."""
        position = data.pop("position", (0, 0, 0))
        cabinet_type = data.pop("cabinet_type", "BASE")
        width = data.pop("width", 0.6)
        height = data.pop("height", 0.72)
        depth = data.pop("depth", 0.55)
        return cls(cabinet_type, width, height, depth, position, **data)


def generate_linear_run(
    start_pos: Vector,
    cabinets: List[CabinetSpec],
    gap: float = 0.0,
    direction: Vector = Vector((1, 0, 0))
) -> List[Vector]:
    """Calculate positions for a linear run of cabinets.

    Args:
        start_pos: Starting position
        cabinets: List of cabinet specs
        gap: Gap between cabinets (default 0)
        direction: Direction of the run (default +X)

    Returns:
        List of positions for each cabinet
    """
    positions = []
    current_pos = start_pos.copy()
    direction = direction.normalized()

    for i, spec in enumerate(cabinets):
        # Center of first cabinet at start position
        if i == 0:
            positions.append(current_pos.copy())
        else:
            # Move by half of previous cabinet + gap + half of current cabinet
            prev_width = cabinets[i - 1].width
            current_width = spec.width
            offset = (prev_width / 2) + gap + (current_width / 2)
            current_pos += direction * offset
            positions.append(current_pos.copy())

    return positions


def generate_l_shaped_layout(
    corner_pos: Vector,
    left_cabinets: List[CabinetSpec],
    right_cabinets: List[CabinetSpec],
    corner_cabinet: CabinetSpec = None,
    gap: float = 0.0
) -> List[tuple]:
    """Generate positions for an L-shaped kitchen layout.

    Args:
        corner_pos: Position of the corner
        left_cabinets: Cabinets going in -X direction from corner
        right_cabinets: Cabinets going in -Y direction from corner
        corner_cabinet: Optional corner cabinet
        gap: Gap between cabinets

    Returns:
        List of (CabinetSpec, position, rotation) tuples
    """
    result = []

    # Corner cabinet (if any)
    if corner_cabinet:
        result.append((corner_cabinet, corner_pos, 0))

    # Left run (-X direction)
    if left_cabinets:
        corner_offset = corner_cabinet.width / 2 if corner_cabinet else 0
        start = corner_pos - Vector((corner_offset + gap, 0, 0))
        positions = generate_linear_run(start, left_cabinets, gap, Vector((-1, 0, 0)))
        for spec, pos in zip(left_cabinets, positions):
            result.append((spec, pos, 0))

    # Right run (-Y direction)
    if right_cabinets:
        corner_offset = corner_cabinet.depth / 2 if corner_cabinet else 0
        start = corner_pos - Vector((0, corner_offset + gap, 0))
        positions = generate_linear_run(start, right_cabinets, gap, Vector((0, -1, 0)))
        for spec, pos in zip(right_cabinets, positions):
            # Rotate 90 degrees for perpendicular run
            result.append((spec, pos, 1.5708))  # 90 degrees in radians

    return result


# ============ BLENDER OPERATORS ============

class CABINET_OT_BatchGenerate(bpy.types.Operator):
    """Generate multiple cabinets in a row"""
    bl_idname = "cabinet.batch_generate"
    bl_label = "Batch Generate"
    bl_description = "Generate multiple cabinets in a linear arrangement"
    bl_options = {'REGISTER', 'UNDO'}

    count: bpy.props.IntProperty(
        name="Count",
        description="Number of cabinets to generate",
        default=3,
        min=1,
        max=20
    )

    gap: bpy.props.FloatProperty(
        name="Gap",
        description="Gap between cabinets",
        default=0.0,
        min=0.0,
        max=0.1,
        unit='LENGTH',
        subtype='DISTANCE'
    )

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[
            ('X', "X Axis", "Arrange along X axis"),
            ('Y', "Y Axis", "Arrange along Y axis"),
            ('-X', "-X Axis", "Arrange along negative X axis"),
            ('-Y', "-Y Axis", "Arrange along negative Y axis"),
        ],
        default='X'
    )

    vary_width: bpy.props.BoolProperty(
        name="Vary Width",
        description="Vary cabinet widths",
        default=False
    )

    width_pattern: bpy.props.StringProperty(
        name="Width Pattern",
        description="Comma-separated widths in meters (e.g., '0.6,0.45,0.6')",
        default="0.6,0.45,0.6"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "count")
        layout.prop(self, "gap")
        layout.prop(self, "direction")
        layout.separator()
        layout.prop(self, "vary_width")
        if self.vary_width:
            layout.prop(self, "width_pattern")

    def execute(self, context):
        from src.nodes import master

        settings = context.scene.cabinet_settings

        # Generate node groups if needed
        if "CabinetMaster" not in bpy.data.node_groups:
            master.generate_all_nodegroups()

        # Parse direction
        dir_map = {
            'X': Vector((1, 0, 0)),
            'Y': Vector((0, 1, 0)),
            '-X': Vector((-1, 0, 0)),
            '-Y': Vector((0, -1, 0)),
        }
        direction = dir_map[self.direction]

        # Parse width pattern
        widths = []
        if self.vary_width:
            try:
                widths = [float(w.strip()) for w in self.width_pattern.split(',')]
            except ValueError:
                self.report({'WARNING'}, "Invalid width pattern, using default")
                widths = []

        # Create cabinet specs
        specs = []
        for i in range(self.count):
            width = widths[i % len(widths)] if widths else settings.width
            specs.append(CabinetSpec(
                cabinet_type=settings.cabinet_type,
                width=width,
                height=settings.height,
                depth=settings.depth
            ))

        # Calculate positions
        cursor = context.scene.cursor.location.copy()
        positions = generate_linear_run(cursor, specs, self.gap, direction)

        # Create cabinets
        created_objects = []
        for spec, pos in zip(specs, positions):
            # Create cabinet
            nodegroup = bpy.data.node_groups["CabinetMaster"]
            obj = master.create_test_object(nodegroup)
            obj.location = pos
            created_objects.append(obj)

            # Set width from spec
            mod = obj.modifiers["GeometryNodes"]
            for item in mod.node_group.interface.items_tree:
                if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                    if item.name == "Width":
                        mod[item.identifier] = spec.width
                        break

        # Select all created objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in created_objects:
            obj.select_set(True)
        if created_objects:
            context.view_layer.objects.active = created_objects[0]

        self.report({'INFO'}, f"Created {len(created_objects)} cabinets")
        return {'FINISHED'}


class CABINET_OT_BatchFromJSON(bpy.types.Operator):
    """Generate cabinets from JSON specification"""
    bl_idname = "cabinet.batch_from_json"
    bl_label = "Batch from JSON"
    bl_description = "Generate multiple cabinets from a JSON specification file"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH'
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        from src.nodes import master

        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.report({'ERROR'}, f"Failed to load JSON: {e}")
            return {'CANCELLED'}

        # Generate node groups if needed
        if "CabinetMaster" not in bpy.data.node_groups:
            master.generate_all_nodegroups()

        # Parse cabinet list
        cabinets = data.get("cabinets", [])
        if not cabinets:
            self.report({'WARNING'}, "No cabinets found in JSON")
            return {'CANCELLED'}

        created_objects = []
        for cab_data in cabinets:
            spec = CabinetSpec.from_dict(cab_data)

            # Create cabinet
            nodegroup = bpy.data.node_groups["CabinetMaster"]
            obj = master.create_test_object(nodegroup)
            obj.location = spec.position

            # Apply rotation if specified
            if "rotation" in cab_data:
                obj.rotation_euler.z = cab_data["rotation"]

            created_objects.append(obj)

        # Select all created objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in created_objects:
            obj.select_set(True)
        if created_objects:
            context.view_layer.objects.active = created_objects[0]

        self.report({'INFO'}, f"Created {len(created_objects)} cabinets from JSON")
        return {'FINISHED'}


class CABINET_OT_GenerateKitchenRun(bpy.types.Operator):
    """Generate a kitchen cabinet run"""
    bl_idname = "cabinet.generate_kitchen_run"
    bl_label = "Generate Kitchen Run"
    bl_description = "Generate a typical kitchen cabinet arrangement"
    bl_options = {'REGISTER', 'UNDO'}

    layout_type: bpy.props.EnumProperty(
        name="Layout",
        items=[
            ('STRAIGHT', "Straight Run", "Single wall of cabinets"),
            ('L_SHAPE', "L-Shaped", "Corner layout"),
            ('U_SHAPE', "U-Shaped", "Three-wall layout"),
            ('GALLEY', "Galley", "Two parallel walls"),
        ],
        default='STRAIGHT'
    )

    total_width: bpy.props.FloatProperty(
        name="Total Width",
        description="Total width of the run",
        default=3.0,
        min=1.0,
        max=6.0,
        unit='LENGTH'
    )

    include_sink: bpy.props.BoolProperty(
        name="Include Sink Cabinet",
        default=True
    )

    include_corner: bpy.props.BoolProperty(
        name="Include Corner Cabinet",
        default=True
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "layout_type")
        layout.prop(self, "total_width")
        layout.prop(self, "include_sink")
        if self.layout_type in ('L_SHAPE', 'U_SHAPE'):
            layout.prop(self, "include_corner")

    def execute(self, context):
        from src.nodes import master

        # Generate node groups if needed
        if "CabinetMaster" not in bpy.data.node_groups:
            master.generate_all_nodegroups()

        cursor = context.scene.cursor.location.copy()
        created = []

        if self.layout_type == 'STRAIGHT':
            # Simple straight run
            remaining = self.total_width
            x_pos = cursor.x

            # Start with a drawer base
            cab_width = min(0.6, remaining)
            remaining -= cab_width
            obj = self._create_cabinet(context, "DRAWER_BASE", cab_width, 0.72, 0.55)
            obj.location = Vector((x_pos + cab_width / 2, cursor.y, cursor.z))
            created.append(obj)
            x_pos += cab_width

            # Sink cabinet in the middle (if enabled)
            if self.include_sink and remaining >= 0.9:
                obj = self._create_cabinet(context, "SINK_BASE", 0.9, 0.72, 0.55)
                obj.location = Vector((x_pos + 0.45, cursor.y, cursor.z))
                created.append(obj)
                x_pos += 0.9
                remaining -= 0.9

            # Fill rest with base cabinets
            while remaining >= 0.3:
                cab_width = min(0.6, remaining)
                obj = self._create_cabinet(context, "BASE", cab_width, 0.72, 0.55)
                obj.location = Vector((x_pos + cab_width / 2, cursor.y, cursor.z))
                created.append(obj)
                x_pos += cab_width
                remaining -= cab_width

        elif self.layout_type == 'L_SHAPE':
            # L-shaped layout
            # Start with corner
            if self.include_corner:
                obj = self._create_cabinet(context, "BLIND_CORNER", 0.9, 0.72, 0.6)
                obj.location = cursor
                created.append(obj)

            # Add cabinets along X
            x_pos = cursor.x + 0.6
            for i in range(3):
                obj = self._create_cabinet(context, "BASE", 0.6, 0.72, 0.55)
                obj.location = Vector((x_pos, cursor.y, cursor.z))
                created.append(obj)
                x_pos += 0.6

            # Add cabinets along Y
            y_pos = cursor.y - 0.6
            for i in range(2):
                obj = self._create_cabinet(context, "BASE", 0.6, 0.72, 0.55)
                obj.location = Vector((cursor.x, y_pos, cursor.z))
                obj.rotation_euler.z = 1.5708  # 90 degrees
                created.append(obj)
                y_pos -= 0.6

        # Select all created
        bpy.ops.object.select_all(action='DESELECT')
        for obj in created:
            obj.select_set(True)
        if created:
            context.view_layer.objects.active = created[0]

        self.report({'INFO'}, f"Created kitchen run with {len(created)} cabinets")
        return {'FINISHED'}

    def _create_cabinet(self, context, cab_type, width, height, depth):
        """Helper to create a single cabinet."""
        from src.nodes import master

        nodegroup = bpy.data.node_groups["CabinetMaster"]
        obj = master.create_test_object(nodegroup)

        # Set basic dimensions
        mod = obj.modifiers["GeometryNodes"]
        for item in mod.node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                if item.name == "Width":
                    mod[item.identifier] = width
                elif item.name == "Height":
                    mod[item.identifier] = height
                elif item.name == "Depth":
                    mod[item.identifier] = depth

        return obj


# Registration
classes = (
    CABINET_OT_BatchGenerate,
    CABINET_OT_BatchFromJSON,
    CABINET_OT_GenerateKitchenRun,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
