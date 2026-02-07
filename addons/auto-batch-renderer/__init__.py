bl_info = {
    "name": "ZDC - Auto Batch Renderer",
    "author": "Ziti Design & Creative",
    "version": (5, 3, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > ZDC",
    "description": "Automated batch rendering system for product visualization",
    "category": "ZDC Tools",
}

import bpy

from .properties import (
    ABR_TurntableSegment,
    ABR_TurntableHoldPoint,
    ABR_ViewSettings,
    ABR_Settings,
)
from .operators import (
    ABR_OT_ToggleExcludeFraming,
    ABR_OT_UpdateMarkers,
    ABR_OT_AddView,
    ABR_OT_RemoveView,
    ABR_OT_ClearMarkers,
    ABR_OT_AddSegment,
    ABR_OT_RemoveSegment,
    ABR_OT_AddHoldPoint,
    ABR_OT_RemoveHoldPoint,
    ABR_OT_InitializeScene,
    ABR_OT_CancelRender,
    ABR_OT_RenderAll,
)
from .panels import ABR_PT_MainPanel
from .handlers import (
    timeline_update_handler,
    _deferred_data_check,
)

classes = (
    ABR_TurntableSegment,
    ABR_TurntableHoldPoint,
    ABR_ViewSettings,
    ABR_Settings,
    ABR_PT_MainPanel,
    ABR_OT_UpdateMarkers,
    ABR_OT_AddView,
    ABR_OT_RemoveView,
    ABR_OT_ClearMarkers,
    ABR_OT_AddSegment,
    ABR_OT_RemoveSegment,
    ABR_OT_AddHoldPoint,
    ABR_OT_RemoveHoldPoint,
    ABR_OT_InitializeScene,
    ABR_OT_CancelRender,
    ABR_OT_RenderAll,
    ABR_OT_ToggleExcludeFraming,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.abr_settings = bpy.props.PointerProperty(type=ABR_Settings)

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
