# Auto Batch Renderer — Operators module
# All ZDC_OT_BatchRender_* operator classes

import bpy
from mathutils import Vector
from math import radians
import os
import shutil
import random
import blf  # For drawing progress in the viewport

from .properties import GLOBAL_ANGLES, ORTHOGRAPHIC_VIEWS
from .src.framing import frame_object_rig


class ZDC_OT_BatchRender_toggle_exclude_framing(bpy.types.Operator):
    """Toggle the abr_exclude_framing custom property on selected objects"""
    bl_idname = "zdc.batchrender_toggle_exclude_framing"
    bl_label = "Toggle Exclude from Framing"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        toggled_count = 0
        for obj in context.selected_objects:
            current_value = obj.get("abr_exclude_framing", False)
            obj["abr_exclude_framing"] = not current_value
            toggled_count += 1

            # Create a custom property UI entry if it doesn't exist
            if "_RNA_UI" not in obj:
                obj["_RNA_UI"] = {}
            obj["_RNA_UI"]["abr_exclude_framing"] = {
                "description": "Exclude this object from ABR camera framing calculations",
                "default": False,
            }

        new_state = "excluded" if not obj.get("abr_exclude_framing", False) else "included"
        self.report({'INFO'}, f"Toggled {toggled_count} object(s) - now {new_state} in framing")
        return {'FINISHED'}


class ZDC_OT_BatchRender_update_markers(bpy.types.Operator):
    """Synchronize timeline markers with the current set of enabled views."""
    bl_idname = "zdc.batchrender_update_markers"
    bl_label = "Update Markers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.abr_settings
        scene = context.scene

        # Clear existing markers to avoid duplicates
        for m in reversed(scene.timeline_markers):
            scene.timeline_markers.remove(m)

        # Create a new marker for each enabled view
        for i, view in enumerate(settings.views):
            frame = i + 1
            # Show frame info for all views now
            marker_name = f"{view.view_name} (F:{view.animation_frame})"
            scene.timeline_markers.new(name=marker_name, frame=frame)

        self.report({'INFO'}, f"Updated {len(settings.views)} timeline markers.")
        return {'FINISHED'}


class ZDC_OT_BatchRender_add_view(bpy.types.Operator):
    """Add a new optional studio or application view to the render list."""
    bl_idname = "zdc.batchrender_add_view"
    bl_label = "Add View"
    bl_options = {'REGISTER', 'UNDO'}

    category: bpy.props.StringProperty()

    def execute(self, context):
        settings = context.scene.abr_settings
        new_view = settings.views.add()

        if self.category == 'STUDIO_OPTION':
            num_existing = len([v for v in settings.views if v.view_category == 'STUDIO_OPTION'])
            new_view.view_name = f"Optional {chr(65 + num_existing)}"
            new_view.suffix = f"_Optional{chr(65 + num_existing)}"
            new_view.view_category = 'STUDIO_OPTION'
            angle_deg = GLOBAL_ANGLES.get("Default Optional")
            if angle_deg:
                new_view.camera_angle = [radians(a) for a in angle_deg]

        elif self.category == 'APPLICATION':
            num_existing = len([v for v in settings.views if v.view_category == 'APPLICATION'])
            new_view.view_name = f"Application {chr(65 + num_existing)}"
            new_view.suffix = f"_Application{chr(65 + num_existing)}"
            new_view.view_category = 'APPLICATION'
            angle_deg = GLOBAL_ANGLES.get("Default Application")
            if angle_deg:
                new_view.camera_angle = [radians(a) for a in angle_deg]

        bpy.ops.zdc.batchrender_update_markers()
        return {'FINISHED'}


class ZDC_OT_BatchRender_remove_view(bpy.types.Operator):
    """Remove an optional view from the render list by index."""
    bl_idname = "zdc.batchrender_remove_view"
    bl_label = "Remove View"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.abr_settings
        settings.views.remove(self.index)
        bpy.ops.zdc.batchrender_update_markers()
        return {'FINISHED'}


class ZDC_OT_BatchRender_clear_markers(bpy.types.Operator):
    """Remove all timeline markers from the scene."""
    bl_idname = "zdc.batchrender_clear_markers"
    bl_label = "Clear Markers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        for m in reversed(scene.timeline_markers):
            scene.timeline_markers.remove(m)
        self.report({'INFO'}, "Cleared all timeline markers.")
        return {'FINISHED'}


class ZDC_OT_BatchRender_reset_views(bpy.types.Operator):
    """Reset to the 8 standard studio views. Removes all optional/application views."""
    bl_idname = "zdc.batchrender_reset_views"
    bl_label = "Reset Standard Views"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.abr_settings
        settings.views.clear()
        from .handlers import data_check_and_populate
        data_check_and_populate(context)
        self.report({'INFO'}, "Standard views restored.")
        return {'FINISHED'}


class ZDC_OT_BatchRender_add_segment(bpy.types.Operator):
    """Add a speed segment to the turntable animation"""
    bl_idname = "zdc.batchrender_add_segment"
    bl_label = "Add Segment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.abr_settings
        if len(s.scrub_segments) < 12:
            seg = s.scrub_segments.add()
            seg.speed = 1.0
            s.scrub_segment_count = len(s.scrub_segments)
        return {'FINISHED'}


