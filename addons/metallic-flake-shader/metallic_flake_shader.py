"""
Metallic Flake Plastic Shader v4.0.0
====================================
A comprehensive procedural shader for realistic metallic sparkle plastic materials.

Features:
- Three independent sparkle layers (Primary/Secondary/Tertiary)
- View-based flake visibility - flakes sparkle when oriented toward camera, BSDF handles lighting
- Per-layer seed control for unique patterns
- Orientation randomness - control flake angle variation
- Sparkle sharpness - control tightness of sparkle points
- Clearcoat, SSS, and anisotropic grain effects
- Full mold texture support (normal, displacement, gloss, AO)

v4.0.0 Changes:
- MAJOR: View-based sparkle visibility (flakes visible when oriented toward camera)
- MAJOR: Per-cell consistent flake normals (each flake has its own orientation)
- NEW: Sparkle Sharpness parameter - controls reflection falloff tightness
- NEW: Orientation Randomness parameter - replaces Surface Alignment (inverted logic)
- NEW: Per-layer Seed parameter - generate unique patterns per layer
- REMOVED: Shadow Visibility, Highlight Boost, Depth Variation, Depth Blur (physics handles this now)
- IMPROVED: Sparkles naturally cluster near specular highlights
- IMPROVED: Rotating view/light changes which flakes are visible

Created for Blender 4.0+
Author: Claude (Anthropic) for Ken @ Ziti Design & Creative

INSTALLATION:
1. Edit > Preferences > Add-ons > Install
2. Select this .py file
3. Enable "Material: Metallic Flake Plastic v4.0.0"

USAGE:
1. Select an object
2. Go to Material Properties panel
3. Click "Create Metallic Flake Plastic Material"
4. Adjust settings in the expandable panels below
"""

# bl_info is defined in __init__.py (the authoritative source for addon metadata)

import bpy
import math
import json
import os
from bpy.props import (
    FloatProperty,
    FloatVectorProperty,
    PointerProperty,
    BoolProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
    CollectionProperty,
)
from bpy.types import PropertyGroup, Panel, Operator


# =============================================================================
# PRESET SYSTEM
# =============================================================================

def get_user_presets_path():
    """Get path to user presets JSON file."""
    config_dir = bpy.utils.user_resource('CONFIG')
    return os.path.join(config_dir, 'metallic_flake_presets.json')


def load_user_presets():
    """Load user presets from JSON file."""
    path = get_user_presets_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_user_presets(presets):
    """Save user presets to JSON file."""
    path = get_user_presets_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(presets, f, indent=2)


# Built-in presets with real-world reference values
# Each preset is designed to match specific real-world materials
BUILTIN_PRESETS = {
    "default": {
        "name": "Default (Gray Metallic)",
        "description": "Neutral gray metallic flake plastic - good starting point",
        "values": {
            # Base
            "base_color": (0.498, 0.490, 0.502, 1.0),
            "base_roughness": 0.35,
            "ior": 1.46,
            # Surface
            "surface_grain_enable": True,
            "surface_grain_amount": 0.03,
            "surface_grain_scale": 120.0,
            "aniso_enable": False,
            # SSS
            "sss_enable": True,
            "sss_weight": 0.08,
            "sss_radius": 0.5,
            "sss_scale": 1.0,
            # Clearcoat
            "clearcoat_enable": True,
            "clearcoat_weight": 0.25,
            "clearcoat_roughness": 0.08,
            # Primary
            "primary_enable": True,
            "primary_density": 800.0,
            "primary_size": 0.10,
            "primary_size_var": 0.35,
            "primary_intensity": 1.0,
            # Secondary
            "secondary_enable": True,
            "secondary_density": 500.0,
            "secondary_size": 0.08,
            "secondary_size_var": 0.4,
            "secondary_intensity": 0.8,
            # Tertiary
            "tertiary_enable": True,
            "tertiary_density": 80.0,
            "tertiary_size": 0.12,
            "tertiary_size_var": 0.5,
            "tertiary_intensity": 1.8,
            # Sparkle color
            "sparkle_color": (0.9, 0.9, 0.9, 1.0),
            "sparkle_hue_var": 0.02,
            "sparkle_sat_var": 0.1,
            "sparkle_val_var": 0.15,
            "sparkle_base_influence": 0.1,
            "sparkle_metallic": 0.97,
            "fresnel_shift": 0.03,
            "fresnel_direction": 0.55,
            # Response
            "sparkle_roughness": 0.06,
            "sparkle_sharpness": 5.0,
            "orientation_randomness": 0.20,
            "overdrive": 1.0,
            "emission_strength": 0.15,
        }
    },
    "silver_automotive": {
        "name": "Silver Automotive",
        "description": "Classic silver car paint with fine metallic flakes - like Honda Lunar Silver",
        "values": {
            "base_color": (0.55, 0.55, 0.58, 1.0),
            "base_roughness": 0.30,
            "ior": 1.5,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.02,
            "surface_grain_scale": 150.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.05,
            "sss_radius": 0.3,
            "sss_scale": 1.0,
            "clearcoat_enable": True,
            "clearcoat_weight": 0.6,
            "clearcoat_roughness": 0.03,
            "primary_enable": True,
            "primary_density": 1000.0,
            "primary_size": 0.08,
            "primary_size_var": 0.3,
            "primary_intensity": 1.2,
            "secondary_enable": True,
            "secondary_density": 600.0,
            "secondary_size": 0.06,
            "secondary_size_var": 0.35,
            "secondary_intensity": 0.9,
            "tertiary_enable": True,
            "tertiary_density": 100.0,
            "tertiary_size": 0.10,
            "tertiary_size_var": 0.4,
            "tertiary_intensity": 2.0,
            "sparkle_color": (0.95, 0.95, 0.98, 1.0),
            "sparkle_hue_var": 0.01,
            "sparkle_sat_var": 0.05,
            "sparkle_val_var": 0.1,
            "sparkle_base_influence": 0.05,
            "sparkle_metallic": 0.98,
            "fresnel_shift": 0.02,
            "fresnel_direction": 0.5,
            "sparkle_roughness": 0.04,
            "sparkle_sharpness": 6.0,
            "orientation_randomness": 0.15,
            "overdrive": 1.0,
            "emission_strength": 0.1,
        }
    },
    "gold_metallic": {
        "name": "Gold Metallic",
        "description": "Warm gold metallic with brass-toned flakes",
        "values": {
            "base_color": (0.45, 0.35, 0.20, 1.0),
            "base_roughness": 0.32,
            "ior": 1.48,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.025,
            "surface_grain_scale": 130.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.06,
            "sss_radius": 0.4,
            "sss_scale": 1.0,
            "clearcoat_enable": True,
            "clearcoat_weight": 0.4,
            "clearcoat_roughness": 0.05,
            "primary_enable": True,
            "primary_density": 850.0,
            "primary_size": 0.09,
            "primary_size_var": 0.35,
            "primary_intensity": 1.1,
            "secondary_enable": True,
            "secondary_density": 520.0,
            "secondary_size": 0.07,
            "secondary_size_var": 0.4,
            "secondary_intensity": 0.85,
            "tertiary_enable": True,
            "tertiary_density": 90.0,
            "tertiary_size": 0.11,
            "tertiary_size_var": 0.5,
            "tertiary_intensity": 1.9,
            "sparkle_color": (1.0, 0.85, 0.55, 1.0),
            "sparkle_hue_var": 0.03,
            "sparkle_sat_var": 0.15,
            "sparkle_val_var": 0.12,
            "sparkle_base_influence": 0.15,
            "sparkle_metallic": 0.95,
            "fresnel_shift": 0.04,
            "fresnel_direction": 0.65,
            "sparkle_roughness": 0.07,
            "sparkle_sharpness": 5.0,
            "orientation_randomness": 0.22,
            "overdrive": 1.0,
            "emission_strength": 0.12,
        }
    },
    "midnight_blue": {
        "name": "Midnight Blue Pearl",
        "description": "Deep blue with subtle pearl effect - like BMW Monaco Blue",
        "values": {
            "base_color": (0.08, 0.12, 0.25, 1.0),
            "base_roughness": 0.28,
            "ior": 1.52,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.02,
            "surface_grain_scale": 140.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.04,
            "sss_radius": 0.3,
            "sss_scale": 1.0,
            "clearcoat_enable": True,
            "clearcoat_weight": 0.7,
            "clearcoat_roughness": 0.02,
            "primary_enable": True,
            "primary_density": 900.0,
            "primary_size": 0.07,
            "primary_size_var": 0.3,
            "primary_intensity": 0.9,
            "secondary_enable": True,
            "secondary_density": 550.0,
            "secondary_size": 0.05,
            "secondary_size_var": 0.35,
            "secondary_intensity": 0.7,
            "tertiary_enable": True,
            "tertiary_density": 70.0,
            "tertiary_size": 0.09,
            "tertiary_size_var": 0.45,
            "tertiary_intensity": 1.5,
            "sparkle_color": (0.7, 0.8, 1.0, 1.0),
            "sparkle_hue_var": 0.04,
            "sparkle_sat_var": 0.2,
            "sparkle_val_var": 0.15,
            "sparkle_base_influence": 0.2,
            "sparkle_metallic": 0.92,
            "fresnel_shift": 0.05,
            "fresnel_direction": 0.4,
            "sparkle_roughness": 0.05,
            "sparkle_sharpness": 7.0,
            "orientation_randomness": 0.18,
            "overdrive": 1.0,
            "emission_strength": 0.08,
        }
    },
    "candy_red": {
        "name": "Candy Apple Red",
        "description": "Vibrant red with dense sparkle - like classic hot rod candy paint",
        "values": {
            "base_color": (0.5, 0.05, 0.05, 1.0),
            "base_roughness": 0.25,
            "ior": 1.55,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.015,
            "surface_grain_scale": 160.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.12,
            "sss_radius": 0.8,
            "sss_scale": 1.0,
            "clearcoat_enable": True,
            "clearcoat_weight": 0.8,
            "clearcoat_roughness": 0.02,
            "primary_enable": True,
            "primary_density": 950.0,
            "primary_size": 0.08,
            "primary_size_var": 0.32,
            "primary_intensity": 1.0,
            "secondary_enable": True,
            "secondary_density": 580.0,
            "secondary_size": 0.06,
            "secondary_size_var": 0.38,
            "secondary_intensity": 0.75,
            "tertiary_enable": True,
            "tertiary_density": 85.0,
            "tertiary_size": 0.10,
            "tertiary_size_var": 0.48,
            "tertiary_intensity": 1.7,
            "sparkle_color": (1.0, 0.7, 0.7, 1.0),
            "sparkle_hue_var": 0.02,
            "sparkle_sat_var": 0.1,
            "sparkle_val_var": 0.12,
            "sparkle_base_influence": 0.25,
            "sparkle_metallic": 0.90,
            "fresnel_shift": 0.03,
            "fresnel_direction": 0.6,
            "sparkle_roughness": 0.04,
            "sparkle_sharpness": 6.5,
            "orientation_randomness": 0.16,
            "overdrive": 1.1,
            "emission_strength": 0.15,
        }
    },
    "gunmetal": {
        "name": "Gunmetal Gray",
        "description": "Dark metallic gray with subtle blue undertone - industrial look",
        "values": {
            "base_color": (0.18, 0.18, 0.20, 1.0),
            "base_roughness": 0.38,
            "ior": 1.45,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.035,
            "surface_grain_scale": 110.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.03,
            "sss_radius": 0.25,
            "sss_scale": 1.0,
            "clearcoat_enable": True,
            "clearcoat_weight": 0.3,
            "clearcoat_roughness": 0.1,
            "primary_enable": True,
            "primary_density": 750.0,
            "primary_size": 0.11,
            "primary_size_var": 0.4,
            "primary_intensity": 0.85,
            "secondary_enable": True,
            "secondary_density": 450.0,
            "secondary_size": 0.09,
            "secondary_size_var": 0.45,
            "secondary_intensity": 0.65,
            "tertiary_enable": True,
            "tertiary_density": 60.0,
            "tertiary_size": 0.14,
            "tertiary_size_var": 0.55,
            "tertiary_intensity": 1.4,
            "sparkle_color": (0.75, 0.78, 0.85, 1.0),
            "sparkle_hue_var": 0.015,
            "sparkle_sat_var": 0.08,
            "sparkle_val_var": 0.18,
            "sparkle_base_influence": 0.15,
            "sparkle_metallic": 0.95,
            "fresnel_shift": 0.025,
            "fresnel_direction": 0.45,
            "sparkle_roughness": 0.08,
            "sparkle_sharpness": 4.5,
            "orientation_randomness": 0.25,
            "overdrive": 1.0,
            "emission_strength": 0.08,
        }
    },
    "champagne": {
        "name": "Champagne",
        "description": "Elegant warm beige with fine sparkle - like luxury car interiors",
        "values": {
            "base_color": (0.55, 0.48, 0.40, 1.0),
            "base_roughness": 0.33,
            "ior": 1.47,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.025,
            "surface_grain_scale": 125.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.07,
            "sss_radius": 0.45,
            "sss_scale": 1.0,
            "clearcoat_enable": True,
            "clearcoat_weight": 0.35,
            "clearcoat_roughness": 0.06,
            "primary_enable": True,
            "primary_density": 820.0,
            "primary_size": 0.09,
            "primary_size_var": 0.36,
            "primary_intensity": 1.0,
            "secondary_enable": True,
            "secondary_density": 510.0,
            "secondary_size": 0.07,
            "secondary_size_var": 0.42,
            "secondary_intensity": 0.78,
            "tertiary_enable": True,
            "tertiary_density": 75.0,
            "tertiary_size": 0.11,
            "tertiary_size_var": 0.52,
            "tertiary_intensity": 1.6,
            "sparkle_color": (1.0, 0.95, 0.85, 1.0),
            "sparkle_hue_var": 0.025,
            "sparkle_sat_var": 0.12,
            "sparkle_val_var": 0.14,
            "sparkle_base_influence": 0.12,
            "sparkle_metallic": 0.94,
            "fresnel_shift": 0.035,
            "fresnel_direction": 0.58,
            "sparkle_roughness": 0.065,
            "sparkle_sharpness": 5.5,
            "orientation_randomness": 0.21,
            "overdrive": 1.0,
            "emission_strength": 0.1,
        }
    },
    "plastic_toy": {
        "name": "Plastic Toy (Coarse)",
        "description": "Chunky visible flakes like cheap plastic toys - larger, sparser sparkles",
        "values": {
            "base_color": (0.4, 0.4, 0.45, 1.0),
            "base_roughness": 0.45,
            "ior": 1.45,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.05,
            "surface_grain_scale": 80.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.15,
            "sss_radius": 1.2,
            "sss_scale": 1.0,
            "clearcoat_enable": False,
            "clearcoat_weight": 0.0,
            "clearcoat_roughness": 0.15,
            "primary_enable": True,
            "primary_density": 300.0,
            "primary_size": 0.25,
            "primary_size_var": 0.5,
            "primary_intensity": 1.3,
            "secondary_enable": True,
            "secondary_density": 180.0,
            "secondary_size": 0.20,
            "secondary_size_var": 0.55,
            "secondary_intensity": 1.0,
            "tertiary_enable": True,
            "tertiary_density": 40.0,
            "tertiary_size": 0.30,
            "tertiary_size_var": 0.6,
            "tertiary_intensity": 2.2,
            "sparkle_color": (0.85, 0.85, 0.9, 1.0),
            "sparkle_hue_var": 0.04,
            "sparkle_sat_var": 0.15,
            "sparkle_val_var": 0.2,
            "sparkle_base_influence": 0.2,
            "sparkle_metallic": 0.85,
            "fresnel_shift": 0.04,
            "fresnel_direction": 0.5,
            "sparkle_roughness": 0.12,
            "sparkle_sharpness": 3.5,
            "orientation_randomness": 0.4,
            "overdrive": 1.0,
            "emission_strength": 0.2,
        }
    },
}


def get_preset_items(self, context):
    """Generate enum items for preset dropdown."""
    items = [
        ('NONE', "-- Select Preset --", "Choose a preset to apply", 0),
    ]

    # Add built-in presets
    idx = 1
    for key, preset in BUILTIN_PRESETS.items():
        items.append((f"BUILTIN_{key}", preset["name"], preset["description"], idx))
        idx += 1

    # Add separator
    items.append(('SEP', "─── User Presets ───", "", idx))
    idx += 1

    # Add user presets
    user_presets = load_user_presets()
    for key, preset in user_presets.items():
        desc = preset.get("description", "User-created preset")
        items.append((f"USER_{key}", preset.get("name", key), desc, idx))
        idx += 1

    return items


# Properties to exclude from presets (non-material properties)
PRESET_EXCLUDE_PROPS = {'mold_normal_map', 'mold_displacement_map', 'mold_gloss_map', 'mold_ao_map'}


# =============================================================================
# PROPERTY GROUP
# =============================================================================

def update_shader(self, context):
    """Called when any property changes - updates the shader nodes."""
    if context.object and context.object.active_material:
        mat = context.object.active_material
        update_shader_from_properties(mat)


def update_texture(self, context):
    """Called when a texture property changes."""
    if context.object and context.object.active_material:
        mat = context.object.active_material
        update_textures_from_properties(mat)


