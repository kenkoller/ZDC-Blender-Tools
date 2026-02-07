# Operators for Cabinet Generator addon

import bpy
from bpy.types import Operator


def set_modifier_input(mod, name, value):
    """Set a modifier input by socket name."""
    ng = mod.node_group
    if ng is None:
        print(f"[Cabinet Generator] Modifier has no node group, cannot set '{name}'")
        return False
    for item in ng.interface.items_tree:
        if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
            if item.name == name:
                mod[item.identifier] = value
                return True
    print(f"[Cabinet Generator] Socket '{name}' not found in '{ng.name}'")
    return False


def get_modifier(obj, report_func=None):
    """Safely get the GeometryNodes modifier from an object.

    Args:
        obj: The Blender object
        report_func: Optional operator self.report function for user feedback

    Returns:
        The modifier, or None if not found
    """
    if obj is None:
        if report_func:
            report_func({'ERROR'}, "Failed to create object")
        return None
    mod = obj.modifiers.get("GeometryNodes")
    if mod is None:
        if report_func:
            report_func({'ERROR'}, f"Object '{obj.name}' has no GeometryNodes modifier")
    return mod


class CABINET_OT_CreateCabinet(Operator):
    """Create a complete cabinet"""
    bl_idname = "cabinet.create_cabinet"
    bl_label = "Create Cabinet"
    bl_description = "Create a complete parametric cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes import master

        # Only generate node groups if CabinetMaster doesn't exist
        if "CabinetMaster" not in bpy.data.node_groups:
            try:
                master.generate_all_nodegroups()
            except Exception as e:
                self.report({'ERROR'}, f"Failed to generate node groups: {e}")
                return {'CANCELLED'}

        # Create cabinet object using existing node group
        nodegroup = bpy.data.node_groups.get("CabinetMaster")
        if nodegroup is None:
            self.report({'ERROR'}, "CabinetMaster node group not found after generation")
            return {'CANCELLED'}
        obj = master.create_test_object(nodegroup)

        # Apply settings from panel
        settings = context.scene.cabinet_settings
        mod = get_modifier(obj, self.report)
        if mod is None:
            return {'CANCELLED'}

        # Map enum values to integers
        front_type_map = {'DOORS': 0, 'DRAWERS': 1}
        door_style_map = {'FLAT': 0, 'SHAKER': 1, 'RAISED': 2, 'RECESSED': 3, 'DOUBLE_SHAKER': 4}
        handle_style_map = {'BAR': 0, 'WIRE': 1, 'KNOB': 2, 'CUP': 3, 'EDGE': 4}
        cabinet_type_map = {
            'BASE': 0, 'WALL': 1, 'TALL': 2, 'DRAWER_BASE': 3, 'BLIND_CORNER': 4,
            'SINK_BASE': 5, 'APPLIANCE': 6, 'OPEN_SHELVING': 7, 'DIAGONAL_CORNER': 8, 'PULLOUT_PANTRY': 9
        }
        hinge_style_map = {'EUROPEAN': 0, 'BARREL': 1, 'PIANO': 2}
        drawer_slide_map = {'SIDE_MOUNT': 0, 'UNDERMOUNT': 1, 'CENTER_MOUNT': 2}
        appliance_type_map = {'MICROWAVE': 0, 'WALL_OVEN': 1, 'BUILT_IN_FRIDGE': 2}
        corner_type_map = {'LEFT': 0, 'RIGHT': 1}

        # Set all parameters
        set_modifier_input(mod, "Cabinet Type", cabinet_type_map.get(settings.cabinet_type, 0))
        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Front Type", front_type_map.get(settings.front_type, 0))
        set_modifier_input(mod, "Door Style", door_style_map.get(settings.door_style, 1))
        set_modifier_input(mod, "Double Doors", settings.double_doors)
        set_modifier_input(mod, "Drawer Count", settings.drawer_count)
        set_modifier_input(mod, "Handle Style", handle_style_map.get(settings.handle_style, 0))
        set_modifier_input(mod, "Shelf Count", settings.shelf_count if settings.has_shelves else 0)
        set_modifier_input(mod, "Has Back", settings.has_back)

        # Glass door options
        set_modifier_input(mod, "Glass Insert", settings.glass_insert)
        set_modifier_input(mod, "Glass Frame Width", settings.glass_frame_width)

        # Bevel options
        set_modifier_input(mod, "Bevel Width", settings.bevel_width)
        set_modifier_input(mod, "Bevel Segments", settings.bevel_segments)

        # Animation options
        set_modifier_input(mod, "Door Open Angle", settings.door_open_angle)
        set_modifier_input(mod, "Drawer Open", settings.drawer_open)

        # Toe kick options
        set_modifier_input(mod, "Has Toe Kick", settings.has_toe_kick)
        set_modifier_input(mod, "Toe Kick Height", settings.toe_kick_height)
        set_modifier_input(mod, "Toe Kick Depth", settings.toe_kick_depth)

        # Lazy susan options
        lazy_susan_style_map = {
            'FULL_CIRCLE': 0, 'KIDNEY': 1, 'PIE_CUT': 2, 'D_SHAPE': 3, 'HALF_MOON': 4
        }
        set_modifier_input(mod, "Has Lazy Susan", settings.has_lazy_susan)
        set_modifier_input(mod, "Lazy Susan Count", settings.lazy_susan_count)
        set_modifier_input(mod, "Lazy Susan Style", lazy_susan_style_map.get(settings.lazy_susan_style, 0))
        set_modifier_input(mod, "Lazy Susan Diameter", settings.lazy_susan_diameter)

        # Corner cabinet options
        set_modifier_input(mod, "Corner Type", corner_type_map.get(settings.corner_type, 0))
        set_modifier_input(mod, "Blind Width", settings.blind_width)

        # Hardware options
        set_modifier_input(mod, "Hinge Style", hinge_style_map.get(settings.hinge_style, 0))
        set_modifier_input(mod, "Drawer Slide Style", drawer_slide_map.get(settings.drawer_slide_style, 0))

        # Face frame options
        set_modifier_input(mod, "Has Face Frame", settings.has_face_frame)
        set_modifier_input(mod, "Face Frame Width", settings.face_frame_width)

        # Appliance options
        set_modifier_input(mod, "Appliance Type", appliance_type_map.get(settings.appliance_type, 0))
        set_modifier_input(mod, "Appliance Opening Height", settings.appliance_opening_height)
        set_modifier_input(mod, "Has Trim Frame", settings.has_trim_frame)

        # Sink base options
        set_modifier_input(mod, "Has Plumbing Cutout", settings.has_plumbing_cutout)

        # Open shelving options
        set_modifier_input(mod, "Has Side Panels", settings.has_side_panels)

        # Pull-out options
        set_modifier_input(mod, "Pullout Extension", settings.pullout_extension)

        # Insert options
        set_modifier_input(mod, "Has Trash Pullout", settings.has_trash_pullout)
        set_modifier_input(mod, "Double Trash Bins", settings.double_trash_bins)
        set_modifier_input(mod, "Has Spice Rack", settings.has_spice_rack)
        set_modifier_input(mod, "Spice Rack Tiers", settings.spice_rack_tiers)

        # Shelf pin options
        set_modifier_input(mod, "Has Adjustable Shelves", settings.has_adjustable_shelves)
        set_modifier_input(mod, "Shelf Pin Rows", settings.shelf_pin_rows)

        # Select the new object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created cabinet: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_GenerateNodeGroups(Operator):
    """Generate all cabinet node groups"""
    bl_idname = "cabinet.generate_nodegroups"
    bl_label = "Generate All Node Groups"
    bl_description = "Generate all cabinet geometry node groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes import master

        master.generate_all_nodegroups()

        self.report({'INFO'}, "Generated all node groups")
        return {'FINISHED'}


