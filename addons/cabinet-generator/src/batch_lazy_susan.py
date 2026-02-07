# Batch Lazy Susan Corner Cabinet Generator
# Creates multiple lazy susan cabinet configurations using Rev-A-Shelf specs
#
# Usage in Blender Python Console:
#   from src import batch_lazy_susan
#   batch_lazy_susan.generate_lazy_susan_batch()
#   # Or with specific configs:
#   batch_lazy_susan.generate_lazy_susan_batch(
#       bc_codes=['BC24', 'BC28', 'BC32'],
#       shapes=['FULL_CIRCLE', 'KIDNEY'],
#       construction='FF'
#   )

import bpy
from mathutils import Vector
from typing import List, Optional, Dict

from .revashelf_specs import (
    CABINET_SPECS,
    TRAY_SPECS,
    SHAPE_AVAILABILITY,
    SHAPE_NAMES,
    SHAPE_IDS,
    FULL_CIRCLE, KIDNEY, PIE_CUT, D_SHAPE, HALF_MOON,
    FF, FL,
    get_cabinet_dims,
    get_tray_spec,
    get_available_shapes,
    get_all_bc_codes,
)


# Map shape constants to style enum values (matching GN Style input)
SHAPE_TO_STYLE = {
    FULL_CIRCLE: 0,
    KIDNEY: 1,
    PIE_CUT: 2,
    D_SHAPE: 3,
    HALF_MOON: 4,
}

# Map shape names (strings) to constants
SHAPE_NAME_MAP = {
    'FULL_CIRCLE': FULL_CIRCLE,
    'KIDNEY': KIDNEY,
    'PIE_CUT': PIE_CUT,
    'D_SHAPE': D_SHAPE,
    'HALF_MOON': HALF_MOON,
}


def _ensure_nodegroups():
    """Ensure CabinetMaster and all child node groups exist."""
    if "CabinetMaster" not in bpy.data.node_groups:
        from .nodes import master
        master.generate_all_nodegroups()


def _set_modifier_input(mod, name, value):
    """Set a modifier input by socket name."""
    for item in mod.node_group.interface.items_tree:
        if (item.item_type == 'SOCKET'
                and item.in_out == 'INPUT'
                and item.name == name):
            mod[item.identifier] = value
            return True
    return False


def _create_cabinet_object(name="LazySusan_Cabinet"):
    """Create a new object with CabinetMaster geometry nodes modifier."""
    nodegroup = bpy.data.node_groups["CabinetMaster"]
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = nodegroup
    return obj, mod


def generate_single_cabinet(
    bc_code: str,
    shape: int,
    construction: str = FF,
    tiers: int = 2,
    position: Vector = Vector((0, 0, 0)),
) -> Optional[bpy.types.Object]:
    """Generate a single lazy susan corner cabinet from spec.

    Args:
        bc_code: Cabinet code (e.g. "BC24")
        shape: Shape constant (FULL_CIRCLE, KIDNEY, etc.)
        construction: "FF" for face frame, "FL" for frameless
        tiers: Number of lazy susan tiers (1-4)
        position: World position for the cabinet

    Returns:
        Created Blender object, or None if spec not found.
    """
    _ensure_nodegroups()

    # Look up specs
    cab_dims = get_cabinet_dims(bc_code, construction)
    if cab_dims is None:
        print(f"[BatchLS] No cabinet spec for {bc_code}")
        return None

    tray = get_tray_spec(bc_code, shape)
    if tray is None:
        print(f"[BatchLS] No tray spec for {bc_code} + {SHAPE_NAMES.get(shape, '?')}")
        return None

    # Check shape availability
    available = get_available_shapes(bc_code)
    if shape not in available:
        print(f"[BatchLS] {SHAPE_NAMES[shape]} not available for {bc_code}")
        return None

    # Build name
    shape_name = SHAPE_NAMES[shape].replace(" ", "").replace("-", "")
    con_suffix = "FF" if construction == FF else "FL"
    obj_name = f"{bc_code}_{shape_name}_{con_suffix}"

    # Create object
    obj, mod = _create_cabinet_object(obj_name)

    # Set cabinet type: BLIND_CORNER = 4
    _set_modifier_input(mod, "Cabinet Type", 4)

    # Set dimensions
    _set_modifier_input(mod, "Width", cab_dims["width"])
    _set_modifier_input(mod, "Depth", cab_dims["depth"])
    _set_modifier_input(mod, "Height", cab_dims["height"])

    # Panel thickness: 3/4" = 0.019m standard
    _set_modifier_input(mod, "Panel Thickness", 0.019)

    # Blind width: face frame width (1.5" standard)
    _set_modifier_input(mod, "Blind Width", cab_dims["face_frame_width"])

    # Face frame
    is_ff = construction == FF
    _set_modifier_input(mod, "Has Face Frame", is_ff)
    if is_ff:
        _set_modifier_input(mod, "Face Frame Width", cab_dims["face_frame_width"])

    # Lazy susan configuration
    _set_modifier_input(mod, "Has Lazy Susan", True)
    _set_modifier_input(mod, "Lazy Susan Count", tiers)
    _set_modifier_input(mod, "Lazy Susan Style", SHAPE_TO_STYLE[shape])
    _set_modifier_input(mod, "Lazy Susan Diameter", tray.diameter)

    # Standard options
    _set_modifier_input(mod, "Has Back", True)
    _set_modifier_input(mod, "Has Toe Kick", True)
    _set_modifier_input(mod, "Toe Kick Height", 0.1)  # ~4"
    _set_modifier_input(mod, "Corner Type", 0)  # Left corner

    # Position
    obj.location = position

    return obj