class MetallicFlakePlasticProperties(PropertyGroup):
    """Property group containing all shader parameters."""
    
    # =========================================================================
    # BASE MATERIAL
    # =========================================================================
    base_color: FloatVectorProperty(
        name="Base Color",
        description="The base plastic color visible between sparkles",
        subtype='COLOR',
        size=4,
        min=0.0, max=1.0,
        default=(0.498, 0.490, 0.502, 1.0),  # #7F7D80
        update=update_shader
    )
    base_roughness: FloatProperty(
        name="Roughness",
        description="Base plastic roughness. Lower = glossier",
        min=0.0, max=1.0,
        default=0.35,
        update=update_shader
    )
    ior: FloatProperty(
        name="IOR",
        description="Index of Refraction. Typical plastic: 1.4-1.6",
        min=1.0, max=3.0,
        default=1.46,
        update=update_shader
    )
    
    # =========================================================================
    # SURFACE EFFECTS
    # =========================================================================
    # --- Surface Grain ---
    surface_grain_enable: BoolProperty(
        name="Surface Grain",
        description="Enable micro-roughness variation",
        default=True,
        update=update_shader
    )
    surface_grain_amount: FloatProperty(
        name="Amount",
        description="Strength of surface grain roughness variation",
        min=0.0, max=1.0,
        default=0.03,
        update=update_shader
    )
    surface_grain_scale: FloatProperty(
        name="Scale",
        description="Scale of surface grain pattern",
        min=0.0, max=2000.0,
        default=120.0,
        update=update_shader
    )
    
    # --- Anisotropic Grain ---
    aniso_enable: BoolProperty(
        name="Anisotropic Grain",
        description="Enable directional grain lines from manufacturing",
        default=False,
        update=update_shader
    )
    aniso_intensity: FloatProperty(
        name="Intensity",
        description="Strength of anisotropic grain",
        min=0.0, max=2.0,
        default=0.12,
        update=update_shader
    )
    aniso_scale: FloatProperty(
        name="Scale",
        description="Scale of grain pattern",
        min=0.0, max=2000.0,
        default=250.0,
        update=update_shader
    )
    aniso_ratio: FloatProperty(
        name="Ratio",
        description="Grain elongation. Lower = more stretched",
        min=0.01, max=1.0,
        default=0.1,
        update=update_shader
    )
    aniso_angle: FloatProperty(
        name="Angle",
        description="Grain direction in degrees",
        min=-180.0, max=180.0,
        default=0.0,
        update=update_shader
    )
    aniso_normal_strength: FloatProperty(
        name="Normal Strength",
        description="How much grain affects surface normals",
        min=0.0, max=2.0,
        default=0.25,
        update=update_shader
    )
    aniso_roughness: FloatProperty(
        name="Roughness Effect",
        description="Anisotropic roughness stretching",
        min=0.0, max=1.0,
        default=0.4,
        update=update_shader
    )
    
    # --- Subsurface ---
    # Real-world reference: Metallic flake plastic has reduced SSS due to flakes blocking light.
    # Typical plastic SSS radius: 1-5mm for light colors, 0.2-1mm for dark/pigmented.
    # Weight should be low (0.05-0.2) since metallic flakes obstruct light penetration.
    sss_enable: BoolProperty(
        name="Subsurface Scattering",
        description="Enable light scattering inside plastic. Metallic flakes reduce SSS effect",
        default=True,
        update=update_shader
    )
    sss_weight: FloatProperty(
        name="Weight",
        description="SSS intensity. Low values (0.05-0.15) typical for metallic flake plastic since flakes block light. Higher for translucent base colors",
        min=0.0, max=1.0,
        default=0.08,
        update=update_shader
    )
    sss_radius: FloatProperty(
        name="Radius (mm)",
        description="Mean free path in millimeters. Typical values: 0.3-1.0mm dark plastic, 1-3mm light plastic, 3-8mm translucent",
        min=0.0, max=50.0,
        soft_min=0.1, soft_max=5.0,
        default=0.5,
        update=update_shader
    )
    sss_scale: FloatProperty(
        name="Scale",
        description="Multiplier for SSS radius. Use to adjust for scene scale (1.0 = millimeters)",
        min=0.0, max=10.0,
        default=1.0,
        update=update_shader
    )
    
    # --- Clearcoat ---
    clearcoat_enable: BoolProperty(
        name="Clearcoat",
        description="Enable clear layer on top",
        default=True,
        update=update_shader
    )
    clearcoat_weight: FloatProperty(
        name="Weight",
        description="Clearcoat intensity",
        min=0.0, max=1.0,
        default=0.25,
        update=update_shader
    )
    clearcoat_roughness: FloatProperty(
        name="Roughness",
        description="Clearcoat roughness",
        min=0.0, max=1.0,
        default=0.08,
        update=update_shader
    )
    
    # =========================================================================
    # PRIMARY SPARKLES
    # =========================================================================
    primary_enable: BoolProperty(
        name="Enable Primary Sparkles",
        description="Enable the primary (densest) sparkle layer - forms the base sparkle field",
        default=True,
        update=update_shader
    )
    primary_seed: IntProperty(
        name="Seed",
        description="Random seed for this layer's flake pattern",
        min=0, max=1000,
        default=0,
        update=update_shader
    )
    primary_density: FloatProperty(
        name="Density",
        description="Sparkle pattern density. Higher = more, finer sparkles",
        min=0.0, max=2000.0,
        soft_min=50.0, soft_max=1200.0,
        default=800.0,
        update=update_shader
    )
    primary_size: FloatProperty(
        name="Size",
        description="Individual sparkle size threshold",
        min=0.0, max=2.0,
        soft_min=0.05, soft_max=0.5,
        default=0.10,
        update=update_shader
    )
    primary_size_var: FloatProperty(
        name="Size Variation",
        description="Randomizes sparkle sizes for natural appearance",
        min=0.0, max=1.0,
        default=0.35,
        update=update_shader
    )
    primary_intensity: FloatProperty(
        name="Intensity",
        description="Layer brightness multiplier",
        min=0.0, max=10.0,
        soft_min=0.0, soft_max=3.0,
        default=1.0,
        update=update_shader
    )
    
    # =========================================================================
    # SECONDARY SPARKLES
    # =========================================================================
    secondary_enable: BoolProperty(
        name="Enable Secondary Sparkles",
        description="Enable the secondary sparkle layer - fills gaps in primary field",
        default=True,
        update=update_shader
    )
    secondary_seed: IntProperty(
        name="Seed",
        description="Random seed for this layer's flake pattern",
        min=0, max=1000,
        default=100,
        update=update_shader
    )
    secondary_density: FloatProperty(
        name="Density",
        description="Sparkle pattern density",
        min=0.0, max=2000.0,
        soft_min=50.0, soft_max=800.0,
        default=500.0,
        update=update_shader
    )
    secondary_size: FloatProperty(
        name="Size",
        description="Individual sparkle size threshold",
        min=0.0, max=2.0,
        soft_min=0.05, soft_max=0.4,
        default=0.08,
        update=update_shader
    )
    secondary_size_var: FloatProperty(
        name="Size Variation",
        description="Randomizes sparkle sizes",
        min=0.0, max=1.0,
        default=0.4,
        update=update_shader
    )
    secondary_intensity: FloatProperty(
        name="Intensity",
        description="Layer brightness multiplier",
        min=0.0, max=10.0,
        soft_min=0.0, soft_max=3.0,
        default=0.8,
        update=update_shader
    )
    
    # =========================================================================
    # TERTIARY SPARKLES (Hero Sparkles)
    # =========================================================================
    tertiary_enable: BoolProperty(
        name="Enable Tertiary Sparkles",
        description="Enable the tertiary (sparse hero) sparkle layer - bright accent sparkles",
        default=True,
        update=update_shader
    )
    tertiary_seed: IntProperty(
        name="Seed",
        description="Random seed for this layer's flake pattern",
        min=0, max=1000,
        default=200,
        update=update_shader
    )
    tertiary_density: FloatProperty(
        name="Density",
        description="Sparkle pattern density - keep low for hero effect",
        min=0.0, max=2000.0,
        soft_min=20.0, soft_max=200.0,
        default=80.0,
        update=update_shader
    )
    tertiary_size: FloatProperty(
        name="Size",
        description="Individual sparkle size threshold",
        min=0.0, max=2.0,
        soft_min=0.05, soft_max=0.5,
        default=0.12,
        update=update_shader
    )
    tertiary_size_var: FloatProperty(
        name="Size Variation",
        description="Randomizes sparkle sizes",
        min=0.0, max=1.0,
        default=0.5,
        update=update_shader
    )
    tertiary_intensity: FloatProperty(
        name="Intensity",
        description="Layer brightness multiplier - typically higher than other layers",
        min=0.0, max=10.0,
        soft_min=0.0, soft_max=5.0,
        default=1.8,
        update=update_shader
    )
    
    # =========================================================================
    # SPARKLE COLOR
    # =========================================================================
    sparkle_color: FloatVectorProperty(
        name="Sparkle Color",
        description="Base color of all sparkles",
        subtype='COLOR',
        size=4,
        min=0.0, max=1.0,
        default=(0.9, 0.9, 0.9, 1.0),
        update=update_shader
    )
    sparkle_hue_var: FloatProperty(
        name="Hue Variation",
        description="Per-sparkle random hue shift",
        min=0.0, max=0.5,
        default=0.02,
        update=update_shader
    )
    sparkle_sat_var: FloatProperty(
        name="Saturation Variation",
        description="Per-sparkle saturation variation",
        min=0.0, max=1.0,
        default=0.1,
        update=update_shader
    )
    sparkle_val_var: FloatProperty(
        name="Value Variation",
        description="Per-sparkle brightness variation",
        min=0.0, max=1.0,
        default=0.15,
        update=update_shader
    )
    sparkle_base_influence: FloatProperty(
        name="Base Color Influence",
        description="Blend base plastic color into sparkles",
        min=0.0, max=1.0,
        default=0.1,
        update=update_shader
    )
    sparkle_metallic: FloatProperty(
        name="Metallic",
        description="Metallic property of sparkles",
        min=0.0, max=1.0,
        default=0.97,
        update=update_shader
    )
    fresnel_shift: FloatProperty(
        name="Fresnel Color Shift",
        description="Hue shift at grazing angles",
        min=0.0, max=1.0,
        default=0.03,
        update=update_shader
    )
    fresnel_direction: FloatProperty(
        name="Fresnel Direction",
        description="Shift direction. <0.5 = cool, >0.5 = warm",
        min=0.0, max=1.0,
        default=0.55,
        update=update_shader
    )
    
    # =========================================================================
    # SPARKLE RESPONSE & APPEARANCE
    # =========================================================================
    sparkle_roughness: FloatProperty(
        name="Sparkle Roughness",
        description="Reflection sharpness of flakes. Lower = sharper mirror-like reflections",
        min=0.0, max=1.0,
        soft_min=0.02, soft_max=0.3,
        default=0.06,
        update=update_shader
    )
    sparkle_sharpness: FloatProperty(
        name="Sparkle Sharpness",
        description="How tight/sharp the sparkle points are. Higher = tighter pinpoints, lower = softer glow",
        min=1.0, max=50.0,
        soft_min=4.0, soft_max=25.0,
        default=5.0,
        update=update_shader
    )
    orientation_randomness: FloatProperty(
        name="Orientation Randomness",
        description="How much flake normals deviate from surface. 0 = flat/uniform metallic, 1 = random angles/maximum sparkle variation",
        min=0.0, max=1.0,
        soft_min=0.1, soft_max=0.6,
        default=0.20,
        update=update_shader
    )
    overdrive: FloatProperty(
        name="Overdrive",
        description="Global intensity multiplier. Values >1 push sparkles beyond realistic limits",
        min=0.0, max=10.0,
        soft_min=0.5, soft_max=3.0,
        default=1.0,
        update=update_shader
    )
    emission_strength: FloatProperty(
        name="Emission",
        description="Direct light emission from brightest sparkles (for bloom effects)",
        min=0.0, max=20.0,
        soft_min=0.0, soft_max=2.0,
        default=0.15,
        update=update_shader
    )
    global_density_multiplier: FloatProperty(
        name="Global Density",
        description="Multiplier for all sparkle layer densities. Higher = more/smaller cells, lower = fewer/larger cells",
        min=0.01, max=10.0,
        soft_min=0.1, soft_max=5.0,
        default=1.0,
        update=update_shader
    )
    global_size_multiplier: FloatProperty(
        name="Global Size",
        description="Multiplier for all sparkle layer sizes. Higher = larger flakes, lower = smaller flakes",
        min=0.01, max=10.0,
        soft_min=0.1, soft_max=5.0,
        default=1.0,
        update=update_shader
    )

    # =========================================================================
    # MOLD TEXTURE
    # =========================================================================
    mold_enable: BoolProperty(
        name="Enable Mold Texture",
        description="Enable mold texture maps",
        default=False,
        update=update_shader
    )
    mold_intensity: FloatProperty(
        name="Intensity",
        description="Master mold texture intensity",
        min=0.0, max=2.0,
        default=1.0,
        update=update_shader
    )
    mold_scale: FloatProperty(
        name="Scale",
        description="Texture tiling scale",
        min=0.0, max=50.0,
        default=1.0,
        update=update_shader
    )
    mold_normal_map: PointerProperty(
        name="Normal Map",
        type=bpy.types.Image,
        update=update_texture
    )
    mold_normal_strength: FloatProperty(
        name="Normal Strength",
        min=0.0, max=5.0,
        default=1.0,
        update=update_shader
    )
    mold_normal_invert: BoolProperty(
        name="Invert",
        default=False,
        update=update_shader
    )
    mold_displacement_map: PointerProperty(
        name="Displacement Map",
        type=bpy.types.Image,
        update=update_texture
    )
    mold_bump_strength: FloatProperty(
        name="Bump Strength",
        min=0.0, max=5.0,
        default=0.5,
        update=update_shader
    )
    mold_bump_invert: BoolProperty(
        name="Invert",
        default=False,
        update=update_shader
    )
    mold_gloss_map: PointerProperty(
        name="Gloss Map",
        type=bpy.types.Image,
        update=update_texture
    )
    mold_roughness_strength: FloatProperty(
        name="Roughness Strength",
        min=0.0, max=5.0,
        default=1.0,
        update=update_shader
    )
    mold_ao_map: PointerProperty(
        name="AO Map",
        type=bpy.types.Image,
        update=update_texture
    )
    mold_ao_strength: FloatProperty(
        name="AO Strength",
        min=0.0, max=5.0,
        default=1.0,
        update=update_shader
    )
    
    # =========================================================================
    # ADVANCED
    # =========================================================================
    overall_effect: FloatProperty(
        name="Overall Effect",
        description="Global mix. 0 = pure plastic, 1 = full sparkle effect",
        min=0.0, max=1.0,
        default=1.0,
        update=update_shader
    )


# =============================================================================
# UI PANELS
# =============================================================================

class MATERIAL_PT_mfp_main(Panel):
    bl_label = "Metallic Flake Plastic v4.0.0"
    bl_idname = "MATERIAL_PT_mfp_main"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_material
    
    def draw(self, context):
        layout = self.layout
        mat = context.object.active_material
        
        if not mat:
            layout.label(text="No active material")
            return
        
        has_shader = mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
        
        if not has_shader:
            layout.operator("material.create_metallic_flake_plastic", icon='MATERIAL')
        else:
            row = layout.row()
            row.label(text="Shader Active", icon='CHECKMARK')
            row.operator("material.create_metallic_flake_plastic", text="Rebuild", icon='FILE_REFRESH')


class MATERIAL_PT_mfp_presets(Panel):
    bl_label = "Presets"
    bl_idname = "MATERIAL_PT_mfp_presets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout

        # Built-in presets section
        box = layout.box()
        box.label(text="Built-in Presets", icon='PRESET')

        col = box.column(align=True)
        for key, preset in BUILTIN_PRESETS.items():
            row = col.row(align=True)
            op = row.operator("material.mfp_apply_preset", text=preset["name"])
            op.preset_id = f"BUILTIN_{key}"

        # User presets section
        box = layout.box()
        row = box.row()
        row.label(text="User Presets", icon='USER')
        row.operator("material.mfp_save_preset", text="", icon='ADD')

        user_presets = load_user_presets()
        if user_presets:
            col = box.column(align=True)
            for key, preset in user_presets.items():
                row = col.row(align=True)
                op = row.operator("material.mfp_apply_preset", text=preset.get("name", key))
                op.preset_id = f"USER_{key}"
                del_op = row.operator("material.mfp_delete_preset", text="", icon='X')
                del_op.preset_key = key
        else:
            box.label(text="No user presets saved", icon='INFO')

        # Info about preset location
        layout.separator()
        col = layout.column()
        col.scale_y = 0.7
        col.label(text="User presets saved to:", icon='FILE_FOLDER')
        col.label(text=get_user_presets_path())


class MATERIAL_PT_mfp_base(Panel):
    bl_label = "Base Material"
    bl_idname = "MATERIAL_PT_mfp_base"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        
        layout.prop(props, "base_color")
        
        row = layout.row(align=True)
        row.prop(props, "base_roughness")
        row.prop(props, "ior")


