# This is the standard information block required for all Blender add-ons.
# It tells Blender the name of the add-on, author, version, etc.
bl_info = {
    "name": "Auto Batch Renderer",
    "author": "Gemini & Ken",
    "version": (5, 3, 0),  # Added Scrub (variable speed turntable) feature
    "blender": (4, 2, 0),  # Minimum version - works with 5.0+
    "location": "Properties > Render Properties > Auto Batch Renderer",
    "description": "Automatically frames and renders multiple views, including turntables, for product collections.",
    "warning": "",
    "doc_url": "",
    "category": "Render",
}

# Import necessary Blender Python modules
import bpy
from mathutils import Vector
from math import tan, degrees, radians, isinf, atan
import os
import random
import blf  # For drawing progress in the viewport
from bpy_extras.object_utils import world_to_camera_view

# --- GLOBAL DATA ---

# A dictionary to store the default camera angles for different views.
# This makes it easy to manage and reuse angles throughout the script.
# Angles are stored in degrees (X, Y, Z Euler).
GLOBAL_ANGLES = {
    "Main": (71.9, 0, 15.7),
    "Front": (90, 0, 0),
    "Back": (90, 0, 180),
    "Left": (90, 0, 90),
    "Right": (90, 0, -90),
    "Top": (0, 0, 0),
    "Bottom": (180, 0, 0),
    "PropISO": (71.9, 0, 15.7),
    "Default Optional": (60, 0, 30),
    "Default Application": (60, 0, 30),
}

# List of views that should use orthographic projection when ortho mode is enabled
ORTHOGRAPHIC_VIEWS = ["Front", "Back", "Left", "Right", "Top", "Bottom"]


# --- UTILITY FUNCTIONS ---

def should_exclude_object_from_framing(obj, settings):
    """
    Determines if an object should be excluded from camera framing calculations.
    
    Exclusion criteria (any match excludes the object):
    1. Object is in the designated light modifiers collection
    2. Object has the custom property 'abr_exclude_framing' set to True
    3. Object name contains the exclusion string pattern
    
    Returns True if the object should be EXCLUDED from framing.
    """
    # Check 1: Light modifiers collection
    if settings.light_modifiers_collection:
        # Check if object is in the light modifiers collection or any of its children
        lm_coll = settings.light_modifiers_collection
        if obj.name in lm_coll.all_objects:
            return True
    
    # Check 2: Custom property on the object
    if obj.get("abr_exclude_framing", False):
        return True
    
    # Check 3: Name pattern matching (case-insensitive)
    if settings.framing_exclusion_pattern:
        patterns = [p.strip().lower() for p in settings.framing_exclusion_pattern.split(",")]
        obj_name_lower = obj.name.lower()
        for pattern in patterns:
            if pattern and pattern in obj_name_lower:
                return True
    
    return False


def get_all_world_vertices(collection, depsgraph, context, settings=None):
    """
    Gets all world-space vertices from all VISIBLE MESH objects within a given collection,
    excluding objects designated as light modifiers or other non-product geometry.
    
    This function now correctly uses the evaluated dependency graph to get the mesh state
    at the current frame, which is crucial for animations.
    
    Args:
        collection: The Blender collection to gather vertices from
        depsgraph: The evaluated dependency graph
        context: The Blender context
        settings: ABR_Settings property group (optional, for exclusion filtering)
    """
    if not collection:
        return []

    all_vertices = []
    
    # Get settings from scene if not provided
    if settings is None:
        settings = context.scene.abr_settings

    # Iterate through visible objects in the collection
    for obj in [o for o in collection.all_objects if o.visible_get(view_layer=context.view_layer)]:
        if obj.type != 'MESH':
            continue
        
        # Check if this object should be excluded from framing calculations
        if should_exclude_object_from_framing(obj, settings):
            continue

        # Get the evaluated object from the dependency graph. This is essential for
        # getting the correct mesh data for objects with modifiers or animations.
        eval_obj = obj.evaluated_get(depsgraph)
        try:
            mesh = eval_obj.to_mesh()
        except RuntimeError:
            print(f"Warning: Could not get mesh data for object '{obj.name}'. Skipping.")
            continue

        if not mesh.vertices:
            # It's good practice to clear the temporary mesh data
            eval_obj.to_mesh_clear()
            continue

        world_matrix = obj.matrix_world
        all_vertices.extend([world_matrix @ v.co for v in mesh.vertices])

        # Free the temporary mesh data to save memory
        eval_obj.to_mesh_clear()

    return all_vertices


def get_bounding_box_from_vertices(vertices):
    """
    Calculates the axis-aligned bounding box (AABB) for a given list of world-space vertices.
    """
    if not vertices:
        return None, None, Vector((0, 0, 0))

    min_coord = Vector((min(v.x for v in vertices), min(v.y for v in vertices), min(v.z for v in vertices)))
    max_coord = Vector((max(v.x for v in vertices), max(v.y for v in vertices), max(v.z for v in vertices)))
    center = (min_coord + max_coord) / 2.0

    return min_coord, max_coord, center