def generate_lazy_susan_batch(
    bc_codes: Optional[List[str]] = None,
    shapes: Optional[List[str]] = None,
    construction: str = FF,
    tiers: int = 2,
    grid_spacing: float = 1.5,
    start_position: Optional[Vector] = None,
) -> List[bpy.types.Object]:
    """Generate a grid of lazy susan cabinets across multiple sizes and shapes.

    Args:
        bc_codes: List of BC codes to generate (None = top 5 priority)
        shapes: List of shape names as strings (None = all available per code)
        construction: "FF" or "FL"
        tiers: Number of lazy susan tiers per cabinet
        grid_spacing: Distance between cabinets in grid (meters)
        start_position: Starting position (None = cursor location or origin)

    Returns:
        List of created Blender objects.
    """
    _ensure_nodegroups()

    # Defaults
    if bc_codes is None:
        bc_codes = ["BC24", "BC28", "BC32", "BC42", "BC20"]

    if shapes is not None:
        shape_filter = [SHAPE_NAME_MAP[s] for s in shapes if s in SHAPE_NAME_MAP]
    else:
        shape_filter = None

    if start_position is None:
        start_position = bpy.context.scene.cursor.location.copy()

    # Collect all shape IDs we'll use (for column headers)
    all_shapes_used = set()
    for code in bc_codes:
        available = get_available_shapes(code)
        for s in available:
            if shape_filter is None or s in shape_filter:
                all_shapes_used.add(s)
    all_shapes_sorted = sorted(all_shapes_used)

    created = []
    row = 0

    for code in bc_codes:
        available = get_available_shapes(code)
        col = 0

        for shape_id in all_shapes_sorted:
            if shape_id not in available:
                continue
            if shape_filter is not None and shape_id not in shape_filter:
                continue

            pos = Vector((
                start_position.x + col * grid_spacing,
                start_position.y - row * grid_spacing,
                start_position.z,
            ))

            obj = generate_single_cabinet(
                bc_code=code,
                shape=shape_id,
                construction=construction,
                tiers=tiers,
                position=pos,
            )

            if obj is not None:
                created.append(obj)
                col += 1

        if col > 0:
            row += 1

    # Select all created objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in created:
        obj.select_set(True)
    if created:
        bpy.context.view_layer.objects.active = created[0]

    print(f"[BatchLS] Created {len(created)} lazy susan cabinets")
    return created


def generate_all_configurations(
    construction: str = FF,
    tiers: int = 2,
    grid_spacing: float = 1.5,
) -> List[bpy.types.Object]:
    """Generate ALL available lazy susan configurations.

    Creates every valid (bc_code, shape) combination from the spec.
    Results in a grid with rows = BC codes, columns = shapes.

    Args:
        construction: "FF" or "FL"
        tiers: Number of lazy susan tiers
        grid_spacing: Distance between cabinets

    Returns:
        List of created objects.
    """
    return generate_lazy_susan_batch(
        bc_codes=get_all_bc_codes(),
        shapes=None,  # All available shapes per code
        construction=construction,
        tiers=tiers,
        grid_spacing=grid_spacing,
    )


def print_batch_summary():
    """Print a summary of what generate_all_configurations would create."""
    total = 0
    for code in get_all_bc_codes():
        available = get_available_shapes(code)
        shapes_str = ", ".join(SHAPE_NAMES[s] for s in available)
        count = len(available)
        total += count
        print(f"  {code}: {count} configs ({shapes_str})")
    print(f"\n  Total configurations: {total}")
    print(f"  x2 for FF/FL = {total * 2} total cabinets")


# ---------------------------------------------------------------------------
# Blender Operator
# ---------------------------------------------------------------------------