class CABINET_OT_CreateShelf(Operator):
    """Create a shelf object with the Shelf node group"""
    bl_idname = "cabinet.create_shelf"
    bl_label = "Create Shelf"
    bl_description = "Create a new shelf object using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import shelf

        obj = shelf.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Thickness", settings.shelf_thickness)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created shelf: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateDoorPanel(Operator):
    """Create a door panel object"""
    bl_idname = "cabinet.create_door_panel"
    bl_label = "Create Door Panel"
    bl_description = "Create a new door panel using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import door_panel

        obj = door_panel.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        door_style_map = {'FLAT': 0, 'SHAKER': 1, 'RAISED': 2, 'RECESSED': 3, 'DOUBLE_SHAKER': 4}

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Style", door_style_map.get(settings.door_style, 1))

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created door panel: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateDrawer(Operator):
    """Create a drawer object"""
    bl_idname = "cabinet.create_drawer"
    bl_label = "Create Drawer"
    bl_description = "Create a new drawer using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import drawer

        obj = drawer.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height * 0.2)
        set_modifier_input(mod, "Depth", settings.depth)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created drawer: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateHandle(Operator):
    """Create a handle object"""
    bl_idname = "cabinet.create_handle"
    bl_label = "Create Handle"
    bl_description = "Create a new handle using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import hardware

        obj = hardware.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        handle_style_map = {'BAR': 0, 'WIRE': 1, 'KNOB': 2, 'CUP': 3, 'EDGE': 4}
        set_modifier_input(mod, "Style", handle_style_map.get(settings.handle_style, 0))

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created handle: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateCabinetBox(Operator):
    """Create a cabinet box (carcass only)"""
    bl_idname = "cabinet.create_cabinet_box"
    bl_label = "Create Cabinet Box"
    bl_description = "Create a cabinet carcass without doors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.systems import cabinet_box

        obj = cabinet_box.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Has Back", settings.has_back)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created cabinet box: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateToeKick(Operator):
    """Create a toe kick object"""
    bl_idname = "cabinet.create_toe_kick"
    bl_label = "Create Toe Kick"
    bl_description = "Create a toe kick base using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import toe_kick

        obj = toe_kick.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.toe_kick_height)
        set_modifier_input(mod, "Depth", settings.toe_kick_depth)
        set_modifier_input(mod, "Cabinet Depth", settings.depth)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created toe kick: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateLazySusan(Operator):
    """Create a lazy susan object"""
    bl_idname = "cabinet.create_lazy_susan"
    bl_label = "Create Lazy Susan"
    bl_description = "Create a rotating lazy susan shelf using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import lazy_susan

        obj = lazy_susan.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        diameter = min(settings.width, settings.depth) * 0.85
        set_modifier_input(mod, "Diameter", diameter)
        set_modifier_input(mod, "Rotation", settings.lazy_susan_rotation)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created lazy susan: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateBlindCorner(Operator):
    """Create a blind corner cabinet"""
    bl_idname = "cabinet.create_blind_corner"
    bl_label = "Create Blind Corner"
    bl_description = "Create a blind corner cabinet with lazy susan using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.systems import blind_corner

        obj = blind_corner.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        corner_type_map = {'LEFT': 0, 'RIGHT': 1}

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Blind Width", settings.blind_width)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Has Lazy Susan", settings.has_lazy_susan)
        set_modifier_input(mod, "Lazy Susan Count", settings.lazy_susan_count)
        set_modifier_input(mod, "Corner Type", corner_type_map.get(settings.corner_type, 0))
        set_modifier_input(mod, "Has Back", settings.has_back)
        set_modifier_input(mod, "Has Toe Kick", settings.has_toe_kick)
        set_modifier_input(mod, "Toe Kick Height", settings.toe_kick_height)
        set_modifier_input(mod, "Toe Kick Depth", settings.toe_kick_depth)
        set_modifier_input(mod, "Bevel Width", settings.bevel_width)
        set_modifier_input(mod, "Bevel Segments", settings.bevel_segments)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created blind corner cabinet: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateHinges(Operator):
    """Create hinge hardware"""
    bl_idname = "cabinet.create_hinges"
    bl_label = "Create Hinges"
    bl_description = "Create hinge hardware using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import hinges

        obj = hinges.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        hinge_style_map = {'EUROPEAN': 0, 'BARREL': 1, 'PIANO': 2}
        set_modifier_input(mod, "Style", hinge_style_map.get(settings.hinge_style, 0))
        set_modifier_input(mod, "Door Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Height", settings.height)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created hinges: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateDrawerSlides(Operator):
    """Create drawer slide hardware"""
    bl_idname = "cabinet.create_drawer_slides"
    bl_label = "Create Drawer Slides"
    bl_description = "Create drawer slides using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import drawer_slides

        obj = drawer_slides.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        slide_style_map = {'SIDE_MOUNT': 0, 'UNDERMOUNT': 1, 'CENTER_MOUNT': 2}
        set_modifier_input(mod, "Style", slide_style_map.get(settings.drawer_slide_style, 0))
        set_modifier_input(mod, "Length", settings.depth - 0.05)
        set_modifier_input(mod, "Width", settings.width - settings.panel_thickness * 2)
        set_modifier_input(mod, "Extension", settings.pullout_extension)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created drawer slides: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateShelfPins(Operator):
    """Create shelf pin holes"""
    bl_idname = "cabinet.create_shelf_pins"
    bl_label = "Create Shelf Pins"
    bl_description = "Create adjustable shelf pin holes using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import shelf_pins

        obj = shelf_pins.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Row Count", settings.shelf_pin_rows)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created shelf pins: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateTrashPullout(Operator):
    """Create trash pull-out insert"""
    bl_idname = "cabinet.create_trash_pullout"
    bl_label = "Create Trash Pull-out"
    bl_description = "Create pull-out trash bin insert using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import trash_pullout

        obj = trash_pullout.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width - settings.panel_thickness * 2 - 0.02)
        set_modifier_input(mod, "Depth", settings.depth - 0.05)
        set_modifier_input(mod, "Height", settings.height * 0.6)
        set_modifier_input(mod, "Double Bins", settings.double_trash_bins)
        set_modifier_input(mod, "Extension", settings.pullout_extension)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created trash pull-out: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateSpiceRack(Operator):
    """Create spice rack insert"""
    bl_idname = "cabinet.create_spice_rack"
    bl_label = "Create Spice Rack"
    bl_description = "Create pull-out spice rack using geometry nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.atomic import spice_rack

        obj = spice_rack.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", 0.1)
        set_modifier_input(mod, "Depth", settings.depth - 0.05)
        set_modifier_input(mod, "Height", settings.height * 0.8)
        set_modifier_input(mod, "Tier Count", settings.spice_rack_tiers)
        set_modifier_input(mod, "Extension", settings.pullout_extension)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created spice rack: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateSinkBase(Operator):
    """Create sink base cabinet"""
    bl_idname = "cabinet.create_sink_base"
    bl_label = "Create Sink Base"
    bl_description = "Create sink base cabinet with open interior"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.systems import sink_base

        obj = sink_base.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Has Plumbing Cutout", settings.has_plumbing_cutout)
        set_modifier_input(mod, "Has Toe Kick", settings.has_toe_kick)
        set_modifier_input(mod, "Toe Kick Height", settings.toe_kick_height)
        set_modifier_input(mod, "Toe Kick Depth", settings.toe_kick_depth)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created sink base: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateApplianceCabinet(Operator):
    """Create appliance cabinet"""
    bl_idname = "cabinet.create_appliance_cabinet"
    bl_label = "Create Appliance Cabinet"
    bl_description = "Create cabinet with appliance opening"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.systems import appliance_cabinet

        obj = appliance_cabinet.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        appliance_type_map = {'MICROWAVE': 0, 'WALL_OVEN': 1, 'BUILT_IN_FRIDGE': 2}

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Appliance Type", appliance_type_map.get(settings.appliance_type, 0))
        set_modifier_input(mod, "Opening Height", settings.appliance_opening_height)
        set_modifier_input(mod, "Has Trim Frame", settings.has_trim_frame)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created appliance cabinet: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateOpenShelving(Operator):
    """Create open shelving unit"""
    bl_idname = "cabinet.create_open_shelving"
    bl_label = "Create Open Shelving"
    bl_description = "Create open shelf unit without doors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.systems import open_shelving

        obj = open_shelving.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Shelf Count", settings.shelf_count)
        set_modifier_input(mod, "Has Side Panels", settings.has_side_panels)
        set_modifier_input(mod, "Has Back", settings.has_back)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created open shelving: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreateDiagonalCorner(Operator):
    """Create diagonal corner cabinet"""
    bl_idname = "cabinet.create_diagonal_corner"
    bl_label = "Create Diagonal Corner"
    bl_description = "Create 45-degree angled corner cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.systems import diagonal_corner

        obj = diagonal_corner.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Has Lazy Susan", settings.has_lazy_susan)
        set_modifier_input(mod, "Lazy Susan Count", settings.lazy_susan_count)
        set_modifier_input(mod, "Has Back", settings.has_back)
        set_modifier_input(mod, "Has Toe Kick", settings.has_toe_kick)
        set_modifier_input(mod, "Toe Kick Height", settings.toe_kick_height)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created diagonal corner: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_CreatePulloutPantry(Operator):
    """Create pull-out pantry"""
    bl_idname = "cabinet.create_pullout_pantry"
    bl_label = "Create Pull-out Pantry"
    bl_description = "Create narrow cabinet with pull-out rack"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes.systems import pullout_pantry

        obj = pullout_pantry.create_test_object()
        settings = context.scene.cabinet_settings
        mod = obj.modifiers["GeometryNodes"]

        set_modifier_input(mod, "Width", settings.width)
        set_modifier_input(mod, "Height", settings.height)
        set_modifier_input(mod, "Depth", settings.depth)
        set_modifier_input(mod, "Panel Thickness", settings.panel_thickness)
        set_modifier_input(mod, "Shelf Count", settings.shelf_count)
        set_modifier_input(mod, "Extension", settings.pullout_extension)
        set_modifier_input(mod, "Has Toe Kick", settings.has_toe_kick)
        set_modifier_input(mod, "Toe Kick Height", settings.toe_kick_height)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        self.report({'INFO'}, f"Created pull-out pantry: {obj.name}")
        return {'FINISHED'}