def calculate_camera_distance_perspective(camera, all_world_vertices, margin):
    """
    Calculates the required distance for a perspective camera to frame all provided vertices.
    """
    if not all_world_vertices:
        return 10.0

    cam_data = camera.data
    scene = bpy.context.scene
    render = scene.render

    render_width = render.resolution_x * (render.resolution_percentage / 100)
    render_height = render.resolution_y * (render.resolution_percentage / 100)
    aspect_ratio = render_width / render_height if render_height > 0 else 1.0

    sensor_fit = cam_data.sensor_fit
    if sensor_fit == 'AUTO':
        sensor_fit = 'HORIZONTAL' if aspect_ratio >= 1 else 'VERTICAL'

    if sensor_fit == 'HORIZONTAL':
        fov_x = cam_data.angle
        fov_y = 2 * atan(tan(fov_x / 2) / aspect_ratio) if aspect_ratio > 0 else 0
    else:  # VERTICAL
        fov_y = cam_data.angle
        fov_x = 2 * atan(tan(fov_y / 2) * aspect_ratio)

    if fov_x <= 0.0 or fov_y <= 0.0:
        return 10.0

    cam_matrix_inv = camera.matrix_world.inverted()
    corners_cam_space = [cam_matrix_inv @ v for v in all_world_vertices]

    if not corners_cam_space:
        return 10.0

    min_x_cam = min(v.x for v in corners_cam_space)
    max_x_cam = max(v.x for v in corners_cam_space)
    min_y_cam = min(v.y for v in corners_cam_space)
    max_y_cam = max(v.y for v in corners_cam_space)
    min_z_cam = min(v.z for v in corners_cam_space)
    max_z_cam = max(v.z for v in corners_cam_space)

    object_width_cam = max_x_cam - min_x_cam
    object_height_cam = max_y_cam - min_y_cam
    object_depth_cam = max_z_cam - min_z_cam

    dist_for_width = (object_width_cam / 2.0) / tan(fov_x / 2) if tan(fov_x / 2) > 0 else 0
    dist_for_height = (object_height_cam / 2.0) / tan(fov_y / 2) if tan(fov_y / 2) > 0 else 0

    required_distance_xy_fit = max(dist_for_width, dist_for_height)
    final_required_distance = required_distance_xy_fit + (object_depth_cam / 2.0)
    final_required_distance *= (1 + margin)

    return final_required_distance


def _check_all_vertices_in_frustum(all_world_vertices, camera, context, target_margin):
    """
    Checks if all world-space vertices are within the render camera's view frustum.
    """
    if not all_world_vertices:
        return True

    scene = context.scene
    render = scene.render
    cam_inv_matrix = camera.matrix_world.inverted()

    try:
        proj_matrix = camera.calc_matrix_camera(
            context.evaluated_depsgraph_get(),
            x=render.resolution_x,
            y=render.resolution_y,
        )
    except Exception as e:
        print(f"Error getting camera projection matrix: {e}. Assuming visible.")
        return True

    view_proj_matrix = proj_matrix @ cam_inv_matrix
    x_threshold = 1.0 - target_margin
    y_threshold = 1.0 - target_margin
    z_min_threshold = -1.0
    z_max_threshold = 1.0

    for vert_world in all_world_vertices:
        clip_coords = view_proj_matrix @ Vector((vert_world.x, vert_world.y, vert_world.z, 1.0))
        if abs(clip_coords.w) < 1e-6:
            return False

        ndc_x = clip_coords.x / clip_coords.w
        ndc_y = clip_coords.y / clip_coords.w
        ndc_z = clip_coords.z / clip_coords.w

        if not (-x_threshold <= ndc_x <= x_threshold) or \
           not (-y_threshold <= ndc_y <= y_threshold) or \
           not (z_min_threshold <= ndc_z <= z_max_threshold):
            return False

    return True


