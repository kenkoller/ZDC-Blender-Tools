# Auto Batch Renderer — Properties module
# All property groups, global data, and property update callbacks

import bpy
from math import radians, degrees

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
            bpy.ops.zdc.batchrender_update_markers()
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


# --- SCRUB UTILITY FUNCTIONS ---
# These must be defined BEFORE ZDC_PG_BatchRender_settings which references them via lambda update callbacks

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


# --- PROPERTY GROUPS ---

class ZDC_PG_BatchRender_view_settings(bpy.types.PropertyGroup):
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


class ZDC_PG_BatchRender_turntable_segment(bpy.types.PropertyGroup):
    """A single speed segment for multi-segment turntable ramp."""
    speed: bpy.props.FloatProperty(
        name="Speed",
        description="Relative speed for this segment (1.0 = normal, 0.5 = half, 2.0 = double)",
        default=1.0,
        min=0.1,
        max=5.0,
        precision=2
    )


class ZDC_PG_BatchRender_turntable_hold_point(bpy.types.PropertyGroup):
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


class ZDC_PG_BatchRender_settings(bpy.types.PropertyGroup):
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
    views: bpy.props.CollectionProperty(type=ZDC_PG_BatchRender_view_settings)

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
    scrub_segments: bpy.props.CollectionProperty(type=ZDC_PG_BatchRender_turntable_segment)
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
    scrub_hold_points: bpy.props.CollectionProperty(type=ZDC_PG_BatchRender_turntable_hold_point)
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
