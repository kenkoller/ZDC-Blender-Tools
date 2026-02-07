"""
Universal PBR Shader v2.0.0
============================
Comprehensive PBR shader with full texture map support, metallic flake sparkle
system, and extensive built-in presets.

Features:
- 10 texture map slots (Base Color, Normal, Roughness, Metallic, Displacement,
  Height, AO, Opacity, Emission, Gloss)
- Shared UV mapping controls (scale, rotation, offset, projection mode)
- Per-map strength/influence and invert controls
- Optional three-layer sparkle system for metallic flake materials
- Surface grain, anisotropic grain, SSS, and clearcoat effects
- 13 built-in presets including 7 metallic flake material presets
- Full preset system with save/load

Created for Blender 5.0+
Author: Ziti Design & Creative
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
    return os.path.join(config_dir, 'universal_pbr_presets.json')


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
BUILTIN_PRESETS = {
    "default": {
        "name": "Default (Standard Plastic)",
        "description": "Neutral gray non-metallic plastic - good starting point",
        "values": {
            # Base
            "base_color": (0.5, 0.5, 0.5, 1.0),
            "base_roughness": 0.4,
            "base_metallic": 0.0,
            "ior": 1.46,
            # Surface
            "surface_grain_enable": True,
            "surface_grain_amount": 0.02,
            "surface_grain_scale": 120.0,
            "aniso_enable": False,
            # SSS
            "sss_enable": True,
            "sss_weight": 0.05,
            "sss_radius": 0.3,
            "sss_scale": 1.0,
            # Clearcoat
            "clearcoat_enable": True,
            "clearcoat_weight": 0.2,
            "clearcoat_roughness": 0.1,
            # Sparkle (OFF by default)
            "sparkle_enable": False,
            "primary_enable": True,
            "primary_density": 800.0,
            "primary_size": 0.10,
            "primary_size_var": 0.35,
            "primary_intensity": 1.0,
            "secondary_enable": True,
            "secondary_density": 500.0,
            "secondary_size": 0.08,
            "secondary_size_var": 0.4,
            "secondary_intensity": 0.8,
            "tertiary_enable": True,
            "tertiary_density": 80.0,
            "tertiary_size": 0.12,
            "tertiary_size_var": 0.5,
            "tertiary_intensity": 1.8,
            "sparkle_color": (0.9, 0.9, 0.9, 1.0),
            "sparkle_hue_var": 0.02,
            "sparkle_sat_var": 0.1,
            "sparkle_val_var": 0.15,
            "sparkle_base_influence": 0.1,
            "sparkle_metallic": 0.97,
            "fresnel_shift": 0.03,
            "fresnel_direction": 0.55,
            "sparkle_roughness": 0.06,
            "sparkle_sharpness": 5.0,
            "orientation_randomness": 0.20,
            "overdrive": 1.0,
            "emission_strength": 0.15,
            # Texture
            "tex_enable": False,
            # Advanced
            "overall_effect": 1.0,
        }
    },
    "metal_brushed": {
        "name": "Brushed Steel",
        "description": "Brushed stainless steel with anisotropic highlights",
        "values": {
            "base_color": (0.6, 0.6, 0.62, 1.0),
            "base_roughness": 0.35,
            "base_metallic": 0.95,
            "ior": 2.5,
            "surface_grain_enable": False,
            "surface_grain_amount": 0.0,
            "surface_grain_scale": 120.0,
            "aniso_enable": True,
            "aniso_intensity": 0.15,
            "aniso_scale": 300.0,
            "aniso_ratio": 0.08,
            "aniso_angle": 0.0,
            "aniso_normal_strength": 0.3,
            "aniso_roughness": 0.5,
            "sss_enable": False,
            "sss_weight": 0.0,
            "sss_radius": 0.0,
            "sss_scale": 0.0,
            "clearcoat_enable": False,
            "clearcoat_weight": 0.0,
            "clearcoat_roughness": 0.0,
            "sparkle_enable": False,
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "wood_base": {
        "name": "Wood Base",
        "description": "Base for wood materials - designed for adding wood textures",
        "values": {
            "base_color": (0.35, 0.22, 0.12, 1.0),
            "base_roughness": 0.55,
            "base_metallic": 0.0,
            "ior": 1.5,
            "surface_grain_enable": False,
            "surface_grain_amount": 0.0,
            "surface_grain_scale": 120.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.03,
            "sss_radius": 0.5,
            "sss_scale": 0.8,
            "clearcoat_enable": False,
            "clearcoat_weight": 0.0,
            "clearcoat_roughness": 0.0,
            "sparkle_enable": False,
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "ceramic": {
        "name": "Glazed Ceramic",
        "description": "Smooth glazed ceramic with heavy clearcoat",
        "values": {
            "base_color": (0.9, 0.88, 0.85, 1.0),
            "base_roughness": 0.15,
            "base_metallic": 0.0,
            "ior": 1.55,
            "surface_grain_enable": False,
            "surface_grain_amount": 0.0,
            "surface_grain_scale": 120.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.12,
            "sss_radius": 0.8,
            "sss_scale": 1.2,
            "clearcoat_enable": True,
            "clearcoat_weight": 0.8,
            "clearcoat_roughness": 0.02,
            "sparkle_enable": False,
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "rubber": {
        "name": "Soft Rubber",
        "description": "Soft matte rubber material with surface texture",
        "values": {
            "base_color": (0.15, 0.15, 0.15, 1.0),
            "base_roughness": 0.75,
            "base_metallic": 0.0,
            "ior": 1.52,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.06,
            "surface_grain_scale": 200.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.08,
            "sss_radius": 0.4,
            "sss_scale": 0.8,
            "clearcoat_enable": False,
            "clearcoat_weight": 0.0,
            "clearcoat_roughness": 0.0,
            "sparkle_enable": False,
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "glass_frosted": {
        "name": "Frosted Glass",
        "description": "Frosted translucent glass with high SSS",
        "values": {
            "base_color": (0.95, 0.95, 0.97, 1.0),
            "base_roughness": 0.25,
            "base_metallic": 0.0,
            "ior": 1.52,
            "surface_grain_enable": True,
            "surface_grain_amount": 0.01,
            "surface_grain_scale": 250.0,
            "aniso_enable": False,
            "sss_enable": True,
            "sss_weight": 0.35,
            "sss_radius": 1.5,
            "sss_scale": 2.0,
            "clearcoat_enable": True,
            "clearcoat_weight": 1.0,
            "clearcoat_roughness": 0.15,
            "sparkle_enable": False,
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    # =========================================================================
    # METALLIC FLAKE PRESETS (ported from metallic-flake-shader addon)
    # =========================================================================
    "metallic_flake_silver": {
        "name": "Metallic Flake \u2014 Silver Automotive",
        "description": "Classic silver car paint with fine metallic flakes",
        "values": {
            "base_color": (0.55, 0.55, 0.58, 1.0),
            "base_roughness": 0.30,
            "base_metallic": 0.0,
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
            "sparkle_enable": True,
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
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "metallic_flake_gold": {
        "name": "Metallic Flake \u2014 Gold",
        "description": "Warm gold metallic with brass-toned flakes",
        "values": {
            "base_color": (0.45, 0.35, 0.20, 1.0),
            "base_roughness": 0.32,
            "base_metallic": 0.0,
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
            "sparkle_enable": True,
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
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "metallic_flake_midnight_blue": {
        "name": "Metallic Flake \u2014 Midnight Blue Pearl",
        "description": "Deep blue with subtle pearl effect",
        "values": {
            "base_color": (0.08, 0.12, 0.25, 1.0),
            "base_roughness": 0.28,
            "base_metallic": 0.0,
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
            "sparkle_enable": True,
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
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "metallic_flake_candy_red": {
        "name": "Metallic Flake \u2014 Candy Apple Red",
        "description": "Vibrant red with dense sparkle",
        "values": {
            "base_color": (0.5, 0.05, 0.05, 1.0),
            "base_roughness": 0.25,
            "base_metallic": 0.0,
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
            "sparkle_enable": True,
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
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "metallic_flake_gunmetal": {
        "name": "Metallic Flake \u2014 Gunmetal Gray",
        "description": "Dark metallic gray with subtle blue undertone",
        "values": {
            "base_color": (0.18, 0.18, 0.20, 1.0),
            "base_roughness": 0.38,
            "base_metallic": 0.0,
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
            "sparkle_enable": True,
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
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "metallic_flake_champagne": {
        "name": "Metallic Flake \u2014 Champagne",
        "description": "Elegant warm beige with fine sparkle",
        "values": {
            "base_color": (0.55, 0.48, 0.40, 1.0),
            "base_roughness": 0.33,
            "base_metallic": 0.0,
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
            "sparkle_enable": True,
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
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
    "metallic_flake_plastic_toy": {
        "name": "Metallic Flake \u2014 Plastic Toy (Coarse)",
        "description": "Chunky visible flakes like cheap plastic toys",
        "values": {
            "base_color": (0.4, 0.4, 0.45, 1.0),
            "base_roughness": 0.45,
            "base_metallic": 0.0,
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
            "sparkle_enable": True,
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
            "tex_enable": False,
            "overall_effect": 1.0,
        }
    },
}


def get_preset_items(self, context):
    """Generate preset enum items for the UI."""
    items = []
    # Built-in presets
    for key, preset in BUILTIN_PRESETS.items():
        items.append((
            f"BUILTIN_{key}",
            preset["name"],
            preset.get("description", ""),
        ))
    # User presets
    user_presets = load_user_presets()
    for key, preset in user_presets.items():
        items.append((
            f"USER_{key}",
            preset["name"],
            preset.get("description", ""),
        ))
    return items


PRESET_EXCLUDE_PROPS = {
    'base_color_map', 'normal_map', 'roughness_map', 'metallic_map',
    'displacement_map', 'height_map', 'ao_map', 'opacity_map',
    'emission_map', 'gloss_map'
}


# =============================================================================
# UPDATE CALLBACKS
# =============================================================================

def update_shader(self, context):
    """Called when a shader property changes."""
    mat = context.object.active_material
    if mat and mat.use_nodes:
        update_shader_from_properties(mat)


def update_texture(self, context):
    """Called when a texture property changes."""
    mat = context.object.active_material
    if mat and mat.use_nodes:
        update_textures_from_properties(mat)


# =============================================================================
# PROPERTY GROUP
# =============================================================================

class UniversalPBRProperties(PropertyGroup):
    """All properties for the Universal PBR Shader."""

    # =========================================================================
    # BASE MATERIAL
    # =========================================================================
    base_color: FloatVectorProperty(
        name="Base Color",
        description="Base material color",
        subtype='COLOR',
        size=4,
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5, 1.0),
        update=update_shader
    )
    base_roughness: FloatProperty(
        name="Roughness",
        description="Base surface roughness",
        min=0.0, max=1.0,
        default=0.4,
        update=update_shader
    )
    base_metallic: FloatProperty(
        name="Metallic",
        description="Base metallic value. 0 = dielectric, 1 = metallic",
        min=0.0, max=1.0,
        default=0.0,
        update=update_shader
    )
    ior: FloatProperty(
        name="IOR",
        description="Index of refraction",
        min=1.0, max=3.0,
        default=1.46,
        update=update_shader
    )

    # =========================================================================
    # SURFACE EFFECTS - GRAIN
    # =========================================================================
    surface_grain_enable: BoolProperty(
        name="Enable Surface Grain",
        description="Add micro surface grain texture to roughness",
        default=True,
        update=update_shader
    )
    surface_grain_amount: FloatProperty(
        name="Grain Amount",
        description="How much grain affects roughness",
        min=0.0, max=1.0,
        default=0.02,
        update=update_shader
    )
    surface_grain_scale: FloatProperty(
        name="Grain Scale",
        description="Scale of grain texture",
        min=0.0, max=2000.0,
        soft_min=10.0, soft_max=500.0,
        default=120.0,
        update=update_shader
    )

    # =========================================================================
    # SURFACE EFFECTS - ANISOTROPIC GRAIN
    # =========================================================================
    aniso_enable: BoolProperty(
        name="Enable Anisotropic",
        description="Enable directional grain pattern",
        default=False,
        update=update_shader
    )
    aniso_intensity: FloatProperty(
        name="Intensity",
        description="Anisotropic grain bump intensity",
        min=0.0, max=2.0,
        default=0.12,
        update=update_shader
    )
    aniso_scale: FloatProperty(
        name="Scale",
        description="Anisotropic grain pattern scale",
        min=0.0, max=2000.0,
        soft_min=50.0, soft_max=500.0,
        default=250.0,
        update=update_shader
    )
    aniso_ratio: FloatProperty(
        name="Ratio",
        description="Width/height ratio of anisotropic pattern",
        min=0.01, max=1.0,
        default=0.1,
        update=update_shader
    )
    aniso_angle: FloatProperty(
        name="Angle",
        description="Rotation angle of anisotropic pattern in degrees",
        min=-180.0, max=180.0,
        default=0.0,
        update=update_shader
    )
    aniso_normal_strength: FloatProperty(
        name="Normal Strength",
        description="How much aniso pattern affects surface normal",
        min=0.0, max=2.0,
        default=0.25,
        update=update_shader
    )
    aniso_roughness: FloatProperty(
        name="Anisotropic Roughness",
        description="Directional roughness for anisotropic reflections",
        min=0.0, max=1.0,
        default=0.4,
        update=update_shader
    )

    # =========================================================================
    # SURFACE EFFECTS - SSS
    # =========================================================================
    sss_enable: BoolProperty(
        name="Enable SSS",
        description="Enable subsurface scattering",
        default=True,
        update=update_shader
    )
    sss_weight: FloatProperty(
        name="SSS Weight",
        description="Amount of subsurface scattering",
        min=0.0, max=1.0,
        default=0.05,
        update=update_shader
    )
    sss_radius: FloatProperty(
        name="SSS Radius",
        description="Subsurface scattering radius",
        min=0.0, max=50.0,
        soft_max=5.0,
        default=0.3,
        update=update_shader
    )
    sss_scale: FloatProperty(
        name="SSS Scale",
        description="Subsurface scattering scale",
        min=0.0, max=10.0,
        default=1.0,
        update=update_shader
    )

    # =========================================================================
    # SURFACE EFFECTS - CLEARCOAT
    # =========================================================================
    clearcoat_enable: BoolProperty(
        name="Enable Clearcoat",
        description="Enable clearcoat layer",
        default=True,
        update=update_shader
    )
    clearcoat_weight: FloatProperty(
        name="Clearcoat Weight",
        description="Clearcoat layer intensity",
        min=0.0, max=1.0,
        default=0.2,
        update=update_shader
    )
    clearcoat_roughness: FloatProperty(
        name="Clearcoat Roughness",
        description="Clearcoat surface roughness",
        min=0.0, max=1.0,
        default=0.1,
        update=update_shader
    )

    # =========================================================================
    # SPARKLE SYSTEM
    # =========================================================================
    sparkle_enable: BoolProperty(
        name="Enable Sparkle System",
        description="Enable the metallic flake sparkle system",
        default=False,
        update=update_shader
    )

    # Primary Sparkles
    primary_enable: BoolProperty(
        name="Enable Primary",
        description="Enable primary sparkle layer",
        default=True,
        update=update_shader
    )
    primary_seed: IntProperty(
        name="Seed",
        description="Random seed for primary layer pattern",
        min=0, max=1000,
        default=0,
        update=update_shader
    )
    primary_density: FloatProperty(
        name="Density",
        description="Number of flakes per unit area",
        min=0.0, max=2000.0,
        soft_min=10.0, soft_max=1500.0,
        default=800.0,
        update=update_shader
    )
    primary_size: FloatProperty(
        name="Size",
        description="Individual flake size",
        min=0.0, max=2.0,
        soft_max=0.5,
        default=0.10,
        update=update_shader
    )
    primary_size_var: FloatProperty(
        name="Size Variation",
        description="Random variation in flake size",
        min=0.0, max=1.0,
        default=0.35,
        update=update_shader
    )
    primary_intensity: FloatProperty(
        name="Intensity",
        description="Brightness of primary sparkles",
        min=0.0, max=10.0,
        soft_max=3.0,
        default=1.0,
        update=update_shader
    )

    # Secondary Sparkles
    secondary_enable: BoolProperty(
        name="Enable Secondary",
        description="Enable secondary sparkle layer",
        default=True,
        update=update_shader
    )
    secondary_seed: IntProperty(
        name="Seed",
        description="Random seed for secondary layer pattern",
        min=0, max=1000,
        default=100,
        update=update_shader
    )
    secondary_density: FloatProperty(
        name="Density",
        description="Number of flakes per unit area",
        min=0.0, max=2000.0,
        soft_min=10.0, soft_max=1500.0,
        default=500.0,
        update=update_shader
    )
    secondary_size: FloatProperty(
        name="Size",
        description="Individual flake size",
        min=0.0, max=2.0,
        soft_max=0.5,
        default=0.08,
        update=update_shader
    )
    secondary_size_var: FloatProperty(
        name="Size Variation",
        description="Random variation in flake size",
        min=0.0, max=1.0,
        default=0.4,
        update=update_shader
    )
    secondary_intensity: FloatProperty(
        name="Intensity",
        description="Brightness of secondary sparkles",
        min=0.0, max=10.0,
        soft_max=3.0,
        default=0.8,
        update=update_shader
    )

    # Tertiary Sparkles
    tertiary_enable: BoolProperty(
        name="Enable Tertiary",
        description="Enable tertiary sparkle layer",
        default=True,
        update=update_shader
    )
    tertiary_seed: IntProperty(
        name="Seed",
        description="Random seed for tertiary layer pattern",
        min=0, max=1000,
        default=200,
        update=update_shader
    )
    tertiary_density: FloatProperty(
        name="Density",
        description="Number of flakes per unit area",
        min=0.0, max=2000.0,
        soft_min=10.0, soft_max=1500.0,
        default=80.0,
        update=update_shader
    )
    tertiary_size: FloatProperty(
        name="Size",
        description="Individual flake size",
        min=0.0, max=2.0,
        soft_max=0.5,
        default=0.12,
        update=update_shader
    )
    tertiary_size_var: FloatProperty(
        name="Size Variation",
        description="Random variation in flake size",
        min=0.0, max=1.0,
        default=0.5,
        update=update_shader
    )
    tertiary_intensity: FloatProperty(
        name="Intensity",
        description="Brightness of tertiary sparkles",
        min=0.0, max=10.0,
        soft_max=3.0,
        default=1.8,
        update=update_shader
    )

    # Sparkle Color
    sparkle_color: FloatVectorProperty(
        name="Sparkle Color",
        description="Base color for sparkle flakes",
        subtype='COLOR',
        size=4,
        min=0.0, max=1.0,
        default=(0.9, 0.9, 0.9, 1.0),
        update=update_shader
    )
    sparkle_hue_var: FloatProperty(
        name="Hue Variation",
        description="Random hue variation per sparkle",
        min=0.0, max=0.5,
        default=0.02,
        update=update_shader
    )
    sparkle_sat_var: FloatProperty(
        name="Saturation Variation",
        description="Random saturation variation per sparkle",
        min=0.0, max=1.0,
        default=0.1,
        update=update_shader
    )
    sparkle_val_var: FloatProperty(
        name="Value Variation",
        description="Random brightness variation per sparkle",
        min=0.0, max=1.0,
        default=0.15,
        update=update_shader
    )
    sparkle_base_influence: FloatProperty(
        name="Base Influence",
        description="How much the base color influences sparkle color",
        min=0.0, max=1.0,
        default=0.1,
        update=update_shader
    )
    sparkle_metallic: FloatProperty(
        name="Sparkle Metallic",
        description="Metallic value for sparkle flakes",
        min=0.0, max=1.0,
        default=0.97,
        update=update_shader
    )
    fresnel_shift: FloatProperty(
        name="Fresnel Shift",
        description="How much Fresnel effect shifts sparkle hue",
        min=0.0, max=1.0,
        default=0.03,
        update=update_shader
    )
    fresnel_direction: FloatProperty(
        name="Fresnel Direction",
        description="Direction of Fresnel hue shift",
        min=0.0, max=1.0,
        default=0.55,
        update=update_shader
    )

    # Sparkle Response
    sparkle_roughness: FloatProperty(
        name="Sparkle Roughness",
        description="Roughness of sparkle flake surfaces",
        min=0.0, max=1.0,
        default=0.06,
        update=update_shader
    )
    sparkle_sharpness: FloatProperty(
        name="Sparkle Sharpness",
        description="How tight/focused the sparkle points are. Higher = tighter sparkles",
        min=1.0, max=50.0,
        soft_max=20.0,
        default=5.0,
        update=update_shader
    )
    orientation_randomness: FloatProperty(
        name="Orientation Randomness",
        description="How randomly oriented the flakes are. 0 = flat, 1 = wild",
        min=0.0, max=1.0,
        default=0.20,
        update=update_shader
    )
    overdrive: FloatProperty(
        name="Overdrive",
        description="Boost sparkle intensity beyond physical limits",
        min=0.0, max=10.0,
        soft_max=3.0,
        default=1.0,
        update=update_shader
    )
    emission_strength: FloatProperty(
        name="Emission",
        description="Self-illumination of sparkle flakes",
        min=0.0, max=20.0,
        soft_max=5.0,
        default=0.15,
        update=update_shader
    )
    global_density_multiplier: FloatProperty(
        name="Global Density",
        description="Multiplier for all sparkle layer densities",
        min=0.01, max=10.0,
        soft_min=0.1, soft_max=5.0,
        default=1.0,
        update=update_shader
    )
    global_size_multiplier: FloatProperty(
        name="Global Size",
        description="Multiplier for all sparkle layer sizes",
        min=0.01, max=10.0,
        soft_min=0.1, soft_max=5.0,
        default=1.0,
        update=update_shader
    )

    # =========================================================================
    # TEXTURE MAPS
    # =========================================================================
    tex_enable: BoolProperty(
        name="Enable Texture Maps",
        description="Enable texture map system",
        default=False,
        update=update_shader
    )
    tex_projection: EnumProperty(
        name="Projection",
        description="Texture projection mode",
        items=[
            ('FLAT', "Flat", "Standard UV projection"),
            ('BOX', "Box", "Box projection for seamless tiling"),
            ('SPHERE', "Sphere", "Spherical projection"),
            ('TUBE', "Tube", "Cylindrical projection"),
        ],
        default='BOX',
        update=update_shader
    )
    tex_box_blend: FloatProperty(
        name="Box Blend",
        description="Blending between box projection faces",
        min=0.0, max=1.0,
        default=0.2,
        update=update_shader
    )
    tex_scale: FloatVectorProperty(
        name="Scale",
        description="Texture coordinate scale",
        subtype='XYZ',
        size=3,
        default=(1.0, 1.0, 1.0),
        update=update_shader
    )
    tex_rotation: FloatVectorProperty(
        name="Rotation",
        description="Texture coordinate rotation",
        subtype='EULER',
        size=3,
        default=(0.0, 0.0, 0.0),
        update=update_shader
    )
    tex_offset: FloatVectorProperty(
        name="Offset",
        description="Texture coordinate offset",
        subtype='TRANSLATION',
        size=3,
        default=(0.0, 0.0, 0.0),
        update=update_shader
    )
    tex_show_advanced_uv: BoolProperty(
        name="Show Advanced UV",
        description="Show advanced per-map UV overrides",
        default=False,
    )

    # Base Color Map
    base_color_map: PointerProperty(
        name="Base Color Map",
        type=bpy.types.Image,
        update=update_texture
    )
    base_color_map_strength: FloatProperty(
        name="Strength",
        description="Blend between solid color (0) and texture (1)",
        min=0.0, max=1.0,
        default=1.0,
        update=update_shader
    )
    base_color_tint_enable: BoolProperty(
        name="Tint",
        description="Multiply texture by solid base color for tinting",
        default=False,
        update=update_shader
    )

    # Normal Map
    normal_map: PointerProperty(
        name="Normal Map",
        type=bpy.types.Image,
        update=update_texture
    )
    normal_map_strength: FloatProperty(
        name="Normal Strength",
        description="Normal map influence strength",
        min=0.0, max=5.0,
        default=1.0,
        update=update_shader
    )
    normal_map_invert: BoolProperty(
        name="Invert Normal",
        description="Invert R and G channels (flip normal direction)",
        default=False,
        update=update_shader
    )

    # Roughness Map
    roughness_map: PointerProperty(
        name="Roughness Map",
        type=bpy.types.Image,
        update=update_texture
    )
    roughness_map_strength: FloatProperty(
        name="Roughness Strength",
        description="How much the roughness map affects final roughness",
        min=0.0, max=2.0,
        default=1.0,
        update=update_shader
    )
    roughness_map_invert: BoolProperty(
        name="Invert",
        description="Invert roughness map (use when loading a Gloss map here)",
        default=False,
        update=update_shader
    )

    # Metallic Map
    metallic_map: PointerProperty(
        name="Metallic Map",
        type=bpy.types.Image,
        update=update_texture
    )
    metallic_map_strength: FloatProperty(
        name="Metallic Strength",
        description="How much the metallic map affects final metallic value",
        min=0.0, max=1.0,
        default=1.0,
        update=update_shader
    )

    # Displacement / Bump Map
    displacement_map: PointerProperty(
        name="Displacement Map",
        type=bpy.types.Image,
        update=update_texture
    )
    displacement_map_strength: FloatProperty(
        name="Bump Strength",
        description="Displacement/bump map influence",
        min=0.0, max=5.0,
        default=0.5,
        update=update_shader
    )
    displacement_map_invert: BoolProperty(
        name="Invert",
        description="Invert displacement/bump direction",
        default=False,
        update=update_shader
    )

    # Height Map (true displacement)
    height_map: PointerProperty(
        name="Height Map",
        type=bpy.types.Image,
        update=update_texture
    )
    height_map_scale: FloatProperty(
        name="Height Scale",
        description="Scale of true displacement from height map",
        min=0.0, max=10.0,
        soft_max=2.0,
        default=0.1,
        update=update_shader
    )
    height_map_midlevel: FloatProperty(
        name="Midlevel",
        description="Height map midlevel (values below push in, above push out)",
        min=0.0, max=1.0,
        default=0.5,
        update=update_shader
    )

    # AO Map
    ao_map: PointerProperty(
        name="AO Map",
        type=bpy.types.Image,
        update=update_texture
    )
    ao_map_strength: FloatProperty(
        name="AO Strength",
        description="Ambient occlusion darkening strength",
        min=0.0, max=5.0,
        default=1.0,
        update=update_shader
    )

    # Opacity Map
    opacity_map: PointerProperty(
        name="Opacity Map",
        type=bpy.types.Image,
        update=update_texture
    )
    opacity_map_strength: FloatProperty(
        name="Opacity Strength",
        description="How much the opacity map affects transparency",
        min=0.0, max=1.0,
        default=1.0,
        update=update_shader
    )
    opacity_map_invert: BoolProperty(
        name="Invert",
        description="Invert opacity (white=transparent instead of white=opaque)",
        default=False,
        update=update_shader
    )

    # Emission Map
    emission_map: PointerProperty(
        name="Emission Map",
        type=bpy.types.Image,
        update=update_texture
    )
    emission_map_strength: FloatProperty(
        name="Emission Strength",
        description="Emission map intensity",
        min=0.0, max=20.0,
        soft_max=5.0,
        default=1.0,
        update=update_shader
    )

    # Gloss Map
    gloss_map: PointerProperty(
        name="Gloss Map",
        type=bpy.types.Image,
        update=update_texture
    )
    gloss_map_strength: FloatProperty(
        name="Gloss Strength",
        description="How much the gloss map affects roughness (inverted)",
        min=0.0, max=5.0,
        default=1.0,
        update=update_shader
    )

    # =========================================================================
    # ADVANCED
    # =========================================================================
    overall_effect: FloatProperty(
        name="Overall Effect",
        description="Global mix. 0 = base material only, 1 = full effect with sparkles",
        min=0.0, max=1.0,
        default=1.0,
        update=update_shader
    )


# =============================================================================
# UI PANELS
# =============================================================================

class MATERIAL_PT_upbr_main(Panel):
    bl_label = "Universal PBR Shader v1.0.0"
    bl_idname = "MATERIAL_PT_upbr_main"
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

        if mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes:
            row = layout.row()
            row.label(text="Shader Active", icon='CHECKMARK')
            row.operator("material.create_universal_pbr", text="Rebuild", icon='FILE_REFRESH')
        else:
            layout.operator("material.create_universal_pbr", text="Create Universal PBR Material", icon='MATERIAL')


class MATERIAL_PT_upbr_presets(Panel):
    bl_label = "Presets"
    bl_idname = "MATERIAL_PT_upbr_presets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout

        # Built-in presets
        layout.label(text="Built-in Presets:")
        col = layout.column(align=True)
        for key, preset in BUILTIN_PRESETS.items():
            op = col.operator("material.upbr_apply_preset", text=preset["name"])
            op.preset_id = f"BUILTIN_{key}"

        # User presets
        user_presets = load_user_presets()
        if user_presets:
            layout.separator()
            layout.label(text="User Presets:")
            col = layout.column(align=True)
            for key, preset in user_presets.items():
                row = col.row(align=True)
                op = row.operator("material.upbr_apply_preset", text=preset["name"])
                op.preset_id = f"USER_{key}"
                op_del = row.operator("material.upbr_delete_preset", text="", icon='X')
                op_del.preset_key = key

        layout.separator()
        layout.operator("material.upbr_save_preset", text="Save Current as Preset", icon='ADD')


class MATERIAL_PT_upbr_base(Panel):
    bl_label = "Base Material"
    bl_idname = "MATERIAL_PT_upbr_base"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_main"

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr

        layout.prop(props, "base_color")
        col = layout.column(align=True)
        col.prop(props, "base_roughness")
        col.prop(props, "base_metallic")
        col.prop(props, "ior")


class MATERIAL_PT_upbr_textures(Panel):
    bl_label = "Texture Maps"
    bl_idname = "MATERIAL_PT_upbr_textures"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_main"

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw_header(self, context):
        props = context.object.active_material.universal_pbr
        self.layout.prop(props, "tex_enable", text="")

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr
        layout.enabled = props.tex_enable

        # Shared UV Controls
        box = layout.box()
        box.label(text="UV Mapping:", icon='UV')
        col = box.column(align=True)
        col.prop(props, "tex_scale")
        col.prop(props, "tex_rotation")
        col.prop(props, "tex_offset")
        row = box.row(align=True)
        row.prop(props, "tex_projection", text="Projection")
        if props.tex_projection == 'BOX':
            row.prop(props, "tex_box_blend", text="Blend")

        layout.separator()

        # Base Color Map
        box = layout.box()
        box.label(text="Base Color Map:", icon='IMAGE_DATA')
        box.template_ID(props, "base_color_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "base_color_map_strength", text="Strength")
        row.prop(props, "base_color_tint_enable", text="Tint", toggle=True)

        # Normal Map
        box = layout.box()
        box.label(text="Normal Map:", icon='NORMALS_FACE')
        box.template_ID(props, "normal_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "normal_map_strength", text="Strength")
        row.prop(props, "normal_map_invert", text="Invert", toggle=True)

        # Roughness Map
        box = layout.box()
        box.label(text="Roughness Map:", icon='MATSPHERE')
        box.template_ID(props, "roughness_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "roughness_map_strength", text="Strength")
        row.prop(props, "roughness_map_invert", text="Invert (Gloss)", toggle=True)

        # Metallic Map
        box = layout.box()
        box.label(text="Metallic Map:", icon='SHADING_RENDERED')
        box.template_ID(props, "metallic_map", open="image.open")
        box.prop(props, "metallic_map_strength", text="Strength")

        # Displacement / Bump Map
        box = layout.box()
        box.label(text="Displacement / Bump:", icon='MOD_DISPLACE')
        box.template_ID(props, "displacement_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "displacement_map_strength", text="Strength")
        row.prop(props, "displacement_map_invert", text="Invert", toggle=True)

        # Height Map
        box = layout.box()
        box.label(text="Height Map (True Displacement):", icon='RNDCURVE')
        box.template_ID(props, "height_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "height_map_scale", text="Scale")
        row.prop(props, "height_map_midlevel", text="Midlevel")

        # AO Map
        box = layout.box()
        box.label(text="AO Map:", icon='SHADING_TEXTURE')
        box.template_ID(props, "ao_map", open="image.open")
        box.prop(props, "ao_map_strength", text="Strength")

        # Opacity Map
        box = layout.box()
        box.label(text="Opacity Map:", icon='IMAGE_ALPHA')
        box.template_ID(props, "opacity_map", open="image.open")
        row = box.row(align=True)
        row.prop(props, "opacity_map_strength", text="Strength")
        row.prop(props, "opacity_map_invert", text="Invert", toggle=True)

        # Emission Map
        box = layout.box()
        box.label(text="Emission Map:", icon='LIGHT_SUN')
        box.template_ID(props, "emission_map", open="image.open")
        box.prop(props, "emission_map_strength", text="Strength")

        # Gloss Map
        box = layout.box()
        box.label(text="Gloss Map:", icon='BRUSH_DATA')
        box.template_ID(props, "gloss_map", open="image.open")
        box.prop(props, "gloss_map_strength", text="Strength")

        # Advanced UV
        layout.separator()
        row = layout.row()
        row.prop(props, "tex_show_advanced_uv", text="Advanced UV Options",
                 icon='TRIA_DOWN' if props.tex_show_advanced_uv else 'TRIA_RIGHT')
        if props.tex_show_advanced_uv:
            box = layout.box()
            box.label(text="Per-map UV overrides coming in v1.1", icon='INFO')


class MATERIAL_PT_upbr_surface(Panel):
    bl_label = "Surface Effects"
    bl_idname = "MATERIAL_PT_upbr_surface"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr

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
            col.prop(props, "aniso_roughness", text="Roughness")

        # SSS
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


class MATERIAL_PT_upbr_sparkles(Panel):
    bl_label = "Sparkle System"
    bl_idname = "MATERIAL_PT_upbr_sparkles"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw_header(self, context):
        props = context.object.active_material.universal_pbr
        self.layout.prop(props, "sparkle_enable", text="")

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr
        layout.enabled = props.sparkle_enable


class MATERIAL_PT_upbr_sparkle_primary(Panel):
    bl_label = "Primary Layer"
    bl_idname = "MATERIAL_PT_upbr_sparkle_primary"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_sparkles"

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw_header(self, context):
        props = context.object.active_material.universal_pbr
        self.layout.prop(props, "primary_enable", text="")

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr
        layout.enabled = props.sparkle_enable and props.primary_enable

        layout.prop(props, "primary_seed", text="Seed")
        col = layout.column(align=True)
        col.prop(props, "primary_density", text="Density")
        col.prop(props, "primary_size", text="Size")
        col.prop(props, "primary_size_var", text="Size Variation")
        col.prop(props, "primary_intensity", text="Intensity")


class MATERIAL_PT_upbr_sparkle_secondary(Panel):
    bl_label = "Secondary Layer"
    bl_idname = "MATERIAL_PT_upbr_sparkle_secondary"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_sparkles"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw_header(self, context):
        props = context.object.active_material.universal_pbr
        self.layout.prop(props, "secondary_enable", text="")

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr
        layout.enabled = props.sparkle_enable and props.secondary_enable

        layout.prop(props, "secondary_seed", text="Seed")
        col = layout.column(align=True)
        col.prop(props, "secondary_density", text="Density")
        col.prop(props, "secondary_size", text="Size")
        col.prop(props, "secondary_size_var", text="Size Variation")
        col.prop(props, "secondary_intensity", text="Intensity")


class MATERIAL_PT_upbr_sparkle_tertiary(Panel):
    bl_label = "Tertiary Layer"
    bl_idname = "MATERIAL_PT_upbr_sparkle_tertiary"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_sparkles"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw_header(self, context):
        props = context.object.active_material.universal_pbr
        self.layout.prop(props, "tertiary_enable", text="")

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr
        layout.enabled = props.sparkle_enable and props.tertiary_enable

        layout.prop(props, "tertiary_seed", text="Seed")
        col = layout.column(align=True)
        col.prop(props, "tertiary_density", text="Density")
        col.prop(props, "tertiary_size", text="Size")
        col.prop(props, "tertiary_size_var", text="Size Variation")
        col.prop(props, "tertiary_intensity", text="Intensity")


class MATERIAL_PT_upbr_sparkle_color(Panel):
    bl_label = "Sparkle Color"
    bl_idname = "MATERIAL_PT_upbr_sparkle_color"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_sparkles"

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr
        layout.enabled = props.sparkle_enable

        layout.prop(props, "sparkle_color")

        layout.label(text="Color Variation:")
        col = layout.column(align=True)
        col.prop(props, "sparkle_hue_var", text="Hue")
        col.prop(props, "sparkle_sat_var", text="Saturation")
        col.prop(props, "sparkle_val_var", text="Value")

        layout.separator()
        layout.prop(props, "sparkle_base_influence", text="Base Color Influence")
        layout.prop(props, "sparkle_metallic", text="Metallic")

        layout.separator()
        layout.label(text="Fresnel Color Shift:")
        col = layout.column(align=True)
        col.prop(props, "fresnel_shift", text="Amount")
        col.prop(props, "fresnel_direction", text="Direction")


class MATERIAL_PT_upbr_sparkle_response(Panel):
    bl_label = "Sparkle Response"
    bl_idname = "MATERIAL_PT_upbr_sparkle_response"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_sparkles"

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr
        layout.enabled = props.sparkle_enable

        layout.label(text="View Response:")
        col = layout.column(align=True)
        col.prop(props, "sparkle_sharpness", text="Sharpness")
        col.prop(props, "orientation_randomness", text="Orientation Randomness")

        layout.separator()
        layout.prop(props, "sparkle_roughness", text="Roughness")

        layout.separator()
        layout.label(text="Intensity:")
        col = layout.column(align=True)
        col.prop(props, "overdrive", text="Overdrive")
        col.prop(props, "emission_strength", text="Emission")

        layout.separator()
        layout.label(text="Global Scale:")
        col = layout.column(align=True)
        col.prop(props, "global_density_multiplier", text="Density Multiplier")
        col.prop(props, "global_size_multiplier", text="Size Multiplier")


class MATERIAL_PT_upbr_advanced(Panel):
    bl_label = "Advanced"
    bl_idname = "MATERIAL_PT_upbr_advanced"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "MATERIAL_PT_upbr_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object or not context.object.active_material:
            return False
        mat = context.object.active_material
        return mat.use_nodes and "Universal PBR Shader v1.0.0" in mat.node_tree.nodes

    def draw(self, context):
        layout = self.layout
        props = context.object.active_material.universal_pbr

        layout.prop(props, "overall_effect")


# =============================================================================
# OPERATORS
# =============================================================================

class MATERIAL_OT_create_universal_pbr(Operator):
    bl_idname = "material.create_universal_pbr"
    bl_label = "Create Universal PBR Material"
    bl_description = "Create or rebuild the Universal PBR shader node tree"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        if not obj.active_material:
            mat = bpy.data.materials.new("Universal PBR")
            obj.active_material = mat
        mat = obj.active_material
        mat.use_nodes = True
        create_shader(mat)
        update_shader_from_properties(mat)
        update_textures_from_properties(mat)
        self.report({'INFO'}, "Universal PBR shader created")
        return {'FINISHED'}


class MATERIAL_OT_upbr_apply_preset(Operator):
    bl_idname = "material.upbr_apply_preset"
    bl_label = "Apply Preset"
    bl_description = "Apply a preset to the current material"
    bl_options = {'REGISTER', 'UNDO'}

    preset_id: StringProperty()

    def execute(self, context):
        mat = context.object.active_material
        if not mat:
            self.report({'ERROR'}, "No active material")
            return {'CANCELLED'}

        props = mat.universal_pbr

        # Determine source
        if self.preset_id.startswith("BUILTIN_"):
            key = self.preset_id[8:]
            if key not in BUILTIN_PRESETS:
                self.report({'ERROR'}, f"Unknown preset: {key}")
                return {'CANCELLED'}
            preset = BUILTIN_PRESETS[key]
        elif self.preset_id.startswith("USER_"):
            key = self.preset_id[5:]
            user_presets = load_user_presets()
            if key not in user_presets:
                self.report({'ERROR'}, f"Unknown user preset: {key}")
                return {'CANCELLED'}
            preset = user_presets[key]
        else:
            self.report({'ERROR'}, "Invalid preset ID")
            return {'CANCELLED'}

        values = preset.get("values", {})
        for prop_name, value in values.items():
            if hasattr(props, prop_name) and prop_name not in PRESET_EXCLUDE_PROPS:
                try:
                    setattr(props, prop_name, value)
                except (TypeError, AttributeError):
                    pass

        self.report({'INFO'}, f"Applied preset: {preset.get('name', key)}")
        return {'FINISHED'}


class MATERIAL_OT_upbr_save_preset(Operator):
    bl_idname = "material.upbr_save_preset"
    bl_label = "Save Preset"
    bl_description = "Save current settings as a user preset"
    bl_options = {'REGISTER'}

    preset_name: StringProperty(
        name="Name",
        description="Name for the preset",
        default="My Preset"
    )
    preset_description: StringProperty(
        name="Description",
        description="Description of what this preset looks like",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        layout.prop(self, "preset_description")

    def execute(self, context):
        mat = context.object.active_material
        if not mat:
            self.report({'ERROR'}, "No active material")
            return {'CANCELLED'}

        props = mat.universal_pbr

        # Collect values
        values = {}
        for prop_name in props.__annotations__:
            if prop_name in PRESET_EXCLUDE_PROPS:
                continue
            try:
                val = getattr(props, prop_name)
                # Convert to JSON-serializable types
                if hasattr(val, '__len__') and not isinstance(val, str):
                    values[prop_name] = list(val)
                elif isinstance(val, bool):
                    values[prop_name] = val
                elif isinstance(val, (int, float)):
                    values[prop_name] = val
                elif isinstance(val, str):
                    values[prop_name] = val
            except (TypeError, AttributeError):
                pass

        # Generate safe key
        safe_key = ''.join(c if c.isalnum() else '_' for c in self.preset_name.lower()).strip('_')
        if not safe_key:
            safe_key = 'preset'

        # Load existing, add new, save
        user_presets = load_user_presets()

        # Make key unique
        base_key = safe_key
        counter = 1
        while safe_key in user_presets:
            safe_key = f"{base_key}_{counter}"
            counter += 1

        user_presets[safe_key] = {
            "name": self.preset_name,
            "description": self.preset_description,
            "values": values
        }
        save_user_presets(user_presets)
        self.report({'INFO'}, f"Saved preset: {self.preset_name}")
        return {'FINISHED'}


class MATERIAL_OT_upbr_delete_preset(Operator):
    bl_idname = "material.upbr_delete_preset"
    bl_label = "Delete Preset"
    bl_description = "Delete a user preset"
    bl_options = {'REGISTER'}

    preset_key: StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        user_presets = load_user_presets()
        if self.preset_key in user_presets:
            del user_presets[self.preset_key]
            save_user_presets(user_presets)
            self.report({'INFO'}, "Preset deleted")
        else:
            self.report({'WARNING'}, "Preset not found")
        return {'FINISHED'}


# =============================================================================
# SHADER NODE CREATION
# =============================================================================

def create_node(nodes, node_type, location, name, label):
    """Create a shader node with given properties."""
    node = nodes.new(type=node_type)
    node.location = location
    node.name = name
    node.label = label
    return node


def create_shader(mat):
    """Build the complete Universal PBR shader node tree."""
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing
    nodes.clear()

    # Frame wrapper for identification
    frame = nodes.new('NodeFrame')
    frame.name = "Universal PBR Shader v1.0.0"
    frame.label = "Universal PBR Shader v1.0.0"

    # ==========================================================================
    # COORDINATE AND GEOMETRY SETUP
    # ==========================================================================

    tex_coord = create_node(nodes, 'ShaderNodeTexCoord', (-2000, 0), 'tex_coord', 'Tex Coord')
    geometry = create_node(nodes, 'ShaderNodeNewGeometry', (-2000, -200), 'geometry', 'Geometry')

    # Shared UV Mapping node - all texture maps use this
    uv_mapping = create_node(nodes, 'ShaderNodeMapping', (-1800, 0), 'uv_mapping', 'UV Mapping')
    uv_mapping.vector_type = 'POINT'
    links.new(tex_coord.outputs['Object'], uv_mapping.inputs['Vector'])

    # ==========================================================================
    # VALUE NODES - All controllable parameters
    # ==========================================================================

    # Base Material
    base_color_node = create_node(nodes, 'ShaderNodeRGB', (-1600, 500), 'base_color', 'Base Color')
    base_rough_node = create_node(nodes, 'ShaderNodeValue', (-1600, 450), 'base_roughness', 'Base Roughness')
    base_metallic_node = create_node(nodes, 'ShaderNodeValue', (-1600, 400), 'base_metallic', 'Base Metallic')
    ior_node = create_node(nodes, 'ShaderNodeValue', (-1600, 350), 'ior', 'IOR')

    # Surface Grain
    grain_amount_node = create_node(nodes, 'ShaderNodeValue', (-1600, 280), 'surface_grain_amount', 'Grain Amount')
    grain_scale_node = create_node(nodes, 'ShaderNodeValue', (-1600, 230), 'surface_grain_scale', 'Grain Scale')

    # Anisotropic
    aniso_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1600, 160), 'aniso_intensity', 'Aniso Intensity')
    aniso_scale_node = create_node(nodes, 'ShaderNodeValue', (-1600, 110), 'aniso_scale', 'Aniso Scale')
    aniso_ratio_node = create_node(nodes, 'ShaderNodeValue', (-1600, 60), 'aniso_ratio', 'Aniso Ratio')
    aniso_angle_node = create_node(nodes, 'ShaderNodeValue', (-1600, 10), 'aniso_angle', 'Aniso Angle')
    aniso_normal_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -40), 'aniso_normal_strength', 'Aniso Norm Str')
    aniso_rough_node = create_node(nodes, 'ShaderNodeValue', (-1600, -90), 'aniso_roughness', 'Aniso Roughness')

    # SSS
    sss_weight_node = create_node(nodes, 'ShaderNodeValue', (-1600, -150), 'sss_weight', 'SSS Weight')
    sss_radius_node = create_node(nodes, 'ShaderNodeValue', (-1600, -200), 'sss_radius', 'SSS Radius')
    sss_scale_node = create_node(nodes, 'ShaderNodeValue', (-1600, -250), 'sss_scale', 'SSS Scale')

    # Clearcoat
    coat_weight_node = create_node(nodes, 'ShaderNodeValue', (-1600, -310), 'coat_weight', 'Coat Weight')
    coat_rough_node = create_node(nodes, 'ShaderNodeValue', (-1600, -360), 'coat_roughness', 'Coat Roughness')

    # Sparkle System
    sparkle_enable_node = create_node(nodes, 'ShaderNodeValue', (-1400, 800), 'sparkle_enable', 'Sparkle Enable')

    # Primary Sparkle
    primary_enable_node = create_node(nodes, 'ShaderNodeValue', (-1400, 750), 'primary_enable', 'Primary Enable')
    primary_seed_node = create_node(nodes, 'ShaderNodeValue', (-1400, 700), 'primary_seed', 'Primary Seed')
    primary_density_node = create_node(nodes, 'ShaderNodeValue', (-1400, 650), 'primary_density', 'Primary Density')
    primary_size_node = create_node(nodes, 'ShaderNodeValue', (-1400, 600), 'primary_size', 'Primary Size')
    primary_size_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, 550), 'primary_size_var', 'Primary Size Var')
    primary_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1400, 500), 'primary_intensity', 'Primary Intensity')

    # Secondary Sparkle
    secondary_enable_node = create_node(nodes, 'ShaderNodeValue', (-1400, 430), 'secondary_enable', 'Secondary Enable')
    secondary_seed_node = create_node(nodes, 'ShaderNodeValue', (-1400, 380), 'secondary_seed', 'Secondary Seed')
    secondary_density_node = create_node(nodes, 'ShaderNodeValue', (-1400, 330), 'secondary_density', 'Secondary Density')
    secondary_size_node = create_node(nodes, 'ShaderNodeValue', (-1400, 280), 'secondary_size', 'Secondary Size')
    secondary_size_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, 230), 'secondary_size_var', 'Secondary Size Var')
    secondary_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1400, 180), 'secondary_intensity', 'Secondary Intensity')

    # Tertiary Sparkle
    tertiary_enable_node = create_node(nodes, 'ShaderNodeValue', (-1400, 110), 'tertiary_enable', 'Tertiary Enable')
    tertiary_seed_node = create_node(nodes, 'ShaderNodeValue', (-1400, 60), 'tertiary_seed', 'Tertiary Seed')
    tertiary_density_node = create_node(nodes, 'ShaderNodeValue', (-1400, 10), 'tertiary_density', 'Tertiary Density')
    tertiary_size_node = create_node(nodes, 'ShaderNodeValue', (-1400, -40), 'tertiary_size', 'Tertiary Size')
    tertiary_size_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, -90), 'tertiary_size_var', 'Tertiary Size Var')
    tertiary_intensity_node = create_node(nodes, 'ShaderNodeValue', (-1400, -140), 'tertiary_intensity', 'Tertiary Intensity')

    # Sparkle Color
    sparkle_color_node = create_node(nodes, 'ShaderNodeRGB', (-1400, -200), 'sparkle_color', 'Sparkle Color')
    sparkle_hue_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, -250), 'sparkle_hue_var', 'Hue Var')
    sparkle_sat_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, -300), 'sparkle_sat_var', 'Sat Var')
    sparkle_val_var_node = create_node(nodes, 'ShaderNodeValue', (-1400, -350), 'sparkle_val_var', 'Val Var')
    sparkle_base_inf_node = create_node(nodes, 'ShaderNodeValue', (-1400, -400), 'sparkle_base_influence', 'Base Influence')
    sparkle_metallic_node = create_node(nodes, 'ShaderNodeValue', (-1400, -450), 'sparkle_metallic', 'Sparkle Metallic')
    fresnel_shift_node = create_node(nodes, 'ShaderNodeValue', (-1400, -500), 'fresnel_shift', 'Fresnel Shift')
    fresnel_dir_node = create_node(nodes, 'ShaderNodeValue', (-1400, -550), 'fresnel_direction', 'Fresnel Dir')

    # Sparkle Response
    sparkle_roughness_node = create_node(nodes, 'ShaderNodeValue', (-1400, -610), 'sparkle_roughness', 'Sparkle Rough')
    sparkle_sharpness_node = create_node(nodes, 'ShaderNodeValue', (-1400, -660), 'sparkle_sharpness', 'Sharpness')
    orientation_randomness_node = create_node(nodes, 'ShaderNodeValue', (-1400, -710), 'orientation_randomness', 'Orient Rand')
    overdrive_node = create_node(nodes, 'ShaderNodeValue', (-1400, -760), 'overdrive', 'Overdrive')
    emission_str_node = create_node(nodes, 'ShaderNodeValue', (-1400, -810), 'emission_strength', 'Emission')
    global_density_mult_node = create_node(nodes, 'ShaderNodeValue', (-1400, -860), 'global_density_multiplier', 'Global Density')
    global_size_mult_node = create_node(nodes, 'ShaderNodeValue', (-1400, -910), 'global_size_multiplier', 'Global Size')

    # Texture Controls
    tex_enable_node = create_node(nodes, 'ShaderNodeValue', (-1600, -450), 'tex_enable', 'Tex Enable')

    # Per-map strength/control value nodes
    base_color_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -500), 'base_color_map_strength', 'Color Map Str')
    base_color_tint_node = create_node(nodes, 'ShaderNodeValue', (-1600, -550), 'base_color_tint_enable', 'Color Tint')
    normal_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -600), 'normal_map_strength', 'Normal Map Str')
    normal_map_inv_node = create_node(nodes, 'ShaderNodeValue', (-1600, -650), 'normal_map_invert', 'Normal Map Inv')
    roughness_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -700), 'roughness_map_strength', 'Rough Map Str')
    roughness_map_inv_node = create_node(nodes, 'ShaderNodeValue', (-1600, -750), 'roughness_map_invert', 'Rough Map Inv')
    metallic_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -800), 'metallic_map_strength', 'Metal Map Str')
    disp_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -850), 'displacement_map_strength', 'Disp Map Str')
    disp_map_inv_node = create_node(nodes, 'ShaderNodeValue', (-1600, -900), 'displacement_map_invert', 'Disp Map Inv')
    height_map_scale_node = create_node(nodes, 'ShaderNodeValue', (-1600, -950), 'height_map_scale', 'Height Scale')
    height_map_mid_node = create_node(nodes, 'ShaderNodeValue', (-1600, -1000), 'height_map_midlevel', 'Height Mid')
    ao_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -1050), 'ao_map_strength', 'AO Map Str')
    opacity_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -1100), 'opacity_map_strength', 'Opacity Map Str')
    opacity_map_inv_node = create_node(nodes, 'ShaderNodeValue', (-1600, -1150), 'opacity_map_invert', 'Opacity Map Inv')
    emission_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -1200), 'emission_map_strength', 'Emission Map Str')
    gloss_map_str_node = create_node(nodes, 'ShaderNodeValue', (-1600, -1250), 'gloss_map_strength', 'Gloss Map Str')

    # Overall
    overall_effect_node = create_node(nodes, 'ShaderNodeValue', (-1600, -1350), 'overall_effect', 'Overall Effect')

    # ==========================================================================
    # TEXTURE IMAGE NODES - All 10 maps connected to shared UV
    # ==========================================================================

    base_color_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -400), 'base_color_tex', 'Base Color Tex')
    base_color_tex.projection = 'BOX'
    base_color_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], base_color_tex.inputs['Vector'])

    normal_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -600), 'normal_tex', 'Normal Tex')
    normal_tex.projection = 'BOX'
    normal_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], normal_tex.inputs['Vector'])

    roughness_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -800), 'roughness_tex', 'Roughness Tex')
    roughness_tex.projection = 'BOX'
    roughness_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], roughness_tex.inputs['Vector'])

    metallic_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -1000), 'metallic_tex', 'Metallic Tex')
    metallic_tex.projection = 'BOX'
    metallic_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], metallic_tex.inputs['Vector'])

    displacement_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -1200), 'displacement_tex', 'Displacement Tex')
    displacement_tex.projection = 'BOX'
    displacement_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], displacement_tex.inputs['Vector'])

    height_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -1400), 'height_tex', 'Height Tex')
    height_tex.projection = 'BOX'
    height_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], height_tex.inputs['Vector'])

    ao_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -1600), 'ao_tex', 'AO Tex')
    ao_tex.projection = 'BOX'
    ao_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], ao_tex.inputs['Vector'])

    opacity_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -1800), 'opacity_tex', 'Opacity Tex')
    opacity_tex.projection = 'BOX'
    opacity_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], opacity_tex.inputs['Vector'])

    emission_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -2000), 'emission_tex', 'Emission Tex')
    emission_tex.projection = 'BOX'
    emission_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], emission_tex.inputs['Vector'])

    gloss_tex = create_node(nodes, 'ShaderNodeTexImage', (-1200, -2200), 'gloss_tex', 'Gloss Tex')
    gloss_tex.projection = 'BOX'
    gloss_tex.projection_blend = 0.2
    links.new(uv_mapping.outputs[0], gloss_tex.inputs['Vector'])

    # ==========================================================================
    # Safe orientation_randomness to avoid degenerate Map Range
    # ==========================================================================
    orient_rand_safe = create_node(nodes, 'ShaderNodeMath', (-1200, -710), 'orient_rand_safe', 'Orient Rand Safe')
    orient_rand_safe.operation = 'MAXIMUM'
    links.new(orientation_randomness_node.outputs[0], orient_rand_safe.inputs[0])
    orient_rand_safe.inputs[1].default_value = 0.001

    neg_orient_rand = create_node(nodes, 'ShaderNodeMath', (-1050, -710), 'neg_orient_rand', 'Neg Orient Rand')
    neg_orient_rand.operation = 'MULTIPLY'
    neg_orient_rand.inputs[1].default_value = -1.0
    links.new(orient_rand_safe.outputs[0], neg_orient_rand.inputs[0])

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

    base_roughness_with_grain = create_node(nodes, 'ShaderNodeMath', (-400, 100), 'base_roughness_with_grain', 'Rough + Grain')
    base_roughness_with_grain.operation = 'ADD'
    links.new(base_rough_node.outputs[0], base_roughness_with_grain.inputs[0])
    links.new(grain_scaled.outputs[0], base_roughness_with_grain.inputs[1])

    clamp_base_roughness = create_node(nodes, 'ShaderNodeClamp', (-200, 100), 'clamp_base_roughness', 'Clamp Base Rough')
    links.new(base_roughness_with_grain.outputs[0], clamp_base_roughness.inputs['Value'])

    # ==========================================================================
    # ANISOTROPIC GRAIN SYSTEM
    # ==========================================================================

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

    aniso_tangent = create_node(nodes, 'ShaderNodeCombineXYZ', (-600, -200), 'aniso_tangent', 'Aniso Tangent')
    links.new(cos_angle.outputs[0], aniso_tangent.inputs['X'])
    links.new(sin_angle.outputs[0], aniso_tangent.inputs['Y'])
    aniso_tangent.inputs['Z'].default_value = 0.0

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
    # NORMAL MAP PROCESSING - with invert support
    # ==========================================================================

    # Separate normal map channels for invert
    normal_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-500, -400), 'normal_separate', 'Norm Sep')
    normal_separate.mode = 'RGB'
    links.new(normal_tex.outputs['Color'], normal_separate.inputs['Color'])

    # Invert R channel (X)
    normal_r_inv = create_node(nodes, 'ShaderNodeMath', (-350, -380), 'normal_r_inv', 'R Inv')
    normal_r_inv.operation = 'SUBTRACT'
    normal_r_inv.inputs[0].default_value = 1.0
    links.new(normal_separate.outputs['Red'], normal_r_inv.inputs[1])

    normal_r_mix = create_node(nodes, 'ShaderNodeMix', (-200, -380), 'normal_r_mix', 'R Mix')
    normal_r_mix.data_type = 'FLOAT'
    links.new(normal_map_inv_node.outputs[0], normal_r_mix.inputs['Factor'])
    links.new(normal_separate.outputs['Red'], normal_r_mix.inputs[2])
    links.new(normal_r_inv.outputs[0], normal_r_mix.inputs[3])

    # Invert G channel (Y)
    normal_g_inv = create_node(nodes, 'ShaderNodeMath', (-350, -440), 'normal_g_inv', 'G Inv')
    normal_g_inv.operation = 'SUBTRACT'
    normal_g_inv.inputs[0].default_value = 1.0
    links.new(normal_separate.outputs['Green'], normal_g_inv.inputs[1])

    normal_g_mix = create_node(nodes, 'ShaderNodeMix', (-200, -440), 'normal_g_mix', 'G Mix')
    normal_g_mix.data_type = 'FLOAT'
    links.new(normal_map_inv_node.outputs[0], normal_g_mix.inputs['Factor'])
    links.new(normal_separate.outputs['Green'], normal_g_mix.inputs[2])
    links.new(normal_g_inv.outputs[0], normal_g_mix.inputs[3])

    # Recombine normal
    normal_combine = create_node(nodes, 'ShaderNodeCombineColor', (-50, -410), 'normal_combine', 'Norm Comb')
    normal_combine.mode = 'RGB'
    links.new(normal_r_mix.outputs[0], normal_combine.inputs['Red'])
    links.new(normal_g_mix.outputs[0], normal_combine.inputs['Green'])
    links.new(normal_separate.outputs['Blue'], normal_combine.inputs['Blue'])

    normal_map_node = create_node(nodes, 'ShaderNodeNormalMap', (100, -400), 'normal_map_node', 'Normal Map')
    normal_map_node.space = 'TANGENT'
    links.new(normal_combine.outputs['Color'], normal_map_node.inputs['Color'])

    # Normal strength gated by tex_enable
    normal_str_gated = create_node(nodes, 'ShaderNodeMath', (0, -450), 'normal_str_gated', 'Norm Str Gated')
    normal_str_gated.operation = 'MULTIPLY'
    links.new(normal_map_str_node.outputs[0], normal_str_gated.inputs[0])
    links.new(tex_enable_node.outputs[0], normal_str_gated.inputs[1])
    links.new(normal_str_gated.outputs[0], normal_map_node.inputs['Strength'])

    # ==========================================================================
    # DISPLACEMENT / BUMP MAP PROCESSING
    # ==========================================================================

    disp_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-400, -600), 'disp_separate', 'Disp Sep')
    disp_separate.mode = 'RGB'
    links.new(displacement_tex.outputs['Color'], disp_separate.inputs['Color'])

    disp_inv = create_node(nodes, 'ShaderNodeMath', (-250, -600), 'disp_inv', 'Disp Inv')
    disp_inv.operation = 'SUBTRACT'
    disp_inv.inputs[0].default_value = 1.0
    links.new(disp_separate.outputs['Red'], disp_inv.inputs[1])

    disp_mix = create_node(nodes, 'ShaderNodeMix', (-100, -600), 'disp_mix', 'Disp Mix')
    disp_mix.data_type = 'FLOAT'
    links.new(disp_map_inv_node.outputs[0], disp_mix.inputs['Factor'])
    links.new(disp_separate.outputs['Red'], disp_mix.inputs[2])
    links.new(disp_inv.outputs[0], disp_mix.inputs[3])

    # Bump strength gated by tex_enable
    disp_str_gated = create_node(nodes, 'ShaderNodeMath', (-50, -650), 'disp_str_gated', 'Disp Str Gated')
    disp_str_gated.operation = 'MULTIPLY'
    links.new(disp_map_str_node.outputs[0], disp_str_gated.inputs[0])
    links.new(tex_enable_node.outputs[0], disp_str_gated.inputs[1])

    disp_bump = create_node(nodes, 'ShaderNodeBump', (100, -600), 'disp_bump', 'Disp Bump')
    disp_bump.inputs['Distance'].default_value = 0.02
    links.new(disp_mix.outputs[0], disp_bump.inputs['Height'])
    links.new(disp_str_gated.outputs[0], disp_bump.inputs['Strength'])
    links.new(normal_map_node.outputs['Normal'], disp_bump.inputs['Normal'])

    # ==========================================================================
    # COMBINE NORMALS - Aniso + Normal Map + Displacement Bump
    # ==========================================================================

    normal_mix_factor = create_node(nodes, 'ShaderNodeMath', (250, -300), 'normal_mix_factor', 'Normal Mix Fac')
    normal_mix_factor.operation = 'MULTIPLY'
    links.new(tex_enable_node.outputs[0], normal_mix_factor.inputs[0])
    normal_mix_factor.inputs[1].default_value = 1.0

    final_normal = create_node(nodes, 'ShaderNodeMix', (400, -300), 'final_normal', 'Final Normal')
    final_normal.data_type = 'VECTOR'
    links.new(normal_mix_factor.outputs[0], final_normal.inputs['Factor'])
    links.new(aniso_bump.outputs['Normal'], final_normal.inputs[4])
    links.new(disp_bump.outputs['Normal'], final_normal.inputs[5])

    # ==========================================================================
    # BASE COLOR PIPELINE
    # ==========================================================================

    # Effective color map strength = base_color_map_strength * tex_enable
    color_map_str_eff = create_node(nodes, 'ShaderNodeMath', (-800, -400), 'color_map_str_eff', 'Color Str Eff')
    color_map_str_eff.operation = 'MULTIPLY'
    links.new(base_color_map_str_node.outputs[0], color_map_str_eff.inputs[0])
    links.new(tex_enable_node.outputs[0], color_map_str_eff.inputs[1])

    # Mix solid color with texture map
    base_color_mix = create_node(nodes, 'ShaderNodeMix', (-600, -400), 'base_color_mix', 'Color Map Mix')
    base_color_mix.data_type = 'RGBA'
    links.new(color_map_str_eff.outputs[0], base_color_mix.inputs['Factor'])
    links.new(base_color_node.outputs['Color'], base_color_mix.inputs[6])
    links.new(base_color_tex.outputs['Color'], base_color_mix.inputs[7])

    # Tint: multiply texture result by solid color when tint is enabled
    base_color_tinted = create_node(nodes, 'ShaderNodeMix', (-400, -400), 'base_color_tinted', 'Color Tinted')
    base_color_tinted.data_type = 'RGBA'
    base_color_tinted.blend_type = 'MULTIPLY'
    links.new(base_color_tint_node.outputs[0], base_color_tinted.inputs['Factor'])
    links.new(base_color_mix.outputs[2], base_color_tinted.inputs[6])
    # Multiply: mix output * base_color
    tint_mul = create_node(nodes, 'ShaderNodeMix', (-500, -450), 'tint_mul', 'Tint Multiply')
    tint_mul.data_type = 'RGBA'
    tint_mul.blend_type = 'MULTIPLY'
    tint_mul.inputs['Factor'].default_value = 1.0
    links.new(base_color_mix.outputs[2], tint_mul.inputs[6])
    links.new(base_color_node.outputs['Color'], tint_mul.inputs[7])
    links.new(tint_mul.outputs[2], base_color_tinted.inputs[7])

    # ==========================================================================
    # AO PROCESSING - Darkens base color
    # ==========================================================================

    ao_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-250, -1000), 'ao_separate', 'AO Sep')
    ao_separate.mode = 'RGB'
    links.new(ao_tex.outputs['Color'], ao_separate.inputs['Color'])

    ao_powered = create_node(nodes, 'ShaderNodeMath', (-100, -1000), 'ao_powered', 'AO Power')
    ao_powered.operation = 'POWER'
    links.new(ao_separate.outputs['Red'], ao_powered.inputs[0])
    links.new(ao_map_str_node.outputs[0], ao_powered.inputs[1])

    # Mix AO based on tex_enable (1.0 when disabled, AO when enabled)
    ao_factor = create_node(nodes, 'ShaderNodeMix', (50, -1000), 'ao_factor', 'AO Factor')
    ao_factor.data_type = 'FLOAT'
    links.new(tex_enable_node.outputs[0], ao_factor.inputs['Factor'])
    ao_factor.inputs[2].default_value = 1.0  # No texture = white AO
    links.new(ao_powered.outputs[0], ao_factor.inputs[3])

    ao_to_color = create_node(nodes, 'ShaderNodeCombineColor', (100, -1050), 'ao_to_color', 'AO to Color')
    ao_to_color.mode = 'RGB'
    links.new(ao_factor.outputs[0], ao_to_color.inputs['Red'])
    links.new(ao_factor.outputs[0], ao_to_color.inputs['Green'])
    links.new(ao_factor.outputs[0], ao_to_color.inputs['Blue'])

    base_color_with_ao = create_node(nodes, 'ShaderNodeMix', (300, -1050), 'base_color_with_ao', 'Base + AO')
    base_color_with_ao.data_type = 'RGBA'
    base_color_with_ao.blend_type = 'MULTIPLY'
    base_color_with_ao.inputs['Factor'].default_value = 1.0
    links.new(base_color_tinted.outputs[2], base_color_with_ao.inputs[6])
    links.new(ao_to_color.outputs['Color'], base_color_with_ao.inputs[7])

    # ==========================================================================
    # ROUGHNESS MAP PIPELINE
    # ==========================================================================

    # Get roughness texture value
    rough_tex_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-800, -800), 'rough_tex_separate', 'Rough Sep')
    rough_tex_separate.mode = 'RGB'
    links.new(roughness_tex.outputs['Color'], rough_tex_separate.inputs['Color'])

    # Invert if roughness_map_invert is enabled (for Gloss maps)
    rough_tex_inv = create_node(nodes, 'ShaderNodeMath', (-650, -800), 'rough_tex_inv', 'Rough Inv')
    rough_tex_inv.operation = 'SUBTRACT'
    rough_tex_inv.inputs[0].default_value = 1.0
    links.new(rough_tex_separate.outputs['Red'], rough_tex_inv.inputs[1])

    rough_tex_mix = create_node(nodes, 'ShaderNodeMix', (-500, -800), 'rough_tex_mix', 'Rough Inv Mix')
    rough_tex_mix.data_type = 'FLOAT'
    links.new(roughness_map_inv_node.outputs[0], rough_tex_mix.inputs['Factor'])
    links.new(rough_tex_separate.outputs['Red'], rough_tex_mix.inputs[2])
    links.new(rough_tex_inv.outputs[0], rough_tex_mix.inputs[3])

    # Effective roughness map strength = strength * tex_enable
    rough_map_str_eff = create_node(nodes, 'ShaderNodeMath', (-400, -850), 'rough_map_str_eff', 'Rough Str Eff')
    rough_map_str_eff.operation = 'MULTIPLY'
    links.new(roughness_map_str_node.outputs[0], rough_map_str_eff.inputs[0])
    links.new(tex_enable_node.outputs[0], rough_map_str_eff.inputs[1])

    # Mix base roughness with texture roughness
    roughness_map_applied = create_node(nodes, 'ShaderNodeMix', (-250, -800), 'roughness_map_applied', 'Rough Map Applied')
    roughness_map_applied.data_type = 'FLOAT'
    links.new(rough_map_str_eff.outputs[0], roughness_map_applied.inputs['Factor'])
    links.new(clamp_base_roughness.outputs[0], roughness_map_applied.inputs[2])
    links.new(rough_tex_mix.outputs[0], roughness_map_applied.inputs[3])

    # ==========================================================================
    # GLOSS MAP PROCESSING - Affects roughness (additive)
    # ==========================================================================

    gloss_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-250, -900), 'gloss_separate', 'Gloss Sep')
    gloss_separate.mode = 'RGB'
    links.new(gloss_tex.outputs['Color'], gloss_separate.inputs['Color'])

    # Convert gloss to roughness (invert)
    gloss_to_rough = create_node(nodes, 'ShaderNodeMath', (-100, -900), 'gloss_to_rough', 'Gloss to Rough')
    gloss_to_rough.operation = 'SUBTRACT'
    gloss_to_rough.inputs[0].default_value = 1.0
    links.new(gloss_separate.outputs['Red'], gloss_to_rough.inputs[1])

    # Center around 0.5 for additive effect
    gloss_centered = create_node(nodes, 'ShaderNodeMath', (50, -900), 'gloss_centered', 'Gloss Centered')
    gloss_centered.operation = 'SUBTRACT'
    links.new(gloss_to_rough.outputs[0], gloss_centered.inputs[0])
    gloss_centered.inputs[1].default_value = 0.5

    gloss_scaled = create_node(nodes, 'ShaderNodeMath', (200, -900), 'gloss_scaled', 'Gloss Scaled')
    gloss_scaled.operation = 'MULTIPLY'
    links.new(gloss_centered.outputs[0], gloss_scaled.inputs[0])
    links.new(gloss_map_str_node.outputs[0], gloss_scaled.inputs[1])

    # Gate by tex_enable
    gloss_enabled = create_node(nodes, 'ShaderNodeMath', (350, -900), 'gloss_enabled', 'Gloss Enabled')
    gloss_enabled.operation = 'MULTIPLY'
    links.new(gloss_scaled.outputs[0], gloss_enabled.inputs[0])
    links.new(tex_enable_node.outputs[0], gloss_enabled.inputs[1])

    # Add gloss contribution to roughness
    roughness_with_gloss = create_node(nodes, 'ShaderNodeMath', (500, -850), 'roughness_with_gloss', 'Rough + Gloss')
    roughness_with_gloss.operation = 'ADD'
    links.new(roughness_map_applied.outputs[0], roughness_with_gloss.inputs[0])
    links.new(gloss_enabled.outputs[0], roughness_with_gloss.inputs[1])

    roughness_final_clamp = create_node(nodes, 'ShaderNodeClamp', (650, -850), 'roughness_final_clamp', 'Final Rough')
    links.new(roughness_with_gloss.outputs[0], roughness_final_clamp.inputs['Value'])

    # ==========================================================================
    # METALLIC PIPELINE
    # ==========================================================================

    # Get metallic texture value
    metal_tex_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-800, -1000), 'metal_tex_separate', 'Metal Sep')
    metal_tex_separate.mode = 'RGB'
    links.new(metallic_tex.outputs['Color'], metal_tex_separate.inputs['Color'])

    # Effective metallic map strength = strength * tex_enable
    metal_map_str_eff = create_node(nodes, 'ShaderNodeMath', (-600, -1050), 'metal_map_str_eff', 'Metal Str Eff')
    metal_map_str_eff.operation = 'MULTIPLY'
    links.new(metallic_map_str_node.outputs[0], metal_map_str_eff.inputs[0])
    links.new(tex_enable_node.outputs[0], metal_map_str_eff.inputs[1])

    # Mix base metallic with texture metallic
    metallic_final = create_node(nodes, 'ShaderNodeMix', (-400, -1000), 'metallic_final', 'Metallic Final')
    metallic_final.data_type = 'FLOAT'
    links.new(metal_map_str_eff.outputs[0], metallic_final.inputs['Factor'])
    links.new(base_metallic_node.outputs[0], metallic_final.inputs[2])
    links.new(metal_tex_separate.outputs['Red'], metallic_final.inputs[3])

    # ==========================================================================
    # OPACITY PIPELINE
    # ==========================================================================

    # Get opacity texture value
    opacity_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-800, -1200), 'opacity_separate', 'Opacity Sep')
    opacity_separate.mode = 'RGB'
    links.new(opacity_tex.outputs['Color'], opacity_separate.inputs['Color'])

    # Invert if needed
    opacity_inv = create_node(nodes, 'ShaderNodeMath', (-650, -1200), 'opacity_inv', 'Opacity Inv')
    opacity_inv.operation = 'SUBTRACT'
    opacity_inv.inputs[0].default_value = 1.0
    links.new(opacity_separate.outputs['Red'], opacity_inv.inputs[1])

    opacity_inv_mix = create_node(nodes, 'ShaderNodeMix', (-500, -1200), 'opacity_inv_mix', 'Opacity Inv Mix')
    opacity_inv_mix.data_type = 'FLOAT'
    links.new(opacity_map_inv_node.outputs[0], opacity_inv_mix.inputs['Factor'])
    links.new(opacity_separate.outputs['Red'], opacity_inv_mix.inputs[2])
    links.new(opacity_inv.outputs[0], opacity_inv_mix.inputs[3])

    # Effective opacity = mix(1.0, texture_value * strength, tex_enable)
    opacity_str_applied = create_node(nodes, 'ShaderNodeMix', (-350, -1200), 'opacity_str_applied', 'Opacity Str')
    opacity_str_applied.data_type = 'FLOAT'
    links.new(opacity_map_str_node.outputs[0], opacity_str_applied.inputs['Factor'])
    opacity_str_applied.inputs[2].default_value = 1.0  # At strength 0, fully opaque
    links.new(opacity_inv_mix.outputs[0], opacity_str_applied.inputs[3])

    # Gate by tex_enable
    opacity_final = create_node(nodes, 'ShaderNodeMix', (-200, -1200), 'opacity_final', 'Opacity Final')
    opacity_final.data_type = 'FLOAT'
    links.new(tex_enable_node.outputs[0], opacity_final.inputs['Factor'])
    opacity_final.inputs[2].default_value = 1.0  # No texture = fully opaque
    links.new(opacity_str_applied.outputs[0], opacity_final.inputs[3])

    # ==========================================================================
    # EMISSION MAP PIPELINE
    # ==========================================================================

    # Emission color from texture (gated by tex_enable)
    emission_color_gate = create_node(nodes, 'ShaderNodeMix', (-600, -1400), 'emission_color_gate', 'Emission Color Gate')
    emission_color_gate.data_type = 'RGBA'
    links.new(tex_enable_node.outputs[0], emission_color_gate.inputs['Factor'])
    # When tex disabled: black (no emission)
    emission_color_gate.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
    links.new(emission_tex.outputs['Color'], emission_color_gate.inputs[7])

    # Emission strength gated by tex_enable
    emission_str_gated = create_node(nodes, 'ShaderNodeMath', (-400, -1400), 'emission_str_gated', 'Emission Str Gated')
    emission_str_gated.operation = 'MULTIPLY'
    links.new(emission_map_str_node.outputs[0], emission_str_gated.inputs[0])
    links.new(tex_enable_node.outputs[0], emission_str_gated.inputs[1])

    # ==========================================================================
    # HEIGHT MAP - TRUE DISPLACEMENT
    # ==========================================================================

    height_separate = create_node(nodes, 'ShaderNodeSeparateColor', (-800, -1600), 'height_separate', 'Height Sep')
    height_separate.mode = 'RGB'
    links.new(height_tex.outputs['Color'], height_separate.inputs['Color'])

    # Height scale gated by tex_enable
    height_scale_gated = create_node(nodes, 'ShaderNodeMath', (-600, -1600), 'height_scale_gated', 'Height Scale Gated')
    height_scale_gated.operation = 'MULTIPLY'
    links.new(height_map_scale_node.outputs[0], height_scale_gated.inputs[0])
    links.new(tex_enable_node.outputs[0], height_scale_gated.inputs[1])

    height_displacement = create_node(nodes, 'ShaderNodeDisplacement', (-400, -1600), 'height_displacement', 'Height Displacement')
    links.new(height_separate.outputs['Red'], height_displacement.inputs['Height'])
    links.new(height_map_mid_node.outputs[0], height_displacement.inputs['Midlevel'])
    links.new(height_scale_gated.outputs[0], height_displacement.inputs['Scale'])
    links.new(final_normal.outputs[1], height_displacement.inputs['Normal'])

    # ==========================================================================
    # FRESNEL FOR COLOR SHIFT
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

    # Random noise for per-sparkle variation
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
    random_offset_1 = create_node(nodes, 'ShaderNodeVectorMath', (-200, 200), 'random_offset_1', 'Rand Offset 1')
    random_offset_1.operation = 'ADD'
    links.new(tex_coord.outputs['Object'], random_offset_1.inputs[0])
    random_offset_1.inputs[1].default_value = (100.0, 0.0, 0.0)
    links.new(random_offset_1.outputs[0], color_random_2.inputs['Vector'])

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
    random_offset_2 = create_node(nodes, 'ShaderNodeVectorMath', (-200, 100), 'random_offset_2', 'Rand Offset 2')
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

    view_negate = create_node(nodes, 'ShaderNodeVectorMath', (200, -600), 'view_negate', 'View Negate')
    view_negate.operation = 'SCALE'
    view_negate.inputs['Scale'].default_value = -1.0
    links.new(geometry.outputs['Incoming'], view_negate.inputs[0])

    surface_dot = create_node(nodes, 'ShaderNodeVectorMath', (400, -600), 'surface_dot', 'Surface Dot')
    surface_dot.operation = 'DOT_PRODUCT'
    links.new(final_normal.outputs[1], surface_dot.inputs[0])
    links.new(view_negate.outputs[0], surface_dot.inputs[1])

    # ==========================================================================
    # PRIMARY SPARKLE LAYER
    # ==========================================================================

    primary_seed_vec = create_node(nodes, 'ShaderNodeCombineXYZ', (100, 850), 'primary_seed_vec', 'Primary Seed Vec')
    links.new(primary_seed_node.outputs[0], primary_seed_vec.inputs['X'])
    links.new(primary_seed_node.outputs[0], primary_seed_vec.inputs['Y'])
    links.new(primary_seed_node.outputs[0], primary_seed_vec.inputs['Z'])
    primary_coord_offset = create_node(nodes, 'ShaderNodeVectorMath', (300, 800), 'primary_coord_offset', 'Primary Coord')
    primary_coord_offset.operation = 'ADD'
    links.new(tex_coord.outputs['Object'], primary_coord_offset.inputs[0])
    links.new(primary_seed_vec.outputs[0], primary_coord_offset.inputs[1])

    primary_density_scaled = create_node(nodes, 'ShaderNodeMath', (300, 750), 'primary_density_scaled', 'Primary Density Scaled')
    primary_density_scaled.operation = 'MULTIPLY'
    links.new(primary_density_node.outputs[0], primary_density_scaled.inputs[0])
    links.new(global_density_mult_node.outputs[0], primary_density_scaled.inputs[1])

    primary_voronoi = create_node(nodes, 'ShaderNodeTexVoronoi', (500, 800), 'primary_voronoi', 'Primary Voronoi')
    primary_voronoi.voronoi_dimensions = '3D'
    primary_voronoi.feature = 'F1'
    links.new(primary_coord_offset.outputs[0], primary_voronoi.inputs['Vector'])
    links.new(primary_density_scaled.outputs[0], primary_voronoi.inputs['Scale'])

    primary_size_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (500, 700), 'primary_size_noise', 'Primary Size Noise')
    primary_size_noise.noise_dimensions = '3D'
    links.new(primary_voronoi.outputs['Position'], primary_size_noise.inputs['Vector'])

    primary_size_var_min = create_node(nodes, 'ShaderNodeMath', (500, 650), 'primary_size_var_min', 'Primary Var Min')
    primary_size_var_min.operation = 'SUBTRACT'
    primary_size_var_min.inputs[0].default_value = 1.0
    links.new(primary_size_var_node.outputs[0], primary_size_var_min.inputs[1])

    primary_size_var_calc = create_node(nodes, 'ShaderNodeMapRange', (700, 700), 'primary_size_var_calc', 'Primary Size Var')
    links.new(primary_size_noise.outputs['Value'], primary_size_var_calc.inputs['Value'])
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

    primary_mask = create_node(nodes, 'ShaderNodeMath', (1100, 750), 'primary_mask', 'Primary Mask')
    primary_mask.operation = 'LESS_THAN'
    links.new(primary_voronoi.outputs['Distance'], primary_mask.inputs[0])
    links.new(primary_size_scaled.outputs[0], primary_mask.inputs[1])

    # Per-cell flake normal
    primary_normal_x_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 600), 'primary_normal_x', 'Primary Norm X')
    primary_normal_x_noise.noise_dimensions = '3D'
    links.new(primary_voronoi.outputs['Position'], primary_normal_x_noise.inputs['Vector'])

    primary_normal_y_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, 550), 'primary_ny_offset', 'Primary NY Offset')
    primary_normal_y_offset.operation = 'ADD'
    links.new(primary_voronoi.outputs['Position'], primary_normal_y_offset.inputs[0])
    primary_normal_y_offset.inputs[1].default_value = (73.156, 0.0, 0.0)
    primary_normal_y_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 550), 'primary_normal_y', 'Primary Norm Y')
    primary_normal_y_noise.noise_dimensions = '3D'
    links.new(primary_normal_y_offset.outputs[0], primary_normal_y_noise.inputs['Vector'])

    primary_normal_z_offset = create_node(nodes, 'ShaderNodeVectorMath', (500, 500), 'primary_nz_offset', 'Primary NZ Offset')
    primary_normal_z_offset.operation = 'ADD'
    links.new(primary_voronoi.outputs['Position'], primary_normal_z_offset.inputs[0])
    primary_normal_z_offset.inputs[1].default_value = (0.0, 91.372, 0.0)
    primary_normal_z_noise = create_node(nodes, 'ShaderNodeTexWhiteNoise', (700, 500), 'primary_normal_z', 'Primary Norm Z')
    primary_normal_z_noise.noise_dimensions = '3D'
    links.new(primary_normal_z_offset.outputs[0], primary_normal_z_noise.inputs['Vector'])

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

    primary_random_dir = create_node(nodes, 'ShaderNodeCombineXYZ', (1100, 550), 'primary_random_dir', 'Primary Rand Dir')
    links.new(primary_nx_map.outputs[0], primary_random_dir.inputs['X'])
    links.new(primary_ny_map.outputs[0], primary_random_dir.inputs['Y'])
    links.new(primary_nz_map.outputs[0], primary_random_dir.inputs['Z'])

    primary_random_norm = create_node(nodes, 'ShaderNodeVectorMath', (1300, 550), 'primary_random_norm', 'Primary Rand Norm')
    primary_random_norm.operation = 'NORMALIZE'
    links.new(primary_random_dir.outputs[0], primary_random_norm.inputs[0])

    primary_flake_normal = create_node(nodes, 'ShaderNodeMix', (1500, 550), 'primary_flake_normal', 'Primary Flake N')
    primary_flake_normal.data_type = 'VECTOR'
    links.new(orientation_randomness_node.outputs[0], primary_flake_normal.inputs['Factor'])
    links.new(final_normal.outputs[1], primary_flake_normal.inputs[4])
    links.new(primary_random_norm.outputs[0], primary_flake_normal.inputs[5])

    primary_flake_normal_norm = create_node(nodes, 'ShaderNodeVectorMath', (1700, 550), 'primary_flake_n_norm', 'Primary Flake Norm')
    primary_flake_normal_norm.operation = 'NORMALIZE'
    links.new(primary_flake_normal.outputs[1], primary_flake_normal_norm.inputs[0])

    primary_flake_dot = create_node(nodes, 'ShaderNodeVectorMath', (1900, 600), 'primary_flake_dot', 'Primary Flake Dot')
    primary_flake_dot.operation = 'DOT_PRODUCT'
    links.new(primary_flake_normal_norm.outputs[0], primary_flake_dot.inputs[0])
    links.new(view_negate.outputs[0], primary_flake_dot.inputs[1])

    primary_deviation = create_node(nodes, 'ShaderNodeMath', (2100, 600), 'primary_deviation', 'Primary Deviation')
    primary_deviation.operation = 'SUBTRACT'
    links.new(primary_flake_dot.outputs['Value'], primary_deviation.inputs[0])
    links.new(surface_dot.outputs['Value'], primary_deviation.inputs[1])

    primary_dev_map = create_node(nodes, 'ShaderNodeMapRange', (2300, 600), 'primary_dev_map', 'Primary Dev Normalize')
    links.new(primary_deviation.outputs[0], primary_dev_map.inputs['Value'])
    links.new(neg_orient_rand.outputs[0], primary_dev_map.inputs['From Min'])
    links.new(orient_rand_safe.outputs[0], primary_dev_map.inputs['From Max'])
    primary_dev_map.inputs['To Min'].default_value = 0.0
    primary_dev_map.inputs['To Max'].default_value = 1.0

    primary_sparkle_sharp = create_node(nodes, 'ShaderNodeMath', (2500, 600), 'primary_sparkle_sharp', 'Primary Sharp')
    primary_sparkle_sharp.operation = 'POWER'
    links.new(primary_dev_map.outputs[0], primary_sparkle_sharp.inputs[0])
    links.new(sparkle_sharpness_node.outputs[0], primary_sparkle_sharp.inputs[1])

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
    # SECONDARY SPARKLE LAYER
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

    secondary_flake_dot = create_node(nodes, 'ShaderNodeVectorMath', (1900, 100), 'secondary_flake_dot', 'Secondary Flake Dot')
    secondary_flake_dot.operation = 'DOT_PRODUCT'
    links.new(secondary_flake_normal_norm.outputs[0], secondary_flake_dot.inputs[0])
    links.new(view_negate.outputs[0], secondary_flake_dot.inputs[1])

    secondary_deviation = create_node(nodes, 'ShaderNodeMath', (2100, 100), 'secondary_deviation', 'Secondary Deviation')
    secondary_deviation.operation = 'SUBTRACT'
    links.new(secondary_flake_dot.outputs['Value'], secondary_deviation.inputs[0])
    links.new(surface_dot.outputs['Value'], secondary_deviation.inputs[1])

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
    # TERTIARY SPARKLE LAYER
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

    tertiary_flake_dot = create_node(nodes, 'ShaderNodeVectorMath', (1900, -400), 'tertiary_flake_dot', 'Tertiary Flake Dot')
    tertiary_flake_dot.operation = 'DOT_PRODUCT'
    links.new(tertiary_flake_normal_norm.outputs[0], tertiary_flake_dot.inputs[0])
    links.new(view_negate.outputs[0], tertiary_flake_dot.inputs[1])

    tertiary_deviation = create_node(nodes, 'ShaderNodeMath', (2100, -400), 'tertiary_deviation', 'Tertiary Deviation')
    tertiary_deviation.operation = 'SUBTRACT'
    links.new(tertiary_flake_dot.outputs['Value'], tertiary_deviation.inputs[0])
    links.new(surface_dot.outputs['Value'], tertiary_deviation.inputs[1])

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
    sparkle_clamp.inputs['Max'].default_value = 10.0
    links.new(sparkle_all.outputs[0], sparkle_clamp.inputs['Value'])

    # Gate by sparkle_enable master toggle
    sparkle_gated = create_node(nodes, 'ShaderNodeMath', (4100, 300), 'sparkle_gated', 'Sparkle Gated')
    sparkle_gated.operation = 'MULTIPLY'
    links.new(sparkle_clamp.outputs[0], sparkle_gated.inputs[0])
    links.new(sparkle_enable_node.outputs[0], sparkle_gated.inputs[1])

    sparkle_normal_final = primary_flake_normal_norm  # Reuse primary normal

    # ==========================================================================
    # SPARKLE BSDF
    # ==========================================================================

    sparkle_rough_clamp = create_node(nodes, 'ShaderNodeClamp', (4100, -400), 'sparkle_rough_clamp', 'Sparkle Rough')
    links.new(sparkle_roughness_node.outputs[0], sparkle_rough_clamp.inputs['Value'])

    sparkle_bsdf = create_node(nodes, 'ShaderNodeBsdfPrincipled', (2800, 200), 'sparkle_bsdf', 'Sparkle BSDF')
    links.new(sparkle_with_base.outputs[2], sparkle_bsdf.inputs['Base Color'])
    links.new(sparkle_metallic_node.outputs[0], sparkle_bsdf.inputs['Metallic'])
    links.new(sparkle_rough_clamp.outputs[0], sparkle_bsdf.inputs['Roughness'])
    links.new(sparkle_normal_final.outputs[0], sparkle_bsdf.inputs['Normal'])

    # Emission from sparkle overdrive
    sparkle_emission_calc = create_node(nodes, 'ShaderNodeMath', (2600, 100), 'sparkle_emission_calc', 'Sparkle Emission Calc')
    sparkle_emission_calc.operation = 'MULTIPLY'
    links.new(sparkle_gated.outputs[0], sparkle_emission_calc.inputs[0])
    links.new(emission_str_node.outputs[0], sparkle_emission_calc.inputs[1])

    links.new(sparkle_emission_calc.outputs[0], sparkle_bsdf.inputs['Emission Strength'])
    links.new(sparkle_with_base.outputs[2], sparkle_bsdf.inputs['Emission Color'])

    # ==========================================================================
    # MAIN PBR BSDF
    # ==========================================================================

    main_bsdf = create_node(nodes, 'ShaderNodeBsdfPrincipled', (3000, -100), 'main_bsdf', 'Main BSDF')
    # Zero out defaults
    main_bsdf.inputs['Subsurface Weight'].default_value = 0.0
    main_bsdf.inputs['Subsurface Scale'].default_value = 0.0

    # Base Color (with AO applied)
    links.new(base_color_with_ao.outputs[2], main_bsdf.inputs['Base Color'])

    # Metallic (from metallic pipeline)
    links.new(metallic_final.outputs[0], main_bsdf.inputs['Metallic'])

    # Roughness (from roughness pipeline with gloss)
    links.new(roughness_final_clamp.outputs[0], main_bsdf.inputs['Roughness'])

    # IOR
    links.new(ior_node.outputs[0], main_bsdf.inputs['IOR'])

    # Normal
    links.new(final_normal.outputs[1], main_bsdf.inputs['Normal'])

    # Tangent (for aniso)
    links.new(aniso_tangent.outputs[0], main_bsdf.inputs['Tangent'])

    # SSS
    links.new(sss_weight_node.outputs[0], main_bsdf.inputs['Subsurface Weight'])
    links.new(sss_radius_node.outputs[0], main_bsdf.inputs['Subsurface Radius'])
    links.new(sss_scale_node.outputs[0], main_bsdf.inputs['Subsurface Scale'])

    # Clearcoat
    links.new(coat_weight_node.outputs[0], main_bsdf.inputs['Coat Weight'])
    links.new(coat_rough_node.outputs[0], main_bsdf.inputs['Coat Roughness'])

    # Anisotropic
    links.new(aniso_rough_node.outputs[0], main_bsdf.inputs['Anisotropic'])

    # Emission from emission map
    links.new(emission_color_gate.outputs[2], main_bsdf.inputs['Emission Color'])
    links.new(emission_str_gated.outputs[0], main_bsdf.inputs['Emission Strength'])

    # Alpha from opacity pipeline
    links.new(opacity_final.outputs[0], main_bsdf.inputs['Alpha'])

    # ==========================================================================
    # FINAL MIX
    # ==========================================================================

    # Sparkle mix factor (clamped 0-1 for shader mix)
    mix_factor = create_node(nodes, 'ShaderNodeClamp', (3000, 100), 'mix_factor', 'Mix Factor')
    mix_factor.inputs['Min'].default_value = 0.0
    mix_factor.inputs['Max'].default_value = 1.0
    links.new(sparkle_gated.outputs[0], mix_factor.inputs['Value'])

    plastic_sparkle_mix = create_node(nodes, 'ShaderNodeMixShader', (3200, 100), 'plastic_sparkle_mix', 'Main + Sparkle')
    links.new(mix_factor.outputs[0], plastic_sparkle_mix.inputs['Fac'])
    links.new(main_bsdf.outputs['BSDF'], plastic_sparkle_mix.inputs[1])
    links.new(sparkle_bsdf.outputs['BSDF'], plastic_sparkle_mix.inputs[2])

    # Overall effect mix
    overall_mix = create_node(nodes, 'ShaderNodeMixShader', (3400, 100), 'overall_mix', 'Overall Mix')
    links.new(overall_effect_node.outputs[0], overall_mix.inputs['Fac'])
    links.new(main_bsdf.outputs['BSDF'], overall_mix.inputs[1])
    links.new(plastic_sparkle_mix.outputs['Shader'], overall_mix.inputs[2])

    # Output
    output = create_node(nodes, 'ShaderNodeOutputMaterial', (3600, 100), 'output', 'Output')
    links.new(overall_mix.outputs['Shader'], output.inputs['Surface'])
    links.new(height_displacement.outputs['Displacement'], output.inputs['Displacement'])


# =============================================================================
# UPDATE FUNCTIONS
# =============================================================================

def update_shader_from_properties(mat):
    """Update shader node values from material properties."""
    if not mat.use_nodes:
        return

    nodes = mat.node_tree.nodes
    props = mat.universal_pbr

    def set_value(name, value):
        if name in nodes:
            nodes[name].outputs[0].default_value = value

    def set_color(name, color):
        if name in nodes:
            nodes[name].outputs[0].default_value = color

    # Base Material
    set_color('base_color', props.base_color)
    set_value('base_roughness', props.base_roughness)
    set_value('base_metallic', props.base_metallic)
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

    # SSS
    set_value('sss_weight', props.sss_weight if props.sss_enable else 0.0)
    set_value('sss_radius', props.sss_radius if props.sss_enable else 0.0)
    set_value('sss_scale', props.sss_scale if props.sss_enable else 0.0)

    # Clearcoat
    set_value('coat_weight', props.clearcoat_weight if props.clearcoat_enable else 0.0)
    set_value('coat_roughness', props.clearcoat_roughness)

    # Sparkle System
    set_value('sparkle_enable', 1.0 if props.sparkle_enable else 0.0)

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

    # Sparkle Response
    set_value('sparkle_roughness', props.sparkle_roughness)
    set_value('sparkle_sharpness', props.sparkle_sharpness)
    set_value('orientation_randomness', props.orientation_randomness)
    set_value('overdrive', props.overdrive)
    set_value('emission_strength', props.emission_strength)
    set_value('global_density_multiplier', props.global_density_multiplier)
    set_value('global_size_multiplier', props.global_size_multiplier)

    # Texture Controls
    set_value('tex_enable', 1.0 if props.tex_enable else 0.0)
    set_value('base_color_map_strength', props.base_color_map_strength)
    set_value('base_color_tint_enable', 1.0 if props.base_color_tint_enable else 0.0)
    set_value('normal_map_strength', props.normal_map_strength)
    set_value('normal_map_invert', 1.0 if props.normal_map_invert else 0.0)
    set_value('roughness_map_strength', props.roughness_map_strength)
    set_value('roughness_map_invert', 1.0 if props.roughness_map_invert else 0.0)
    set_value('metallic_map_strength', props.metallic_map_strength)
    set_value('displacement_map_strength', props.displacement_map_strength)
    set_value('displacement_map_invert', 1.0 if props.displacement_map_invert else 0.0)
    set_value('height_map_scale', props.height_map_scale)
    set_value('height_map_midlevel', props.height_map_midlevel)
    set_value('ao_map_strength', props.ao_map_strength)
    set_value('opacity_map_strength', props.opacity_map_strength)
    set_value('opacity_map_invert', 1.0 if props.opacity_map_invert else 0.0)
    set_value('emission_map_strength', props.emission_map_strength)
    set_value('gloss_map_strength', props.gloss_map_strength)

    # UV Mapping
    if 'uv_mapping' in nodes:
        mapping = nodes['uv_mapping']
        mapping.inputs['Location'].default_value = props.tex_offset
        mapping.inputs['Rotation'].default_value = props.tex_rotation
        mapping.inputs['Scale'].default_value = props.tex_scale

    # Projection mode update on all texture nodes
    projection = props.tex_projection
    tex_node_names = [
        'base_color_tex', 'normal_tex', 'roughness_tex', 'metallic_tex',
        'displacement_tex', 'height_tex', 'ao_tex', 'opacity_tex',
        'emission_tex', 'gloss_tex'
    ]
    for node_name in tex_node_names:
        if node_name in nodes:
            nodes[node_name].projection = projection
            if projection == 'BOX':
                nodes[node_name].projection_blend = props.tex_box_blend

    # Overall
    set_value('overall_effect', props.overall_effect)


def update_textures_from_properties(mat):
    """Update texture node images and colorspaces."""
    if not mat.use_nodes:
        return

    nodes = mat.node_tree.nodes
    props = mat.universal_pbr

    texture_mapping = {
        'base_color_tex': (props.base_color_map, 'sRGB'),
        'normal_tex': (props.normal_map, 'Non-Color'),
        'roughness_tex': (props.roughness_map, 'Non-Color'),
        'metallic_tex': (props.metallic_map, 'Non-Color'),
        'displacement_tex': (props.displacement_map, 'Non-Color'),
        'height_tex': (props.height_map, 'Non-Color'),
        'ao_tex': (props.ao_map, 'Non-Color'),
        'opacity_tex': (props.opacity_map, 'Non-Color'),
        'emission_tex': (props.emission_map, 'sRGB'),
        'gloss_tex': (props.gloss_map, 'Non-Color'),
    }

    for node_name, (image, colorspace) in texture_mapping.items():
        if node_name in nodes:
            nodes[node_name].image = image
            if image:
                image.colorspace_settings.name = colorspace


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    UniversalPBRProperties,
    MATERIAL_OT_create_universal_pbr,
    MATERIAL_OT_upbr_apply_preset,
    MATERIAL_OT_upbr_save_preset,
    MATERIAL_OT_upbr_delete_preset,
    MATERIAL_PT_upbr_main,
    MATERIAL_PT_upbr_presets,
    MATERIAL_PT_upbr_base,
    MATERIAL_PT_upbr_textures,
    MATERIAL_PT_upbr_surface,
    MATERIAL_PT_upbr_sparkles,
    MATERIAL_PT_upbr_sparkle_primary,
    MATERIAL_PT_upbr_sparkle_secondary,
    MATERIAL_PT_upbr_sparkle_tertiary,
    MATERIAL_PT_upbr_sparkle_color,
    MATERIAL_PT_upbr_sparkle_response,
    MATERIAL_PT_upbr_advanced,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.universal_pbr = PointerProperty(type=UniversalPBRProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Material.universal_pbr


if __name__ == "__main__":
    register()
