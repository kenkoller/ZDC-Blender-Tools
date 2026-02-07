# UI Panels for Cabinet Generator addon

import bpy
from bpy.types import Panel


class CABINET_PT_MainPanel(Panel):
    """Main panel in 3D View sidebar"""
    bl_label = "Cabinet Generator"
    bl_idname = "CABINET_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        # Cabinet type/preset selector
        layout.prop(settings, "cabinet_type")

        layout.separator()

        # Main create button
        col = layout.column(align=True)
        col.scale_y = 2.0
        col.operator("cabinet.create_cabinet", icon='MESH_CUBE', text="Create Cabinet")


class CABINET_PT_DimensionsPanel(Panel):
    """Dimensions subpanel"""
    bl_label = "Dimensions"
    bl_idname = "CABINET_PT_dimensions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        col = layout.column(align=True)
        col.prop(settings, "width")
        col.prop(settings, "height")
        col.prop(settings, "depth")

        layout.separator()

        col = layout.column(align=True)
        col.prop(settings, "panel_thickness")


class CABINET_PT_FrontPanel(Panel):
    """Front options subpanel"""
    bl_label = "Front"
    bl_idname = "CABINET_PT_front"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        layout.prop(settings, "front_type", expand=True)

        layout.separator()

        if settings.front_type == 'DOORS':
            col = layout.column(align=True)
            col.prop(settings, "door_style")
            col.prop(settings, "double_doors")

            # Glass insert options
            layout.separator()
            box = layout.box()
            box.prop(settings, "glass_insert")
            if settings.glass_insert:
                box.prop(settings, "glass_frame_width")
        else:
            layout.prop(settings, "drawer_count")

        layout.separator()
        layout.prop(settings, "handle_style")

        # Handle position offsets
        col = layout.column(align=True)
        col.prop(settings, "handle_offset_x")
        col.prop(settings, "handle_offset_z")


class CABINET_PT_InteriorPanel(Panel):
    """Interior options subpanel"""
    bl_label = "Interior"
    bl_idname = "CABINET_PT_interior"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        col = layout.column(align=True)
        col.prop(settings, "has_back")
        col.prop(settings, "has_shelves")

        if settings.has_shelves:
            col.prop(settings, "shelf_count")
            col.prop(settings, "shelf_thickness")

        # Adjustable shelf pins
        layout.separator()
        box = layout.box()
        box.prop(settings, "has_adjustable_shelves")
        if settings.has_adjustable_shelves:
            box.prop(settings, "shelf_pin_rows")

        # Side panels option for open shelving
        if settings.cabinet_type == 'OPEN_SHELVING':
            layout.separator()
            layout.prop(settings, "has_side_panels")


class CABINET_PT_BevelPanel(Panel):
    """Bevel options subpanel"""
    bl_label = "Bevel"
    bl_idname = "CABINET_PT_bevel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        col = layout.column(align=True)
        col.prop(settings, "bevel_width")
        col.prop(settings, "bevel_segments")


class CABINET_PT_ToeKickPanel(Panel):
    """Toe kick options subpanel"""
    bl_label = "Toe Kick"
    bl_idname = "CABINET_PT_toekick"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.cabinet_settings
        # Only show for floor-standing cabinets
        return settings.cabinet_type in ('BASE', 'TALL', 'DRAWER_BASE', 'BLIND_CORNER', 'SINK_BASE', 'DIAGONAL_CORNER', 'PULLOUT_PANTRY')

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        col = layout.column(align=True)
        col.prop(settings, "has_toe_kick")

        if settings.has_toe_kick:
            col.prop(settings, "toe_kick_height")
            col.prop(settings, "toe_kick_depth")