def frame_object_rig(context, controller, camera, target_collection, margin, depsgraph, force_ortho=False, view_name=""):
    """
    Frames the target_collection using the provided camera rig and applies automatic visual centering.
    This version does NOT handle scaling; scaling is applied after this function runs.
    
    Now filters out light modifier objects from framing calculations.
    """
    if not all([controller, camera, target_collection]):
        return

    settings = context.scene.abr_settings
    
    # Ensure we get vertices for the current state of the scene, excluding light modifiers
    all_verts = get_all_world_vertices(target_collection, depsgraph, context, settings)
    if not all_verts:
        print(f"Warning: No vertices found in collection '{target_collection.name}' (after exclusions). Cannot frame.")
        return

    _, _, bbox_center = get_bounding_box_from_vertices(all_verts)

    controller.location = bbox_center
    camera.rotation_euler = controller.rotation_euler

    # --- Crucial Reset ---
    # Reset camera shift before calculating framing to avoid leftover values
    # from a previous render job interfering.
    camera.data.shift_x = 0.0
    camera.data.shift_y = 0.0

    # Force a viewport update to ensure matrices are current before calculations
    context.view_layer.update()

    use_ortho = force_ortho and view_name in ORTHOGRAPHIC_VIEWS
    camera.data.type = 'ORTHO' if use_ortho else 'PERSP'

    cam_forward = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    cam_forward.normalize()

    if camera.data.type == 'PERSP':
        max_iterations = 5
        current_calc_margin = margin

        for i in range(max_iterations):
            required_distance = calculate_camera_distance_perspective(camera, all_verts, current_calc_margin)

            camera.location = controller.location - cam_forward * required_distance
            context.view_layer.update()

            if _check_all_vertices_in_frustum(all_verts, camera, context, margin):
                break
            else:
                # If framing fails, slightly increase the margin and try again.
                current_calc_margin += 0.02
                current_calc_margin = min(current_calc_margin, 0.5)
                if i == max_iterations - 1:
                    print(f"Warning: Max framing iterations reached for view '{view_name}'. Framing may be imperfect.")
    else:  # Orthographic
        bbox_min, bbox_max, _ = get_bounding_box_from_vertices(all_verts)
        bbox_diagonal_length = (bbox_max - bbox_min).length if bbox_min and bbox_max else 1.0
        # Set a reasonable starting distance for the ortho camera
        default_distance = bbox_diagonal_length * 2.5
        camera.location = controller.location - cam_forward * default_distance

        context.view_layer.update()
        cam_matrix_inv = camera.matrix_world.inverted()
        corners_cam_space = [cam_matrix_inv @ v for v in all_verts]

        if not corners_cam_space:
            camera.data.ortho_scale = 1.0 * (1 + margin)
            return

        min_x_cam = min(v.x for v in corners_cam_space)
        max_x_cam = max(v.x for v in corners_cam_space)
        min_y_cam = min(v.y for v in corners_cam_space)
        max_y_cam = max(v.y for v in corners_cam_space)

        object_width_cam = max_x_cam - min_x_cam
        object_height_cam = max_y_cam - min_y_cam

        render = context.scene.render
        aspect_ratio = render.resolution_x / render.resolution_y if render.resolution_y > 0 else 1.0

        # Corrected orthographic scale calculation for non-square aspect ratios.
        # Blender's ortho_scale is width-based. To fit height, we must account for aspect ratio.
        ortho_scale = max(object_width_cam, object_height_cam * aspect_ratio)
        camera.data.ortho_scale = ortho_scale * (1 + margin)

    # --- VISUAL CENTERING LOGIC ---
    # This part shifts the camera sensor to center the object visually.
    min_cam_x, max_cam_x = 1.0, 0.0
    min_cam_y, max_cam_y = 1.0, 0.0

    for v in all_verts:
        cam_coords = world_to_camera_view(context.scene, camera, v)
        min_cam_x = min(min_cam_x, cam_coords.x)
        max_cam_x = max(max_cam_x, cam_coords.x)
        min_cam_y = min(min_cam_y, cam_coords.y)
        max_cam_y = max(max_cam_y, cam_coords.y)

    visual_center_x = (min_cam_x + max_cam_x) / 2.0
    visual_center_y = (min_cam_y + max_cam_y) / 2.0

    center_offset_x = visual_center_x - 0.5
    center_offset_y = visual_center_y - 0.5

    camera.data.shift_x = -center_offset_x
    camera.data.shift_y = -center_offset_y

    context.view_layer.update()


# --- PROPERTIES ---

def get_base_angle_options(self, context):
    """Dynamically generate base angle options for the UI dropdown."""
    return [(name, name, "") for name in GLOBAL_ANGLES if "Default" not in name]


def update_base_angle(self, context):
    """Callback to update the view's camera angle when a preset is chosen."""
    angle_deg = GLOBAL_ANGLES.get(self.base_angle_choice)
    if angle_deg:
        self.camera_angle = [radians(a) for a in angle_deg]


# --- FIX: Timer callback for marker updates ---
# This is a proper timer function that calls the operator safely
def _deferred_update_markers():
    """Timer callback to safely update markers outside of property update context."""
    try:
        if hasattr(bpy.context, 'scene') and bpy.context.scene:
            bpy.ops.abr.update_markers()
    except Exception as e:
        print(f"ABR: Could not update markers: {e}")
    return None  # Return None to run only once


def update_marker_name(self, context):
    """Updates the timeline marker name when a property changes."""
    # Using a timer avoids potential issues with running operators inside an update callback.
    # We check if the timer is already registered to avoid duplicate calls.
    if not bpy.app.timers.is_registered(_deferred_update_markers):
        bpy.app.timers.register(_deferred_update_markers, first_interval=0.05)