class CABINET_OT_ApplyMaterialPresets(Operator):
    """Apply material presets to selected cabinet"""
    bl_idname = "cabinet.apply_material_presets"
    bl_label = "Apply Materials"
    bl_description = "Apply material presets to the selected cabinet object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from src.nodes import material_presets

        settings = context.scene.cabinet_settings
        obj = context.active_object

        if not obj or 'GeometryNodes' not in obj.modifiers:
            self.report({'WARNING'}, "No cabinet selected")
            return {'CANCELLED'}

        mod = obj.modifiers['GeometryNodes']
        materials_applied = []

        # Apply carcass material
        if settings.carcass_preset != 'NONE':
            if settings.carcass_preset in ('WHITE', 'GRAY', 'BLACK', 'CREAM', 'NAVY', 'SAGE'):
                mat = material_presets.create_preset_material('LAMINATE', settings.carcass_preset)
            else:
                mat = material_presets.create_preset_material('WOOD', settings.carcass_preset)
            if mat:
                set_modifier_input(mod, "Carcass Material", mat)
                materials_applied.append(f"Carcass: {mat.name}")

        # Apply front material
        if settings.front_preset != 'NONE':
            if settings.front_preset in ('WHITE', 'GRAY', 'NAVY', 'SAGE'):
                mat = material_presets.create_preset_material('LAMINATE', settings.front_preset)
            else:
                mat = material_presets.create_preset_material('WOOD', settings.front_preset)
            if mat:
                set_modifier_input(mod, "Front Material", mat)
                materials_applied.append(f"Front: {mat.name}")

        # Apply handle material
        if settings.handle_preset != 'NONE':
            mat = material_presets.create_preset_material('METAL', settings.handle_preset)
            if mat:
                set_modifier_input(mod, "Handle Material", mat)
                materials_applied.append(f"Handle: {mat.name}")

        if materials_applied:
            self.report({'INFO'}, f"Applied: {', '.join(materials_applied)}")
        else:
            self.report({'INFO'}, "No material presets selected")

        return {'FINISHED'}


