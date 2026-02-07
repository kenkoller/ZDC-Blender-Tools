# Cabinet Presets - Save/Load cabinet configurations
# Allows users to save favorite configurations and share them

import bpy
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


# Default presets directory
def get_presets_dir() -> Path:
    """Get the presets directory path."""
    addon_dir = Path(__file__).parent.parent
    presets_dir = addon_dir / "presets"
    presets_dir.mkdir(exist_ok=True)
    return presets_dir


# Properties to save/load
PRESET_PROPERTIES = [
    # Cabinet type
    "cabinet_type",
    # Dimensions
    "width", "height", "depth",
    "panel_thickness", "shelf_thickness",
    # Front type
    "front_type",
    # Door options
    "door_style", "double_doors", "glass_insert", "glass_frame_width",
    # Drawer options
    "drawer_count",
    # Handle options
    "handle_style", "handle_offset_x", "handle_offset_z",
    # Interior options
    "has_back", "has_shelves", "shelf_count",
    # Bevel options
    "bevel_width", "bevel_segments",
    # Toe kick options
    "has_toe_kick", "toe_kick_height", "toe_kick_depth",
    # Lazy susan options
    "has_lazy_susan", "lazy_susan_count", "lazy_susan_style", "lazy_susan_diameter",
    # Corner cabinet options
    "corner_type", "blind_width",
    # Hardware options
    "hinge_style", "drawer_slide_style",
    # Face frame options
    "has_face_frame", "face_frame_width",
    # Appliance options
    "appliance_type", "appliance_opening_height", "has_trim_frame",
    # Sink base options
    "has_plumbing_cutout",
    # Open shelving options
    "has_side_panels",
    # Insert options
    "has_trash_pullout", "double_trash_bins",
    "has_spice_rack", "spice_rack_tiers",
    # Shelf pin options
    "has_adjustable_shelves", "shelf_pin_rows",
    # Material presets (names only)
    "carcass_preset", "front_preset", "handle_preset",
]


def settings_to_dict(settings) -> Dict:
    """Convert settings property group to dictionary.

    Args:
        settings: CABINET_PG_Settings property group

    Returns:
        Dictionary of setting values
    """
    data = {}
    for prop_name in PRESET_PROPERTIES:
        if hasattr(settings, prop_name):
            value = getattr(settings, prop_name)
            # Convert Blender types to JSON-serializable
            if isinstance(value, float):
                data[prop_name] = round(value, 6)
            else:
                data[prop_name] = value
    return data


def dict_to_settings(data: Dict, settings):
    """Apply dictionary values to settings property group.

    Args:
        data: Dictionary of setting values
        settings: CABINET_PG_Settings property group
    """
    for prop_name, value in data.items():
        if hasattr(settings, prop_name):
            try:
                setattr(settings, prop_name, value)
            except (TypeError, ValueError) as e:
                print(f"Warning: Could not set {prop_name}: {e}")


def save_preset(name: str, settings, filepath: Optional[str] = None) -> str:
    """Save current settings as a preset.

    Args:
        name: Name for the preset
        settings: CABINET_PG_Settings property group
        filepath: Optional custom filepath, otherwise uses default presets dir

    Returns:
        Path to saved preset file
    """
    data = {
        "name": name,
        "version": "1.0",
        "settings": settings_to_dict(settings)
    }

    if filepath is None:
        # Sanitize name for filename
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
        filepath = str(get_presets_dir() / f"{safe_name}.json")

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return filepath