def update_main_view_rotation(self, context):
    """
    Callback to update the camera angles for 'Main' and 'PropISO' views
    when the main rotation UI properties change.
    """
    settings = context.scene.abr_settings

    new_angle_rad = settings.main_view_angle
    new_angle_deg = (degrees(new_angle_rad[0]), degrees(new_angle_rad[1]), degrees(new_angle_rad[2]))
    GLOBAL_ANGLES['Main'] = new_angle_deg
    GLOBAL_ANGLES['PropISO'] = new_angle_deg

    for view in settings.views:
        if view.view_name == 'Main' or view.view_name == 'PropISO':
            view.camera_angle = new_angle_rad

    if not settings.disable_live_updates:
        # Trigger a scene update to reflect the change
        context.scene.frame_set(context.scene.frame_current)


class ABR_ViewSettings(bpy.types.PropertyGroup):
    """Property group for individual view settings."""
    view_name: bpy.props.StringProperty(name="View Name", default="", update=update_marker_name)
    enabled: bpy.props.BoolProperty(name="Enable", default=True, update=update_marker_name)
    suffix: bpy.props.StringProperty(name="File Suffix", default="")
    camera_angle: bpy.props.FloatVectorProperty(name="Angle", size=3, subtype='EULER', description="Fine-tune the camera angle")
    view_category: bpy.props.StringProperty(default="")

    use_custom_background: bpy.props.BoolProperty(name="Background", default=False)
    background_color: bpy.props.FloatVectorProperty(
        name="Color", subtype='COLOR', default=(1.0, 1.0, 1.0), min=0.0, max=1.0
    )
    animation_frame: bpy.props.IntProperty(
        name="Frame", default=1, min=1, description="Frame to render for this view", update=update_marker_name
    )

    base_angle_choice: bpy.props.EnumProperty(
        name="Base Angle", items=get_base_angle_options, update=update_base_angle,
        description="Select a base camera angle preset"
    )
    enable_fine_tune: bpy.props.BoolProperty(name="Fine-Tune", default=False, description="Enable to manually adjust angle, shift, and scale")
    fine_tune_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, subtype='TRANSLATION', description="Fine-tune the camera position offset (X, Y, Z)")
    fine_tune_scale: bpy.props.FloatProperty(name="Scale (Zoom)", default=1.0, min=0.1, max=10.0, precision=3, description="Fine-tune scale adjustment ( > 1 zooms in, < 1 zooms out)")

    show_in_ui: bpy.props.BoolProperty(name="Expand View", default=True)


class ABR_TurntableSegment(bpy.types.PropertyGroup):
    """A single speed segment for multi-segment turntable ramp."""
    speed: bpy.props.FloatProperty(
        name="Speed",
        description="Relative speed for this segment (1.0 = normal, 0.5 = half, 2.0 = double)",
        default=1.0,
        min=0.1,
        max=5.0,
        precision=2
    )


class ABR_TurntableHoldPoint(bpy.types.PropertyGroup):
    """A pause/hold point in the turntable animation."""
    angle: bpy.props.FloatProperty(
        name="Angle",
        description="Angle at which to pause (degrees)",
        default=0.0,
        min=0.0,
        max=360.0,
    )
    hold_duration: bpy.props.IntProperty(
        name="Hold",
        description="Number of frames to hold at this angle",
        default=12,
        min=1,
        max=120
    )