class ZDC_OT_BatchRender_remove_segment(bpy.types.Operator):
    """Remove a speed segment from the turntable animation"""
    bl_idname = "zdc.batchrender_remove_segment"
    bl_label = "Remove Segment"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        s = context.scene.abr_settings
        if len(s.scrub_segments) > 2:
            s.scrub_segments.remove(self.index)
            s.scrub_segment_count = len(s.scrub_segments)
            if s.scrub_active_segment >= len(s.scrub_segments):
                s.scrub_active_segment = max(0, len(s.scrub_segments) - 1)
        return {'FINISHED'}


class ZDC_OT_BatchRender_add_hold_point(bpy.types.Operator):
    """Add a hold point to the turntable animation"""
    bl_idname = "zdc.batchrender_add_hold_point"
    bl_label = "Add Hold Point"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.abr_settings
        hp = s.scrub_hold_points.add()
        existing = len(s.scrub_hold_points)
        if existing > 1:
            hp.angle = (360.0 / existing) * (existing - 1)
        hp.hold_duration = 12
        return {'FINISHED'}


class ZDC_OT_BatchRender_remove_hold_point(bpy.types.Operator):
    """Remove a hold point from the turntable animation"""
    bl_idname = "zdc.batchrender_remove_hold_point"
    bl_label = "Remove Hold Point"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        s = context.scene.abr_settings
        s.scrub_hold_points.remove(self.index)
        if s.scrub_active_hold_point >= len(s.scrub_hold_points):
            s.scrub_active_hold_point = max(0, len(s.scrub_hold_points) - 1)
        return {'FINISHED'}


class ZDC_OT_BatchRender_initialize_scene(bpy.types.Operator):
    """Initialize the scene with all required ABR objects and collections"""
    bl_idname = "zdc.batchrender_initialize_scene"
    bl_label = "Initialize Scene"
    bl_options = {'REGISTER', 'UNDO'}

    # Track what needs to be created
    create_controller: bpy.props.BoolProperty(default=False)
    create_studio_camera: bpy.props.BoolProperty(default=False)
    create_target_collection: bpy.props.BoolProperty(default=False)
    create_preview_collection: bpy.props.BoolProperty(default=False)
    create_light_modifiers_collection: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        """Check what's missing and prompt the user"""
        settings = context.scene.abr_settings

        # Detect what's missing
        self.create_controller = settings.camera_controller is None
        self.create_studio_camera = settings.studio_camera is None
        self.create_target_collection = settings.target_collection is None
        self.create_preview_collection = settings.preview_collection is None
        self.create_light_modifiers_collection = settings.light_modifiers_collection is None

        # If everything exists, inform the user
        if not any([self.create_controller, self.create_studio_camera,
                    self.create_target_collection, self.create_preview_collection,
                    self.create_light_modifiers_collection]):
            self.report({'INFO'}, "Scene is already fully initialized.")
            return {'CANCELLED'}

        # Show confirmation dialog
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.label(text="The following items will be created:")
        layout.separator()

        col = layout.column(align=True)
        if self.create_controller or self.create_studio_camera:
            col.label(text="• ABR_Rig (Collection)", icon='OUTLINER_COLLECTION')
        if self.create_controller:
            col.label(text="  • ABR_Camera_Controller (Empty)", icon='EMPTY_DATA')
        if self.create_studio_camera:
            col.label(text="  • ABR_Studio_Camera (Camera)", icon='CAMERA_DATA')
        if self.create_target_collection:
            col.label(text="• ABR_Products (Collection)", icon='OUTLINER_COLLECTION')
        if self.create_preview_collection:
            col.label(text="• ABR_Preview (Collection)", icon='OUTLINER_COLLECTION')
        if self.create_light_modifiers_collection:
            col.label(text="• ABR_Light_Modifiers (Collection)", icon='OUTLINER_COLLECTION')

        layout.separator()
        layout.label(text="Existing assignments will not be changed.")

    def _get_or_create_rig_collection(self, scene):
        """Get or create the ABR_Rig collection for camera rig objects."""
        rig_coll = bpy.data.collections.get("ABR_Rig")
        if not rig_coll:
            rig_coll = bpy.data.collections.new("ABR_Rig")
            scene.collection.children.link(rig_coll)
        elif rig_coll.name not in scene.collection.children:
            scene.collection.children.link(rig_coll)
        return rig_coll

    def execute(self, context):
        settings = context.scene.abr_settings
        scene = context.scene
        created_items = []

        # Get or create the rig collection for controller + camera
        rig_coll = None
        if self.create_controller or self.create_studio_camera:
            rig_coll = self._get_or_create_rig_collection(scene)

        # Create Camera Controller (Empty)
        if self.create_controller:
            controller = bpy.data.objects.new("ABR_Camera_Controller", None)
            controller.empty_display_type = 'PLAIN_AXES'
            controller.empty_display_size = 0.5
            rig_coll.objects.link(controller)
            settings.camera_controller = controller
            created_items.append("Camera Controller")

        # Create Studio Camera
        if self.create_studio_camera:
            cam_data = bpy.data.cameras.new("ABR_Studio_Camera")
            studio_camera = bpy.data.objects.new("ABR_Studio_Camera", cam_data)
            rig_coll.objects.link(studio_camera)
            settings.studio_camera = studio_camera
            # Set as active camera if none exists
            if scene.camera is None:
                scene.camera = studio_camera
            created_items.append("Studio Camera")

        # Create Target Collection (Products)
        if self.create_target_collection:
            target_coll = bpy.data.collections.new("ABR_Products")
            scene.collection.children.link(target_coll)
            settings.target_collection = target_coll
            created_items.append("Products Collection")

        # Create Preview Collection
        if self.create_preview_collection:
            preview_coll = bpy.data.collections.new("ABR_Preview")
            scene.collection.children.link(preview_coll)
            settings.preview_collection = preview_coll
            created_items.append("Preview Collection")

        # Create Light Modifiers Collection
        if self.create_light_modifiers_collection:
            lm_coll = bpy.data.collections.new("ABR_Light_Modifiers")
            scene.collection.children.link(lm_coll)
            settings.light_modifiers_collection = lm_coll
            created_items.append("Light Modifiers Collection")

        # Report what was created
        if created_items:
            self.report({'INFO'}, f"Created: {', '.join(created_items)}")

        return {'FINISHED'}


