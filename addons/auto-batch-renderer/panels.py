# Auto Batch Renderer — Panels module
# UI panel classes for the Render Properties sidebar

import bpy


class ABR_PT_MainPanel(bpy.types.Panel):
    """Main panel for the Auto Batch Renderer, shown in Render Properties."""
    bl_label = "Auto Batch Renderer"
    bl_idname = "RENDER_PT_auto_batch_renderer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.abr_settings

        # Import operator classes needed for bl_idname references
        from .operators import ABR_OT_InitializeScene, ABR_OT_UpdateMarkers, ABR_OT_ClearMarkers, ABR_OT_CancelRender, ABR_OT_RenderAll

        def draw_fine_tune_panel(layout, view):
            box = layout.box()
            box.active = view.enabled

            row = box.row(align=True)
            row.label(text="Angle", icon='ORIENTATION_GIMBAL')
            row.prop(view, "camera_angle", text="")

            row = box.row(align=True)
            row.label(text="Position", icon='EMPTY_DATA')
            row.prop(view, "fine_tune_position", text="")

            row = box.row(align=True)
            row.label(text="Scale", icon='VIEWZOOM')
            row.prop(view, "fine_tune_scale", text="")

        def draw_view_row(view_layout, view, index):
            main_box = view_layout.box()
            row = main_box.row(align=True)

            row.prop(view, "show_in_ui",
                     icon="TRIA_DOWN" if view.show_in_ui else "TRIA_RIGHT",
                     icon_only=True, emboss=False)

            row.prop(view, "enabled", text="")
            row.prop(view, "view_name", text="")

            if not view.show_in_ui:
                return

            sub_box = main_box.box()
            sub_row = sub_box.row(align=True)
            sub_row.active = view.enabled

            if view.view_category == 'STUDIO_OPTION':
                sub_row.prop(view, "base_angle_choice", text="")

            sub_row.prop(view, "suffix", text="")

            # Show animation frame for ALL views
            sub_row.prop(view, "animation_frame", text="")

            sub_row.prop(view, "use_custom_background", text="", icon='IMAGE_BACKGROUND')
            if view.use_custom_background:
                sub_row.prop(view, "background_color", text="")

            sub_row.prop(view, "enable_fine_tune", text="", icon='TOOL_SETTINGS')

            if view.view_category != 'STUDIO_STANDARD':
                op = sub_row.operator("abr.remove_view", text="", icon='REMOVE')
                op.index = index

            if view.enable_fine_tune:
                draw_fine_tune_panel(sub_box, view)

        box = layout.box()
        row = box.row()
        row.prop(settings, "show_setup", icon="TRIA_DOWN" if settings.show_setup else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Setup", icon='SETTINGS')
        if settings.show_setup:
            # Initialize Scene button
            row = box.row()
            row.scale_y = 1.2
            row.operator(ABR_OT_InitializeScene.bl_idname, text="Initialize Scene", icon='ADD')
            box.separator()
            row = box.row()
            row.prop(settings, "target_collection")
            row = box.row()
            row.prop(settings, "preview_collection")
            row = box.row(align=True)
            row.operator(ABR_OT_UpdateMarkers.bl_idname, text="Update Markers", icon='FILE_REFRESH')
            row.operator(ABR_OT_ClearMarkers.bl_idname, text="Clear Markers", icon='X')

        box = layout.box()
        row = box.row()
        row.prop(settings, "show_cameras_framing", icon="TRIA_DOWN" if settings.show_cameras_framing else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Cameras & Framing", icon='CAMERA_DATA')
        if settings.show_cameras_framing:
            row = box.row()
            row.prop(settings, "camera_controller")
            row = box.row()
            row.prop(settings, "studio_camera")
            row = box.row()
            row.prop(settings, "application_camera_object")
            box.separator()
            col = box.column(align=True)
            col.label(text="Main View Adjustments:")
            col.prop(settings, "main_view_angle")
            box.separator()
            box.prop(settings, "margin")
            box.prop(settings, "use_orthographic")
            box.prop(settings, "disable_live_updates")
            box.separator()
            row = box.row()
            row.operator("abr.preview_framing", text="Preview Framing", icon='CAMERA_DATA')

            # --- LIGHT MODIFIERS SUB-PANEL ---
            box.separator()
            lm_box = box.box()
            lm_row = lm_box.row()
            lm_row.prop(settings, "show_light_modifiers",
                         icon="TRIA_DOWN" if settings.show_light_modifiers else "TRIA_RIGHT",
                         icon_only=True, emboss=False)
            lm_row.label(text="Light Modifiers", icon='LIGHT')

            if settings.show_light_modifiers:
                lm_box.label(text="Objects that affect lighting but are hidden from camera:", icon='INFO')
                lm_box.prop(settings, "light_modifiers_collection", text="Collection")
                lm_box.prop(settings, "light_modifiers_hide_from_camera")
                lm_box.separator()
                lm_box.label(text="Additional framing exclusions (name patterns):")
                lm_box.prop(settings, "framing_exclusion_pattern", text="Pattern")
                lm_box.label(text="Tip: Add 'abr_exclude_framing' property to objects", icon='QUESTION')

        box = layout.box()
        row = box.row()
        row.prop(settings, "show_turntable", icon="TRIA_DOWN" if settings.show_turntable else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="360 Turntable", icon='OUTLINER_OB_CAMERA')
        if settings.show_turntable:
            box.prop(settings, "enable_turntable")
            col = box.column()
            col.active = settings.enable_turntable

            # Basic settings
            col.prop(settings, "turntable_duration")
            col.prop(settings, "turntable_suffix")

            col.separator()

            # Direction
            row = col.row(align=True)
            row.label(text="Direction:")
            row.prop(settings, "turntable_direction", expand=True)

            # Start angle and rotation amount
            row = col.row(align=True)
            row.prop(settings, "turntable_start_angle")
            row.prop(settings, "turntable_rotation_amount")

            # Ping-pong
            col.prop(settings, "turntable_ping_pong")

            # Hold start/end
            row = col.row(align=True)
            row.prop(settings, "turntable_hold_start")
            row.prop(settings, "turntable_hold_end")

            # Ease in/out
            row = col.row(align=True)
            row.prop(settings, "turntable_ease_in_frames")
            row.prop(settings, "turntable_ease_out_frames")

            # Total frames (read-only)
            row = col.row()
            row.enabled = False
            row.label(text=f"Total Frames: {settings.turntable_total_frames}")

            col.separator()

            # --- SCRUB SUB-PANEL ---
            scrub_box = col.box()
            scrub_row = scrub_box.row()
            scrub_row.prop(settings, "show_scrub",
                           icon="TRIA_DOWN" if settings.show_scrub else "TRIA_RIGHT",
                           icon_only=True, emboss=False)
            scrub_row.label(text="Scrub (Variable Speed)", icon='IPO_BEZIER')

            if settings.show_scrub:
                scrub_box.prop(settings, "scrub_preset")
                scrub_box.prop(settings, "scrub_mode")
                scrub_box.separator()

                # --- Mode-specific UI ---
                if settings.scrub_mode == 'EASING':
                    scrub_box.prop(settings, "scrub_easing_type")
                    if settings.scrub_easing_type != 'LINEAR':
                        scrub_box.prop(settings, "scrub_easing_direction")

                elif settings.scrub_mode == 'MULTI_SEGMENT':
                    scrub_box.prop(settings, "scrub_segment_count")
                    num_segs = len(settings.scrub_segments)
                    for i, seg in enumerate(settings.scrub_segments):
                        seg_row = scrub_box.row(align=True)
                        angle_start = (settings.turntable_rotation_amount / max(num_segs, 1)) * i
                        angle_end = (settings.turntable_rotation_amount / max(num_segs, 1)) * (i + 1)
                        seg_row.label(text=f"{angle_start:.0f}\u00b0-{angle_end:.0f}\u00b0")
                        seg_row.prop(seg, "speed", text="")
                        op = seg_row.operator("abr.remove_segment", text="", icon='X')
                        op.index = i
                    row = scrub_box.row()
                    row.operator("abr.add_segment", text="Add Segment", icon='ADD')

                elif settings.scrub_mode == 'RANDOM':
                    scrub_box.prop(settings, "scrub_random_seed")
                    scrub_box.prop(settings, "scrub_random_intensity", slider=True)
                    scrub_box.prop(settings, "scrub_random_points")
                    scrub_box.prop(settings, "scrub_random_allow_reverse")

                elif settings.scrub_mode == 'HOLD_POINTS':
                    for i, hp in enumerate(settings.scrub_hold_points):
                        hp_row = scrub_box.row(align=True)
                        hp_row.prop(hp, "angle", text="Angle")
                        hp_row.prop(hp, "hold_duration", text="Hold")
                        op = hp_row.operator("abr.remove_hold_point", text="", icon='X')
                        op.index = i
                    row = scrub_box.row()
                    row.operator("abr.add_hold_point", text="Add Hold Point", icon='ADD')

        if any(v.view_category == 'STUDIO_STANDARD' for v in settings.views):
            box = layout.box()
            row = box.row()
            row.prop(settings, "show_studio_standard", icon="TRIA_DOWN" if settings.show_studio_standard else "TRIA_RIGHT", icon_only=True, emboss=False)
            row.label(text="Standard Studio Renders")
            if settings.show_studio_standard:
                for i, view in enumerate(settings.views):
                    if view.view_category == 'STUDIO_STANDARD':
                        draw_view_row(box, view, i)

        if True:
            box = layout.box()
            row = box.row()
            row.prop(settings, "show_studio_optional", icon="TRIA_DOWN" if settings.show_studio_optional else "TRIA_RIGHT", icon_only=True, emboss=False)
            row.label(text="Optional Studio Renders")
            op = row.operator("abr.add_view", text="", icon='ADD')
            op.category = 'STUDIO_OPTION'
            if settings.show_studio_optional:
                for i, view in enumerate(settings.views):
                    if view.view_category == 'STUDIO_OPTION':
                        draw_view_row(box, view, i)

        if True:
            box = layout.box()
            row = box.row()
            row.prop(settings, "show_application", icon="TRIA_DOWN" if settings.show_application else "TRIA_RIGHT", icon_only=True, emboss=False)
            row.label(text="Application Renders")
            op = row.operator("abr.add_view", text="", icon='ADD')
            op.category = 'APPLICATION'
            if settings.show_application:
                for i, view in enumerate(settings.views):
                    if view.view_category == 'APPLICATION':
                        draw_view_row(box, view, i)

        box = layout.box()
        row = box.row()
        row.prop(settings, "show_output_settings", icon="TRIA_DOWN" if settings.show_output_settings else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Output Settings", icon='OUTPUT')
        if settings.show_output_settings:
            box.prop(settings, "output_path")
            split = box.split()
            col = split.column()
            col.label(text="Resolution:")
            row = col.row(align=True)
            row.prop(settings, "resolution_x")
            row.prop(settings, "resolution_y")
            row = col.row(align=True)
            row.prop(settings, "resolution_percentage", expand=True)
            col = split.column()
            col.label(text="File Format:")
            col.prop(settings, "file_format", text="")
            if settings.file_format == 'PNG':
                col.prop(settings, "png_color_mode", text="")

            row = box.row()
            row.scale_y = 1.5
            if context.window_manager.get("abr_is_rendering", False):
                row.operator(ABR_OT_CancelRender.bl_idname, text="Cancel Batch Render", icon='CANCEL')
            else:
                row.operator(ABR_OT_RenderAll.bl_idname, text="Render Enabled Views", icon='RENDER_ANIMATION')
