# Auto Batch Renderer — Handlers module
# Frame change handlers and startup data population

import bpy
from mathutils import Vector
from math import radians

from .src.framing import frame_object_rig
from .properties import GLOBAL_ANGLES, _deferred_update_markers


_handler_is_running = False


@bpy.app.handlers.persistent
def timeline_update_handler(scene):
    """
    This handler updates the camera view in real-time as the user scrubs the timeline.
    """
    global _handler_is_running
    if _handler_is_running:
        return

    s = scene.abr_settings
    if s.disable_live_updates or bpy.app.is_job_running('RENDER'):
        return

    _handler_is_running = True
    try:
        c, cam, coll = s.camera_controller, s.studio_camera, s.preview_collection
        if not all([c, cam, coll]):
            return

        view_index = scene.frame_current - 1
        if 0 <= view_index < len(s.views):
            view = s.views[view_index]
            if view.view_category.startswith('STUDIO'):

                original_frame = scene.frame_current

                # Use view.animation_frame for ALL views in live preview
                scene.frame_set(view.animation_frame)

                # Use the exact same logic as the render operator for a perfect preview
                c.rotation_euler = view.camera_angle
                bpy.context.view_layer.update()

                depsgraph = bpy.context.evaluated_depsgraph_get()
                frame_object_rig(bpy.context, c, cam, coll, s.margin, depsgraph, s.use_orthographic, view.view_name)

                # --- CONSISTENCY FIX ---
                # Add the same update here to ensure the preview logic matches the render logic.
                # This guarantees that fine-tuning calculations are correct in the viewport.
                bpy.context.view_layer.update()

                scale = 1.0
                pos_offset = Vector((0.0, 0.0, 0.0))

                if view.enable_fine_tune:
                    scale = view.fine_tune_scale
                    pos_offset = Vector(view.fine_tune_position)

                if cam.data.type == 'ORTHO':
                    cam.data.ortho_scale /= scale
                else:  # PERSP
                    cam_direction = (cam.location - c.location).normalized()
                    current_distance = (cam.location - c.location).length
                    new_distance = current_distance / scale
                    cam.location = c.location + cam_direction * new_distance

                world_offset = cam.matrix_world.to_quaternion() @ pos_offset
                cam.location += world_offset

                # Restore original frame so the timeline playhead doesn't jump
                scene.frame_set(original_frame)
                bpy.context.view_layer.update()
    finally:
        # This ensures the lock is always released, even if an error occurs.
        _handler_is_running = False


def _deferred_data_check():
    """Timer callback to safely populate data on startup."""
    try:
        if hasattr(bpy.context, 'scene') and bpy.context.scene:
            data_check_and_populate(bpy.context)
    except Exception as e:
        print(f"ABR: Could not populate default data: {e}")
    return None  # Run only once


def data_check_and_populate(context):
    """Checks for old data structure and populates views if needed."""
    settings = context.scene.abr_settings

    # Simple migration check for new properties
    if settings.views and len(settings.views) > 0:
        # Check if the first view has the fine_tune_position attribute
        first_view = settings.views[0]
        if not hasattr(first_view, 'fine_tune_position') or first_view.fine_tune_position is None:
            print("ABR: Old view settings detected. Resetting to default to add new features.")
            settings.views.clear()

    if not settings.views:
        view_data = [
            ('Main', "Main", '_Main', 'STUDIO_STANDARD'),
            ('Front', "Front", '_Front', 'STUDIO_STANDARD'),
            ('Back', "Back", '_Back', 'STUDIO_STANDARD'),
            ('Left', "Left", '_Left', 'STUDIO_STANDARD'),
            ('Right', "Right", '_Right', 'STUDIO_STANDARD'),
            ('Top', "Top", '_Top', 'STUDIO_STANDARD'),
            ('Bottom', "Bottom", '_Bottom', 'STUDIO_STANDARD'),
            ('PropISO', "PropISO", '_PropISO', 'STUDIO_STANDARD'),
        ]
        for name, angle_key, suffix, category in view_data:
            v = settings.views.add()
            v.view_name = name
            v.suffix = suffix
            v.view_category = category
            angle_deg = GLOBAL_ANGLES.get(angle_key)
            if angle_deg:
                v.camera_angle = [radians(a) for a in angle_deg]

        # Use timer to safely call the operator
        if not bpy.app.timers.is_registered(_deferred_update_markers):
            bpy.app.timers.register(_deferred_update_markers, first_interval=0.1)