class CABINET_PT_CornerPanel(Panel):
    """Corner cabinet options subpanel"""
    bl_label = "Corner Options"
    bl_idname = "CABINET_PT_corner"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.cabinet_settings
        return settings.cabinet_type in ('BLIND_CORNER', 'DIAGONAL_CORNER')

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        if settings.cabinet_type == 'BLIND_CORNER':
            col = layout.column(align=True)
            col.prop(settings, "corner_type", expand=True)
            col.separator()
            col.prop(settings, "blind_width")

        # Lazy susan options (for corner cabinets)
        layout.separator()
        box = layout.box()
        box.prop(settings, "has_lazy_susan")
        if settings.has_lazy_susan:
            box.prop(settings, "lazy_susan_style")
            box.prop(settings, "lazy_susan_count")
            box.prop(settings, "lazy_susan_diameter")
            box.prop(settings, "lazy_susan_rotation")


class CABINET_PT_HardwarePanel(Panel):
    """Hardware options subpanel"""
    bl_label = "Hardware"
    bl_idname = "CABINET_PT_hardware"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        # Hinge style (for door cabinets)
        if settings.front_type == 'DOORS':
            col = layout.column(align=True)
            col.label(text="Hinges:")
            col.prop(settings, "hinge_style", text="")

        # Drawer slide style (for drawer cabinets)
        if settings.front_type == 'DRAWERS' or settings.cabinet_type == 'DRAWER_BASE':
            layout.separator()
            col = layout.column(align=True)
            col.label(text="Drawer Slides:")
            col.prop(settings, "drawer_slide_style", text="")


class CABINET_PT_ConstructionPanel(Panel):
    """Construction options subpanel"""
    bl_label = "Construction"
    bl_idname = "CABINET_PT_construction"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        # Face frame option
        box = layout.box()
        box.prop(settings, "has_face_frame")
        if settings.has_face_frame:
            box.prop(settings, "face_frame_width")


class CABINET_PT_AppliancePanel(Panel):
    """Appliance cabinet options subpanel"""
    bl_label = "Appliance Options"
    bl_idname = "CABINET_PT_appliance"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.cabinet_settings
        return settings.cabinet_type == 'APPLIANCE'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        col = layout.column(align=True)
        col.prop(settings, "appliance_type")
        col.prop(settings, "appliance_opening_height")

        layout.separator()
        layout.prop(settings, "has_trim_frame")


class CABINET_PT_SinkPanel(Panel):
    """Sink cabinet options subpanel"""
    bl_label = "Sink Options"
    bl_idname = "CABINET_PT_sink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.cabinet_settings
        return settings.cabinet_type == 'SINK_BASE'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        layout.prop(settings, "has_plumbing_cutout")


class CABINET_PT_InsertsPanel(Panel):
    """Cabinet inserts subpanel"""
    bl_label = "Inserts"
    bl_idname = "CABINET_PT_inserts"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.cabinet_settings
        # Show for cabinets that can have inserts
        return settings.cabinet_type in ('BASE', 'TALL', 'DRAWER_BASE', 'SINK_BASE')

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        # Trash pull-out
        box = layout.box()
        box.prop(settings, "has_trash_pullout")
        if settings.has_trash_pullout:
            box.prop(settings, "double_trash_bins")

        # Spice rack
        layout.separator()
        box = layout.box()
        box.prop(settings, "has_spice_rack")
        if settings.has_spice_rack:
            box.prop(settings, "spice_rack_tiers")


class CABINET_PT_AnimationPanel(Panel):
    """Animation options subpanel"""
    bl_label = "Animation"
    bl_idname = "CABINET_PT_animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        col = layout.column(align=True)
        if settings.front_type == 'DOORS':
            col.prop(settings, "door_open_angle")
        else:
            col.prop(settings, "drawer_open")

        # Pull-out extension for pantry and inserts
        if settings.cabinet_type == 'PULLOUT_PANTRY' or settings.has_trash_pullout or settings.has_spice_rack:
            col.separator()
            col.prop(settings, "pullout_extension")

        # Lazy susan rotation for corner cabinets
        if settings.cabinet_type in ('BLIND_CORNER', 'DIAGONAL_CORNER') and settings.has_lazy_susan:
            col.separator()
            col.prop(settings, "lazy_susan_rotation")