class CABINET_OT_BatchLazySusan(bpy.types.Operator):
    """Generate a batch of lazy susan corner cabinets from Rev-A-Shelf specs"""
    bl_idname = "cabinet.batch_lazy_susan"
    bl_label = "Batch Lazy Susan Cabinets"
    bl_description = "Generate multiple lazy susan corner cabinets using Rev-A-Shelf specifications"
    bl_options = {'REGISTER', 'UNDO'}

    construction: bpy.props.EnumProperty(
        name="Construction",
        items=[
            ('FF', "Face Frame", "Face frame construction (1-1/2\" frame)"),
            ('FL', "Frameless", "Frameless / full access construction"),
        ],
        default='FF',
    )

    tiers: bpy.props.IntProperty(
        name="Tiers",
        description="Number of lazy susan shelf tiers",
        default=2,
        min=1,
        max=4,
    )

    grid_spacing: bpy.props.FloatProperty(
        name="Grid Spacing",
        description="Distance between cabinets in the layout grid",
        default=1.5,
        min=0.5,
        max=3.0,
        unit='LENGTH',
    )

    # BC code toggles
    use_bc16: bpy.props.BoolProperty(name="BC16 (16\")", default=False)
    use_bc18: bpy.props.BoolProperty(name="BC18 (18\")", default=True)
    use_bc20: bpy.props.BoolProperty(name="BC20 (20\")", default=True)
    use_bc22: bpy.props.BoolProperty(name="BC22 (22\")", default=False)
    use_bc24: bpy.props.BoolProperty(name="BC24 (24\")", default=True)
    use_bc28: bpy.props.BoolProperty(name="BC28 (28\")", default=True)
    use_bc31: bpy.props.BoolProperty(name="BC31 (31\")", default=False)
    use_bc32: bpy.props.BoolProperty(name="BC32 (32\")", default=True)
    use_bc42: bpy.props.BoolProperty(name="BC42 (42\" Half-Moon)", default=False)
    use_bc45: bpy.props.BoolProperty(name="BC45 (45\" Half-Moon)", default=False)
    use_bc48: bpy.props.BoolProperty(name="BC48 (48\" Half-Moon)", default=False)
    use_bc24x33: bpy.props.BoolProperty(name="BC24x33 (Special)", default=False)

    # Shape toggles
    use_full_circle: bpy.props.BoolProperty(name="Full Circle", default=True)
    use_kidney: bpy.props.BoolProperty(name="Kidney", default=True)
    use_pie_cut: bpy.props.BoolProperty(name="Pie Cut", default=True)
    use_d_shape: bpy.props.BoolProperty(name="D-Shape", default=True)
    use_half_moon: bpy.props.BoolProperty(name="Half-Moon", default=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "construction", expand=True)
        layout.prop(self, "tiers")
        layout.prop(self, "grid_spacing")

        layout.separator()
        layout.label(text="Cabinet Sizes:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "use_bc16", toggle=True)
        row.prop(self, "use_bc18", toggle=True)
        row.prop(self, "use_bc20", toggle=True)
        row = col.row(align=True)
        row.prop(self, "use_bc22", toggle=True)
        row.prop(self, "use_bc24", toggle=True)
        row.prop(self, "use_bc28", toggle=True)
        row = col.row(align=True)
        row.prop(self, "use_bc31", toggle=True)
        row.prop(self, "use_bc32", toggle=True)
        row.prop(self, "use_bc24x33", toggle=True)
        row = col.row(align=True)
        row.prop(self, "use_bc42", toggle=True)
        row.prop(self, "use_bc45", toggle=True)
        row.prop(self, "use_bc48", toggle=True)

        layout.separator()
        layout.label(text="Tray Shapes:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "use_full_circle", toggle=True)
        row.prop(self, "use_kidney", toggle=True)
        row.prop(self, "use_pie_cut", toggle=True)
        row = col.row(align=True)
        row.prop(self, "use_d_shape", toggle=True)
        row.prop(self, "use_half_moon", toggle=True)

    def execute(self, context):
        # Build BC code list
        bc_map = {
            "BC16": self.use_bc16, "BC18": self.use_bc18,
            "BC20": self.use_bc20, "BC22": self.use_bc22,
            "BC24": self.use_bc24, "BC28": self.use_bc28,
            "BC31": self.use_bc31, "BC32": self.use_bc32,
            "BC42": self.use_bc42, "BC45": self.use_bc45,
            "BC48": self.use_bc48, "BC24x33": self.use_bc24x33,
        }
        bc_codes = [code for code, enabled in bc_map.items() if enabled]

        if not bc_codes:
            self.report({'WARNING'}, "No cabinet sizes selected")
            return {'CANCELLED'}

        # Build shape list
        shape_map = {
            'FULL_CIRCLE': self.use_full_circle,
            'KIDNEY': self.use_kidney,
            'PIE_CUT': self.use_pie_cut,
            'D_SHAPE': self.use_d_shape,
            'HALF_MOON': self.use_half_moon,
        }
        shapes = [name for name, enabled in shape_map.items() if enabled]

        if not shapes:
            self.report({'WARNING'}, "No tray shapes selected")
            return {'CANCELLED'}

        created = generate_lazy_susan_batch(
            bc_codes=bc_codes,
            shapes=shapes,
            construction=self.construction,
            tiers=self.tiers,
            grid_spacing=self.grid_spacing,
        )

        self.report({'INFO'}, f"Created {len(created)} lazy susan cabinets")
        return {'FINISHED'}


# Registration
classes = (
    CABINET_OT_BatchLazySusan,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
