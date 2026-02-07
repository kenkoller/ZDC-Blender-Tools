# Auto Batch Renderer — Framing module
# Camera framing and bounding box calculation functions

import bpy
from mathutils import Vector
from math import tan, atan
from bpy_extras.object_utils import world_to_camera_view

from ..properties import ORTHOGRAPHIC_VIEWS


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