class ZDC_OT_BatchRender_preview_framing(bpy.types.Operator):
    """Preview camera framing for the selected view without rendering.
    Uses the preview collection if set, otherwise the first child of the target collection."""
    bl_idname = "zdc.batchrender_preview_framing"
    bl_label = "Preview Camera Framing"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.scene.abr_settings
        has_camera = s.studio_camera is not None and s.camera_controller is not None
        has_collection = s.preview_collection is not None or s.target_collection is not None
        return has_camera and has_collection

    def execute(self, context):
        s = context.scene.abr_settings
        scene = context.scene

        cam = s.studio_camera
        controller = s.camera_controller

        # Determine which collection to frame
        # Check preview_collection has actual objects; empty collection is not useful
        collection = s.preview_collection if s.preview_collection and len(s.preview_collection.all_objects) > 0 else None
        if not collection:
            # Use first child of target collection, or target itself
            if s.target_collection and s.target_collection.children:
                children = [c for c in s.target_collection.children if c.name != "Props"]
                collection = children[0] if children else s.target_collection
            elif s.target_collection:
                collection = s.target_collection

        if not collection:
            self.report({'ERROR'}, "No collection available for framing preview.")
            return {'CANCELLED'}

        # Determine which view to preview based on the current frame position
        enabled_views = [v for v in s.views if v.enabled]
        if not enabled_views:
            self.report({'WARNING'}, "No enabled views to preview.")
            return {'CANCELLED'}

        # Map frame position to view index (frame 1 = first view, etc.)
        view_index = max(0, min(scene.frame_current - 1, len(enabled_views) - 1))
        view = enabled_views[view_index]

        # Replicate the exact render_still framing logic
        scene.frame_set(view.animation_frame)
        controller.rotation_euler = view.camera_angle
        context.view_layer.update()
        depsgraph = context.evaluated_depsgraph_get()

        frame_object_rig(
            context, controller, cam, collection,
            s.margin, depsgraph, s.use_orthographic, view.view_name
        )
        context.view_layer.update()

        # Apply fine-tuning if enabled
        if view.enable_fine_tune:
            scale = view.fine_tune_scale
            pos_offset = Vector(view.fine_tune_position)

            if cam.data.type == 'ORTHO':
                cam.data.ortho_scale /= scale
            else:
                cam_direction = (cam.location - controller.location).normalized()
                current_distance = (cam.location - controller.location).length
                new_distance = current_distance / scale
                cam.location = controller.location + cam_direction * new_distance

            world_offset = cam.matrix_world.to_quaternion() @ pos_offset
            cam.location += world_offset

        scene.camera = cam
        context.view_layer.update()

        self.report({'INFO'}, f"Camera framed for: {view.view_name} ({collection.name})")
        return {'FINISHED'}


class ZDC_OT_BatchRender_cancel_render(bpy.types.Operator):
    """Request cancellation of the currently running batch render."""
    bl_idname = "zdc.batchrender_cancel_render"
    bl_label = "Cancel Batch Render"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.window_manager["abr_cancel_requested"] = True
        self.report({'INFO'}, "Cancellation requested. Finishing current job...")
        return {'FINISHED'}