class ABR_Settings(bpy.types.PropertyGroup):
    """Main property group for the add-on."""
    target_collection: bpy.props.PointerProperty(
        name="Product Collection",
        type=bpy.types.Collection,
        description="Collection containing products to render. Use 'Initialize Scene' to create ABR_Products"
    )
    preview_collection: bpy.props.PointerProperty(
        name="Preview Collection",
        type=bpy.types.Collection,
        description="Collection used for live viewport preview. Use 'Initialize Scene' to create ABR_Preview"
    )
    camera_controller: bpy.props.PointerProperty(
        name="Camera Controller",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'EMPTY',
        description="Empty object that controls camera positioning. Use 'Initialize Scene' to create ABR_Camera_Controller"
    )
    studio_camera: bpy.props.PointerProperty(
        name="Studio Camera",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'CAMERA',
        description="Camera used for studio renders. Use 'Initialize Scene' to create ABR_Studio_Camera"
    )
    application_camera_object: bpy.props.PointerProperty(
        name="Application Camera",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'CAMERA',
        description="Optional camera for application-specific renders (not auto-framed)"
    )
    output_path: bpy.props.StringProperty(name="Output Directory", subtype='DIR_PATH', default='//renders\\')
    margin: bpy.props.FloatProperty(
        name="Margin", min=-0.5, max=0.95, default=0.1, subtype='PERCENTAGE',
        description="Percentage of frame space around the object. Can be negative to zoom in."
    )
    views: bpy.props.CollectionProperty(type=ABR_ViewSettings)

    main_view_angle: bpy.props.FloatVectorProperty(
        name="Main View Angle",
        subtype='EULER',
        update=update_main_view_rotation,
        default=(radians(71.9), 0, radians(15.7)),
        description="Set the precise X, Y, and Z rotation for the Main and PropISO views"
    )

    # --- LIGHT MODIFIERS / FRAMING EXCLUSION SETTINGS ---
    light_modifiers_collection: bpy.props.PointerProperty(
        name="Light Modifiers Collection",
        type=bpy.types.Collection,
        description="Objects in this collection affect lighting (shadows, bounces, negative fill) but are hidden from camera and excluded from framing. Use 'Initialize Scene' to create ABR_Light_Modifiers"
    )
    light_modifiers_hide_from_camera: bpy.props.BoolProperty(
        name="Hide from Camera",
        default=True,
        description="Hide light modifier objects from camera rays during render (they still affect lighting, shadows, and reflections)"
    )
    framing_exclusion_pattern: bpy.props.StringProperty(
        name="Exclusion Pattern",
        default="_LM,LightMod,Bounce,Flag,Scrim",
        description="Comma-separated list of name patterns. Objects containing any of these strings (case-insensitive) will be excluded from framing"
    )
    show_light_modifiers: bpy.props.BoolProperty(name="Light Modifiers", default=False)

    resolution_x: bpy.props.IntProperty(name="X", min=1, default=1920)
    resolution_y: bpy.props.IntProperty(name="Y", min=1, default=1080)
    resolution_percentage: bpy.props.EnumProperty(
        name="Scale",
        items=[('10', "10%", ""), ('25', "25%", ""), ('50', "50%", ""), ('100', "100%", "")],
        default='100'
    )
    file_format: bpy.props.EnumProperty(
        items=[('PNG', "PNG", ""), ('JPEG', "JPEG", "")], default='PNG'
    )
    png_color_mode: bpy.props.EnumProperty(
        name="PNG Alpha",
        items=[('RGBA', "With Alpha", "Save with a transparent background"),
               ('RGB', "No Alpha", "Save with an opaque background")],
        default='RGBA'
    )

    enable_turntable: bpy.props.BoolProperty(name="Enable 360 Turntable Render", default=False)
    turntable_duration: bpy.props.IntProperty(name="Duration (Frames)", default=120, min=2)
    turntable_suffix: bpy.props.StringProperty(name="File Suffix", default="_Turntable")

    # --- TURNTABLE DIRECTION & RANGE ---
    turntable_direction: bpy.props.EnumProperty(
        name="Direction",
        description="Rotation direction",
        items=[
            ('CCW', "CCW", "Counter-clockwise (default)"),
            ('CW', "CW", "Clockwise"),
        ],
        default='CCW'
    )
    turntable_start_angle: bpy.props.FloatProperty(
        name="Start Angle",
        description="Starting angle for the turntable rotation (degrees)",
        default=0.0,
        min=0.0,
        max=360.0,
    )
    turntable_rotation_amount: bpy.props.FloatProperty(
        name="Rotation",
        description="Total degrees to rotate (less than 360 for partial rotations)",
        default=360.0,
        min=1.0,
        max=360.0,
    )
    turntable_ping_pong: bpy.props.BoolProperty(
        name="Ping-Pong",
        description="Rotate forward then reverse back to start",
        default=False
    )
    turntable_hold_start: bpy.props.IntProperty(
        name="Hold Start",
        description="Static frames before rotation begins",
        default=0, min=0, max=120
    )
    turntable_hold_end: bpy.props.IntProperty(
        name="Hold End",
        description="Static frames after rotation completes",
        default=0, min=0, max=120
    )
    turntable_ease_in_frames: bpy.props.IntProperty(
        name="Ease In",
        description="Frames for acceleration at the start of rotation",
        default=0, min=0, max=60
    )
    turntable_ease_out_frames: bpy.props.IntProperty(
        name="Ease Out",
        description="Frames for deceleration at the end of rotation",
        default=0, min=0, max=60
    )

    # --- SCRUB (VARIABLE SPEED) SETTINGS ---
    show_scrub: bpy.props.BoolProperty(name="Scrub Settings", default=False)

    scrub_preset: bpy.props.EnumProperty(
        name="Preset",
        description="Quick preset configurations for turntable animation",
        items=[
            ('CONSTANT', "Constant (Default)", "Linear constant-speed rotation"),
            ('SMOOTH_SHOWCASE', "Smooth Showcase", "Professional product turntable with ease in/out"),
            ('STOP_MOTION', "Stop Motion", "Holds at 12 evenly spaced angles"),
            ('DRAMATIC_REVEAL', "Dramatic Reveal", "Slow start, accelerates, holds at key angles"),
            ('BROKEN_MICROWAVE', "Broken Microwave", "Jerky, random speed with pauses and reversals"),
        ],
        default='CONSTANT',
        update=lambda self, ctx: _apply_scrub_preset(self, ctx)
    )
    scrub_mode: bpy.props.EnumProperty(
        name="Mode",
        description="Variable speed mode for turntable animation",
        items=[
            ('EASING', "Easing", "Use Blender interpolation curves"),
            ('MULTI_SEGMENT', "Multi-Segment", "Define speed per angular segment"),
            ('RANDOM', "Random Variation", "Organic random speed variation"),
            ('HOLD_POINTS', "Hold Points", "Pause at specific angles"),
        ],
        default='EASING'
    )

    # Easing mode
    scrub_easing_type: bpy.props.EnumProperty(
        name="Interpolation",
        description="Keyframe interpolation type",
        items=[
            ('LINEAR', "Linear", "Constant speed"),
            ('BEZIER', "Bezier", "Smooth S-curve"),
            ('SINE', "Sine", "Sinusoidal easing"),
            ('QUAD', "Quadratic", "Quadratic easing"),
            ('CUBIC', "Cubic", "Cubic easing"),
            ('QUART', "Quartic", "Quartic easing"),
            ('QUINT', "Quintic", "Quintic easing"),
            ('EXPO', "Exponential", "Exponential easing"),
            ('CIRC', "Circular", "Circular easing"),
            ('BACK', "Back", "Overshoot easing"),
            ('BOUNCE', "Bounce", "Bouncing easing"),
            ('ELASTIC', "Elastic", "Elastic/spring easing"),
        ],
        default='LINEAR'
    )
    scrub_easing_direction: bpy.props.EnumProperty(
        name="Easing",
        description="Direction of the easing curve",
        items=[
            ('EASE_IN', "Ease In", "Start slow, end fast"),
            ('EASE_OUT', "Ease Out", "Start fast, end slow"),
            ('EASE_IN_OUT', "Ease In/Out", "Start and end slow"),
        ],
        default='EASE_IN_OUT'
    )

    # Multi-segment mode
    scrub_segment_count: bpy.props.IntProperty(
        name="Segments",
        description="Number of speed segments (each covers an equal angular portion)",
        default=4, min=2, max=12,
        update=lambda self, ctx: _update_segment_count(self, ctx)
    )
    scrub_segments: bpy.props.CollectionProperty(type=ABR_TurntableSegment)
    scrub_active_segment: bpy.props.IntProperty(default=0)

    # Random variation mode
    scrub_random_seed: bpy.props.IntProperty(
        name="Seed",
        description="Random seed for reproducible variation",
        default=0, min=0
    )
    scrub_random_intensity: bpy.props.FloatProperty(
        name="Intensity",
        description="Amount of speed variation (0 = none, 1 = maximum)",
        default=0.3, min=0.0, max=1.0, subtype='FACTOR'
    )
    scrub_random_points: bpy.props.IntProperty(
        name="Variation Points",
        description="Number of speed variation keyframes",
        default=8, min=4, max=24
    )
    scrub_random_allow_reverse: bpy.props.BoolProperty(
        name="Allow Reversals",
        description="Allow brief reverse motion segments for a broken/jerky effect",
        default=False
    )

    # Hold points mode
    scrub_hold_points: bpy.props.CollectionProperty(type=ABR_TurntableHoldPoint)
    scrub_active_hold_point: bpy.props.IntProperty(default=0)

    def get_total_turntable_frames(self):
        """Calculate total frames including holds, ease, and ping-pong."""
        base = self.turntable_duration
        total = base
        total += self.turntable_hold_start
        total += self.turntable_hold_end
        if self.turntable_ping_pong:
            total += base
        if self.scrub_mode == 'HOLD_POINTS':
            for hp in self.scrub_hold_points:
                total += hp.hold_duration
        return total

    turntable_total_frames: bpy.props.IntProperty(
        name="Total Frames",
        description="Calculated total animation length",
        get=get_total_turntable_frames
    )

    disable_live_updates: bpy.props.BoolProperty(name="Disable Live Updates", default=False, description="Disable live camera updates in the viewport when changing frames. Useful for very heavy scenes.")
    use_orthographic: bpy.props.BoolProperty(name="Use Orthographic for Standard Views", default=False)

    show_setup: bpy.props.BoolProperty(name="Setup", default=True)
    show_cameras_framing: bpy.props.BoolProperty(name="Cameras & Framing", default=True)
    show_turntable: bpy.props.BoolProperty(name="360 Turntable", default=True)
    show_output_settings: bpy.props.BoolProperty(name="Output Settings", default=True)
    show_studio_standard: bpy.props.BoolProperty(name="Standard Studio Renders", default=True)
    show_studio_optional: bpy.props.BoolProperty(name="Optional Studio Renders", default=True)
    show_application: bpy.props.BoolProperty(name="Application Renders", default=True)