class MATERIAL_PT_mfp_surface(Panel):
    bl_label = "Surface Effects"
    bl_idname = "MATERIAL_PT_mfp_surface"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        
        # Surface Grain
        box = layout.box()
        row = box.row()
        row.prop(props, "surface_grain_enable", text="Surface Grain")
        if props.surface_grain_enable:
            col = box.column(align=True)
            col.prop(props, "surface_grain_amount", text="Amount")
            col.prop(props, "surface_grain_scale", text="Scale")
        
        # Anisotropic Grain
        box = layout.box()
        row = box.row()
        row.prop(props, "aniso_enable", text="Anisotropic Grain")
        if props.aniso_enable:
            col = box.column(align=True)
            col.prop(props, "aniso_intensity", text="Intensity")
            col.prop(props, "aniso_scale", text="Scale")
            col.prop(props, "aniso_ratio", text="Ratio")
            col.prop(props, "aniso_angle", text="Angle")
            col.separator()
            col.prop(props, "aniso_normal_strength", text="Normal Strength")
            col.prop(props, "aniso_roughness", text="Roughness Effect")
        
        # Subsurface
        box = layout.box()
        row = box.row()
        row.prop(props, "sss_enable", text="Subsurface Scattering")
        if props.sss_enable:
            col = box.column(align=True)
            col.prop(props, "sss_weight", text="Weight")
            col.prop(props, "sss_radius", text="Radius")
            col.prop(props, "sss_scale", text="Scale")
        
        # Clearcoat
        box = layout.box()
        row = box.row()
        row.prop(props, "clearcoat_enable", text="Clearcoat")
        if props.clearcoat_enable:
            col = box.column(align=True)
            col.prop(props, "clearcoat_weight", text="Weight")
            col.prop(props, "clearcoat_roughness", text="Roughness")


class MATERIAL_PT_mfp_primary(Panel):
    bl_label = "Primary Sparkles"
    bl_idname = "MATERIAL_PT_mfp_primary"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw_header(self, context):
        props = context.object.active_material.metallic_flake_plastic
        self.layout.prop(props, "primary_enable", text="")
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        layout.enabled = props.primary_enable

        col = layout.column(align=True)
        col.prop(props, "primary_seed", text="Seed")
        col.prop(props, "primary_density", text="Density")

        row = col.row(align=True)
        row.prop(props, "primary_size", text="Size")
        row.prop(props, "primary_size_var", text="Variation")

        col.separator()
        col.prop(props, "primary_intensity", text="Intensity")


class MATERIAL_PT_mfp_secondary(Panel):
    bl_label = "Secondary Sparkles"
    bl_idname = "MATERIAL_PT_mfp_secondary"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw_header(self, context):
        props = context.object.active_material.metallic_flake_plastic
        self.layout.prop(props, "secondary_enable", text="")
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        layout.enabled = props.secondary_enable

        col = layout.column(align=True)
        col.prop(props, "secondary_seed", text="Seed")
        col.prop(props, "secondary_density", text="Density")

        row = col.row(align=True)
        row.prop(props, "secondary_size", text="Size")
        row.prop(props, "secondary_size_var", text="Variation")

        col.separator()
        col.prop(props, "secondary_intensity", text="Intensity")


class MATERIAL_PT_mfp_tertiary(Panel):
    bl_label = "Tertiary Sparkles"
    bl_idname = "MATERIAL_PT_mfp_tertiary"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw_header(self, context):
        props = context.object.active_material.metallic_flake_plastic
        self.layout.prop(props, "tertiary_enable", text="")
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        layout.enabled = props.tertiary_enable

        col = layout.column(align=True)
        col.prop(props, "tertiary_seed", text="Seed")
        col.prop(props, "tertiary_density", text="Density")

        row = col.row(align=True)
        row.prop(props, "tertiary_size", text="Size")
        row.prop(props, "tertiary_size_var", text="Variation")

        col.separator()
        col.prop(props, "tertiary_intensity", text="Intensity")


class MATERIAL_PT_mfp_sparkle_color(Panel):
    bl_label = "Sparkle Color"
    bl_idname = "MATERIAL_PT_mfp_sparkle_color"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        
        layout.prop(props, "sparkle_color")
        
        col = layout.column(align=True)
        col.prop(props, "sparkle_hue_var", text="Hue Variation")
        col.prop(props, "sparkle_sat_var", text="Saturation Variation")
        col.prop(props, "sparkle_val_var", text="Value Variation")
        
        layout.separator()
        
        row = layout.row(align=True)
        row.prop(props, "sparkle_base_influence", text="Base Color Influence")
        row.prop(props, "sparkle_metallic", text="Metallic")
        
        layout.separator()
        layout.label(text="Fresnel Effect:")
        row = layout.row(align=True)
        row.prop(props, "fresnel_shift", text="Shift")
        row.prop(props, "fresnel_direction", text="Direction")


class MATERIAL_PT_mfp_lighting(Panel):
    bl_label = "Sparkle Response"
    bl_idname = "MATERIAL_PT_mfp_lighting"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic

        # Reflection behavior
        layout.label(text="Reflection Behavior:")
        col = layout.column(align=True)
        col.prop(props, "sparkle_sharpness", text="Sharpness")
        col.prop(props, "orientation_randomness", text="Orientation Randomness")

        layout.separator()

        # Appearance
        layout.label(text="Appearance:")
        col = layout.column(align=True)
        col.prop(props, "sparkle_roughness", text="Roughness")

        layout.separator()

        # Intensity controls
        layout.label(text="Intensity:")
        col = layout.column(align=True)
        col.prop(props, "overdrive", text="Overdrive")
        col.prop(props, "emission_strength", text="Emission")

        layout.separator()

        # Global scale controls
        layout.label(text="Global Scale:")
        col = layout.column(align=True)
        col.prop(props, "global_density_multiplier", text="Density Multiplier")
        col.prop(props, "global_size_multiplier", text="Size Multiplier")