class CABINET_OT_RunAllTests(Operator):
    """Run all component tests"""
    bl_idname = "cabinet.run_all_tests"
    bl_label = "Run All Tests"
    bl_description = "Run validation tests on all node group generators"
    bl_options = {'REGISTER'}

    def execute(self, context):
        import importlib
        import traceback
        import json
        import os
        from datetime import datetime

        test_results = context.scene.cabinet_test_results
        test_results.results.clear()
        test_results.is_running = True

        passed = 0
        failed = 0
        log_entries = []  # For saving to file

        # Define all tests
        atomic_tests = [
            ("Shelf", "src.nodes.atomic.shelf", "create_shelf_nodegroup"),
            ("DoorPanel", "src.nodes.atomic.door_panel", "create_door_panel_nodegroup"),
            ("Drawer", "src.nodes.atomic.drawer", "create_drawer_nodegroup"),
            ("Handle", "src.nodes.atomic.hardware", "create_handle_nodegroup"),
            ("ToeKick", "src.nodes.atomic.toe_kick", "create_toe_kick_nodegroup"),
            ("LazySusan", "src.nodes.atomic.lazy_susan", "create_lazy_susan_nodegroup"),
            ("Hinge", "src.nodes.atomic.hinges", "create_hinge_nodegroup"),
            ("DrawerSlides", "src.nodes.atomic.drawer_slides", "create_drawer_slides_nodegroup"),
            ("TrashPullout", "src.nodes.atomic.trash_pullout", "create_trash_pullout_nodegroup"),
            ("SpiceRack", "src.nodes.atomic.spice_rack", "create_spice_rack_nodegroup"),
            ("ShelfPins", "src.nodes.atomic.shelf_pins", "create_shelf_pins_nodegroup"),
            ("LEDStrip", "src.nodes.atomic.led_strip", "create_led_strip_nodegroup"),
            ("CrownMolding", "src.nodes.atomic.crown_molding", "create_crown_molding_nodegroup"),
            ("LightRail", "src.nodes.atomic.light_rail", "create_light_rail_nodegroup"),
        ]

        system_tests = [
            ("CabinetBox", "src.nodes.systems.cabinet_box", "create_cabinet_box_nodegroup"),
            ("ShelfArray", "src.nodes.systems.shelf_array", "create_shelf_array_nodegroup"),
            ("DoorAssembly", "src.nodes.systems.door_assembly", "create_door_assembly_nodegroup"),
            ("DrawerStack", "src.nodes.systems.drawer_stack", "create_drawer_stack_nodegroup"),
            ("BlindCorner", "src.nodes.systems.blind_corner", "create_blind_corner_nodegroup"),
            ("SinkBase", "src.nodes.systems.sink_base", "create_sink_base_nodegroup"),
            ("ApplianceCabinet", "src.nodes.systems.appliance_cabinet", "create_appliance_cabinet_nodegroup"),
            ("OpenShelving", "src.nodes.systems.open_shelving", "create_open_shelving_nodegroup"),
            ("DiagonalCorner", "src.nodes.systems.diagonal_corner", "create_diagonal_corner_nodegroup"),
            ("PulloutPantry", "src.nodes.systems.pullout_pantry", "create_pullout_pantry_nodegroup"),
        ]

        master_tests = [
            ("CabinetMaster", "src.nodes.master", "create_cabinet_master_nodegroup"),
        ]

        # Helper to run a test and log results
        def run_test(name, mod_path, func_name, category):
            nonlocal passed, failed
            result = test_results.results.add()
            result.name = name
            result.category = category

            log_entry = {
                "name": name,
                "category": category,
                "module": mod_path,
                "function": func_name,
            }

            try:
                mod = importlib.import_module(mod_path)
                importlib.reload(mod)
                ng = getattr(mod, func_name)()
                result.passed = True
                result.message = f"{len(ng.nodes)} nodes"
                passed += 1
                log_entry["status"] = "PASS"
                log_entry["message"] = f"{len(ng.nodes)} nodes"
            except Exception as e:
                result.passed = False
                result.message = str(e)[:100]
                failed += 1
                log_entry["status"] = "FAIL"
                log_entry["error"] = str(e)
                log_entry["traceback"] = traceback.format_exc()
                # Also print to console for immediate visibility
                print(f"\n[FAIL] {name}:")
                print(traceback.format_exc())

            log_entries.append(log_entry)

        # Run atomic tests
        for name, mod_path, func_name in atomic_tests:
            run_test(name, mod_path, func_name, "atomic")

        # Run system tests
        for name, mod_path, func_name in system_tests:
            run_test(name, mod_path, func_name, "system")

        # Run master test
        for name, mod_path, func_name in master_tests:
            run_test(name, mod_path, func_name, "master")

        # Update summary
        test_results.total_tests = passed + failed
        test_results.passed_tests = passed
        test_results.failed_tests = failed
        test_results.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_results.is_running = False

        # Save log to file
        log_file = os.path.join(
            '/Users/KK/My Drive/Assets-Cloud/Blender/Scripts/Development/blender-addons/cabinet-generator',
            'test_log.json'
        )
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": passed + failed,
                "passed": passed,
                "failed": failed,
            },
            "tests": log_entries
        }
        try:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"\nTest log saved to: {log_file}")
        except Exception as e:
            print(f"Warning: Could not save log file: {e}")

        if failed == 0:
            self.report({'INFO'}, f"All {passed} tests passed!")
        else:
            self.report({'WARNING'}, f"{passed} passed, {failed} failed")

        return {'FINISHED'}