class ZDC_OT_BatchRender_render_all(bpy.types.Operator):
    """Render all enabled views for every child collection in the target collection.

    Operates as a modal operator with a timer. For each collection, renders
    still images for each enabled view, then optionally a turntable animation.
    Restores all original scene settings on completion or cancellation.
    """
    bl_idname = "zdc.batchrender_render_all"
    bl_label = "Render Enabled Views"
    bl_options = {'REGISTER'}

    _timer = None
    _draw_handle = None
    render_jobs = []
    total_job_count = 0
    original_settings = {}
    original_collection_visibility = {}
    original_light_modifier_visibility = {}  # Store original camera ray visibility
    original_frame = 1

    def invoke(self, context, event):
        s = context.scene.abr_settings
        if not s.target_collection:
            self.report({'ERROR'}, "Target Collection not set.")
            return {'CANCELLED'}

        if not s.studio_camera or not s.camera_controller:
            self.report({'ERROR'}, "Studio Camera or Camera Controller not set.")
            return {'CANCELLED'}

        context.window_manager["abr_cancel_requested"] = False
        context.window_manager["abr_is_rendering"] = True

        enabled_views = [v for v in s.views if v.enabled]
        collections_to_render = [c for c in s.target_collection.children if c.name != "Props"]
        if not collections_to_render:
            collections_to_render = [s.target_collection]

        self.render_jobs.clear()
        for coll in collections_to_render:
            for view in enabled_views:
                self.render_jobs.append({'type': 'still', 'collection': coll, 'view': view})
            if s.enable_turntable:
                self.render_jobs.append({'type': 'turntable', 'collection': coll})

        self.total_job_count = len(self.render_jobs)
        if not self.render_jobs:
            self.report({'WARNING'}, "No render jobs created.")
            context.window_manager["abr_is_rendering"] = False
            return {'CANCELLED'}

        self.original_settings = self.store_settings(context)
        self.original_collection_visibility = {c: c.hide_render for c in s.target_collection.children}
        self.original_frame = context.scene.frame_current

        # Store and apply light modifier visibility settings
        self.original_light_modifier_visibility = {}
        self.apply_light_modifier_visibility(context, hide=True)

        self.apply_settings(context)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        ZDC_OT_BatchRender_render_all._draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_progress, (context,), 'WINDOW', 'POST_PIXEL')

        self.report({'INFO'}, f"Starting batch render of {self.total_job_count} jobs...")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.window_manager.get("abr_cancel_requested", False):
            self.finish(context, cancelled=True)
            return {'CANCELLED'}

        if bpy.app.is_job_running('RENDER'):
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            if not self.render_jobs:
                self.finish(context)
                return {'FINISHED'}

            job = self.render_jobs.pop(0)
            self.process_job(context, job)
            if context.area:
                context.area.tag_redraw()

        return {'PASS_THROUGH'}

    def process_job(self, context, job):
        s = context.scene.abr_settings
        collection = job['collection']

        # Isolate the collection to be rendered
        for child_coll in s.target_collection.children:
            child_coll.hide_render = True
            child_coll.hide_viewport = True
        collection.hide_render = False
        collection.hide_viewport = False

        context.view_layer.update()

        if job['type'] == 'still':
            self.render_still(context, collection, job['view'])
        elif job['type'] == 'turntable':
            self.render_turntable(context, collection)

    def render_still(self, context, collection, view):
        s = context.scene.abr_settings
        scene = context.scene

        # Use view.animation_frame for ALL views
        scene.frame_set(view.animation_frame)

        # Determine which camera to use
        cam = None
        if view.view_category == 'APPLICATION':
            cam = s.application_camera_object
            if not cam:
                print(f"Warning: Application camera not set for view '{view.view_name}'. Skipping.")
                return
            # NOTE: Application camera does not use the controller rig, so we skip framing
        else:  # Studio views
            cam = s.studio_camera
            c = s.camera_controller
            if not all([c, cam]):
                print(f"Warning: Studio camera or controller not set for view '{view.view_name}'. Skipping.")
                return

            # --- FIX for WANDERING CAMERA & STUCK VIEWS ---
            # This is the full, clean setup sequence for each render.
            # 1. Set the base rotation from the view settings.
            c.rotation_euler = view.camera_angle

            # 2. Force the view layer to update with all visibility and rotation changes.
            context.view_layer.update()

            # 3. Get the dependency graph *after* the update. This is the crucial step
            #    to ensure it reflects the currently visible collection.
            depsgraph = context.evaluated_depsgraph_get()

            # 4. Run auto-framing, passing the correct depsgraph down the chain.
            frame_object_rig(context, c, cam, collection, s.margin, depsgraph, s.use_orthographic, view.view_name)

            # --- CORE FIX ---
            # Force one more update AFTER auto-framing. This ensures the camera's
            # world matrix is 100% current before we read it to calculate the
            # fine-tune offsets. This makes it work reliably when "Disable Live Updates" is checked.
            context.view_layer.update()

            # 5. Now, apply fine-tuning adjustments to the newly framed position.
            #    This logic is non-cumulative because frame_object_rig resets the base state.
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

            # The position offset is applied in the camera's local space, which is more intuitive.
            world_offset = cam.matrix_world.to_quaternion() @ pos_offset
            cam.location += world_offset

        scene.camera = cam
        context.view_layer.update()  # Final update before render

        self.setup_compositor(context, view.use_custom_background, view.background_color)

        safe_name = bpy.path.clean_name(collection.name)
        filename = f"{safe_name}{view.suffix}"  # Extension will be added by Blender
        output_dir = os.path.join(bpy.path.abspath(s.output_path), safe_name)

        try:
            os.makedirs(output_dir, exist_ok=True)
        except (PermissionError, OSError) as e:
            print(f"ABR Error: Cannot create directory '{output_dir}': {e}")
            return

        # Check available disk space (warn below 50MB)
        try:
            free_space = shutil.disk_usage(output_dir).free
            if free_space < 50 * 1024 * 1024:
                print(f"ABR Warning: Low disk space ({free_space // (1024 * 1024)}MB free). Render may fail.")
        except OSError:
            pass  # disk_usage may not be available on all platforms

        scene.render.filepath = os.path.join(output_dir, filename)
        bpy.ops.render.render(write_still=True)

    # --- KEYFRAME GENERATION HELPERS ---

    @staticmethod
    def _set_fcurve_interpolation(controller, interpolation='LINEAR', easing='AUTO'):
        """Set interpolation on all Z-rotation keyframes."""
        if not controller.animation_data or not controller.animation_data.action:
            return
        for fcurve in controller.animation_data.action.fcurves:
            if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = interpolation
                    if interpolation != 'LINEAR' and interpolation != 'CONSTANT':
                        kp.easing = easing

    @staticmethod
    def _keyframes_easing(controller, s, start_frame, end_frame, start_angle, end_angle):
        """Create keyframes using Blender's interpolation types."""
        controller.rotation_euler.z = start_angle
        controller.keyframe_insert(data_path="rotation_euler", frame=start_frame, index=2)
        controller.rotation_euler.z = end_angle
        controller.keyframe_insert(data_path="rotation_euler", frame=end_frame, index=2)

        if not controller.animation_data or not controller.animation_data.action:
            return
        for fcurve in controller.animation_data.action.fcurves:
            if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                for kp in fcurve.keyframe_points:
                    if s.scrub_easing_type == 'LINEAR':
                        kp.interpolation = 'LINEAR'
                    elif s.scrub_easing_type == 'BEZIER':
                        kp.interpolation = 'BEZIER'
                        kp.easing = s.scrub_easing_direction
                    else:
                        kp.interpolation = s.scrub_easing_type
                        kp.easing = s.scrub_easing_direction

    @staticmethod
    def _keyframes_multi_segment(controller, s, start_frame, duration, start_angle, total_rotation):
        """Create keyframes for multi-segment variable speed."""
        segments = s.scrub_segments
        if len(segments) == 0:
            return start_frame + duration

        # Frame allocation: inversely proportional to speed
        total_weight = sum(1.0 / max(seg.speed, 0.1) for seg in segments)
        angle_per_seg = total_rotation / len(segments)

        current_frame = start_frame
        current_angle = start_angle

        controller.rotation_euler.z = current_angle
        controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

        for seg in segments:
            seg_weight = (1.0 / max(seg.speed, 0.1)) / total_weight
            seg_frames = max(int(duration * seg_weight), 1)
            current_frame += seg_frames
            current_angle += angle_per_seg

            controller.rotation_euler.z = current_angle
            controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

        # Set all to linear (constant speed within each segment)
        ZDC_OT_BatchRender_render_all._set_fcurve_interpolation(controller, 'LINEAR')
        return int(current_frame)

    @staticmethod
    def _keyframes_random(controller, s, start_frame, duration, start_angle, total_rotation):
        """Create keyframes with random speed variation."""
        random.seed(s.scrub_random_seed)

        num_points = s.scrub_random_points
        intensity = s.scrub_random_intensity
        allow_reverse = s.scrub_random_allow_reverse

        frame_step = duration / num_points
        angle_step = total_rotation / num_points

        current_frame = float(start_frame)
        current_angle = start_angle

        # Start keyframe
        controller.rotation_euler.z = current_angle
        controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

        cumulative_angle = 0.0
        for i in range(1, num_points):
            # Timing variation
            time_var = random.uniform(-intensity * 0.5, intensity * 0.5)
            current_frame += max(frame_step * (1.0 + time_var), 1.0)

            if i < num_points - 1:
                # Angle variation
                angle_var = random.uniform(-intensity * 0.3, intensity * 0.3)
                step = angle_step * (1.0 + angle_var)

                # Occasional brief reversal
                if allow_reverse and random.random() < 0.15 * intensity:
                    step = -abs(angle_step) * 0.15

                cumulative_angle += step
                controller.rotation_euler.z = start_angle + cumulative_angle
            else:
                # Final point must hit target exactly
                controller.rotation_euler.z = start_angle + total_rotation

            controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

        # Ensure we end at the right place and time
        final_frame = start_frame + duration
        controller.rotation_euler.z = start_angle + total_rotation
        controller.keyframe_insert(data_path="rotation_euler", frame=int(final_frame), index=2)

        # Bezier for organic feel
        ZDC_OT_BatchRender_render_all._set_fcurve_interpolation(controller, 'BEZIER', 'AUTO')
        return int(final_frame)

    @staticmethod
    def _keyframes_hold_points(controller, s, start_frame, duration, start_angle, total_rotation):
        """Create keyframes with hold/pause points at specific angles."""
        # Sort hold points by angle
        sorted_holds = sorted(s.scrub_hold_points, key=lambda hp: hp.angle)

        if len(sorted_holds) == 0:
            # Fallback to simple linear
            controller.rotation_euler.z = start_angle
            controller.keyframe_insert(data_path="rotation_euler", frame=start_frame, index=2)
            end_frame = start_frame + duration
            controller.rotation_euler.z = start_angle + total_rotation
            controller.keyframe_insert(data_path="rotation_euler", frame=end_frame, index=2)
            ZDC_OT_BatchRender_render_all._set_fcurve_interpolation(controller, 'LINEAR')
            return end_frame

        # Time per degree during motion (holds are added on top of duration)
        rotation_deg = abs(total_rotation) if total_rotation != 0 else 360.0
        time_per_deg = duration / rotation_deg if rotation_deg > 0 else 1.0
        direction = 1.0 if total_rotation >= 0 else -1.0

        current_frame = float(start_frame)
        last_angle_deg = 0.0

        # Start keyframe
        controller.rotation_euler.z = start_angle
        controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

        for hp in sorted_holds:
            hp_angle_deg = hp.angle
            if hp_angle_deg <= last_angle_deg:
                continue
            if hp_angle_deg > abs(total_rotation / radians(1)) if total_rotation != 0 else 360.0:
                continue

            # Move to this hold point
            delta_deg = hp_angle_deg - last_angle_deg
            frames_to_here = delta_deg * time_per_deg
            current_frame += frames_to_here
            hold_angle_rad = start_angle + radians(hp_angle_deg) * direction

            # Arrive at hold angle
            controller.rotation_euler.z = hold_angle_rad
            controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

            # Hold (duplicate keyframe offset by hold_duration)
            current_frame += hp.hold_duration
            controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

            last_angle_deg = hp_angle_deg

        # Continue to end
        remaining_deg = (abs(total_rotation / radians(1)) if total_rotation != 0 else 360.0) - last_angle_deg
        if remaining_deg > 0.01:
            remaining_frames = remaining_deg * time_per_deg
            current_frame += remaining_frames

        controller.rotation_euler.z = start_angle + total_rotation
        controller.keyframe_insert(data_path="rotation_euler", frame=int(current_frame), index=2)

        ZDC_OT_BatchRender_render_all._set_fcurve_interpolation(controller, 'LINEAR')
        return int(current_frame)

    # --- TURNTABLE RENDER ---

    def render_turntable(self, context, collection):
        """Render a turntable animation with variable speed (scrub) support."""
        s = context.scene.abr_settings
        scene = context.scene

        cam, controller = s.studio_camera, s.camera_controller
        if not cam or not controller:
            return
        scene.camera = cam

        # Clear any previous animation data
        if controller.animation_data:
            controller.animation_data_clear()

        # Set to the main angle for the turntable and frame the object
        controller.rotation_euler = s.main_view_angle
        scene.frame_set(1)
        context.view_layer.update()
        depsgraph = context.evaluated_depsgraph_get()
        frame_object_rig(context, controller, cam, collection, s.margin, depsgraph, s.use_orthographic, "Main")

        # Calculate rotation parameters
        dir_mul = 1.0 if s.turntable_direction == 'CCW' else -1.0
        start_angle = radians(s.turntable_start_angle) * dir_mul
        total_rotation = radians(s.turntable_rotation_amount) * dir_mul

        current_frame = 1

        # Hold start (static frames before rotation)
        if s.turntable_hold_start > 0:
            controller.rotation_euler.z = start_angle
            controller.keyframe_insert(data_path="rotation_euler", frame=current_frame, index=2)
            current_frame += s.turntable_hold_start
            controller.keyframe_insert(data_path="rotation_euler", frame=current_frame, index=2)

        rotation_start = current_frame

        # Ease in
        if s.turntable_ease_in_frames > 0 and s.turntable_ease_in_frames < s.turntable_duration:
            ease_in_end = rotation_start + s.turntable_ease_in_frames
            ease_in_frac = s.turntable_ease_in_frames / s.turntable_duration
            ease_in_angle = total_rotation * ease_in_frac

            controller.rotation_euler.z = start_angle
            controller.keyframe_insert(data_path="rotation_euler", frame=rotation_start, index=2)
            controller.rotation_euler.z = start_angle + ease_in_angle
            controller.keyframe_insert(data_path="rotation_euler", frame=ease_in_end, index=2)

            # Set ease-in keyframes to BEZIER with EASE_OUT (slow start)
            if controller.animation_data and controller.animation_data.action:
                for fcurve in controller.animation_data.action.fcurves:
                    if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                        for kp in fcurve.keyframe_points:
                            kp.interpolation = 'SINE'
                            kp.easing = 'EASE_IN'

            main_start_angle = start_angle + ease_in_angle
            main_start_frame = ease_in_end
        else:
            main_start_angle = start_angle
            main_start_frame = rotation_start

        # Ease out calculation
        if s.turntable_ease_out_frames > 0 and s.turntable_ease_out_frames < s.turntable_duration:
            ease_out_frac = s.turntable_ease_out_frames / s.turntable_duration
            ease_out_angle = total_rotation * ease_out_frac
            main_end_angle = start_angle + total_rotation - ease_out_angle
        else:
            ease_out_angle = 0
            main_end_angle = start_angle + total_rotation

        main_duration_frames = s.turntable_duration - s.turntable_ease_in_frames - s.turntable_ease_out_frames
        main_duration_frames = max(main_duration_frames, 1)
        main_rotation = main_end_angle - main_start_angle

        # Main rotation section based on scrub mode
        if s.scrub_mode == 'EASING':
            main_end_frame = main_start_frame + main_duration_frames
            self._keyframes_easing(controller, s, main_start_frame, main_end_frame,
                                   main_start_angle, main_end_angle)
            current_frame = main_end_frame
        elif s.scrub_mode == 'MULTI_SEGMENT':
            current_frame = self._keyframes_multi_segment(controller, s, main_start_frame,
                                                          main_duration_frames, main_start_angle,
                                                          main_rotation)
        elif s.scrub_mode == 'RANDOM':
            current_frame = self._keyframes_random(controller, s, main_start_frame,
                                                   main_duration_frames, main_start_angle,
                                                   main_rotation)
        elif s.scrub_mode == 'HOLD_POINTS':
            current_frame = self._keyframes_hold_points(controller, s, main_start_frame,
                                                        main_duration_frames, main_start_angle,
                                                        main_rotation)

        # Ease out
        if s.turntable_ease_out_frames > 0 and ease_out_angle != 0:
            ease_out_end = current_frame + s.turntable_ease_out_frames
            controller.rotation_euler.z = start_angle + total_rotation
            controller.keyframe_insert(data_path="rotation_euler", frame=ease_out_end, index=2)

            # Set the last keyframe pair to ease-out
            if controller.animation_data and controller.animation_data.action:
                for fcurve in controller.animation_data.action.fcurves:
                    if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                        points = fcurve.keyframe_points
                        if len(points) >= 1:
                            points[-1].interpolation = 'SINE'
                            points[-1].easing = 'EASE_OUT'
                        if len(points) >= 2:
                            points[-2].interpolation = 'SINE'
                            points[-2].easing = 'EASE_OUT'

            current_frame = ease_out_end

        # Ping-pong: reverse the rotation
        if s.turntable_ping_pong:
            pp_start = current_frame
            pp_end = pp_start + s.turntable_duration

            controller.rotation_euler.z = start_angle + total_rotation
            controller.keyframe_insert(data_path="rotation_euler", frame=pp_start, index=2)
            controller.rotation_euler.z = start_angle
            controller.keyframe_insert(data_path="rotation_euler", frame=pp_end, index=2)

            # Match main interpolation for return journey
            if controller.animation_data and controller.animation_data.action:
                for fcurve in controller.animation_data.action.fcurves:
                    if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                        points = fcurve.keyframe_points
                        if len(points) >= 2:
                            points[-1].interpolation = 'LINEAR'
                            points[-2].interpolation = 'LINEAR'

            current_frame = pp_end

        # Hold end (static frames after rotation)
        if s.turntable_hold_end > 0:
            final_angle = start_angle if s.turntable_ping_pong else start_angle + total_rotation
            controller.rotation_euler.z = final_angle
            controller.keyframe_insert(data_path="rotation_euler", frame=current_frame, index=2)
            current_frame += s.turntable_hold_end
            controller.keyframe_insert(data_path="rotation_euler", frame=current_frame, index=2)

        # Set frame range and render
        scene.frame_start = 1
        scene.frame_end = max(current_frame - 1, 1)
        self.setup_compositor(context, False, (0, 0, 0))

        safe_name = bpy.path.clean_name(collection.name)
        turntable_dir = os.path.join(bpy.path.abspath(s.output_path), safe_name, "Turntable")

        try:
            os.makedirs(turntable_dir, exist_ok=True)
        except (PermissionError, OSError) as e:
            print(f"ABR Error: Cannot create directory '{turntable_dir}': {e}")
            return

        try:
            free_space = shutil.disk_usage(turntable_dir).free
            if free_space < 50 * 1024 * 1024:
                print(f"ABR Warning: Low disk space ({free_space // (1024 * 1024)}MB free). Turntable render may fail.")
        except OSError:
            pass

        filename = f"{safe_name}{s.turntable_suffix}_####"
        scene.render.filepath = os.path.join(turntable_dir, filename)
        bpy.ops.render.render(animation=True)

        # Clean up animation data after render
        if controller.animation_data:
            controller.animation_data_clear()

    def setup_compositor(self, context, use_background, color):
        """
        Sets up the compositor nodes for background color handling.
        FIX: Multiple fallback methods to access/create the compositor node tree.
        """
        scene = context.scene

        # --- NOTE ---
        # Film must be transparent for the Alpha Over node to work correctly.
        scene.render.film_transparent = True

        # If not using a custom background and we have transparency, we can skip compositor setup
        if not use_background:
            # For transparent renders without custom background, we don't need compositor nodes
            # Just ensure use_nodes is disabled to avoid issues
            scene.use_nodes = False
            return

        # We need compositor for custom background color
        # Try multiple methods to get the node tree
        tree = None

        # Method 1: Direct access after enabling use_nodes
        try:
            scene.use_nodes = True
            if hasattr(scene, 'node_tree') and scene.node_tree is not None:
                tree = scene.node_tree
        except Exception as e:
            print(f"ABR: Method 1 failed: {e}")

        # Method 2: Access through bpy.data.scenes
        if tree is None:
            try:
                scene_data = bpy.data.scenes.get(scene.name)
                if scene_data:
                    scene_data.use_nodes = True
                    if hasattr(scene_data, 'node_tree') and scene_data.node_tree is not None:
                        tree = scene_data.node_tree
            except Exception as e:
                print(f"ABR: Method 2 failed: {e}")

        # Method 3: Force update and try again
        if tree is None:
            try:
                context.view_layer.update()
                bpy.context.view_layer.update()
                scene.use_nodes = True
                # Small delay via depsgraph update
                depsgraph = context.evaluated_depsgraph_get()
                if hasattr(scene, 'node_tree'):
                    tree = scene.node_tree
            except Exception as e:
                print(f"ABR: Method 3 failed: {e}")

        # If all methods failed, skip compositor setup but warn user
        if tree is None:
            print("ABR Warning: Could not access compositor node tree. Custom background will not be applied.")
            print("ABR Warning: The render will proceed with transparent background instead.")
            scene.use_nodes = False
            return

        # Clear existing nodes
        for node in list(tree.nodes):
            tree.nodes.remove(node)

        render_layers = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers.location = (0, 0)

        composite = tree.nodes.new(type='CompositorNodeComposite')
        composite.location = (400, 0)

        # Custom background setup
        alpha_over = tree.nodes.new(type='CompositorNodeAlphaOver')
        alpha_over.location = (200, 0)

        rgb_node = tree.nodes.new(type='CompositorNodeRGB')
        rgb_node.location = (0, -150)
        rgb_node.outputs[0].default_value = (*color, 1.0)

        tree.links.new(rgb_node.outputs[0], alpha_over.inputs[1])
        tree.links.new(render_layers.outputs['Image'], alpha_over.inputs[2])
        tree.links.new(render_layers.outputs['Alpha'], alpha_over.inputs[0])
        tree.links.new(alpha_over.outputs['Image'], composite.inputs['Image'])

    def finish(self, context, cancelled=False):
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
            self._timer = None
        if ZDC_OT_BatchRender_render_all._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(ZDC_OT_BatchRender_render_all._draw_handle, 'WINDOW')
            ZDC_OT_BatchRender_render_all._draw_handle = None

        self.restore_settings(context)

        # Restore light modifier visibility
        self.apply_light_modifier_visibility(context, hide=False)

        s = context.scene.abr_settings
        if s.target_collection:
            for child in s.target_collection.children:
                if child in self.original_collection_visibility:
                    child.hide_render = self.original_collection_visibility[child]
                    child.hide_viewport = not self.original_collection_visibility[child]

        # Final cleanup of any leftover animation data
        if s.camera_controller and s.camera_controller.animation_data:
            s.camera_controller.animation_data_clear()

        wm["abr_is_rendering"] = False
        wm["abr_cancel_requested"] = False

        if context.area:
            context.area.tag_redraw()
        report_msg = "Render cancelled." if cancelled else "Batch render finished."
        self.report({'INFO'}, report_msg)

    def apply_light_modifier_visibility(self, context, hide=True):
        """
        Applies or restores camera ray visibility for light modifier objects.

        When hide=True: Stores original visibility and hides objects from camera rays.
        When hide=False: Restores original visibility settings.

        Objects will still affect lighting (diffuse bounces, shadows, reflections)
        but won't appear directly in the render.
        """
        s = context.scene.abr_settings

        if not s.light_modifiers_collection:
            return

        if not s.light_modifiers_hide_from_camera:
            return

        for obj in s.light_modifiers_collection.all_objects:
            if hide:
                # Store original visibility and hide from camera
                self.original_light_modifier_visibility[obj.name] = obj.visible_camera
                obj.visible_camera = False
            else:
                # Restore original visibility
                if obj.name in self.original_light_modifier_visibility:
                    obj.visible_camera = self.original_light_modifier_visibility[obj.name]

    def store_settings(self, context):
        r = context.scene.render
        return {
            "camera": context.scene.camera, "res_x": r.resolution_x, "res_y": r.resolution_y,
            "res_p": r.resolution_percentage, "path": r.filepath, "ff": r.image_settings.file_format,
            "cm": r.image_settings.color_mode, "film_trans": r.film_transparent,
            "frame_start": context.scene.frame_start, "frame_end": context.scene.frame_end,
        }

    def apply_settings(self, context):
        s = context.scene.abr_settings
        r = context.scene.render
        r.resolution_x = s.resolution_x
        r.resolution_y = s.resolution_y
        r.resolution_percentage = int(s.resolution_percentage)
        r.image_settings.file_format = s.file_format
        if s.file_format == 'PNG':
            r.image_settings.color_mode = s.png_color_mode
        else:
            r.image_settings.color_mode = 'RGB'

    def restore_settings(self, context):
        r = context.scene.render
        o = self.original_settings
        context.scene.camera = o.get('camera')
        r.resolution_x = o.get('res_x')
        r.resolution_y = o.get('res_y')
        r.resolution_percentage = o.get('res_p')
        r.filepath = o.get('path')
        r.image_settings.file_format = o.get('ff')
        r.image_settings.color_mode = o.get('cm')
        r.film_transparent = o.get('film_trans')
        context.scene.frame_start = o.get('frame_start')
        context.scene.frame_end = o.get('frame_end')
        context.scene.frame_set(self.original_frame)

    def draw_progress(self, context):
        if not context.window_manager.get("abr_is_rendering", False):
            return
        progress = self.total_job_count - len(self.render_jobs)
        if self.total_job_count > 0:
            text = f"Rendering Job: {progress + 1}/{self.total_job_count} | Press ESC to Cancel"
            font_id = 0
            blf.position(font_id, 15, 30, 0)
            blf.size(font_id, 20)
            blf.draw(font_id, text)