class CABINET_PT_MaterialsPanel(Panel):
    """Material presets subpanel"""
    bl_label = "Material Presets"
    bl_idname = "CABINET_PT_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings

        col = layout.column(align=True)
        col.prop(settings, "carcass_preset")
        col.prop(settings, "front_preset")
        col.prop(settings, "handle_preset")

        layout.separator()
        layout.operator("cabinet.apply_material_presets", icon='MATERIAL')


class CABINET_PT_ComponentsPanel(Panel):
    """Individual components subpanel"""
    bl_label = "Components"
    bl_idname = "CABINET_PT_components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.label(text="Create individual parts:")
        col = layout.column(align=True)
        col.operator("cabinet.create_cabinet_box", icon='CUBE')
        col.operator("cabinet.create_shelf", icon='MESH_PLANE')
        col.operator("cabinet.create_door_panel", icon='MOD_SOLIDIFY')
        col.operator("cabinet.create_drawer", icon='PACKAGE')
        col.operator("cabinet.create_handle", icon='HANDLE_FREE')
        col.operator("cabinet.create_toe_kick", icon='META_PLANE')
        col.operator("cabinet.create_lazy_susan", icon='ORIENTATION_GIMBAL')
        col.operator("cabinet.create_blind_corner", icon='VIEW_PERSPECTIVE')

        layout.separator()
        layout.label(text="Hardware:")
        col = layout.column(align=True)
        col.operator("cabinet.create_hinges", icon='PINNED')
        col.operator("cabinet.create_drawer_slides", icon='FORWARD')
        col.operator("cabinet.create_shelf_pins", icon='SNAP_VERTEX')

        layout.separator()
        layout.label(text="Inserts:")
        col = layout.column(align=True)
        col.operator("cabinet.create_trash_pullout", icon='TRASH')
        col.operator("cabinet.create_spice_rack", icon='LINENUMBERS_ON')

        layout.separator()
        layout.label(text="Cabinet Systems:")
        col = layout.column(align=True)
        col.operator("cabinet.create_sink_base", icon='MOD_FLUIDSIM')
        col.operator("cabinet.create_appliance_cabinet", icon='OUTLINER_OB_LIGHT')
        col.operator("cabinet.create_open_shelving", icon='ALIGN_JUSTIFY')
        col.operator("cabinet.create_diagonal_corner", icon='MOD_TRIANGULATE')
        col.operator("cabinet.create_pullout_pantry", icon='ALIGN_BOTTOM')


class CABINET_PT_ExportPanel(Panel):
    """Export and cut list subpanel"""
    bl_label = "Export"
    bl_idname = "CABINET_PT_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.label(text="Cut List:", icon='FILE_TEXT')
        col = layout.column(align=True)
        col.operator("cabinet.show_cut_list", text="Show Cut List", icon='VIEWZOOM')
        col.operator("cabinet.export_cut_list", text="Export Cut List", icon='EXPORT')


class CABINET_PT_BatchPanel(Panel):
    """Batch generation subpanel"""
    bl_label = "Batch Generation"
    bl_idname = "CABINET_PT_batch"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("cabinet.batch_generate", text="Batch Generate", icon='DUPLICATE')
        col.operator("cabinet.batch_from_json", text="From JSON File", icon='FILE_FOLDER')
        col.operator("cabinet.generate_kitchen_run", text="Kitchen Run", icon='HOME')
        col.operator("cabinet.batch_lazy_susan", text="Lazy Susan Batch", icon='MESH_CIRCLE')


class CABINET_PT_DeveloperPanel(Panel):
    """Developer tools subpanel"""
    bl_label = "Developer"
    bl_idname = "CABINET_PT_developer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("cabinet.generate_nodegroups", icon='NODETREE')
        col.operator("cabinet.reload_generators", icon='FILE_REFRESH')
        col.operator("cabinet.clear_nodegroups", icon='TRASH')