class CABINET_OT_RunAtomicTests(Operator):
    """Run atomic component tests only"""
    bl_idname = "cabinet.run_atomic_tests"
    bl_label = "Test Atomics"
    bl_description = "Run tests on atomic component generators only"
    bl_options = {'REGISTER'}

    def execute(self, context):
        import importlib

        atomic_tests = [
            ("Shelf", "src.nodes.atomic.shelf", "create_shelf_nodegroup"),
            ("DoorPanel", "src.nodes.atomic.door_panel", "create_door_panel_nodegroup"),
            ("Drawer", "src.nodes.atomic.drawer", "create_drawer_nodegroup"),
            ("Handle", "src.nodes.atomic.hardware", "create_handle_nodegroup"),
            ("ToeKick", "src.nodes.atomic.toe_kick", "create_toe_kick_nodegroup"),
            ("LazySusan", "src.nodes.atomic.lazy_susan", "create_lazy_susan_nodegroup"),
            ("Hinge", "src.nodes.atomic.hinges", "create_hinge_nodegroup"),
            ("DrawerSlides", "src.nodes.atomic.drawer_slides", "create_drawer_slides_nodegroup"),
            ("TrashPullout", "src.nodes.atomic.trash_pullout", "create_trash_pullout_nodegroup"),
            ("SpiceRack", "src.nodes.atomic.spice_rack", "create_spice_rack_nodegroup"),
            ("ShelfPins", "src.nodes.atomic.shelf_pins", "create_shelf_pins_nodegroup"),
            ("LEDStrip", "src.nodes.atomic.led_strip", "create_led_strip_nodegroup"),
            ("CrownMolding", "src.nodes.atomic.crown_molding", "create_crown_molding_nodegroup"),
            ("LightRail", "src.nodes.atomic.light_rail", "create_light_rail_nodegroup"),
        ]

        passed, failed = 0, 0
        for name, mod_path, func_name in atomic_tests:
            try:
                mod = importlib.import_module(mod_path)
                importlib.reload(mod)
                getattr(mod, func_name)()
                passed += 1
            except Exception:
                failed += 1

        if failed == 0:
            self.report({'INFO'}, f"All {passed} atomic tests passed!")
        else:
            self.report({'WARNING'}, f"Atomics: {passed} passed, {failed} failed")

        return {'FINISHED'}