# --- UI PANEL ---

class ABR_PT_MainPanel(bpy.types.Panel):
    bl_label = "Auto Batch Renderer"
    bl_idname = "RENDER_PT_auto_batch_renderer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.abr_settings

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


# --- SCRUB UTILITY FUNCTIONS ---

def _apply_scrub_preset(self, context):
    """Apply preset configuration when preset enum changes."""
    s = self
    preset = s.scrub_preset

    if preset == 'CONSTANT':
        s.scrub_mode = 'EASING'
        s.scrub_easing_type = 'LINEAR'
        s.turntable_ease_in_frames = 0
        s.turntable_ease_out_frames = 0
        s.turntable_hold_start = 0
        s.turntable_hold_end = 0
        s.turntable_ping_pong = False

    elif preset == 'SMOOTH_SHOWCASE':
        s.scrub_mode = 'EASING'
        s.scrub_easing_type = 'BEZIER'
        s.scrub_easing_direction = 'EASE_IN_OUT'
        s.turntable_ease_in_frames = 0
        s.turntable_ease_out_frames = 0

    elif preset == 'STOP_MOTION':
        s.scrub_mode = 'HOLD_POINTS'
        s.scrub_hold_points.clear()
        for i in range(12):
            hp = s.scrub_hold_points.add()
            hp.angle = i * 30.0
            hp.hold_duration = 4

    elif preset == 'DRAMATIC_REVEAL':
        s.scrub_mode = 'MULTI_SEGMENT'
        s.scrub_segments.clear()
        for speed in [0.3, 0.5, 1.0, 1.5, 2.0, 1.5, 1.0, 0.5, 0.3]:
            seg = s.scrub_segments.add()
            seg.speed = speed
        s.scrub_segment_count = len(s.scrub_segments)

    elif preset == 'BROKEN_MICROWAVE':
        s.scrub_mode = 'RANDOM'
        s.scrub_random_intensity = 0.85
        s.scrub_random_seed = 42
        s.scrub_random_points = 16
        s.scrub_random_allow_reverse = True