class MATERIAL_PT_mfp_mold(Panel):
    bl_label = "Mold Texture"
    bl_idname = "MATERIAL_PT_mfp_mold"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw_header(self, context):
        props = context.object.active_material.metallic_flake_plastic
        self.layout.prop(props, "mold_enable", text="")
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        layout.enabled = props.mold_enable
        
        row = layout.row(align=True)
        row.prop(props, "mold_intensity", text="Intensity")
        row.prop(props, "mold_scale", text="Scale")
        
        layout.separator()
        
        # Normal
        box = layout.box()
        box.label(text="Normal Map:")
        box.template_ID(props, "mold_normal_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "mold_normal_strength", text="Strength")
        row.prop(props, "mold_normal_invert", text="Invert")
        
        # Displacement
        box = layout.box()
        box.label(text="Displacement:")
        box.template_ID(props, "mold_displacement_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "mold_bump_strength", text="Strength")
        row.prop(props, "mold_bump_invert", text="Invert")
        
        # Gloss
        box = layout.box()
        box.label(text="Gloss Map:")
        box.template_ID(props, "mold_gloss_map", open="image.open")
        box.prop(props, "mold_roughness_strength", text="Strength")
        
        # AO
        box = layout.box()
        box.label(text="AO Map:")
        box.template_ID(props, "mold_ao_map", open="image.open")
        box.prop(props, "mold_ao_strength", text="Strength")


class MATERIAL_PT_mfp_advanced(Panel):
    bl_label = "Advanced"
    bl_idname = "MATERIAL_PT_mfp_advanced"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_mfp_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Metallic Flake Plastic v4.0.0" in mat.node_tree.nodes
    
    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.metallic_flake_plastic
        
        layout.prop(props, "overall_effect")


# =============================================================================
# OPERATORS
# =============================================================================

class MATERIAL_OT_create_metallic_flake_plastic(Operator):
    bl_idname = "material.create_metallic_flake_plastic"
    bl_label = "Create Metallic Flake Plastic Material"
    bl_description = "Create or rebuild the metallic flake plastic shader"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not context.object:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        mat = context.object.active_material
        if not mat:
            mat = bpy.data.materials.new(name="Metallic Flake Plastic")
            context.object.data.materials.append(mat)
            context.object.active_material = mat
        
        mat.use_nodes = True
        create_shader(mat)
        update_shader_from_properties(mat)
        
        self.report({'INFO'}, f"Created Metallic Flake Plastic v4.0.0 on {mat.name}")
        return {'FINISHED'}


class MATERIAL_OT_mfp_apply_preset(Operator):
    """Apply a preset to the current material"""
    bl_idname = "material.mfp_apply_preset"
    bl_label = "Apply Preset"
    bl_description = "Apply the selected preset to the material"
    bl_options = {'REGISTER', 'UNDO'}

    preset_id: StringProperty(
        name="Preset ID",
        description="Internal preset identifier",
        default=""
    )

    def execute(self, context):
        if not context.object or not context.object.active_material:
            self.report({'ERROR'}, "No active material")
            return {'CANCELLED'}

        mat = context.object.active_material
        props = mat.metallic_flake_plastic

        preset_id = self.preset_id

        # Determine preset source
        if preset_id.startswith("BUILTIN_"):
            key = preset_id[8:]  # Remove "BUILTIN_" prefix
            if key not in BUILTIN_PRESETS:
                self.report({'ERROR'}, f"Unknown preset: {key}")
                return {'CANCELLED'}
            preset_data = BUILTIN_PRESETS[key]
        elif preset_id.startswith("USER_"):
            key = preset_id[5:]  # Remove "USER_" prefix
            user_presets = load_user_presets()
            if key not in user_presets:
                self.report({'ERROR'}, f"User preset not found: {key}")
                return {'CANCELLED'}
            preset_data = user_presets[key]
        else:
            self.report({'WARNING'}, "No preset selected")
            return {'CANCELLED'}

        # Apply values
        values = preset_data.get("values", {})
        for prop_name, value in values.items():
            if hasattr(props, prop_name):
                try:
                    setattr(props, prop_name, value)
                except Exception as e:
                    print(f"Could not set {prop_name}: {e}")

        preset_name = preset_data.get("name", key)
        self.report({'INFO'}, f"Applied preset: {preset_name}")
        return {'FINISHED'}


class MATERIAL_OT_mfp_save_preset(Operator):
    """Save current settings as a user preset"""
    bl_idname = "material.mfp_save_preset"
    bl_label = "Save Preset"
    bl_description = "Save current material settings as a user preset"
    bl_options = {'REGISTER'}

    preset_name: StringProperty(
        name="Preset Name",
        description="Name for the new preset",
        default="My Preset"
    )
    preset_description: StringProperty(
        name="Description",
        description="Optional description for the preset",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        layout.prop(self, "preset_description")

    def execute(self, context):
        if not context.object or not context.object.active_material:
            self.report({'ERROR'}, "No active material")
            return {'CANCELLED'}

        props = context.object.active_material.metallic_flake_plastic

        # Generate safe key from name
        import re
        key = re.sub(r'[^a-z0-9_]', '_', self.preset_name.lower())
        key = re.sub(r'_+', '_', key).strip('_')
        if not key:
            key = "preset"

        # Collect current values
        values = {}
        for prop_name in dir(props):
            if prop_name.startswith('_') or prop_name in PRESET_EXCLUDE_PROPS:
                continue
            if prop_name in ('bl_rna', 'rna_type', 'name'):
                continue
            try:
                val = getattr(props, prop_name)
                # Convert to serializable format
                if hasattr(val, '__iter__') and not isinstance(val, str):
                    val = tuple(val)
                if isinstance(val, (int, float, bool, str, tuple)):
                    values[prop_name] = val
            except Exception:
                pass

        # Load existing presets, add new one, save
        user_presets = load_user_presets()

        # Check for overwrite
        if key in user_presets:
            # Append number to make unique
            base_key = key
            counter = 2
            while key in user_presets:
                key = f"{base_key}_{counter}"
                counter += 1

        user_presets[key] = {
            "name": self.preset_name,
            "description": self.preset_description or f"User preset: {self.preset_name}",
            "values": values
        }

        save_user_presets(user_presets)
        self.report({'INFO'}, f"Saved preset: {self.preset_name}")
        return {'FINISHED'}


class MATERIAL_OT_mfp_delete_preset(Operator):
    """Delete a user preset"""
    bl_idname = "material.mfp_delete_preset"
    bl_label = "Delete Preset"
    bl_description = "Delete a user-created preset"
    bl_options = {'REGISTER'}

    preset_key: StringProperty(
        name="Preset Key",
        description="Internal key of preset to delete",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if not self.preset_key:
            self.report({'ERROR'}, "No preset specified")
            return {'CANCELLED'}

        user_presets = load_user_presets()
        if self.preset_key not in user_presets:
            self.report({'ERROR'}, f"Preset not found: {self.preset_key}")
            return {'CANCELLED'}

        preset_name = user_presets[self.preset_key].get("name", self.preset_key)
        del user_presets[self.preset_key]
        save_user_presets(user_presets)

        self.report({'INFO'}, f"Deleted preset: {preset_name}")
        return {'FINISHED'}


# =============================================================================
# SHADER NODE CREATION
# =============================================================================

def create_node(nodes, node_type, location, name=None, label=None):
    """Helper to create a node."""
    node = nodes.new(type=node_type)
    node.location = location
    if name:
        node.name = name
    if label:
        node.label = label
    return node


def create_shader(mat):
    """Create the complete shader node network with view-based sparkle visibility."""

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Frame for identification
    frame = nodes.new('NodeFrame')
    frame.name = "Metallic Flake Plastic v4.0.0"
    frame.label = "Metallic Flake Plastic v4.0.0"

    # ==========================================================================
    # COORDINATE SETUP
    # ==========================================================================

    tex_coord = create_node(nodes, 'ShaderNodeTexCoord', (-2000, 0), 'tex_coord', 'Coordinates')
    geometry = create_node(nodes, 'ShaderNodeNewGeometry', (-2000, -300), 'geometry', 'Geometry')

    # ==========================================================================
    # VALUE NODES - All controllable parameters
    # ==========================================================================

    # Base Material
    base_color_node = create_node(nodes, 'ShaderNodeRGB', (-1800, 200), 'base_color', 'Base Color')
    base_rough_node = create_node(nodes, 'ShaderNodeValue', (-1800, 100), 'base_roughness', 'Base Roughness')
    ior_node = create_node(nodes, 'ShaderNodeValue', (-1800, 50), 'ior', 'IOR')

    # Surface Effects
    grain_amount_node = create_node(nodes, 'ShaderNodeValue', (-1800, -50), 'surface_grain_amount', 'Grain Amount')
    grain_scale_node = create_node(nodes, 'ShaderNodeValue', (-1800, -100), 'surface_grain_scale', 'Grain Scale')

    # Aniso
    aniso_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1800, -200), 'aniso_intensity', 'Aniso Intensity')
    aniso_scale_node = create_node(nodes, 'ShaderNodeValue', (-1800, -250), 'aniso_scale', 'Aniso Scale')
    aniso_ratio_node = create_node(nodes, 'ShaderNodeValue', (-1800, -300), 'aniso_ratio', 'Aniso Ratio')
    aniso_angle_node = create_node(nodes, 'ShaderNodeValue', (-1800, -350), 'aniso_angle', 'Aniso Angle')
    aniso_normal_str_node = create_node(nodes, 'ShaderNodeValue', (-1800, -400), 'aniso_normal_strength', 'Aniso Normal')
    aniso_rough_node = create_node(nodes, 'ShaderNodeValue', (-1800, -450), 'aniso_roughness', 'Aniso Roughness')

    # SSS
    sss_weight_node = create_node(nodes, 'ShaderNodeValue', (-1800, -550), 'sss_weight', 'SSS Weight')
    sss_radius_node = create_node(nodes, 'ShaderNodeValue', (-1800, -600), 'sss_radius', 'SSS Radius')
    sss_scale_node = create_node(nodes, 'ShaderNodeValue', (-1800, -650), 'sss_scale', 'SSS Scale')

    # Clearcoat
    coat_weight_node = create_node(nodes, 'ShaderNodeValue', (-1800, -750), 'coat_weight', 'Coat Weight')
    coat_rough_node = create_node(nodes, 'ShaderNodeValue', (-1800, -800), 'coat_roughness', 'Coat Roughness')

    # Primary Sparkle params
    primary_enable_node = create_node(nodes, 'ShaderNodeValue', (-1600, 500), 'primary_enable', 'Primary Enable')
    primary_seed_node = create_node(nodes, 'ShaderNodeValue', (-1600, 470), 'primary_seed', 'Primary Seed')
    primary_density_node = create_node(nodes, 'ShaderNodeValue', (-1600, 440), 'primary_density', 'Primary Density')
    primary_size_node = create_node(nodes, 'ShaderNodeValue', (-1600, 410), 'primary_size', 'Primary Size')
    primary_size_var_node = create_node(nodes, 'ShaderNodeValue', (-1600, 380), 'primary_size_var', 'Primary Size Var')
    primary_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1600, 350), 'primary_intensity', 'Primary Intensity')

    # Secondary Sparkle params
    secondary_enable_node = create_node(nodes, 'ShaderNodeValue', (-1600, 250), 'secondary_enable', 'Secondary Enable')
    secondary_seed_node = create_node(nodes, 'ShaderNodeValue', (-1600, 220), 'secondary_seed', 'Secondary Seed')
    secondary_density_node = create_node(nodes, 'ShaderNodeValue', (-1600, 190), 'secondary_density', 'Secondary Density')
    secondary_size_node = create_node(nodes, 'ShaderNodeValue', (-1600, 160), 'secondary_size', 'Secondary Size')
    secondary_size_var_node = create_node(nodes, 'ShaderNodeValue', (-1600, 130), 'secondary_size_var', 'Secondary Size Var')
    secondary_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1600, 100), 'secondary_intensity', 'Secondary Intensity')

    # Tertiary Sparkle params
    tertiary_enable_node = create_node(nodes, 'ShaderNodeValue', (-1600, 0), 'tertiary_enable', 'Tertiary Enable')
    tertiary_seed_node = create_node(nodes, 'ShaderNodeValue', (-1600, -30), 'tertiary_seed', 'Tertiary Seed')
    tertiary_density_node = create_node(nodes, 'ShaderNodeValue', (-1600, -60), 'tertiary_density', 'Tertiary Density')
    tertiary_size_node = create_node(nodes, 'ShaderNodeValue', (-1600, -90), 'tertiary_size', 'Tertiary Size')
    tertiary_size_var_node = create_node(nodes, 'ShaderNodeValue', (-1600, -120), 'tertiary_size_var', 'Tertiary Size Var')
    tertiary_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1600, -150), 'tertiary_intensity', 'Tertiary Intensity')

    # Sparkle Color
    sparkle_color_node = create_node(nodes, 'ShaderNodeRGB', (-1400, 500), 'sparkle_color', 'Sparkle Color')
    sparkle_hue_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, 400), 'sparkle_hue_var', 'Hue Var')
    sparkle_sat_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, 350), 'sparkle_sat_var', 'Sat Var')
    sparkle_val_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, 300), 'sparkle_val_var', 'Val Var')
    sparkle_base_inf_node = create_node(nodes, 'ShaderNodeValue', (-1400, 250), 'sparkle_base_influence', 'Base Influence')
    sparkle_metallic_node = create_node(nodes, 'ShaderNodeValue', (-1400, 200), 'sparkle_metallic', 'Metallic')
    fresnel_shift_node = create_node(nodes, 'ShaderNodeValue', (-1400, 150), 'fresnel_shift', 'Fresnel Shift')
    fresnel_dir_node = create_node(nodes, 'ShaderNodeValue', (-1400, 100), 'fresnel_direction', 'Fresnel Dir')

    # Sparkle Response (NEW parameters)
    sparkle_roughness_node = create_node(nodes, 'ShaderNodeValue', (-1400, 0), 'sparkle_roughness', 'Sparkle Roughness')
    sparkle_sharpness_node = create_node(nodes, 'ShaderNodeValue', (-1400, -50), 'sparkle_sharpness', 'Sparkle Sharpness')
    orientation_randomness_node = create_node(nodes, 'ShaderNodeValue', (-1400, -100), 'orientation_randomness', 'Orientation Randomness')

    # Safe minimum for orientation_randomness to avoid degenerate Map Range (From Min == From Max)
    orient_rand_safe = create_node(nodes, 'ShaderNodeMath', (-1200, -100), 'orient_rand_safe', 'Orient Rand Safe')
    orient_rand_safe.operation = 'MAXIMUM'
    orient_rand_safe.inputs[1].default_value = 0.001
    links.new(orientation_randomness_node.outputs[0], orient_rand_safe.inputs[0])

    # Negative orientation_randomness for Map Range From Min
    neg_orient_rand = create_node(nodes, 'ShaderNodeMath', (-1200, -140), 'neg_orient_rand', 'Neg Orient Rand')
    neg_orient_rand.operation = 'MULTIPLY'
    neg_orient_rand.inputs[1].default_value = -1.0
    links.new(orient_rand_safe.outputs[0], neg_orient_rand.inputs[0])

    overdrive_node = create_node(nodes, 'ShaderNodeValue', (-1400, -150), 'overdrive', 'Overdrive')
    emission_str_node = create_node(nodes, 'ShaderNodeValue', (-1400, -200), 'emission_strength', 'Emission')
    global_density_mult_node = create_node(nodes, 'ShaderNodeValue', (-1400, -230), 'global_density_multiplier', 'Global Density Mult')
    global_size_mult_node = create_node(nodes, 'ShaderNodeValue', (-1400, -260), 'global_size_multiplier', 'Global Size Mult')

    # Mold
    mold_enable_node = create_node(nodes, 'ShaderNodeValue', (-1400, -300), 'mold_enable', 'Mold Enable')
    mold_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1400, -350), 'mold_intensity', 'Mold Intensity')
    mold_scale_node = create_node(nodes, 'ShaderNodeValue', (-1400, -400), 'mold_scale', 'Mold Scale')

    # Overall
    overall_effect_node = create_node(nodes, 'ShaderNodeValue', (-1400, -500), 'overall_effect', 'Overall Effect')
    
    # ==========================================================================
    # MOLD TEXTURE SETUP
    # ==========================================================================
    
    mold_tex_scale = create_node(nodes, 'ShaderNodeVectorMath', (-1200, -500), 'mold_tex_scale', 'Mold Scale')
    mold_tex_scale.operation = 'SCALE'
    links.new(tex_coord.outputs['Object'], mold_tex_scale.inputs[0])
    links.new(mold_scale_node.outputs[0], mold_tex_scale.inputs['Scale'])
    
    # Mold texture nodes
    mold_normal_tex = create_node(nodes, 'ShaderNodeTexImage', (-1000, -400), 'mold_normal_tex', 'Mold Normal')
    mold_normal_tex.projection = 'BOX'
    mold_normal_tex.projection_blend = 0.2
    links.new(mold_tex_scale.outputs[0], mold_normal_tex.inputs['Vector'])
    
    mold_disp_tex = create_node(nodes, 'ShaderNodeTexImage', (-1000, -600), 'mold_disp_tex', 'Mold Disp')
    mold_disp_tex.projection = 'BOX'
    mold_disp_tex.projection_blend = 0.2
    links.new(mold_tex_scale.outputs[0], mold_disp_tex.inputs['Vector'])
    
    mold_gloss_tex = create_node(nodes, 'ShaderNodeTexImage', (-1000, -800), 'mold_gloss_tex', 'Mold Gloss')
    mold_gloss_tex.projection = 'BOX'
    mold_gloss_tex.projection_blend = 0.2
    links.new(mold_tex_scale.outputs[0], mold_gloss_tex.inputs['Vector'])
    
    mold_ao_tex = create_node(nodes, 'ShaderNodeTexImage', (-1000, -1000), 'mold_ao_tex', 'Mold AO')
    mold_ao_tex.projection = 'BOX'
    mold_ao_tex.projection_blend = 0.2
    links.new(mold_tex_scale.outputs[0], mold_ao_tex.inputs['Vector'])
    
    # ==========================================================================
    # SURFACE GRAIN
    # ==========================================================================
    
    grain_noise = create_node(nodes, 'ShaderNodeTexNoise', (-1000, 100), 'grain_noise', 'Surface Grain')
    grain_noise.noise_dimensions = '3D'
    links.new(tex_coord.outputs['Object'], grain_noise.inputs['Vector'])
    links.new(grain_scale_node.outputs[0], grain_noise.inputs['Scale'])
    grain_noise.inputs['Detail'].default_value = 5.0
    
    grain_map = create_node(nodes, 'ShaderNodeMapRange', (-800, 100), 'grain_map', 'Grain Map')
    grain_map.inputs['To Min'].default_value = -1.0
    grain_map.inputs['To Max'].default_value = 1.0
    links.new(grain_noise.outputs['Fac'], grain_map.inputs['Value'])
    
    grain_scaled = create_node(nodes, 'ShaderNodeMath', (-600, 100), 'grain_scaled', 'Grain Scaled')
    grain_scaled.operation = 'MULTIPLY'
    links.new(grain_map.outputs[0], grain_scaled.inputs[0])
    links.new(grain_amount_node.outputs[0], grain_scaled.inputs[1])
    
    final_roughness = create_node(nodes, 'ShaderNodeMath', (-400, 100), 'final_roughness', 'Final Roughness')
    final_roughness.operation = 'ADD'
    links.new(base_rough_node.outputs[0], final_roughness.inputs[0])
    links.new(grain_scaled.outputs[0], final_roughness.inputs[1])
    
    clamp_roughness = create_node(nodes, 'ShaderNodeClamp', (-200, 100), 'clamp_roughness', 'Clamp Rough')
    links.new(final_roughness.outputs[0], clamp_roughness.inputs['Value'])
    
    # ==========================================================================
    # ANISOTROPIC GRAIN SYSTEM
    # ==========================================================================
    
    # Angle to radians
    angle_rad = create_node(nodes, 'ShaderNodeMath', (-1000, -200), 'angle_rad', 'Angle Rad')
    angle_rad.operation = 'MULTIPLY'
    links.new(aniso_angle_node.outputs[0], angle_rad.inputs[0])
    angle_rad.inputs[1].default_value = math.pi / 180.0
    
    cos_angle = create_node(nodes, 'ShaderNodeMath', (-800, -150), 'cos_angle', 'Cos')
    cos_angle.operation = 'COSINE'
    links.new(angle_rad.outputs[0], cos_angle.inputs[0])
    
    sin_angle = create_node(nodes, 'ShaderNodeMath', (-800, -250), 'sin_angle', 'Sin')
    sin_angle.operation = 'SINE'
    links.new(angle_rad.outputs[0], sin_angle.inputs[0])
    
    # Tangent for aniso
    aniso_tangent = create_node(nodes, 'ShaderNodeCombineXYZ', (-600, -200), 'aniso_tangent', 'Aniso Tangent')
    links.new(cos_angle.outputs[0], aniso_tangent.inputs['X'])
    links.new(sin_angle.outputs[0], aniso_tangent.inputs['Y'])
    aniso_tangent.inputs['Z'].default_value = 0.0
    
    # Aniso grain wave
    separate_obj = create_node(nodes, 'ShaderNodeSeparateXYZ', (-1000, 0), 'separate_obj', 'Sep XYZ')
    links.new(tex_coord.outputs['Object'], separate_obj.inputs[0])
    
    aniso_x_scale = create_node(nodes, 'ShaderNodeMath', (-800, 0), 'aniso_x_scale', 'X Scale')
    aniso_x_scale.operation = 'MULTIPLY'
    links.new(separate_obj.outputs['X'], aniso_x_scale.inputs[0])
    links.new(aniso_scale_node.outputs[0], aniso_x_scale.inputs[1])
    
    aniso_y_ratio = create_node(nodes, 'ShaderNodeMath', (-800, -50), 'aniso_y_ratio', 'Y Ratio')
    aniso_y_ratio.operation = 'MULTIPLY'
    links.new(aniso_scale_node.outputs[0], aniso_y_ratio.inputs[0])
    links.new(aniso_ratio_node.outputs[0], aniso_y_ratio.inputs[1])
    
    aniso_y_scale = create_node(nodes, 'ShaderNodeMath', (-600, -50), 'aniso_y_scale', 'Y Scale')
    aniso_y_scale.operation = 'MULTIPLY'
    links.new(separate_obj.outputs['Y'], aniso_y_scale.inputs[0])
    links.new(aniso_y_ratio.outputs[0], aniso_y_scale.inputs[1])
    
    aniso_combine = create_node(nodes, 'ShaderNodeCombineXYZ', (-400, 0), 'aniso_combine', 'Aniso Coord')
    links.new(aniso_x_scale.outputs[0], aniso_combine.inputs['X'])
    links.new(aniso_y_scale.outputs[0], aniso_combine.inputs['Y'])
    aniso_combine.inputs['Z'].default_value = 0.0
    
    aniso_wave = create_node(nodes, 'ShaderNodeTexWave', (-200, 0), 'aniso_wave', 'Aniso Wave')
    aniso_wave.wave_type = 'BANDS'
    aniso_wave.bands_direction = 'X'
    aniso_wave.wave_profile = 'SAW'
    aniso_wave.inputs['Scale'].default_value = 1.0
    aniso_wave.inputs['Distortion'].default_value = 0.5
    aniso_wave.inputs['Detail'].default_value = 2.0
    links.new(aniso_combine.outputs[0], aniso_wave.inputs['Vector'])
    
    aniso_bump_str = create_node(nodes, 'ShaderNodeMath', (0, 0), 'aniso_bump_str', 'Aniso Bump Str')
    aniso_bump_str.operation = 'MULTIPLY'
    links.new(aniso_wave.outputs['Fac'], aniso_bump_str.inputs[0])
    links.new(aniso_intensity_node.outputs[0], aniso_bump_str.inputs[1])
    
    aniso_bump = create_node(nodes, 'ShaderNodeBump', (200, 0), 'aniso_bump', 'Aniso Bump')
    aniso_bump.inputs['Distance'].default_value = 0.02
    links.new(aniso_bump_str.outputs[0], aniso_bump.inputs['Height'])
    links.new(aniso_normal_str_node.outputs[0], aniso_bump.inputs['Strength'])
    links.new(geometry.outputs['Normal'], aniso_bump.inputs['Normal'])
    
    # ==========================================================================
    # NORMAL PROCESSING - Combine aniso with mold
    # ==========================================================================
    #
    # Tri-planar (BOX) projection has no UV tangent basis, so the standard
    # Normal Map node in TANGENT space produces incorrect results.  Instead we
    # derive a height signal from the tangent-space normal map and feed it
    # through a Bump node, which works correctly with any projection method.
    #
    # Height derivation: tangent-space normal maps encode (R=X, G=Y, B=Z)
    # with flat = (0.5, 0.5, 1.0).  The Blue channel already acts as a
    # height proxy (concavities are darker, convexities are brighter).  We
    # use it directly — this is the standard trick for tri-planar normal maps.
    # ==========================================================================

    mold_normal_strength_node = create_node(nodes, 'ShaderNodeValue', (-600, -400), 'mold_normal_strength', 'Mold Norm Str')
    mold_normal_invert_node = create_node(nodes, 'ShaderNodeValue', (-600, -450), 'mold_normal_invert', 'Mold Norm Inv')

    # Separate normal map channels
    mold_normal_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-500, -400), 'mold_normal_separate', 'Norm Sep')
    mold_normal_separate.mode = 'RGB'
    links.new(mold_normal_tex.outputs['Color'], mold_normal_separate.inputs['Color'])

    # --- Derive height from normal map for tri-planar-safe bump ---
    # The Blue (Z) channel of a tangent-space normal map encodes how much the
    # surface faces outward (1.0 = flat, <1.0 = tilted).  We also blend in
    # the R and G deviation from 0.5 to capture directional detail.
    #
    # height = B * 0.5 + (1.0 - abs(R - 0.5) - abs(G - 0.5)) * 0.5
    # This gives us a height field that the Bump node can differentiate.

    # R deviation from 0.5
    norm_r_sub = create_node(nodes, 'ShaderNodeMath', (-350, -370), 'norm_r_sub', 'R - 0.5')
    norm_r_sub.operation = 'SUBTRACT'
    links.new(mold_normal_separate.outputs['Red'], norm_r_sub.inputs[0])
    norm_r_sub.inputs[1].default_value = 0.5

    norm_r_abs = create_node(nodes, 'ShaderNodeMath', (-200, -370), 'norm_r_abs', '|R|')
    norm_r_abs.operation = 'ABSOLUTE'
    links.new(norm_r_sub.outputs[0], norm_r_abs.inputs[0])

    # G deviation from 0.5
    norm_g_sub = create_node(nodes, 'ShaderNodeMath', (-350, -430), 'norm_g_sub', 'G - 0.5')
    norm_g_sub.operation = 'SUBTRACT'
    links.new(mold_normal_separate.outputs['Green'], norm_g_sub.inputs[0])
    norm_g_sub.inputs[1].default_value = 0.5

    norm_g_abs = create_node(nodes, 'ShaderNodeMath', (-200, -430), 'norm_g_abs', '|G|')
    norm_g_abs.operation = 'ABSOLUTE'
    links.new(norm_g_sub.outputs[0], norm_g_abs.inputs[0])

    # Combine: height = B - |R-0.5| - |G-0.5|  (unnormalised, Bump node handles scale)
    norm_height_rg = create_node(nodes, 'ShaderNodeMath', (-50, -400), 'norm_height_rg', 'R+G Dev')
    norm_height_rg.operation = 'ADD'
    links.new(norm_r_abs.outputs[0], norm_height_rg.inputs[0])
    links.new(norm_g_abs.outputs[0], norm_height_rg.inputs[1])

    norm_height_raw = create_node(nodes, 'ShaderNodeMath', (100, -400), 'norm_height_raw', 'Height Raw')
    norm_height_raw.operation = 'SUBTRACT'
    links.new(mold_normal_separate.outputs['Blue'], norm_height_raw.inputs[0])
    links.new(norm_height_rg.outputs[0], norm_height_raw.inputs[1])

    # Invert support: flip the height signal
    norm_height_inv = create_node(nodes, 'ShaderNodeMath', (250, -380), 'norm_height_inv', 'Height Inv')
    norm_height_inv.operation = 'SUBTRACT'
    norm_height_inv.inputs[0].default_value = 1.0
    links.new(norm_height_raw.outputs[0], norm_height_inv.inputs[1])

    norm_height_mix = create_node(nodes, 'ShaderNodeMix', (400, -400), 'norm_height_mix', 'Height Mix')
    norm_height_mix.data_type = 'FLOAT'
    links.new(mold_normal_invert_node.outputs[0], norm_height_mix.inputs['Factor'])
    links.new(norm_height_raw.outputs[0], norm_height_mix.inputs[2])
    links.new(norm_height_inv.outputs[0], norm_height_mix.inputs[3])

    # Bump node from normal-map-derived height (tri-planar safe)
    mold_normal_bump = create_node(nodes, 'ShaderNodeBump', (550, -400), 'mold_normal_bump', 'Mold Normal Bump')
    mold_normal_bump.inputs['Distance'].default_value = 0.1
    links.new(norm_height_mix.outputs[0], mold_normal_bump.inputs['Height'])
    links.new(mold_normal_strength_node.outputs[0], mold_normal_bump.inputs['Strength'])
    links.new(geometry.outputs['Normal'], mold_normal_bump.inputs['Normal'])

    # Mold displacement/bump with invert support
    mold_bump_strength_node = create_node(nodes, 'ShaderNodeValue', (-600, -600), 'mold_bump_strength', 'Mold Bump Str')
    mold_bump_invert_node = create_node(nodes, 'ShaderNodeValue', (-600, -650), 'mold_bump_invert', 'Mold Bump Inv')

    # Get displacement value and optionally invert
    mold_disp_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-400, -600), 'mold_disp_separate', 'Disp Sep')
    mold_disp_separate.mode = 'RGB'
    links.new(mold_disp_tex.outputs['Color'], mold_disp_separate.inputs['Color'])

    mold_disp_inv = create_node(nodes, 'ShaderNodeMath', (-250, -600), 'mold_disp_inv', 'Disp Inv')
    mold_disp_inv.operation = 'SUBTRACT'
    mold_disp_inv.inputs[0].default_value = 1.0
    links.new(mold_disp_separate.outputs['Red'], mold_disp_inv.inputs[1])

    mold_disp_mix = create_node(nodes, 'ShaderNodeMix', (-100, -600), 'mold_disp_mix', 'Disp Mix')
    mold_disp_mix.data_type = 'FLOAT'
    links.new(mold_bump_invert_node.outputs[0], mold_disp_mix.inputs['Factor'])
    links.new(mold_disp_separate.outputs['Red'], mold_disp_mix.inputs[2])
    links.new(mold_disp_inv.outputs[0], mold_disp_mix.inputs[3])

    # Chain: geometry normal -> normal map bump -> displacement bump
    # This ensures both normal detail and displacement detail stack correctly
    mold_bump = create_node(nodes, 'ShaderNodeBump', (550, -600), 'mold_bump', 'Mold Bump')
    mold_bump.inputs['Distance'].default_value = 0.02
    links.new(mold_disp_mix.outputs[0], mold_bump.inputs['Height'])
    links.new(mold_bump_strength_node.outputs[0], mold_bump.inputs['Strength'])
    links.new(mold_normal_bump.outputs['Normal'], mold_bump.inputs['Normal'])
    
    # ==========================================================================
    # GLOSS MAP PROCESSING - Affects roughness
    # ==========================================================================
    
    mold_roughness_strength_node = create_node(nodes, 'ShaderNodeValue', (-400, -800), 'mold_roughness_strength', 'Mold Rough Str')
    
    # Get gloss value (white = glossy, black = rough)
    mold_gloss_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-250, -800), 'mold_gloss_separate', 'Gloss Sep')
    mold_gloss_separate.mode = 'RGB'
    links.new(mold_gloss_tex.outputs['Color'], mold_gloss_separate.inputs['Color'])
    
    # Convert gloss to roughness (invert)
    mold_gloss_to_rough = create_node(nodes, 'ShaderNodeMath', (-100, -800), 'mold_gloss_to_rough', 'Gloss to Rough')
    mold_gloss_to_rough.operation = 'SUBTRACT'
    mold_gloss_to_rough.inputs[0].default_value = 1.0
    links.new(mold_gloss_separate.outputs['Red'], mold_gloss_to_rough.inputs[1])
    
    # Center around 0.5 for additive effect
    mold_rough_centered = create_node(nodes, 'ShaderNodeMath', (50, -800), 'mold_rough_centered', 'Rough Centered')
    mold_rough_centered.operation = 'SUBTRACT'
    links.new(mold_gloss_to_rough.outputs[0], mold_rough_centered.inputs[0])
    mold_rough_centered.inputs[1].default_value = 0.5
    
    # Scale by strength
    mold_rough_scaled = create_node(nodes, 'ShaderNodeMath', (200, -800), 'mold_rough_scaled', 'Rough Scaled')
    mold_rough_scaled.operation = 'MULTIPLY'
    links.new(mold_rough_centered.outputs[0], mold_rough_scaled.inputs[0])
    links.new(mold_roughness_strength_node.outputs[0], mold_rough_scaled.inputs[1])
    
    # Apply mold enable and intensity
    mold_rough_enabled = create_node(nodes, 'ShaderNodeMath', (350, -800), 'mold_rough_enabled', 'Rough Enabled')
    mold_rough_enabled.operation = 'MULTIPLY'
    links.new(mold_rough_scaled.outputs[0], mold_rough_enabled.inputs[0])
    links.new(mold_enable_node.outputs[0], mold_rough_enabled.inputs[1])
    
    mold_rough_final = create_node(nodes, 'ShaderNodeMath', (500, -800), 'mold_rough_final', 'Mold Rough Final')
    mold_rough_final.operation = 'MULTIPLY'
    links.new(mold_rough_enabled.outputs[0], mold_rough_final.inputs[0])
    links.new(mold_intensity_node.outputs[0], mold_rough_final.inputs[1])
    
    # Combine normals based on mold enable and intensity
    normal_mix_factor = create_node(nodes, 'ShaderNodeMath', (250, -300), 'normal_mix_factor', 'Normal Mix Fac')
    normal_mix_factor.operation = 'MULTIPLY'
    links.new(mold_enable_node.outputs[0], normal_mix_factor.inputs[0])
    links.new(mold_intensity_node.outputs[0], normal_mix_factor.inputs[1])
    
    final_normal = create_node(nodes, 'ShaderNodeMix', (400, -300), 'final_normal', 'Final Normal')
    final_normal.data_type = 'VECTOR'
    links.new(normal_mix_factor.outputs[0], final_normal.inputs['Factor'])
    links.new(aniso_bump.outputs['Normal'], final_normal.inputs[4])
    links.new(mold_bump.outputs['Normal'], final_normal.inputs[5])
    
    # ==========================================================================
    # AO PROCESSING - Darkens base color AND affects lighting
    # ==========================================================================
    
    mold_ao_strength_node = create_node(nodes, 'ShaderNodeValue', (-400, -1000), 'mold_ao_strength', 'AO Strength')
    
    # Get AO value
    ao_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-250, -1000), 'ao_separate', 'AO Sep')
    ao_separate.mode = 'RGB'
    links.new(mold_ao_tex.outputs['Color'], ao_separate.inputs['Color'])
    
    # Power by strength (1.0 = no change, >1 = more contrast)
    ao_powered = create_node(nodes, 'ShaderNodeMath', (-100, -1000), 'ao_powered', 'AO Power')
    ao_powered.operation = 'POWER'
    links.new(ao_separate.outputs['Red'], ao_powered.inputs[0])
    links.new(mold_ao_strength_node.outputs[0], ao_powered.inputs[1])
    
    # Mix AO based on mold enable (1.0 when disabled, AO when enabled)
    ao_factor = create_node(nodes, 'ShaderNodeMix', (50, -1000), 'ao_factor', 'AO Factor')
    ao_factor.data_type = 'FLOAT'
    links.new(mold_enable_node.outputs[0], ao_factor.inputs['Factor'])
    ao_factor.inputs[2].default_value = 1.0  # No mold = white AO
    links.new(ao_powered.outputs[0], ao_factor.inputs[3])
    
    # Apply AO to base color - convert AO float to grayscale first
    ao_to_color = create_node(nodes, 'ShaderNodeCombineColor', (100, -1050), 'ao_to_color', 'AO to Color')
    ao_to_color.mode = 'RGB'
    links.new(ao_factor.outputs[0], ao_to_color.inputs['Red'])
    links.new(ao_factor.outputs[0], ao_to_color.inputs['Green'])
    links.new(ao_factor.outputs[0], ao_to_color.inputs['Blue'])
    
    base_color_with_ao = create_node(nodes, 'ShaderNodeMix', (300, -1050), 'base_color_with_ao', 'Base + AO')
    base_color_with_ao.data_type = 'RGBA'
    base_color_with_ao.blend_type = 'MULTIPLY'
    base_color_with_ao.inputs['Factor'].default_value = 1.0
    links.new(base_color_node.outputs['Color'], base_color_with_ao.inputs[6])
    links.new(ao_to_color.outputs['Color'], base_color_with_ao.inputs[7])
    
    # ==========================================================================
    # FRESNEL FOR COLOR SHIFT (still used for color effects)
    # ==========================================================================

    fresnel = create_node(nodes, 'ShaderNodeFresnel', (0, -500), 'fresnel', 'Fresnel')
    links.new(ior_node.outputs[0], fresnel.inputs['IOR'])
    links.new(final_normal.outputs[1], fresnel.inputs['Normal'])
    
    # ==========================================================================
    # SPARKLE COLOR SYSTEM
    # ==========================================================================
    
    # Convert sparkle color to HSV for variation
    sparkle_hsv = create_node(nodes, 'ShaderNodeSeparateColor', (0, 400), 'sparkle_hsv', 'Sparkle HSV')
    sparkle_hsv.mode = 'HSV'
    links.new(sparkle_color_node.outputs['Color'], sparkle_hsv.inputs['Color'])
    
    # Random noise for per-sparkle variation (we'll use position-based)
    color_random = create_node(nodes, 'ShaderNodeTexWhiteNoise', (0, 300), 'color_random', 'Color Random')
    color_random.noise_dimensions = '3D'
    links.new(tex_coord.outputs['Object'], color_random.inputs['Vector'])
    
    # Hue variation
    hue_var_map = create_node(nodes, 'ShaderNodeMapRange', (200, 350), 'hue_var_map', 'Hue Var Map')
    hue_var_map.inputs['To Min'].default_value = -0.5
    hue_var_map.inputs['To Max'].default_value = 0.5
    links.new(color_random.outputs['Value'], hue_var_map.inputs['Value'])
    
    hue_var_scaled = create_node(nodes, 'ShaderNodeMath', (400, 350), 'hue_var_scaled', 'Hue Scaled')
    hue_var_scaled.operation = 'MULTIPLY'
    links.new(hue_var_map.outputs[0], hue_var_scaled.inputs[0])
    links.new(sparkle_hue_var_node.outputs[0], hue_var_scaled.inputs[1])
    
    hue_final = create_node(nodes, 'ShaderNodeMath', (600, 400), 'hue_final', 'Hue Final')
    hue_final.operation = 'ADD'
    links.new(sparkle_hsv.outputs['Red'], hue_final.inputs[0])
    links.new(hue_var_scaled.outputs[0], hue_final.inputs[1])
    
    hue_wrap = create_node(nodes, 'ShaderNodeMath', (800, 400), 'hue_wrap', 'Hue Wrap')
    hue_wrap.operation = 'WRAP'
    links.new(hue_final.outputs[0], hue_wrap.inputs[0])
    hue_wrap.inputs[1].default_value = 0.0
    hue_wrap.inputs[2].default_value = 1.0
    
    # Fresnel color shift
    fresnel_shift_amount = create_node(nodes, 'ShaderNodeMath', (600, 300), 'fresnel_shift_amount', 'Fresnel Shift Amt')
    fresnel_shift_amount.operation = 'MULTIPLY'
    links.new(fresnel.outputs['Fac'], fresnel_shift_amount.inputs[0])
    links.new(fresnel_shift_node.outputs[0], fresnel_shift_amount.inputs[1])
    
    fresnel_dir_map = create_node(nodes, 'ShaderNodeMapRange', (600, 250), 'fresnel_dir_map', 'Fresnel Dir Map')
    fresnel_dir_map.inputs['To Min'].default_value = -1.0
    fresnel_dir_map.inputs['To Max'].default_value = 1.0
    links.new(fresnel_dir_node.outputs[0], fresnel_dir_map.inputs['Value'])
    
    fresnel_shift_dir = create_node(nodes, 'ShaderNodeMath', (800, 280), 'fresnel_shift_dir', 'Fresnel Shift Dir')
    fresnel_shift_dir.operation = 'MULTIPLY'
    links.new(fresnel_shift_amount.outputs[0], fresnel_shift_dir.inputs[0])
    links.new(fresnel_dir_map.outputs[0], fresnel_shift_dir.inputs[1])
    
    hue_with_fresnel = create_node(nodes, 'ShaderNodeMath', (1000, 350), 'hue_with_fresnel', 'Hue + Fresnel')
    hue_with_fresnel.operation = 'ADD'
    links.new(hue_wrap.outputs[0], hue_with_fresnel.inputs[0])
    links.new(fresnel_shift_dir.outputs[0], hue_with_fresnel.inputs[1])
    
    # Saturation variation
    color_random_2 = create_node(nodes, 'ShaderNodeTexWhiteNoise', (0, 200), 'color_random_2', 'Color Random 2')
    color_random_2.noise_dimensions = '3D'
    
    random_offset = create_node(nodes, 'ShaderNodeVectorMath', (-200, 200), 'random_offset', 'Random Offset')
    random_offset.operation = 'ADD'
    links.new(tex_coord.outputs['Object'], random_offset.inputs[0])
    random_offset.inputs[1].default_value = (100.0, 0.0, 0.0)
    links.new(random_offset.outputs[0], color_random_2.inputs['Vector'])
    
    sat_var_map = create_node(nodes, 'ShaderNodeMapRange', (200, 200), 'sat_var_map', 'Sat Var Map')
    sat_var_map.inputs['To Min'].default_value = -0.5
    sat_var_map.inputs['To Max'].default_value = 0.5
    links.new(color_random_2.outputs['Value'], sat_var_map.inputs['Value'])
    
    sat_var_scaled = create_node(nodes, 'ShaderNodeMath', (400, 200), 'sat_var_scaled', 'Sat Scaled')
    sat_var_scaled.operation = 'MULTIPLY'
    links.new(sat_var_map.outputs[0], sat_var_scaled.inputs[0])
    links.new(sparkle_sat_var_node.outputs[0], sat_var_scaled.inputs[1])
    
    sat_final = create_node(nodes, 'ShaderNodeMath', (600, 200), 'sat_final', 'Sat Final')
    sat_final.operation = 'ADD'
    links.new(sparkle_hsv.outputs['Green'], sat_final.inputs[0])
    links.new(sat_var_scaled.outputs[0], sat_final.inputs[1])
    
    sat_clamp = create_node(nodes, 'ShaderNodeClamp', (800, 200), 'sat_clamp', 'Sat Clamp')
    links.new(sat_final.outputs[0], sat_clamp.inputs['Value'])
    
    # Value variation
    color_random_3 = create_node(nodes, 'ShaderNodeTexWhiteNoise', (0, 100), 'color_random_3', 'Color Random 3')
    color_random_3.noise_dimensions = '3D'
    
    random_offset_2 = create_node(nodes, 'ShaderNodeVectorMath', (-200, 100), 'random_offset_2', 'Random Offset 2')
    random_offset_2.operation = 'ADD'
    links.new(tex_coord.outputs['Object'], random_offset_2.inputs[0])
    random_offset_2.inputs[1].default_value = (0.0, 100.0, 0.0)
    links.new(random_offset_2.outputs[0], color_random_3.inputs['Vector'])
    
    val_var_map = create_node(nodes, 'ShaderNodeMapRange', (200, 100), 'val_var_map', 'Val Var Map')
    val_var_map.inputs['To Min'].default_value = -0.5
    val_var_map.inputs['To Max'].default_value = 0.5
    links.new(color_random_3.outputs['Value'], val_var_map.inputs['Value'])
    
    val_var_scaled = create_node(nodes, 'ShaderNodeMath', (400, 100), 'val_var_scaled', 'Val Scaled')
    val_var_scaled.operation = 'MULTIPLY'
    links.new(val_var_map.outputs[0], val_var_scaled.inputs[0])
    links.new(sparkle_val_var_node.outputs[0], val_var_scaled.inputs[1])
    
    val_final = create_node(nodes, 'ShaderNodeMath', (600, 100), 'val_final', 'Val Final')
    val_final.operation = 'ADD'
    links.new(sparkle_hsv.outputs['Blue'], val_final.inputs[0])
    links.new(val_var_scaled.outputs[0], val_final.inputs[1])
    
    val_clamp = create_node(nodes, 'ShaderNodeClamp', (800, 100), 'val_clamp', 'Val Clamp')
    links.new(val_final.outputs[0], val_clamp.inputs['Value'])
    
    # Combine final sparkle color
    sparkle_color_final = create_node(nodes, 'ShaderNodeCombineColor', (1200, 250), 'sparkle_color_final', 'Sparkle Color Final')
    sparkle_color_final.mode = 'HSV'
    links.new(hue_with_fresnel.outputs[0], sparkle_color_final.inputs['Red'])
    links.new(sat_clamp.outputs[0], sparkle_color_final.inputs['Green'])
    links.new(val_clamp.outputs[0], sparkle_color_final.inputs['Blue'])
    
    # Blend with base color
    sparkle_with_base = create_node(nodes, 'ShaderNodeMix', (1400, 250), 'sparkle_with_base', 'Sparkle + Base')
    sparkle_with_base.data_type = 'RGBA'
    links.new(sparkle_base_inf_node.outputs[0], sparkle_with_base.inputs['Factor'])
    links.new(sparkle_color_final.outputs['Color'], sparkle_with_base.inputs[6])
    links.new(base_color_node.outputs['Color'], sparkle_with_base.inputs[7])
    
    # ==========================================================================
    # VIEW-BASED SPARKLE VISIBILITY SYSTEM
    # ==========================================================================
    # Each flake has a random orientation. Sparkle visibility is based on how
    # much a flake's normal deviates toward the camera compared to the surface
    # normal. This isolates per-flake variation so sparkles appear everywhere,
    # not just at glancing angles. The BSDF handles actual lighting.
    #
    # Core formula:
    #   surface_dot = dot(surface_N, V)
    #   flake_dot   = dot(flake_N, V)
    #   raw_dev     = flake_dot - surface_dot
    #   deviation   = MapRange(raw_dev, -orient_rand, +orient_rand, 0, 1)
    #   visibility  = pow(deviation, sharpness)
    # ==========================================================================

    # Get view vector (points toward camera)
    # Geometry.Incoming points FROM camera TO surface, so we negate it
    view_negate = create_node(nodes, 'ShaderNodeVectorMath', (200, -600), 'view_negate', 'View Negate')
    view_negate.operation = 'SCALE'
    view_negate.inputs['Scale'].default_value = -1.0
    links.new(geometry.outputs['Incoming'], view_negate.inputs[0])

    # Baseline: dot(surface_normal, view) -- how much the surface faces camera
    surface_dot = create_node(nodes, 'ShaderNodeVectorMath', (400, -600), 'surface_dot', 'Surface Dot')
    surface_dot.operation = 'DOT_PRODUCT'
    links.new(final_normal.outputs[1], surface_dot.inputs[0])
    links.new(view_negate.outputs[0], surface_dot.inputs[1])

    # ==========================================================================
    # HELPER FUNCTION: Create sparkle layer with view-based visibility
    # We'll create each layer inline since Python functions can't access
    # the local scope easily in this context
    # ==========================================================================

    # ==========================================================================
    # PRIMARY SPARKLE LAYER - View Based
    # ==========================================================================

    # Seed offset for unique pattern - combine seed into vector and add to coordinates
    primary_seed_vec = create_node(nodes, 'ShaderNodeCombineXYZ', (100, 850), 'primary_seed_vec', 'Primary Seed Vec')
    links.new(primary_seed_node.outputs[0], primary_seed_vec.inputs['X'])
    links.new(primary_seed_node.outputs[0], primary_seed_vec.inputs['Y'])
    links.new(primary_seed_node.outputs[0], primary_seed_vec.inputs['Z'])
    primary_coord_offset = create_node(nodes, 'ShaderNodeVectorMath', (300, 800), 'primary_coord_offset', 'Primary Coord')
    primary_coord_offset.operation = 'ADD'
    links.new(tex_coord.outputs['Object'], primary_coord_offset.inputs[0])
    links.new(primary_seed_vec.outputs[0], primary_coord_offset.inputs[1])

    # Voronoi for cell distribution - use Position output for per-cell data
    primary_density_scaled = create_node(nodes, 'ShaderNodeMath', (300, 750), 'primary_density_scaled', 'Primary Density Scaled')
    primary_density_scaled.operation = 'MULTIPLY'
    links.new(primary_density_node.outputs[0], primary_density_scaled.inputs[0])
    links.new(global_density_mult_node.outputs[0], primary_density_scaled.inputs[1])

    primary_voronoi = create_node(nodes, 'ShaderNodeTexVoronoi', (500, 800), 'primary_voronoi', 'Primary Voronoi')
    primary_voronoi.voronoi_dimensions = '3D'
    primary_voronoi.feature = 'F1'
    links.new(primary_coord_offset.outputs[0], primary_voronoi.inputs['Vector'])
    links.new(primary_density_scaled.outputs[0], primary_voronoi.inputs['Scale'])

    # Size with variation (use Position for per-cell consistent randomness)
    primary_size_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (500, 700), 'primary_size_noise', 'Primary Size Noise')
    primary_size_noise.noise_dimensions = '3D'
    links.new(primary_voronoi.outputs['Position'], primary_size_noise.inputs['Vector'])

    primary_size_var_calc = create_node(nodes, 'ShaderNodeMapRange', (700, 700), 'primary_size_var_calc', 'Primary Size Var')
    links.new(primary_size_noise.outputs['Value'], primary_size_var_calc.inputs['Value'])
    primary_size_var_calc.inputs['From Min'].default_value = 0.0
    primary_size_var_calc.inputs['From Max'].default_value = 1.0
    # To Min = 1 - size_var, To Max = 1
    primary_size_var_min = create_node(nodes, 'ShaderNodeMath', (500, 650), 'primary_size_var_min', 'Primary Var Min')
    primary_size_var_min.operation = 'SUBTRACT'
    primary_size_var_min.inputs[0].default_value = 1.0
    links.new(primary_size_var_node.outputs[0], primary_size_var_min.inputs[1])
    links.new(primary_size_var_min.outputs[0], primary_size_var_calc.inputs['To Min'])
    primary_size_var_calc.inputs['To Max'].default_value = 1.0

    primary_size_final = create_node(nodes, 'ShaderNodeMath', (900, 700), 'primary_size_final', 'Primary Size')
    primary_size_final.operation = 'MULTIPLY'
    links.new(primary_size_var_calc.outputs[0], primary_size_final.inputs[0])
    links.new(primary_size_node.outputs[0], primary_size_final.inputs[1])

    primary_size_scaled = create_node(nodes, 'ShaderNodeMath', (1000, 720), 'primary_size_scaled', 'Primary Size Scaled')
    primary_size_scaled.operation = 'MULTIPLY'
    links.new(primary_size_final.outputs[0], primary_size_scaled.inputs[0])
    links.new(global_size_mult_node.outputs[0], primary_size_scaled.inputs[1])

    # Cell mask: distance < size
    primary_mask = create_node(nodes, 'ShaderNodeMath', (1100, 750), 'primary_mask', 'Primary Mask')
    primary_mask.operation = 'LESS_THAN'
    links.new(primary_voronoi.outputs['Distance'], primary_mask.inputs[0])
    links.new(primary_size_scaled.outputs[0], primary_mask.inputs[1])

    # Generate per-cell flake normal using Voronoi Position (consistent within cell)
    # X component
    primary_normal_x_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 600), 'primary_normal_x', 'Primary Norm X')
    primary_normal_x_noise.noise_dimensions = '3D'
    links.new(primary_voronoi.outputs['Position'], primary_normal_x_noise.inputs['Vector'])

    # Y component (offset position for different random value)
    primary_normal_y_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, 550), 'primary_ny_offset', 'Primary NY Offset')
    primary_normal_y_offset.operation = 'ADD'
    links.new(primary_voronoi.outputs['Position'], primary_normal_y_offset.inputs[0])
    primary_normal_y_offset.inputs[1].default_value = (73.156, 0.0, 0.0)
    primary_normal_y_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 550), 'primary_normal_y', 'Primary Norm Y')
    primary_normal_y_noise.noise_dimensions = '3D'
    links.new(primary_normal_y_offset.outputs[0], primary_normal_y_noise.inputs['Vector'])

    # Z component
    primary_normal_z_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, 500), 'primary_nz_offset', 'Primary NZ Offset')
    primary_normal_z_offset.operation = 'ADD'
    links.new(primary_voronoi.outputs['Position'], primary_normal_z_offset.inputs[0])
    primary_normal_z_offset.inputs[1].default_value = (0.0, 91.372, 0.0)
    primary_normal_z_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 500), 'primary_normal_z', 'Primary Norm Z')
    primary_normal_z_noise.noise_dimensions = '3D'
    links.new(primary_normal_z_offset.outputs[0], primary_normal_z_noise.inputs['Vector'])

    # Map X,Y to -1..1, Z to 0.3..1 (biased upward/toward surface)
    primary_nx_map = create_node(nodes, 'ShaderNodeMapRange', (900, 600), 'primary_nx_map', 'Primary NX Map')
    primary_nx_map.inputs['To Min'].default_value = -1.0
    primary_nx_map.inputs['To Max'].default_value = 1.0
    links.new(primary_normal_x_noise.outputs['Value'], primary_nx_map.inputs['Value'])

    primary_ny_map = create_node(nodes, 'ShaderNodeMapRange', (900, 550), 'primary_ny_map', 'Primary NY Map')
    primary_ny_map.inputs['To Min'].default_value = -1.0
    primary_ny_map.inputs['To Max'].default_value = 1.0
    links.new(primary_normal_y_noise.outputs['Value'], primary_ny_map.inputs['Value'])

    primary_nz_map = create_node(nodes, 'ShaderNodeMapRange', (900, 500), 'primary_nz_map', 'Primary NZ Map')
    primary_nz_map.inputs['To Min'].default_value = 0.3
    primary_nz_map.inputs['To Max'].default_value = 1.0
    links.new(primary_normal_z_noise.outputs['Value'], primary_nz_map.inputs['Value'])

    # Combine into random direction vector
    primary_random_dir = create_node(nodes, 'ShaderNodeCombineXYZ', (1100, 550), 'primary_random_dir', 'Primary Rand Dir')
    links.new(primary_nx_map.outputs[0], primary_random_dir.inputs['X'])
    links.new(primary_ny_map.outputs[0], primary_random_dir.inputs['Y'])
    links.new(primary_nz_map.outputs[0], primary_random_dir.inputs['Z'])

    primary_random_norm = create_node(nodes, 'ShaderNodeVectorMath', (1300, 550), 'primary_random_norm', 'Primary Rand Norm')
    primary_random_norm.operation = 'NORMALIZE'
    links.new(primary_random_dir.outputs[0], primary_random_norm.inputs[0])

    # Mix random normal with surface normal based on orientation_randomness
    # 0 = surface normal (flat), 1 = random (wild sparkles)
    primary_flake_normal = create_node(nodes, 'ShaderNodeMix', (1500, 550), 'primary_flake_normal', 'Primary Flake N')
    primary_flake_normal.data_type = 'VECTOR'
    links.new(orientation_randomness_node.outputs[0], primary_flake_normal.inputs['Factor'])
    links.new(final_normal.outputs[1], primary_flake_normal.inputs[4])  # A (factor=0)
    links.new(primary_random_norm.outputs[0], primary_flake_normal.inputs[5])  # B (factor=1)

    primary_flake_normal_norm = create_node(nodes, 'ShaderNodeVectorMath', (1700, 550), 'primary_flake_n_norm', 'Primary Flake Norm')
    primary_flake_normal_norm.operation = 'NORMALIZE'
    links.new(primary_flake_normal.outputs[1], primary_flake_normal_norm.inputs[0])

    # Dot product: how well does the flake normal face the camera?
    primary_flake_dot = create_node(nodes, 'ShaderNodeVectorMath', (1900, 600), 'primary_flake_dot', 'Primary Flake Dot')
    primary_flake_dot.operation = 'DOT_PRODUCT'
    links.new(primary_flake_normal_norm.outputs[0], primary_flake_dot.inputs[0])
    links.new(view_negate.outputs[0], primary_flake_dot.inputs[1])

    # Deviation: how much does this flake differ from surface baseline?
    primary_deviation = create_node(nodes, 'ShaderNodeMath', (2100, 600), 'primary_deviation', 'Primary Deviation')
    primary_deviation.operation = 'SUBTRACT'
    links.new(primary_flake_dot.outputs['Value'], primary_deviation.inputs[0])
    links.new(surface_dot.outputs['Value'], primary_deviation.inputs[1])

    # Normalize deviation to full 0-1 range using dynamic Map Range
    # Maps [-orientation_randomness, +orientation_randomness] -> [0, 1]
    primary_dev_map = create_node(nodes, 'ShaderNodeMapRange', (2300, 600), 'primary_dev_map', 'Primary Dev Normalize')
    links.new(primary_deviation.outputs[0], primary_dev_map.inputs['Value'])
    links.new(neg_orient_rand.outputs[0], primary_dev_map.inputs['From Min'])
    links.new(orient_rand_safe.outputs[0], primary_dev_map.inputs['From Max'])
    primary_dev_map.inputs['To Min'].default_value = 0.0
    primary_dev_map.inputs['To Max'].default_value = 1.0

    # Apply sharpness: pow(normalized_deviation, sharpness)
    primary_sparkle_sharp = create_node(nodes, 'ShaderNodeMath', (2500, 600), 'primary_sparkle_sharp', 'Primary Sharp')
    primary_sparkle_sharp.operation = 'POWER'
    links.new(primary_dev_map.outputs[0], primary_sparkle_sharp.inputs[0])
    links.new(sparkle_sharpness_node.outputs[0], primary_sparkle_sharp.inputs[1])

    # Combine: mask * view_visibility * intensity * overdrive * enable
    primary_vis_masked = create_node(nodes, 'ShaderNodeMath', (2700, 650), 'primary_vis_masked', 'Primary Vis Mask')
    primary_vis_masked.operation = 'MULTIPLY'
    links.new(primary_mask.outputs[0], primary_vis_masked.inputs[0])
    links.new(primary_sparkle_sharp.outputs[0], primary_vis_masked.inputs[1])

    primary_vis_intensity = create_node(nodes, 'ShaderNodeMath', (2900, 650), 'primary_vis_int', 'Primary Vis Int')
    primary_vis_intensity.operation = 'MULTIPLY'
    links.new(primary_vis_masked.outputs[0], primary_vis_intensity.inputs[0])
    links.new(primary_intensity_node.outputs[0], primary_vis_intensity.inputs[1])

    primary_vis_od = create_node(nodes, 'ShaderNodeMath', (3100, 650), 'primary_vis_od', 'Primary Vis OD')
    primary_vis_od.operation = 'MULTIPLY'
    links.new(primary_vis_intensity.outputs[0], primary_vis_od.inputs[0])
    links.new(overdrive_node.outputs[0], primary_vis_od.inputs[1])

    primary_enabled = create_node(nodes, 'ShaderNodeMath', (3300, 650), 'primary_enabled', 'Primary Enabled')
    primary_enabled.operation = 'MULTIPLY'
    links.new(primary_vis_od.outputs[0], primary_enabled.inputs[0])
    links.new(primary_enable_node.outputs[0], primary_enabled.inputs[1])

    # ==========================================================================
    # SECONDARY SPARKLE LAYER - View Based
    # ==========================================================================

    secondary_seed_vec = create_node(nodes, 'ShaderNodeCombineXYZ', (100, 350), 'secondary_seed_vec', 'Secondary Seed Vec')
    links.new(secondary_seed_node.outputs[0], secondary_seed_vec.inputs['X'])
    links.new(secondary_seed_node.outputs[0], secondary_seed_vec.inputs['Y'])
    links.new(secondary_seed_node.outputs[0], secondary_seed_vec.inputs['Z'])
    secondary_coord_offset = create_node(nodes, 'ShaderNodeVectorMath', (300, 300), 'secondary_coord_offset', 'Secondary Coord')
    secondary_coord_offset.operation = 'ADD'
    links.new(tex_coord.outputs['Object'], secondary_coord_offset.inputs[0])
    links.new(secondary_seed_vec.outputs[0], secondary_coord_offset.inputs[1])

    secondary_density_scaled = create_node(nodes, 'ShaderNodeMath', (300, 250), 'secondary_density_scaled', 'Secondary Density Scaled')
    secondary_density_scaled.operation = 'MULTIPLY'
    links.new(secondary_density_node.outputs[0], secondary_density_scaled.inputs[0])
    links.new(global_density_mult_node.outputs[0], secondary_density_scaled.inputs[1])

    secondary_voronoi = create_node(nodes, 'ShaderNodeTexVoronoi', (500, 300), 'secondary_voronoi', 'Secondary Voronoi')
    secondary_voronoi.voronoi_dimensions = '3D'
    secondary_voronoi.feature = 'F1'
    links.new(secondary_coord_offset.outputs[0], secondary_voronoi.inputs['Vector'])
    links.new(secondary_density_scaled.outputs[0], secondary_voronoi.inputs['Scale'])

    secondary_size_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (500, 200), 'secondary_size_noise', 'Secondary Size Noise')
    secondary_size_noise.noise_dimensions = '3D'
    links.new(secondary_voronoi.outputs['Position'], secondary_size_noise.inputs['Vector'])

    secondary_size_var_min = create_node(nodes, 'ShaderNodeMath', (500, 150), 'secondary_size_var_min', 'Secondary Var Min')
    secondary_size_var_min.operation = 'SUBTRACT'
    secondary_size_var_min.inputs[0].default_value = 1.0
    links.new(secondary_size_var_node.outputs[0], secondary_size_var_min.inputs[1])

    secondary_size_var_calc = create_node(nodes, 'ShaderNodeMapRange', (700, 200), 'secondary_size_var_calc', 'Secondary Size Var')
    links.new(secondary_size_noise.outputs['Value'], secondary_size_var_calc.inputs['Value'])
    links.new(secondary_size_var_min.outputs[0], secondary_size_var_calc.inputs['To Min'])
    secondary_size_var_calc.inputs['To Max'].default_value = 1.0

    secondary_size_final = create_node(nodes, 'ShaderNodeMath', (900, 200), 'secondary_size_final', 'Secondary Size')
    secondary_size_final.operation = 'MULTIPLY'
    links.new(secondary_size_var_calc.outputs[0], secondary_size_final.inputs[0])
    links.new(secondary_size_node.outputs[0], secondary_size_final.inputs[1])

    secondary_size_scaled = create_node(nodes, 'ShaderNodeMath', (1000, 220), 'secondary_size_scaled', 'Secondary Size Scaled')
    secondary_size_scaled.operation = 'MULTIPLY'
    links.new(secondary_size_final.outputs[0], secondary_size_scaled.inputs[0])
    links.new(global_size_mult_node.outputs[0], secondary_size_scaled.inputs[1])

    secondary_mask = create_node(nodes, 'ShaderNodeMath', (1100, 250), 'secondary_mask', 'Secondary Mask')
    secondary_mask.operation = 'LESS_THAN'
    links.new(secondary_voronoi.outputs['Distance'], secondary_mask.inputs[0])
    links.new(secondary_size_scaled.outputs[0], secondary_mask.inputs[1])

    # Per-cell normal for secondary
    secondary_normal_x_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 100), 'secondary_normal_x', 'Secondary Norm X')
    secondary_normal_x_noise.noise_dimensions = '3D'
    links.new(secondary_voronoi.outputs['Position'], secondary_normal_x_noise.inputs['Vector'])

    secondary_normal_y_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, 50), 'secondary_ny_offset', 'Secondary NY Off')
    secondary_normal_y_offset.operation = 'ADD'
    links.new(secondary_voronoi.outputs['Position'], secondary_normal_y_offset.inputs[0])
    secondary_normal_y_offset.inputs[1].default_value = (73.156, 0.0, 0.0)
    secondary_normal_y_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 50), 'secondary_normal_y', 'Secondary Norm Y')
    secondary_normal_y_noise.noise_dimensions = '3D'
    links.new(secondary_normal_y_offset.outputs[0], secondary_normal_y_noise.inputs['Vector'])

    secondary_normal_z_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, 0), 'secondary_nz_offset', 'Secondary NZ Off')
    secondary_normal_z_offset.operation = 'ADD'
    links.new(secondary_voronoi.outputs['Position'], secondary_normal_z_offset.inputs[0])
    secondary_normal_z_offset.inputs[1].default_value = (0.0, 91.372, 0.0)
    secondary_normal_z_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 0), 'secondary_normal_z', 'Secondary Norm Z')
    secondary_normal_z_noise.noise_dimensions = '3D'
    links.new(secondary_normal_z_offset.outputs[0], secondary_normal_z_noise.inputs['Vector'])

    secondary_nx_map = create_node(nodes, 'ShaderNodeMapRange', (900, 100), 'secondary_nx_map', 'Secondary NX Map')
    secondary_nx_map.inputs['To Min'].default_value = -1.0
    secondary_nx_map.inputs['To Max'].default_value = 1.0
    links.new(secondary_normal_x_noise.outputs['Value'], secondary_nx_map.inputs['Value'])

    secondary_ny_map = create_node(nodes, 'ShaderNodeMapRange', (900, 50), 'secondary_ny_map', 'Secondary NY Map')
    secondary_ny_map.inputs['To Min'].default_value = -1.0
    secondary_ny_map.inputs['To Max'].default_value = 1.0
    links.new(secondary_normal_y_noise.outputs['Value'], secondary_ny_map.inputs['Value'])

    secondary_nz_map = create_node(nodes, 'ShaderNodeMapRange', (900, 0), 'secondary_nz_map', 'Secondary NZ Map')
    secondary_nz_map.inputs['To Min'].default_value = 0.3
    secondary_nz_map.inputs['To Max'].default_value = 1.0
    links.new(secondary_normal_z_noise.outputs['Value'], secondary_nz_map.inputs['Value'])

    secondary_random_dir = create_node(nodes, 'ShaderNodeCombineXYZ', (1100, 50), 'secondary_random_dir', 'Secondary Rand Dir')
    links.new(secondary_nx_map.outputs[0], secondary_random_dir.inputs['X'])
    links.new(secondary_ny_map.outputs[0], secondary_random_dir.inputs['Y'])
    links.new(secondary_nz_map.outputs[0], secondary_random_dir.inputs['Z'])

    secondary_random_norm = create_node(nodes, 'ShaderNodeVectorMath', (1300, 50), 'secondary_random_norm', 'Secondary Rand Norm')
    secondary_random_norm.operation = 'NORMALIZE'
    links.new(secondary_random_dir.outputs[0], secondary_random_norm.inputs[0])

    secondary_flake_normal = create_node(nodes, 'ShaderNodeMix', (1500, 50), 'secondary_flake_normal', 'Secondary Flake N')
    secondary_flake_normal.data_type = 'VECTOR'
    links.new(orientation_randomness_node.outputs[0], secondary_flake_normal.inputs['Factor'])
    links.new(final_normal.outputs[1], secondary_flake_normal.inputs[4])
    links.new(secondary_random_norm.outputs[0], secondary_flake_normal.inputs[5])

    secondary_flake_normal_norm = create_node(nodes, 'ShaderNodeVectorMath', (1700, 50), 'secondary_flake_n_norm', 'Secondary Flake Norm')
    secondary_flake_normal_norm.operation = 'NORMALIZE'
    links.new(secondary_flake_normal.outputs[1], secondary_flake_normal_norm.inputs[0])

    # Dot product: how well does the flake normal face the camera?
    secondary_flake_dot = create_node(nodes, 'ShaderNodeVectorMath', (1900, 100), 'secondary_flake_dot', 'Secondary Flake Dot')
    secondary_flake_dot.operation = 'DOT_PRODUCT'
    links.new(secondary_flake_normal_norm.outputs[0], secondary_flake_dot.inputs[0])
    links.new(view_negate.outputs[0], secondary_flake_dot.inputs[1])

    # Deviation from surface baseline
    secondary_deviation = create_node(nodes, 'ShaderNodeMath', (2100, 100), 'secondary_deviation', 'Secondary Deviation')
    secondary_deviation.operation = 'SUBTRACT'
    links.new(secondary_flake_dot.outputs['Value'], secondary_deviation.inputs[0])
    links.new(surface_dot.outputs['Value'], secondary_deviation.inputs[1])

    # Normalize deviation to full 0-1 range using dynamic Map Range
    secondary_dev_map = create_node(nodes, 'ShaderNodeMapRange', (2300, 100), 'secondary_dev_map', 'Secondary Dev Normalize')
    links.new(secondary_deviation.outputs[0], secondary_dev_map.inputs['Value'])
    links.new(neg_orient_rand.outputs[0], secondary_dev_map.inputs['From Min'])
    links.new(orient_rand_safe.outputs[0], secondary_dev_map.inputs['From Max'])
    secondary_dev_map.inputs['To Min'].default_value = 0.0
    secondary_dev_map.inputs['To Max'].default_value = 1.0

    secondary_sparkle_sharp = create_node(nodes, 'ShaderNodeMath', (2500, 100), 'secondary_sparkle_sharp', 'Secondary Sharp')
    secondary_sparkle_sharp.operation = 'POWER'
    links.new(secondary_dev_map.outputs[0], secondary_sparkle_sharp.inputs[0])
    links.new(sparkle_sharpness_node.outputs[0], secondary_sparkle_sharp.inputs[1])

    secondary_vis_masked = create_node(nodes, 'ShaderNodeMath', (2700, 150), 'secondary_vis_masked', 'Secondary Vis Mask')
    secondary_vis_masked.operation = 'MULTIPLY'
    links.new(secondary_mask.outputs[0], secondary_vis_masked.inputs[0])
    links.new(secondary_sparkle_sharp.outputs[0], secondary_vis_masked.inputs[1])

    secondary_vis_intensity = create_node(nodes, 'ShaderNodeMath', (2900, 150), 'secondary_vis_int', 'Secondary Vis Int')
    secondary_vis_intensity.operation = 'MULTIPLY'
    links.new(secondary_vis_masked.outputs[0], secondary_vis_intensity.inputs[0])
    links.new(secondary_intensity_node.outputs[0], secondary_vis_intensity.inputs[1])

    secondary_vis_od = create_node(nodes, 'ShaderNodeMath', (3100, 150), 'secondary_vis_od', 'Secondary Vis OD')
    secondary_vis_od.operation = 'MULTIPLY'
    links.new(secondary_vis_intensity.outputs[0], secondary_vis_od.inputs[0])
    links.new(overdrive_node.outputs[0], secondary_vis_od.inputs[1])

    secondary_enabled = create_node(nodes, 'ShaderNodeMath', (3300, 150), 'secondary_enabled', 'Secondary Enabled')
    secondary_enabled.operation = 'MULTIPLY'
    links.new(secondary_vis_od.outputs[0], secondary_enabled.inputs[0])
    links.new(secondary_enable_node.outputs[0], secondary_enabled.inputs[1])

    # ==========================================================================
    # TERTIARY SPARKLE LAYER - View Based
    # ==========================================================================

    tertiary_seed_vec = create_node(nodes, 'ShaderNodeCombineXYZ', (100, -150), 'tertiary_seed_vec', 'Tertiary Seed Vec')
    links.new(tertiary_seed_node.outputs[0], tertiary_seed_vec.inputs['X'])
    links.new(tertiary_seed_node.outputs[0], tertiary_seed_vec.inputs['Y'])
    links.new(tertiary_seed_node.outputs[0], tertiary_seed_vec.inputs['Z'])
    tertiary_coord_offset = create_node(nodes, 'ShaderNodeVectorMath', (300, -200), 'tertiary_coord_offset', 'Tertiary Coord')
    tertiary_coord_offset.operation = 'ADD'
    links.new(tex_coord.outputs['Object'], tertiary_coord_offset.inputs[0])
    links.new(tertiary_seed_vec.outputs[0], tertiary_coord_offset.inputs[1])

    tertiary_density_scaled = create_node(nodes, 'ShaderNodeMath', (300, -250), 'tertiary_density_scaled', 'Tertiary Density Scaled')
    tertiary_density_scaled.operation = 'MULTIPLY'
    links.new(tertiary_density_node.outputs[0], tertiary_density_scaled.inputs[0])
    links.new(global_density_mult_node.outputs[0], tertiary_density_scaled.inputs[1])

    tertiary_voronoi = create_node(nodes, 'ShaderNodeTexVoronoi', (500, -200), 'tertiary_voronoi', 'Tertiary Voronoi')
    tertiary_voronoi.voronoi_dimensions = '3D'
    tertiary_voronoi.feature = 'F1'
    links.new(tertiary_coord_offset.outputs[0], tertiary_voronoi.inputs['Vector'])
    links.new(tertiary_density_scaled.outputs[0], tertiary_voronoi.inputs['Scale'])

    tertiary_size_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (500, -300), 'tertiary_size_noise', 'Tertiary Size Noise')
    tertiary_size_noise.noise_dimensions = '3D'
    links.new(tertiary_voronoi.outputs['Position'], tertiary_size_noise.inputs['Vector'])

    tertiary_size_var_min = create_node(nodes, 'ShaderNodeMath', (500, -350), 'tertiary_size_var_min', 'Tertiary Var Min')
    tertiary_size_var_min.operation = 'SUBTRACT'
    tertiary_size_var_min.inputs[0].default_value = 1.0
    links.new(tertiary_size_var_node.outputs[0], tertiary_size_var_min.inputs[1])

    tertiary_size_var_calc = create_node(nodes, 'ShaderNodeMapRange', (700, -300), 'tertiary_size_var_calc', 'Tertiary Size Var')
    links.new(tertiary_size_noise.outputs['Value'], tertiary_size_var_calc.inputs['Value'])
    links.new(tertiary_size_var_min.outputs[0], tertiary_size_var_calc.inputs['To Min'])
    tertiary_size_var_calc.inputs['To Max'].default_value = 1.0

    tertiary_size_final = create_node(nodes, 'ShaderNodeMath', (900, -300), 'tertiary_size_final', 'Tertiary Size')
    tertiary_size_final.operation = 'MULTIPLY'
    links.new(tertiary_size_var_calc.outputs[0], tertiary_size_final.inputs[0])
    links.new(tertiary_size_node.outputs[0], tertiary_size_final.inputs[1])

    tertiary_size_scaled = create_node(nodes, 'ShaderNodeMath', (1000, -280), 'tertiary_size_scaled', 'Tertiary Size Scaled')
    tertiary_size_scaled.operation = 'MULTIPLY'
    links.new(tertiary_size_final.outputs[0], tertiary_size_scaled.inputs[0])
    links.new(global_size_mult_node.outputs[0], tertiary_size_scaled.inputs[1])

    tertiary_mask = create_node(nodes, 'ShaderNodeMath', (1100, -250), 'tertiary_mask', 'Tertiary Mask')
    tertiary_mask.operation = 'LESS_THAN'
    links.new(tertiary_voronoi.outputs['Distance'], tertiary_mask.inputs[0])
    links.new(tertiary_size_scaled.outputs[0], tertiary_mask.inputs[1])

    # Per-cell normal for tertiary
    tertiary_normal_x_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, -400), 'tertiary_normal_x', 'Tertiary Norm X')
    tertiary_normal_x_noise.noise_dimensions = '3D'
    links.new(tertiary_voronoi.outputs['Position'], tertiary_normal_x_noise.inputs['Vector'])

    tertiary_normal_y_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, -450), 'tertiary_ny_offset', 'Tertiary NY Off')
    tertiary_normal_y_offset.operation = 'ADD'
    links.new(tertiary_voronoi.outputs['Position'], tertiary_normal_y_offset.inputs[0])
    tertiary_normal_y_offset.inputs[1].default_value = (73.156, 0.0, 0.0)
    tertiary_normal_y_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, -450), 'tertiary_normal_y', 'Tertiary Norm Y')
    tertiary_normal_y_noise.noise_dimensions = '3D'
    links.new(tertiary_normal_y_offset.outputs[0], tertiary_normal_y_noise.inputs['Vector'])

    tertiary_normal_z_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, -500), 'tertiary_nz_offset', 'Tertiary NZ Off')
    tertiary_normal_z_offset.operation = 'ADD'
    links.new(tertiary_voronoi.outputs['Position'], tertiary_normal_z_offset.inputs[0])
    tertiary_normal_z_offset.inputs[1].default_value = (0.0, 91.372, 0.0)
    tertiary_normal_z_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, -500), 'tertiary_normal_z', 'Tertiary Norm Z')
    tertiary_normal_z_noise.noise_dimensions = '3D'
    links.new(tertiary_normal_z_offset.outputs[0], tertiary_normal_z_noise.inputs['Vector'])

    tertiary_nx_map = create_node(nodes, 'ShaderNodeMapRange', (900, -400), 'tertiary_nx_map', 'Tertiary NX Map')
    tertiary_nx_map.inputs['To Min'].default_value = -1.0
    tertiary_nx_map.inputs['To Max'].default_value = 1.0
    links.new(tertiary_normal_x_noise.outputs['Value'], tertiary_nx_map.inputs['Value'])

    tertiary_ny_map = create_node(nodes, 'ShaderNodeMapRange', (900, -450), 'tertiary_ny_map', 'Tertiary NY Map')
    tertiary_ny_map.inputs['To Min'].default_value = -1.0
    tertiary_ny_map.inputs['To Max'].default_value = 1.0
    links.new(tertiary_normal_y_noise.outputs['Value'], tertiary_ny_map.inputs['Value'])

    tertiary_nz_map = create_node(nodes, 'ShaderNodeMapRange', (900, -500), 'tertiary_nz_map', 'Tertiary NZ Map')
    tertiary_nz_map.inputs['To Min'].default_value = 0.3
    tertiary_nz_map.inputs['To Max'].default_value = 1.0
    links.new(tertiary_normal_z_noise.outputs['Value'], tertiary_nz_map.inputs['Value'])

    tertiary_random_dir = create_node(nodes, 'ShaderNodeCombineXYZ', (1100, -450), 'tertiary_random_dir', 'Tertiary Rand Dir')
    links.new(tertiary_nx_map.outputs[0], tertiary_random_dir.inputs['X'])
    links.new(tertiary_ny_map.outputs[0], tertiary_random_dir.inputs['Y'])
    links.new(tertiary_nz_map.outputs[0], tertiary_random_dir.inputs['Z'])

    tertiary_random_norm = create_node(nodes, 'ShaderNodeVectorMath', (1300, -450), 'tertiary_random_norm', 'Tertiary Rand Norm')
    tertiary_random_norm.operation = 'NORMALIZE'
    links.new(tertiary_random_dir.outputs[0], tertiary_random_norm.inputs[0])

    tertiary_flake_normal = create_node(nodes, 'ShaderNodeMix', (1500, -450), 'tertiary_flake_normal', 'Tertiary Flake N')
    tertiary_flake_normal.data_type = 'VECTOR'
    links.new(orientation_randomness_node.outputs[0], tertiary_flake_normal.inputs['Factor'])
    links.new(final_normal.outputs[1], tertiary_flake_normal.inputs[4])
    links.new(tertiary_random_norm.outputs[0], tertiary_flake_normal.inputs[5])

    tertiary_flake_normal_norm = create_node(nodes, 'ShaderNodeVectorMath', (1700, -450), 'tertiary_flake_n_norm', 'Tertiary Flake Norm')
    tertiary_flake_normal_norm.operation = 'NORMALIZE'
    links.new(tertiary_flake_normal.outputs[1], tertiary_flake_normal_norm.inputs[0])

    # Dot product: how well does the flake normal face the camera?
    tertiary_flake_dot = create_node(nodes, 'ShaderNodeVectorMath', (1900, -400), 'tertiary_flake_dot', 'Tertiary Flake Dot')
    tertiary_flake_dot.operation = 'DOT_PRODUCT'
    links.new(tertiary_flake_normal_norm.outputs[0], tertiary_flake_dot.inputs[0])
    links.new(view_negate.outputs[0], tertiary_flake_dot.inputs[1])

    # Deviation from surface baseline
    tertiary_deviation = create_node(nodes, 'ShaderNodeMath', (2100, -400), 'tertiary_deviation', 'Tertiary Deviation')
    tertiary_deviation.operation = 'SUBTRACT'
    links.new(tertiary_flake_dot.outputs['Value'], tertiary_deviation.inputs[0])
    links.new(surface_dot.outputs['Value'], tertiary_deviation.inputs[1])

    # Normalize deviation to full 0-1 range using dynamic Map Range
    tertiary_dev_map = create_node(nodes, 'ShaderNodeMapRange', (2300, -400), 'tertiary_dev_map', 'Tertiary Dev Normalize')
    links.new(tertiary_deviation.outputs[0], tertiary_dev_map.inputs['Value'])
    links.new(neg_orient_rand.outputs[0], tertiary_dev_map.inputs['From Min'])
    links.new(orient_rand_safe.outputs[0], tertiary_dev_map.inputs['From Max'])
    tertiary_dev_map.inputs['To Min'].default_value = 0.0
    tertiary_dev_map.inputs['To Max'].default_value = 1.0

    tertiary_sparkle_sharp = create_node(nodes, 'ShaderNodeMath', (2500, -400), 'tertiary_sparkle_sharp', 'Tertiary Sharp')
    tertiary_sparkle_sharp.operation = 'POWER'
    links.new(tertiary_dev_map.outputs[0], tertiary_sparkle_sharp.inputs[0])
    links.new(sparkle_sharpness_node.outputs[0], tertiary_sparkle_sharp.inputs[1])

    tertiary_vis_masked = create_node(nodes, 'ShaderNodeMath', (2700, -350), 'tertiary_vis_masked', 'Tertiary Vis Mask')
    tertiary_vis_masked.operation = 'MULTIPLY'
    links.new(tertiary_mask.outputs[0], tertiary_vis_masked.inputs[0])
    links.new(tertiary_sparkle_sharp.outputs[0], tertiary_vis_masked.inputs[1])

    tertiary_vis_intensity = create_node(nodes, 'ShaderNodeMath', (2900, -350), 'tertiary_vis_int', 'Tertiary Vis Int')
    tertiary_vis_intensity.operation = 'MULTIPLY'
    links.new(tertiary_vis_masked.outputs[0], tertiary_vis_intensity.inputs[0])
    links.new(tertiary_intensity_node.outputs[0], tertiary_vis_intensity.inputs[1])

    tertiary_vis_od = create_node(nodes, 'ShaderNodeMath', (3100, -350), 'tertiary_vis_od', 'Tertiary Vis OD')
    tertiary_vis_od.operation = 'MULTIPLY'
    links.new(tertiary_vis_intensity.outputs[0], tertiary_vis_od.inputs[0])
    links.new(overdrive_node.outputs[0], tertiary_vis_od.inputs[1])

    tertiary_enabled = create_node(nodes, 'ShaderNodeMath', (3300, -350), 'tertiary_enabled', 'Tertiary Enabled')
    tertiary_enabled.operation = 'MULTIPLY'
    links.new(tertiary_vis_od.outputs[0], tertiary_enabled.inputs[0])
    links.new(tertiary_enable_node.outputs[0], tertiary_enabled.inputs[1])

    # ==========================================================================
    # COMBINE SPARKLE LAYERS
    # ==========================================================================

    sparkle_1_2 = create_node(nodes, 'ShaderNodeMath', (3500, 400), 'sparkle_1_2', 'Primary + Secondary')
    sparkle_1_2.operation = 'ADD'
    links.new(primary_enabled.outputs[0], sparkle_1_2.inputs[0])
    links.new(secondary_enabled.outputs[0], sparkle_1_2.inputs[1])

    sparkle_all = create_node(nodes, 'ShaderNodeMath', (3700, 300), 'sparkle_all', 'All Sparkles')
    sparkle_all.operation = 'ADD'
    links.new(sparkle_1_2.outputs[0], sparkle_all.inputs[0])
    links.new(tertiary_enabled.outputs[0], sparkle_all.inputs[1])

    sparkle_clamp = create_node(nodes, 'ShaderNodeClamp', (3900, 300), 'sparkle_clamp', 'Sparkle Clamp')
    sparkle_clamp.inputs['Max'].default_value = 10.0  # Allow overdrive
    links.new(sparkle_all.outputs[0], sparkle_clamp.inputs['Value'])

    # ==========================================================================
    # COMBINED FLAKE NORMAL FOR BSDF
    # Use primary layer's flake normal as representative (they're similar)
    # ==========================================================================

    sparkle_normal_final = primary_flake_normal_norm  # Reuse primary's normal

    # ==========================================================================
    # SPARKLE BSDF
    # ==========================================================================

    # Sparkle roughness (directly from parameter, no depth blur)
    sparkle_rough_clamp = create_node(nodes, 'ShaderNodeClamp', (4100, -400), 'sparkle_rough_clamp', 'Sparkle Rough')
    links.new(sparkle_roughness_node.outputs[0], sparkle_rough_clamp.inputs['Value'])
    
    # Sparkle BSDF
    sparkle_bsdf = create_node(nodes, 'ShaderNodeBsdfPrincipled', (2800, 200), 'sparkle_bsdf', 'Sparkle BSDF')
    links.new(sparkle_with_base.outputs[2], sparkle_bsdf.inputs['Base Color'])
    links.new(sparkle_metallic_node.outputs[0], sparkle_bsdf.inputs['Metallic'])
    links.new(sparkle_rough_clamp.outputs[0], sparkle_bsdf.inputs['Roughness'])
    links.new(sparkle_normal_final.outputs[0], sparkle_bsdf.inputs['Normal'])
    
    # Emission from overdrive
    emission_calc = create_node(nodes, 'ShaderNodeMath', (2600, 100), 'emission_calc', 'Emission Calc')
    emission_calc.operation = 'MULTIPLY'
    links.new(sparkle_clamp.outputs[0], emission_calc.inputs[0])
    links.new(emission_str_node.outputs[0], emission_calc.inputs[1])
    
    links.new(emission_calc.outputs[0], sparkle_bsdf.inputs['Emission Strength'])
    links.new(sparkle_with_base.outputs[2], sparkle_bsdf.inputs['Emission Color'])
    
    # ==========================================================================
    # FINAL ROUGHNESS WITH MOLD
    # ==========================================================================
    
    roughness_with_mold = create_node(nodes, 'ShaderNodeMath', (2700, 50), 'roughness_with_mold', 'Rough + Mold')
    roughness_with_mold.operation = 'ADD'
    links.new(clamp_roughness.outputs[0], roughness_with_mold.inputs[0])
    links.new(mold_rough_final.outputs[0], roughness_with_mold.inputs[1])
    
    roughness_final_clamp = create_node(nodes, 'ShaderNodeClamp', (2850, 50), 'roughness_final_clamp', 'Final Rough')
    links.new(roughness_with_mold.outputs[0], roughness_final_clamp.inputs['Value'])
    
    # ==========================================================================
    # BASE PLASTIC BSDF
    # ==========================================================================
    
    plastic_bsdf = create_node(nodes, 'ShaderNodeBsdfPrincipled', (3000, -100), 'plastic_bsdf', 'Plastic BSDF')
    # Zero out BSDF subsurface defaults so SSS is fully off until our nodes provide values
    plastic_bsdf.inputs['Subsurface Weight'].default_value = 0.0
    plastic_bsdf.inputs['Subsurface Scale'].default_value = 0.0
    links.new(base_color_with_ao.outputs[2], plastic_bsdf.inputs['Base Color'])
    links.new(roughness_final_clamp.outputs[0], plastic_bsdf.inputs['Roughness'])  # FIXED: Use mold-adjusted roughness
    links.new(ior_node.outputs[0], plastic_bsdf.inputs['IOR'])
    links.new(final_normal.outputs[1], plastic_bsdf.inputs['Normal'])
    links.new(aniso_tangent.outputs[0], plastic_bsdf.inputs['Tangent'])
    links.new(sss_weight_node.outputs[0], plastic_bsdf.inputs['Subsurface Weight'])
    links.new(sss_radius_node.outputs[0], plastic_bsdf.inputs['Subsurface Radius'])
    links.new(sss_scale_node.outputs[0], plastic_bsdf.inputs['Subsurface Scale'])
    links.new(coat_weight_node.outputs[0], plastic_bsdf.inputs['Coat Weight'])
    links.new(coat_rough_node.outputs[0], plastic_bsdf.inputs['Coat Roughness'])
    links.new(aniso_rough_node.outputs[0], plastic_bsdf.inputs['Anisotropic'])
    
    # ==========================================================================
    # FINAL MIX
    # ==========================================================================
    
    # Mix plastic and sparkle based on combined sparkle factor
    # Clamp to 0-1 for mix factor
    mix_factor = create_node(nodes, 'ShaderNodeClamp', (3000, 100), 'mix_factor', 'Mix Factor')
    mix_factor.inputs['Min'].default_value = 0.0
    mix_factor.inputs['Max'].default_value = 1.0
    links.new(sparkle_clamp.outputs[0], mix_factor.inputs['Value'])
    
    plastic_sparkle_mix = create_node(nodes, 'ShaderNodeMixShader', (3200, 100), 'plastic_sparkle_mix', 'Plastic + Sparkle')
    links.new(mix_factor.outputs[0], plastic_sparkle_mix.inputs['Fac'])
    links.new(plastic_bsdf.outputs['BSDF'], plastic_sparkle_mix.inputs[1])
    links.new(sparkle_bsdf.outputs['BSDF'], plastic_sparkle_mix.inputs[2])
    
    # Overall effect mix
    overall_mix = create_node(nodes, 'ShaderNodeMixShader', (3400, 100), 'overall_mix', 'Overall Mix')
    links.new(overall_effect_node.outputs[0], overall_mix.inputs['Fac'])
    links.new(plastic_bsdf.outputs['BSDF'], overall_mix.inputs[1])
    links.new(plastic_sparkle_mix.outputs['Shader'], overall_mix.inputs[2])
    
    # Output
    output = create_node(nodes, 'ShaderNodeOutputMaterial', (3600, 100), 'output', 'Output')
    links.new(overall_mix.outputs['Shader'], output.inputs['Surface'])