class CABINET_OT_RunSystemTests(Operator):
    """Run system component tests only"""
    bl_idname = "cabinet.run_system_tests"
    bl_label = "Test Systems"
    bl_description = "Run tests on system component generators only"
    bl_options = {'REGISTER'}

    def execute(self, context):
        import importlib

        system_tests = [
            ("CabinetBox", "src.nodes.systems.cabinet_box", "create_cabinet_box_nodegroup"),
            ("ShelfArray", "src.nodes.systems.shelf_array", "create_shelf_array_nodegroup"),
            ("DoorAssembly", "src.nodes.systems.door_assembly", "create_door_assembly_nodegroup"),
            ("DrawerStack", "src.nodes.systems.drawer_stack", "create_drawer_stack_nodegroup"),
            ("BlindCorner", "src.nodes.systems.blind_corner", "create_blind_corner_nodegroup"),
            ("SinkBase", "src.nodes.systems.sink_base", "create_sink_base_nodegroup"),
            ("ApplianceCabinet", "src.nodes.systems.appliance_cabinet", "create_appliance_cabinet_nodegroup"),
            ("OpenShelving", "src.nodes.systems.open_shelving", "create_open_shelving_nodegroup"),
            ("DiagonalCorner", "src.nodes.systems.diagonal_corner", "create_diagonal_corner_nodegroup"),
            ("PulloutPantry", "src.nodes.systems.pullout_pantry", "create_pullout_pantry_nodegroup"),
        ]

        passed, failed = 0, 0
        for name, mod_path, func_name in system_tests:
            try:
                mod = importlib.import_module(mod_path)
                importlib.reload(mod)
                getattr(mod, func_name)()
                passed += 1
            except Exception:
                failed += 1

        if failed == 0:
            self.report({'INFO'}, f"All {passed} system tests passed!")
        else:
            self.report({'WARNING'}, f"Systems: {passed} passed, {failed} failed")

        return {'FINISHED'}


class CABINET_OT_ClearNodeGroups(Operator):
    """Clear all cabinet node groups"""
    bl_idname = "cabinet.clear_nodegroups"
    bl_label = "Clear Node Groups"
    bl_description = "Remove all geometry node groups from the file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        count = 0
        for ng in list(bpy.data.node_groups):
            if ng.type == 'GEOMETRY':
                bpy.data.node_groups.remove(ng)
                count += 1

        self.report({'INFO'}, f"Removed {count} node groups")
        return {'FINISHED'}


def create_debug_materials():
    """Create debug materials with distinct colors for cabinet components."""
    debug_mats = {}

    # Color scheme for different cabinet parts
    colors = {
        'Carcass': (0.6, 0.6, 0.6, 1.0),      # Gray - cabinet box
        'Front': (0.2, 0.5, 0.8, 1.0),         # Blue - doors/drawer fronts
        'Handle': (0.9, 0.7, 0.1, 1.0),        # Gold - handles
        'Hardware': (0.3, 0.3, 0.3, 1.0),      # Dark gray - hinges/slides
        'Glass': (0.7, 0.85, 0.9, 0.3),        # Light blue transparent
        'LED': (1.0, 1.0, 0.5, 1.0),           # Yellow - LED strips
        'Crown': (0.8, 0.2, 0.2, 1.0),         # Red - crown molding
        'Rail': (0.2, 0.8, 0.2, 1.0),          # Green - light rail
        'Shelf': (0.7, 0.5, 0.3, 1.0),         # Brown - shelves
    }

    for name, color in colors.items():
        mat_name = f"Debug_{name}"
        if mat_name in bpy.data.materials:
            debug_mats[name] = bpy.data.materials[mat_name]
        else:
            mat = bpy.data.materials.new(mat_name)
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = color
                if name == 'Glass':
                    bsdf.inputs["Alpha"].default_value = 0.3
                    mat.blend_method = 'BLEND'
            debug_mats[name] = mat

    return debug_mats