class CABINET_PT_TestingPanel(Panel):
    """Testing and debugging subpanel"""
    bl_label = "Testing & Debug"
    bl_idname = "CABINET_PT_testing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        test_results = context.scene.cabinet_test_results

        # Hot Reload section - most important buttons at top
        box = layout.box()
        box.label(text="Development:", icon='TOOL_SETTINGS')
        col = box.column(align=True)
        col.operator("cabinet.reload_and_test", text="Reload & Test All", icon='PLAY')
        row = col.row(align=True)
        row.operator("cabinet.hot_reload_addon", text="Hot Reload", icon='FILE_REFRESH')
        row.operator("cabinet.run_all_tests", text="Run Tests", icon='CHECKMARK')

        # Individual test options
        layout.label(text="Test Individual:", icon='VIEWZOOM')
        row = layout.row(align=True)
        row.operator("cabinet.run_atomic_tests", text="Atomics", icon='CUBE')
        row.operator("cabinet.run_system_tests", text="Systems", icon='PACKAGE')

        # Test scene
        layout.separator()
        layout.operator("cabinet.create_test_scene", text="Create Test Scene", icon='SCENE_DATA')

        # Results section
        if test_results.total_tests > 0:
            layout.separator()
            box = layout.box()

            # Summary header
            row = box.row()
            row.label(text="Results:", icon='INFO')
            row.label(text=test_results.last_run)

            # Pass/fail counts with color
            row = box.row()
            if test_results.failed_tests == 0:
                row.label(text=f"{test_results.passed_tests}/{test_results.total_tests} Passed", icon='CHECKMARK')
            else:
                sub = row.row()
                sub.alert = True
                sub.label(text=f"{test_results.failed_tests} Failed", icon='ERROR')
                row.label(text=f"{test_results.passed_tests} Passed", icon='CHECKMARK')

            # Failed tests details
            if test_results.failed_tests > 0:
                box.separator()
                box.label(text="Failed Tests:", icon='ERROR')
                for result in test_results.results:
                    if not result.passed:
                        row = box.row()
                        row.alert = True
                        row.label(text=f"  {result.name}: {result.message[:40]}", icon='X')


class CABINET_PT_TestResultsPanel(Panel):
    """Detailed test results subpanel"""
    bl_label = "All Test Results"
    bl_idname = "CABINET_PT_test_results"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_testing"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.cabinet_test_results.total_tests > 0

    def draw(self, context):
        layout = self.layout
        test_results = context.scene.cabinet_test_results

        # Group by category
        categories = [
            ("Atomic Components", "atomic", "CUBE"),
            ("System Components", "system", "PACKAGE"),
            ("Master", "master", "NODETREE"),
        ]

        for cat_label, cat_id, icon in categories:
            cat_results = [r for r in test_results.results if r.category == cat_id]
            if cat_results:
                box = layout.box()
                box.label(text=cat_label, icon=icon)
                for result in cat_results:
                    row = box.row()
                    if result.passed:
                        row.label(text=result.name, icon='CHECKMARK')
                        row.label(text=result.message)
                    else:
                        row.alert = True
                        row.label(text=result.name, icon='X')
                        row.label(text=result.message[:30])


# Registration
classes = (
    CABINET_PT_MainPanel,
    CABINET_PT_DimensionsPanel,
    CABINET_PT_FrontPanel,
    CABINET_PT_InteriorPanel,
    CABINET_PT_HardwarePanel,
    CABINET_PT_ConstructionPanel,
    CABINET_PT_ToeKickPanel,
    CABINET_PT_CornerPanel,
    CABINET_PT_AppliancePanel,
    CABINET_PT_SinkPanel,
    CABINET_PT_InsertsPanel,
    CABINET_PT_BevelPanel,
    CABINET_PT_AnimationPanel,
    CABINET_PT_MaterialsPanel,
    CABINET_PT_ExportPanel,
    CABINET_PT_BatchPanel,
    CABINET_PT_ComponentsPanel,
    CABINET_PT_DeveloperPanel,
    CABINET_PT_TestingPanel,
    CABINET_PT_TestResultsPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