def update_shader_from_properties(mat):
    """Update shader node values from material properties."""
    if not mat.use_nodes:
        return
    
    nodes = mat.node_tree.nodes
    props = mat.metallic_flake_plastic
    
    def set_value(name, value):
        if name in nodes:
            nodes[name].outputs[0].default_value = value
    
    def set_color(name, color):
        if name in nodes:
            nodes[name].outputs[0].default_value = color
    
    # Base Material
    set_color('base_color', props.base_color)
    set_value('base_roughness', props.base_roughness)
    set_value('ior', props.ior)
    
    # Surface Effects
    set_value('surface_grain_amount', props.surface_grain_amount if props.surface_grain_enable else 0.0)
    set_value('surface_grain_scale', props.surface_grain_scale)
    
    # Aniso
    set_value('aniso_intensity', props.aniso_intensity if props.aniso_enable else 0.0)
    set_value('aniso_scale', props.aniso_scale)
    set_value('aniso_ratio', props.aniso_ratio)
    set_value('aniso_angle', props.aniso_angle)
    set_value('aniso_normal_strength', props.aniso_normal_strength if props.aniso_enable else 0.0)
    set_value('aniso_roughness', props.aniso_roughness if props.aniso_enable else 0.0)
    
    # SSS - zero all parameters when disabled to fully eliminate subsurface
    set_value('sss_weight', props.sss_weight if props.sss_enable else 0.0)
    set_value('sss_radius', props.sss_radius if props.sss_enable else 0.0)
    set_value('sss_scale', props.sss_scale if props.sss_enable else 0.0)
    
    # Clearcoat
    set_value('coat_weight', props.clearcoat_weight if props.clearcoat_enable else 0.0)
    set_value('coat_roughness', props.clearcoat_roughness)
    
    # Primary Sparkles
    set_value('primary_enable', 1.0 if props.primary_enable else 0.0)
    set_value('primary_seed', float(props.primary_seed))
    set_value('primary_density', props.primary_density)
    set_value('primary_size', props.primary_size)
    set_value('primary_size_var', props.primary_size_var)
    set_value('primary_intensity', props.primary_intensity)

    # Secondary Sparkles
    set_value('secondary_enable', 1.0 if props.secondary_enable else 0.0)
    set_value('secondary_seed', float(props.secondary_seed))
    set_value('secondary_density', props.secondary_density)
    set_value('secondary_size', props.secondary_size)
    set_value('secondary_size_var', props.secondary_size_var)
    set_value('secondary_intensity', props.secondary_intensity)

    # Tertiary Sparkles
    set_value('tertiary_enable', 1.0 if props.tertiary_enable else 0.0)
    set_value('tertiary_seed', float(props.tertiary_seed))
    set_value('tertiary_density', props.tertiary_density)
    set_value('tertiary_size', props.tertiary_size)
    set_value('tertiary_size_var', props.tertiary_size_var)
    set_value('tertiary_intensity', props.tertiary_intensity)

    # Sparkle Color
    set_color('sparkle_color', props.sparkle_color)
    set_value('sparkle_hue_var', props.sparkle_hue_var)
    set_value('sparkle_sat_var', props.sparkle_sat_var)
    set_value('sparkle_val_var', props.sparkle_val_var)
    set_value('sparkle_base_influence', props.sparkle_base_influence)
    set_value('sparkle_metallic', props.sparkle_metallic)
    set_value('fresnel_shift', props.fresnel_shift)
    set_value('fresnel_direction', props.fresnel_direction)

    # Sparkle Response (new parameters)
    set_value('sparkle_roughness', props.sparkle_roughness)
    set_value('sparkle_sharpness', props.sparkle_sharpness)
    set_value('orientation_randomness', props.orientation_randomness)
    set_value('overdrive', props.overdrive)
    set_value('emission_strength', props.emission_strength)
    set_value('global_density_multiplier', props.global_density_multiplier)
    set_value('global_size_multiplier', props.global_size_multiplier)

    # Mold
    set_value('mold_enable', 1.0 if props.mold_enable else 0.0)
    set_value('mold_intensity', props.mold_intensity)
    set_value('mold_scale', props.mold_scale)
    set_value('mold_normal_strength', props.mold_normal_strength)
    set_value('mold_normal_invert', 1.0 if props.mold_normal_invert else 0.0)
    set_value('mold_bump_strength', props.mold_bump_strength)
    set_value('mold_bump_invert', 1.0 if props.mold_bump_invert else 0.0)
    set_value('mold_roughness_strength', props.mold_roughness_strength)
    set_value('mold_ao_strength', props.mold_ao_strength)
    
    # Overall
    set_value('overall_effect', props.overall_effect)