class CABINET_OT_CreateTestScene(Operator):
    """Create a test scene with all cabinet types"""
    bl_idname = "cabinet.create_test_scene"
    bl_label = "Create Test Scene"
    bl_description = "Create a scene with all 10 cabinet types for visual inspection"
    bl_options = {'REGISTER', 'UNDO'}

    use_debug_colors: bpy.props.BoolProperty(
        name="Debug Colors",
        description="Apply distinct colors to different cabinet parts for debugging",
        default=True
    )

    def execute(self, context):
        from src.nodes import master
        import importlib

        # Ensure all node groups exist
        importlib.reload(master)
        try:
            master.generate_all_nodegroups()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate node groups: {e}")
            return {'CANCELLED'}

        ng = bpy.data.node_groups.get("CabinetMaster")
        if not ng:
            self.report({'ERROR'}, "CabinetMaster node group not found")
            return {'CANCELLED'}

        # Create debug materials
        debug_mats = create_debug_materials()

        cabinet_types = [
            (0, "Base", 0.6, 0.72, 0.55),
            (1, "Wall", 0.6, 0.72, 0.3),
            (2, "Tall", 0.6, 2.1, 0.55),
            (3, "DrawerBase", 0.6, 0.72, 0.55),
            (4, "BlindCorner", 0.9, 0.72, 0.55),
            (5, "SinkBase", 0.9, 0.72, 0.55),
            (6, "Appliance", 0.6, 0.72, 0.55),
            (7, "OpenShelving", 0.6, 0.72, 0.3),
            (8, "DiagonalCorner", 0.6, 0.72, 0.55),
            (9, "PulloutPantry", 0.3, 2.1, 0.55),
        ]

        # Build socket identifier lookup
        socket_ids = {}
        for item in ng.interface.items_tree:
            if hasattr(item, 'name') and hasattr(item, 'identifier'):
                socket_ids[item.name] = item.identifier

        # Create root collection for test scene
        root_col_name = "CabinetTestScene"
        if root_col_name in bpy.data.collections:
            # Remove existing test scene collection and all its children
            old_col = bpy.data.collections[root_col_name]
            self._remove_collection_recursive(old_col)
        root_col = bpy.data.collections.new(root_col_name)
        context.scene.collection.children.link(root_col)

        # Create legend collection
        legend_col = bpy.data.collections.new("Legend")
        root_col.children.link(legend_col)

        created = 0
        x_pos = 0.0
        for i, (type_id, name, width, height, depth) in enumerate(cabinet_types):
            try:
                # Create collection for this cabinet type
                cab_col = bpy.data.collections.new(f"{type_id}_{name}")
                root_col.children.link(cab_col)

                mesh = bpy.data.meshes.new(f"TestCabinet_{name}")
                obj = bpy.data.objects.new(f"TestCabinet_{name}", mesh)
                cab_col.objects.link(obj)

                mod = obj.modifiers.new("GeometryNodes", 'NODES')
                mod.node_group = ng

                # Set cabinet type and dimensions
                if "Cabinet Type" in socket_ids:
                    mod[socket_ids["Cabinet Type"]] = type_id
                if "Width" in socket_ids:
                    mod[socket_ids["Width"]] = width
                if "Height" in socket_ids:
                    mod[socket_ids["Height"]] = height
                if "Depth" in socket_ids:
                    mod[socket_ids["Depth"]] = depth

                # Apply debug materials if enabled
                if self.use_debug_colors:
                    if "Carcass Material" in socket_ids:
                        mod[socket_ids["Carcass Material"]] = debug_mats['Carcass']
                    if "Front Material" in socket_ids:
                        mod[socket_ids["Front Material"]] = debug_mats['Front']
                    if "Handle Material" in socket_ids:
                        mod[socket_ids["Handle Material"]] = debug_mats['Handle']
                    if "Hardware Material" in socket_ids:
                        mod[socket_ids["Hardware Material"]] = debug_mats['Hardware']
                    if "Glass Material" in socket_ids:
                        mod[socket_ids["Glass Material"]] = debug_mats['Glass']
                    if "LED Material" in socket_ids:
                        mod[socket_ids["LED Material"]] = debug_mats['LED']

                # Position with proper spacing
                obj.location = (x_pos, 0, 0)

                # Add text label above cabinet
                label_curves = bpy.data.curves.new(f"Label_{name}", 'FONT')
                label_curves.body = f"{type_id}: {name}"
                label_curves.size = 0.08
                label_curves.align_x = 'CENTER'
                label_obj = bpy.data.objects.new(f"Label_{name}", label_curves)
                cab_col.objects.link(label_obj)
                label_obj.location = (x_pos + width/2, -0.3, height + 0.1)

                x_pos += width + 0.15  # Space between cabinets

                created += 1
            except Exception as e:
                self.report({'WARNING'}, f"Failed to create {name}: {e}")

        # Add color legend
        legend_x = -1.0
        legend_z = 0.0
        for part_name, mat in debug_mats.items():
            # Create small cube as color swatch
            mesh = bpy.data.meshes.new(f"Swatch_{part_name}")
            swatch = bpy.data.objects.new(f"Legend_{part_name}", mesh)
            legend_col.objects.link(swatch)
            # Create cube mesh data
            bm_verts = [
                (-0.05, -0.05, -0.05), (0.05, -0.05, -0.05),
                (0.05, 0.05, -0.05), (-0.05, 0.05, -0.05),
                (-0.05, -0.05, 0.05), (0.05, -0.05, 0.05),
                (0.05, 0.05, 0.05), (-0.05, 0.05, 0.05),
            ]
            bm_faces = [
                (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5),
            ]
            mesh.from_pydata(bm_verts, [], bm_faces)
            mesh.update()
            swatch.location = (legend_x, -1.0, legend_z)
            swatch.data.materials.append(mat)

            # Add label
            label_curves = bpy.data.curves.new(f"LegendLabel_{part_name}", 'FONT')
            label_curves.body = part_name
            label_curves.size = 0.06
            label_obj = bpy.data.objects.new(f"LegendLabel_{part_name}", label_curves)
            legend_col.objects.link(label_obj)
            label_obj.location = (legend_x + 0.1, -1.0, legend_z)

            legend_z += 0.15

        self.report({'INFO'}, f"Created {created} test cabinets with debug colors")
        return {'FINISHED'}

    def _remove_collection_recursive(self, collection):
        """Remove a collection and all its contents recursively."""
        # Remove child collections first
        for child in list(collection.children):
            self._remove_collection_recursive(child)
        # Remove all objects in this collection
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        # Remove the collection itself
        bpy.data.collections.remove(collection)