def load_preset(filepath: str, settings) -> bool:
    """Load a preset from file.

    Args:
        filepath: Path to preset file
        settings: CABINET_PG_Settings property group

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        if "settings" not in data:
            print(f"Invalid preset file: {filepath}")
            return False

        dict_to_settings(data["settings"], settings)
        return True

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading preset: {e}")
        return False


def list_presets() -> List[Dict]:
    """List all available presets.

    Returns:
        List of preset info dictionaries
    """
    presets = []
    presets_dir = get_presets_dir()

    for preset_file in presets_dir.glob("*.json"):
        try:
            with open(preset_file, 'r') as f:
                data = json.load(f)
                presets.append({
                    "name": data.get("name", preset_file.stem),
                    "filepath": str(preset_file),
                    "cabinet_type": data.get("settings", {}).get("cabinet_type", "Unknown")
                })
        except (json.JSONDecodeError, KeyError):
            continue

    return sorted(presets, key=lambda x: x["name"])


def delete_preset(filepath: str) -> bool:
    """Delete a preset file.

    Args:
        filepath: Path to preset file

    Returns:
        True if successful
    """
    try:
        os.remove(filepath)
        return True
    except OSError:
        return False


# ============ BUILT-IN PRESETS ============

BUILTIN_PRESETS = {
    "Standard Base 600": {
        "cabinet_type": "BASE",
        "width": 0.6,
        "height": 0.72,
        "depth": 0.55,
        "panel_thickness": 0.018,
        "front_type": "DOORS",
        "door_style": "SHAKER",
        "double_doors": False,
        "has_shelves": True,
        "shelf_count": 1,
        "has_toe_kick": True,
        "toe_kick_height": 0.1,
    },
    "Standard Base 900 Double Door": {
        "cabinet_type": "BASE",
        "width": 0.9,
        "height": 0.72,
        "depth": 0.55,
        "panel_thickness": 0.018,
        "front_type": "DOORS",
        "door_style": "SHAKER",
        "double_doors": True,
        "has_shelves": True,
        "shelf_count": 1,
        "has_toe_kick": True,
    },
    "Drawer Base 3-Drawer": {
        "cabinet_type": "DRAWER_BASE",
        "width": 0.6,
        "height": 0.72,
        "depth": 0.55,
        "front_type": "DRAWERS",
        "drawer_count": 3,
        "has_shelves": False,
        "has_toe_kick": True,
    },
    "Drawer Base 4-Drawer": {
        "cabinet_type": "DRAWER_BASE",
        "width": 0.6,
        "height": 0.72,
        "depth": 0.55,
        "front_type": "DRAWERS",
        "drawer_count": 4,
        "has_shelves": False,
        "has_toe_kick": True,
    },
    "Wall Cabinet 600": {
        "cabinet_type": "WALL",
        "width": 0.6,
        "height": 0.72,
        "depth": 0.35,
        "panel_thickness": 0.018,
        "front_type": "DOORS",
        "door_style": "SHAKER",
        "double_doors": False,
        "has_shelves": True,
        "shelf_count": 2,
        "has_toe_kick": False,
    },
    "Wall Cabinet Glass Door": {
        "cabinet_type": "WALL",
        "width": 0.6,
        "height": 0.72,
        "depth": 0.35,
        "front_type": "DOORS",
        "door_style": "SHAKER",
        "glass_insert": True,
        "glass_frame_width": 0.04,
        "has_shelves": True,
        "shelf_count": 2,
    },
    "Tall Pantry": {
        "cabinet_type": "TALL",
        "width": 0.6,
        "height": 2.1,
        "depth": 0.55,
        "front_type": "DOORS",
        "door_style": "SHAKER",
        "double_doors": False,
        "has_shelves": True,
        "shelf_count": 5,
        "has_toe_kick": True,
    },
    "Sink Base 900": {
        "cabinet_type": "SINK_BASE",
        "width": 0.9,
        "height": 0.72,
        "depth": 0.6,
        "front_type": "DOORS",
        "double_doors": True,
        "has_shelves": False,
        "has_plumbing_cutout": True,
        "has_toe_kick": True,
    },
    "Lazy Susan Corner": {
        "cabinet_type": "BLIND_CORNER",
        "width": 0.9,
        "height": 0.72,
        "depth": 0.6,
        "corner_type": "LEFT",
        "blind_width": 0.15,
        "has_lazy_susan": True,
        "lazy_susan_count": 2,
        "lazy_susan_style": "FULL_CIRCLE",
        "lazy_susan_diameter": 0.0,
        "has_toe_kick": True,
    },
    "Diagonal Corner": {
        "cabinet_type": "DIAGONAL_CORNER",
        "width": 0.6,
        "height": 0.72,
        "depth": 0.6,
        "has_lazy_susan": True,
        "lazy_susan_count": 2,
        "has_toe_kick": True,
    },
    "Microwave Cabinet": {
        "cabinet_type": "APPLIANCE",
        "width": 0.6,
        "height": 0.72,
        "depth": 0.4,
        "appliance_type": "MICROWAVE",
        "appliance_opening_height": 0.4,
        "has_trim_frame": True,
    },
    "Pull-out Pantry": {
        "cabinet_type": "PULLOUT_PANTRY",
        "width": 0.15,
        "height": 2.0,
        "depth": 0.55,
        "shelf_count": 6,
        "has_toe_kick": True,
    },
    "Open Shelving Unit": {
        "cabinet_type": "OPEN_SHELVING",
        "width": 0.8,
        "height": 1.2,
        "depth": 0.3,
        "has_shelves": True,
        "shelf_count": 4,
        "has_side_panels": True,
        "has_back": True,
    },
    "Trash Pull-out Base": {
        "cabinet_type": "BASE",
        "width": 0.45,
        "height": 0.72,
        "depth": 0.55,
        "front_type": "DOORS",
        "has_shelves": False,
        "has_trash_pullout": True,
        "double_trash_bins": True,
        "has_toe_kick": True,
    },
}


def apply_builtin_preset(preset_name: str, settings) -> bool:
    """Apply a built-in preset.

    Args:
        preset_name: Name of built-in preset
        settings: CABINET_PG_Settings property group

    Returns:
        True if preset found and applied
    """
    if preset_name not in BUILTIN_PRESETS:
        return False

    dict_to_settings(BUILTIN_PRESETS[preset_name], settings)
    return True


# ============ BLENDER OPERATORS ============

class CABINET_OT_SavePreset(bpy.types.Operator):
    """Save current settings as a preset"""
    bl_idname = "cabinet.save_preset"
    bl_label = "Save Preset"
    bl_description = "Save current cabinet settings as a preset"
    bl_options = {'REGISTER'}

    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Name for the preset",
        default="My Cabinet Preset"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")

    def execute(self, context):
        settings = context.scene.cabinet_settings
        filepath = save_preset(self.preset_name, settings)
        self.report({'INFO'}, f"Saved preset: {self.preset_name}")
        return {'FINISHED'}


class CABINET_OT_LoadPreset(bpy.types.Operator):
    """Load a preset"""
    bl_idname = "cabinet.load_preset"
    bl_label = "Load Preset"
    bl_description = "Load cabinet settings from a preset"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH'
    )

    def invoke(self, context, event):
        presets_dir = get_presets_dir()
        self.filepath = str(presets_dir)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        settings = context.scene.cabinet_settings
        if load_preset(self.filepath, settings):
            self.report({'INFO'}, f"Loaded preset from {Path(self.filepath).name}")
        else:
            self.report({'ERROR'}, "Failed to load preset")
        return {'FINISHED'}


class CABINET_OT_ApplyBuiltinPreset(bpy.types.Operator):
    """Apply a built-in preset"""
    bl_idname = "cabinet.apply_builtin_preset"
    bl_label = "Apply Built-in Preset"
    bl_description = "Apply a built-in cabinet preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset: bpy.props.EnumProperty(
        name="Preset",
        items=[(name, name, f"Apply {name} preset") for name in BUILTIN_PRESETS.keys()]
    )

    def execute(self, context):
        settings = context.scene.cabinet_settings
        if apply_builtin_preset(self.preset, settings):
            self.report({'INFO'}, f"Applied preset: {self.preset}")
        else:
            self.report({'ERROR'}, "Preset not found")
        return {'FINISHED'}


class CABINET_OT_DeletePreset(bpy.types.Operator):
    """Delete a preset"""
    bl_idname = "cabinet.delete_preset"
    bl_label = "Delete Preset"
    bl_description = "Delete a saved preset"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if delete_preset(self.filepath):
            self.report({'INFO'}, "Preset deleted")
        else:
            self.report({'ERROR'}, "Failed to delete preset")
        return {'FINISHED'}


# ============ UI PANEL FOR PRESETS ============

class CABINET_PT_PresetsPanel(bpy.types.Panel):
    """Presets subpanel"""
    bl_label = "Presets"
    bl_idname = "CABINET_PT_presets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet"
    bl_parent_id = "CABINET_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Built-in presets
        layout.label(text="Built-in Presets:", icon='PRESET')
        col = layout.column(align=True)
        op = col.operator("cabinet.apply_builtin_preset", text="Standard Base 600")
        op.preset = "Standard Base 600"
        op = col.operator("cabinet.apply_builtin_preset", text="Drawer Base 3-Drawer")
        op.preset = "Drawer Base 3-Drawer"
        op = col.operator("cabinet.apply_builtin_preset", text="Wall Cabinet 600")
        op.preset = "Wall Cabinet 600"
        op = col.operator("cabinet.apply_builtin_preset", text="Tall Pantry")
        op.preset = "Tall Pantry"
        op = col.operator("cabinet.apply_builtin_preset", text="Lazy Susan Corner")
        op.preset = "Lazy Susan Corner"

        layout.separator()

        # User presets
        layout.label(text="User Presets:", icon='USER')
        row = layout.row(align=True)
        row.operator("cabinet.save_preset", icon='FILE_NEW')
        row.operator("cabinet.load_preset", icon='FILE_FOLDER')

        # List saved presets
        presets = list_presets()
        if presets:
            box = layout.box()
            for preset in presets[:5]:  # Show first 5
                row = box.row()
                op = row.operator("cabinet.load_preset", text=preset["name"], icon='IMPORT')
                op.filepath = preset["filepath"]


# Registration
classes = (
    CABINET_OT_SavePreset,
    CABINET_OT_LoadPreset,
    CABINET_OT_ApplyBuiltinPreset,
    CABINET_OT_DeletePreset,
    CABINET_PT_PresetsPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