def update_textures_from_properties(mat):
    """Update texture node images."""
    if not mat.use_nodes:
        return
    
    nodes = mat.node_tree.nodes
    props = mat.metallic_flake_plastic
    
    texture_mapping = {
        'mold_normal_tex': props.mold_normal_map,
        'mold_disp_tex': props.mold_displacement_map,
        'mold_gloss_tex': props.mold_gloss_map,
        'mold_ao_tex': props.mold_ao_map,
    }
    
    for node_name, image in texture_mapping.items():
        if node_name in nodes:
            nodes[node_name].image = image
            if image:
                image.colorspace_settings.name = 'Non-Color'


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    MetallicFlakePlasticProperties,
    MATERIAL_OT_create_metallic_flake_plastic,
    MATERIAL_OT_mfp_apply_preset,
    MATERIAL_OT_mfp_save_preset,
    MATERIAL_OT_mfp_delete_preset,
    MATERIAL_PT_mfp_main,
    MATERIAL_PT_mfp_presets,
    MATERIAL_PT_mfp_base,
    MATERIAL_PT_mfp_surface,
    MATERIAL_PT_mfp_primary,
    MATERIAL_PT_mfp_secondary,
    MATERIAL_PT_mfp_tertiary,
    MATERIAL_PT_mfp_sparkle_color,
    MATERIAL_PT_mfp_lighting,
    MATERIAL_PT_mfp_mold,
    MATERIAL_PT_mfp_advanced,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.metallic_flake_plastic = PointerProperty(type=MetallicFlakePlasticProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Material.metallic_flake_plastic


if __name__ == "__main__":
    register()