def _update_segment_count(self, context):
    """Sync segment collection with the count property."""
    s = self
    current = len(s.scrub_segments)
    target = s.scrub_segment_count

    if target > current:
        for _ in range(target - current):
            seg = s.scrub_segments.add()
            seg.speed = 1.0
    elif target < current:
        for _ in range(current - target):
            s.scrub_segments.remove(len(s.scrub_segments) - 1)


# --- OPERATORS ---

class ABR_OT_ToggleExcludeFraming(bpy.types.Operator):
    """Toggle the abr_exclude_framing custom property on selected objects"""
    bl_idname = "abr.toggle_exclude_framing"
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


class ABR_OT_UpdateMarkers(bpy.types.Operator):
    bl_idname = "abr.update_markers"
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


class ABR_OT_AddView(bpy.types.Operator):
    bl_idname = "abr.add_view"
    bl_label = "Add View"
    bl_options = {'REGISTER', 'UNDO'}

    category: bpy.props.StringProperty()

    def execute(self, context):
        settings = context.scene.abr_settings
        new_view = settings.views.add()

        if self.category == 'STUDIO_OPTION':
            num_existing = len([v for v in settings.views if v.view_category == 'STUDIO_OPTION'])
            new_view.view_name = f"Optional {chr(65 + num_existing - 1)}"
            new_view.suffix = f"_Optional{chr(65 + num_existing - 1)}"
            new_view.view_category = 'STUDIO_OPTION'
            new_view.base_angle_choice = 'Default Optional'
            angle_deg = GLOBAL_ANGLES.get("Default Optional")
            if angle_deg:
                new_view.camera_angle = [radians(a) for a in angle_deg]

        elif self.category == 'APPLICATION':
            num_existing = len([v for v in settings.views if v.view_category == 'APPLICATION'])
            new_view.view_name = f"Application {chr(65 + num_existing - 1)}"
            new_view.suffix = f"_Application{chr(65 + num_existing - 1)}"
            new_view.view_category = 'APPLICATION'
            angle_deg = GLOBAL_ANGLES.get("Default Application")
            if angle_deg:
                new_view.camera_angle = [radians(a) for a in angle_deg]

        bpy.ops.abr.update_markers()
        return {'FINISHED'}


class ABR_OT_RemoveView(bpy.types.Operator):
    bl_idname = "abr.remove_view"
    bl_label = "Remove View"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.abr_settings
        settings.views.remove(self.index)
        bpy.ops.abr.update_markers()
        return {'FINISHED'}