class CABINET_OT_ReloadGenerators(Operator):
    """Reload node generator scripts"""
    bl_idname = "cabinet.reload_generators"
    bl_label = "Reload Generators"
    bl_description = "Reload all node generator Python scripts"
    bl_options = {'REGISTER'}

    def execute(self, context):
        import importlib
        from src.nodes import utils, master, material_presets
        from src.nodes.atomic import (
            shelf, door_panel, drawer, hardware, toe_kick, lazy_susan,
            hinges, drawer_slides, trash_pullout, spice_rack, shelf_pins,
            led_strip, crown_molding, light_rail
        )
        from src.nodes.systems import (
            cabinet_box, shelf_array, door_assembly, drawer_stack, blind_corner,
            sink_base, appliance_cabinet, open_shelving, diagonal_corner, pullout_pantry
        )

        # Reload all modules
        importlib.reload(utils)

        # Atomic modules
        importlib.reload(shelf)
        importlib.reload(door_panel)
        importlib.reload(drawer)
        importlib.reload(hardware)
        importlib.reload(toe_kick)
        importlib.reload(lazy_susan)
        importlib.reload(hinges)
        importlib.reload(drawer_slides)
        importlib.reload(trash_pullout)
        importlib.reload(spice_rack)
        importlib.reload(shelf_pins)
        importlib.reload(led_strip)
        importlib.reload(crown_molding)
        importlib.reload(light_rail)

        # System modules
        importlib.reload(cabinet_box)
        importlib.reload(shelf_array)
        importlib.reload(door_assembly)
        importlib.reload(drawer_stack)
        importlib.reload(blind_corner)
        importlib.reload(sink_base)
        importlib.reload(appliance_cabinet)
        importlib.reload(open_shelving)
        importlib.reload(diagonal_corner)
        importlib.reload(pullout_pantry)

        importlib.reload(material_presets)
        importlib.reload(master)

        self.report({'INFO'}, "Reloaded all generator scripts")
        return {'FINISHED'}


class CABINET_OT_HotReloadAddon(Operator):
    """Hot reload the entire addon without restarting Blender"""
    bl_idname = "cabinet.hot_reload_addon"
    bl_label = "Hot Reload Addon"
    bl_description = "Reload all addon modules (generators, clear caches) without restarting Blender"
    bl_options = {'REGISTER'}

    def execute(self, context):
        import importlib
        import sys

        # Get the addon module path
        addon_path = '/Users/KK/My Drive/Assets-Cloud/Blender/Scripts/Development/blender-addons/cabinet-generator'

        # Clear all cached modules related to the addon's node generators
        modules_to_remove = []
        for mod_name in list(sys.modules.keys()):
            # Only clear src.nodes modules - don't touch registered operator/panel modules
            if 'src.nodes' in mod_name or mod_name.startswith('src.'):
                modules_to_remove.append(mod_name)

        for mod_name in modules_to_remove:
            del sys.modules[mod_name]

        # Ensure addon path is in sys.path
        if addon_path not in sys.path:
            sys.path.insert(0, addon_path)

        # Now reload the node generators fresh
        try:
            # Import and reload utils first (other modules depend on it)
            from src.nodes import utils
            importlib.reload(utils)

            # Import and reload atomic modules
            from src.nodes.atomic import (
                shelf, door_panel, drawer, hardware, toe_kick, lazy_susan,
                hinges, drawer_slides, trash_pullout, spice_rack, shelf_pins,
                led_strip, crown_molding, light_rail
            )
            for mod in [shelf, door_panel, drawer, hardware, toe_kick, lazy_susan,
                       hinges, drawer_slides, trash_pullout, spice_rack, shelf_pins,
                       led_strip, crown_molding, light_rail]:
                importlib.reload(mod)

            # Import and reload system modules
            from src.nodes.systems import (
                cabinet_box, shelf_array, door_assembly, drawer_stack, blind_corner,
                sink_base, appliance_cabinet, open_shelving, diagonal_corner, pullout_pantry
            )
            for mod in [cabinet_box, shelf_array, door_assembly, drawer_stack, blind_corner,
                       sink_base, appliance_cabinet, open_shelving, diagonal_corner, pullout_pantry]:
                importlib.reload(mod)

            # Import and reload master and material presets
            from src.nodes import material_presets, master
            importlib.reload(material_presets)
            importlib.reload(master)

            self.report({'INFO'}, f"Hot reload complete! Cleared {len(modules_to_remove)} cached modules.")

        except Exception as e:
            self.report({'ERROR'}, f"Hot reload failed: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

        return {'FINISHED'}


class CABINET_OT_ReloadAndTest(Operator):
    """Hot reload addon and run all tests"""
    bl_idname = "cabinet.reload_and_test"
    bl_label = "Reload & Test"
    bl_description = "Hot reload all modules and immediately run all tests"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # First, hot reload
        bpy.ops.cabinet.hot_reload_addon()

        # Then run all tests
        bpy.ops.cabinet.run_all_tests()

        return {'FINISHED'}


# Registration
classes = (
    CABINET_OT_CreateCabinet,
    CABINET_OT_GenerateNodeGroups,
    CABINET_OT_CreateShelf,
    CABINET_OT_CreateDoorPanel,
    CABINET_OT_CreateDrawer,
    CABINET_OT_CreateHandle,
    CABINET_OT_CreateCabinetBox,
    CABINET_OT_CreateToeKick,
    CABINET_OT_CreateLazySusan,
    CABINET_OT_CreateBlindCorner,
    CABINET_OT_CreateHinges,
    CABINET_OT_CreateDrawerSlides,
    CABINET_OT_CreateShelfPins,
    CABINET_OT_CreateTrashPullout,
    CABINET_OT_CreateSpiceRack,
    CABINET_OT_CreateSinkBase,
    CABINET_OT_CreateApplianceCabinet,
    CABINET_OT_CreateOpenShelving,
    CABINET_OT_CreateDiagonalCorner,
    CABINET_OT_CreatePulloutPantry,
    CABINET_OT_ApplyMaterialPresets,
    CABINET_OT_RunAllTests,
    CABINET_OT_RunAtomicTests,
    CABINET_OT_RunSystemTests,
    CABINET_OT_ClearNodeGroups,
    CABINET_OT_CreateTestScene,
    CABINET_OT_ReloadGenerators,
    CABINET_OT_HotReloadAddon,
    CABINET_OT_ReloadAndTest,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
