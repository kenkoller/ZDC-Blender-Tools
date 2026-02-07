bl_info = {
    "name": "ZDC - Auto Batch Renderer",
    "author": "Ziti Design & Creative",
    "version": (5, 4, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > ZDC",
    "description": "Automated batch rendering system for product visualization",
    "category": "ZDC Tools",
}

import bpy

from .properties import (
    ZDC_PG_BatchRender_turntable_segment,
    ZDC_PG_BatchRender_turntable_hold_point,
    ZDC_PG_BatchRender_view_settings,
    ZDC_PG_BatchRender_settings,
)
from .operators import (
    ZDC_OT_BatchRender_toggle_exclude_framing,
    ZDC_OT_BatchRender_update_markers,
    ZDC_OT_BatchRender_add_view,
    ZDC_OT_BatchRender_remove_view,
    ZDC_OT_BatchRender_clear_markers,
    ZDC_OT_BatchRender_add_segment,
    ZDC_OT_BatchRender_remove_segment,
    ZDC_OT_BatchRender_add_hold_point,
    ZDC_OT_BatchRender_remove_hold_point,
    ZDC_OT_BatchRender_initialize_scene,
    ZDC_OT_BatchRender_preview_framing,
    ZDC_OT_BatchRender_cancel_render,
    ZDC_OT_BatchRender_render_all,
)
from .panels import ZDC_PT_BatchRender_main
from .handlers import (
    timeline_update_handler,
    _deferred_data_check,
)

classes = (
    ZDC_PG_BatchRender_turntable_segment,
    ZDC_PG_BatchRender_turntable_hold_point,
    ZDC_PG_BatchRender_view_settings,
    ZDC_PG_BatchRender_settings,
    ZDC_PT_BatchRender_main,
    ZDC_OT_BatchRender_update_markers,
    ZDC_OT_BatchRender_add_view,
    ZDC_OT_BatchRender_remove_view,
    ZDC_OT_BatchRender_clear_markers,
    ZDC_OT_BatchRender_add_segment,
    ZDC_OT_BatchRender_remove_segment,
    ZDC_OT_BatchRender_add_hold_point,
    ZDC_OT_BatchRender_remove_hold_point,
    ZDC_OT_BatchRender_initialize_scene,
    ZDC_OT_BatchRender_preview_framing,
    ZDC_OT_BatchRender_cancel_render,
    ZDC_OT_BatchRender_render_all,
    ZDC_OT_BatchRender_toggle_exclude_framing,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.abr_settings = bpy.props.PointerProperty(type=ZDC_PG_BatchRender_settings)

    if not bpy.app.background:
        # Add the handler only if it's not already there
        if timeline_update_handler not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(timeline_update_handler)

        # Use a timer to populate data on startup. This is safer than doing it directly in register.
        if not bpy.app.timers.is_registered(_deferred_data_check):
            bpy.app.timers.register(_deferred_data_check, first_interval=0.1)


def unregister():
    if timeline_update_handler in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(timeline_update_handler)

    if hasattr(bpy.types.Scene, 'abr_settings'):
        del bpy.types.Scene.abr_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