class ABR_OT_ClearMarkers(bpy.types.Operator):
    bl_idname = "abr.clear_markers"
    bl_label = "Clear Markers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        for m in reversed(scene.timeline_markers):
            scene.timeline_markers.remove(m)
        self.report({'INFO'}, "Cleared all timeline markers.")
        return {'FINISHED'}


class ABR_OT_AddSegment(bpy.types.Operator):
    """Add a speed segment to the turntable animation"""
    bl_idname = "abr.add_segment"
    bl_label = "Add Segment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.abr_settings
        if len(s.scrub_segments) < 12:
            seg = s.scrub_segments.add()
            seg.speed = 1.0
            s.scrub_segment_count = len(s.scrub_segments)
        return {'FINISHED'}


class ABR_OT_RemoveSegment(bpy.types.Operator):
    """Remove a speed segment from the turntable animation"""
    bl_idname = "abr.remove_segment"
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


class ABR_OT_AddHoldPoint(bpy.types.Operator):
    """Add a hold point to the turntable animation"""
    bl_idname = "abr.add_hold_point"
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


class ABR_OT_RemoveHoldPoint(bpy.types.Operator):
    """Remove a hold point from the turntable animation"""
    bl_idname = "abr.remove_hold_point"
    bl_label = "Remove Hold Point"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        s = context.scene.abr_settings
        s.scrub_hold_points.remove(self.index)
        if s.scrub_active_hold_point >= len(s.scrub_hold_points):
            s.scrub_active_hold_point = max(0, len(s.scrub_hold_points) - 1)
        return {'FINISHED'}


class ABR_OT_InitializeScene(bpy.types.Operator):
    """Initialize the scene with all required ABR objects and collections"""
    bl_idname = "abr.initialize_scene"
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
        if self.create_controller:
            col.label(text="• ABR_Camera_Controller (Empty)", icon='EMPTY_DATA')
        if self.create_studio_camera:
            col.label(text="• ABR_Studio_Camera (Camera)", icon='CAMERA_DATA')
        if self.create_target_collection:
            col.label(text="• ABR_Products (Collection)", icon='OUTLINER_COLLECTION')
        if self.create_preview_collection:
            col.label(text="• ABR_Preview (Collection)", icon='OUTLINER_COLLECTION')
        if self.create_light_modifiers_collection:
            col.label(text="• ABR_Light_Modifiers (Collection)", icon='OUTLINER_COLLECTION')

        layout.separator()
        layout.label(text="Existing assignments will not be changed.")

    def execute(self, context):
        settings = context.scene.abr_settings
        scene = context.scene
        created_items = []

        # Create Camera Controller (Empty)
        if self.create_controller:
            controller = bpy.data.objects.new("ABR_Camera_Controller", None)
            controller.empty_display_type = 'PLAIN_AXES'
            controller.empty_display_size = 0.5
            scene.collection.objects.link(controller)
            settings.camera_controller = controller
            created_items.append("Camera Controller")

        # Create Studio Camera
        if self.create_studio_camera:
            cam_data = bpy.data.cameras.new("ABR_Studio_Camera")
            studio_camera = bpy.data.objects.new("ABR_Studio_Camera", cam_data)
            scene.collection.objects.link(studio_camera)
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


class ABR_OT_CancelRender(bpy.types.Operator):
    bl_idname = "abr.cancel_render"
    bl_label = "Cancel Batch Render"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.window_manager["abr_cancel_requested"] = True
        self.report({'INFO'}, "Cancellation requested. Finishing current job...")
        return {'FINISHED'}


class ABR_OT_RenderAll(bpy.types.Operator):
    bl_idname = "abr.render_all"
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
        ABR_OT_RenderAll._draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_progress, (context,), 'WINDOW', 'POST_PIXEL')

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
        os.makedirs(output_dir, exist_ok=True)
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
        ABR_OT_RenderAll._set_fcurve_interpolation(controller, 'LINEAR')
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
        ABR_OT_RenderAll._set_fcurve_interpolation(controller, 'BEZIER', 'AUTO')
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
            ABR_OT_RenderAll._set_fcurve_interpolation(controller, 'LINEAR')
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

        ABR_OT_RenderAll._set_fcurve_interpolation(controller, 'LINEAR')
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
        os.makedirs(turntable_dir, exist_ok=True)
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
        if ABR_OT_RenderAll._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(ABR_OT_RenderAll._draw_handle, 'WINDOW')
            ABR_OT_RenderAll._draw_handle = None

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
        progress = self.total_job_count - len(self.render_jobs)
        if self.total_job_count > 0:
            text = f"Rendering Job: {progress + 1}/{self.total_job_count} | Press ESC to Cancel"
            font_id = 0
            blf.position(font_id, 15, 30, 0)
            blf.size(font_id, 20)
            blf.draw(font_id, text)


# --- HANDLERS & REGISTRATION ---

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
