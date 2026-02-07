# Material presets for Cabinet Generator
# Provides common cabinet material presets

import bpy


def get_or_create_material(name, create_func):
    """Get existing material or create new one."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    return create_func(name)


def create_wood_material(name, color=(0.4, 0.25, 0.15, 1.0), roughness=0.5):
    """Create a basic wood material with principled BSDF.

    Args:
        name: Material name
        color: RGBA tuple for base color
        roughness: Surface roughness (0-1)

    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Roughness'].default_value = roughness

    # Connect
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    return mat


def create_laminate_material(name, color=(0.8, 0.8, 0.78, 1.0), roughness=0.3):
    """Create a laminate/melamine material.

    Args:
        name: Material name
        color: RGBA tuple for base color
        roughness: Surface roughness (0-1)

    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Specular IOR Level'].default_value = 0.5

    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    return mat


def create_metal_material(name, color=(0.7, 0.7, 0.72, 1.0), roughness=0.2):
    """Create a brushed metal material for handles.

    Args:
        name: Material name
        color: RGBA tuple for base color
        roughness: Surface roughness (0-1)

    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = roughness

    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    return mat


def create_glass_material(name, color=(0.9, 0.95, 1.0, 0.1), roughness=0.0):
    """Create a glass material for cabinet doors.

    Args:
        name: Material name
        color: RGBA tuple (alpha controls transparency)
        roughness: Surface roughness (0-1)

    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'HASHED'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = color[:3] + (1.0,)
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Transmission Weight'].default_value = 0.95
    principled.inputs['IOR'].default_value = 1.45

    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    return mat


# ============ PRESET DEFINITIONS ============

WOOD_PRESETS = {
    'OAK': {
        'color': (0.55, 0.4, 0.25, 1.0),
        'roughness': 0.45,
        'description': 'Natural oak wood'
    },
    'WALNUT': {
        'color': (0.25, 0.15, 0.1, 1.0),
        'roughness': 0.4,
        'description': 'Dark walnut wood'
    },
    'MAPLE': {
        'color': (0.7, 0.55, 0.4, 1.0),
        'roughness': 0.35,
        'description': 'Light maple wood'
    },
    'CHERRY': {
        'color': (0.45, 0.2, 0.15, 1.0),
        'roughness': 0.4,
        'description': 'Rich cherry wood'
    },
    'BIRCH': {
        'color': (0.8, 0.7, 0.55, 1.0),
        'roughness': 0.45,
        'description': 'Light birch wood'
    },
    'ESPRESSO': {
        'color': (0.12, 0.08, 0.05, 1.0),
        'roughness': 0.35,
        'description': 'Dark espresso stain'
    },
}

LAMINATE_PRESETS = {
    'WHITE': {
        'color': (0.95, 0.95, 0.95, 1.0),
        'roughness': 0.25,
        'description': 'Clean white laminate'
    },
    'GRAY': {
        'color': (0.5, 0.5, 0.52, 1.0),
        'roughness': 0.3,
        'description': 'Modern gray laminate'
    },
    'BLACK': {
        'color': (0.05, 0.05, 0.05, 1.0),
        'roughness': 0.2,
        'description': 'Sleek black laminate'
    },
    'CREAM': {
        'color': (0.95, 0.92, 0.85, 1.0),
        'roughness': 0.3,
        'description': 'Warm cream laminate'
    },
    'NAVY': {
        'color': (0.1, 0.15, 0.3, 1.0),
        'roughness': 0.25,
        'description': 'Deep navy laminate'
    },
    'SAGE': {
        'color': (0.6, 0.68, 0.58, 1.0),
        'roughness': 0.3,
        'description': 'Sage green laminate'
    },
}

METAL_PRESETS = {
    'BRUSHED_NICKEL': {
        'color': (0.75, 0.75, 0.78, 1.0),
        'roughness': 0.25,
        'description': 'Brushed nickel finish'
    },
    'CHROME': {
        'color': (0.85, 0.85, 0.88, 1.0),
        'roughness': 0.1,
        'description': 'Polished chrome'
    },
    'MATTE_BLACK': {
        'color': (0.05, 0.05, 0.05, 1.0),
        'roughness': 0.5,
        'description': 'Matte black metal'
    },
    'BRASS': {
        'color': (0.8, 0.6, 0.2, 1.0),
        'roughness': 0.2,
        'description': 'Warm brass finish'
    },
    'COPPER': {
        'color': (0.75, 0.45, 0.3, 1.0),
        'roughness': 0.25,
        'description': 'Copper finish'
    },
    'GOLD': {
        'color': (0.85, 0.7, 0.35, 1.0),
        'roughness': 0.15,
        'description': 'Gold finish'
    },
    'OIL_RUBBED_BRONZE': {
        'color': (0.2, 0.15, 0.1, 1.0),
        'roughness': 0.4,
        'description': 'Oil rubbed bronze'
    },
}

GLASS_PRESETS = {
    'CLEAR': {
        'color': (0.95, 0.97, 1.0, 0.05),
        'roughness': 0.0,
        'description': 'Clear glass'
    },
    'FROSTED': {
        'color': (0.95, 0.97, 1.0, 0.3),
        'roughness': 0.4,
        'description': 'Frosted/satin glass'
    },
    'SMOKED': {
        'color': (0.3, 0.3, 0.32, 0.2),
        'roughness': 0.0,
        'description': 'Smoked gray glass'
    },
    'SEEDED': {
        'color': (0.9, 0.95, 0.92, 0.1),
        'roughness': 0.15,
        'description': 'Seeded/textured glass'
    },
}


def create_preset_material(category, preset_name):
    """Create a material from a preset.

    Args:
        category: 'WOOD', 'LAMINATE', 'METAL', or 'GLASS'
        preset_name: Name of preset within category

    Returns:
        The created material or None if preset not found
    """
    presets = {
        'WOOD': (WOOD_PRESETS, create_wood_material),
        'LAMINATE': (LAMINATE_PRESETS, create_laminate_material),
        'METAL': (METAL_PRESETS, create_metal_material),
        'GLASS': (GLASS_PRESETS, create_glass_material),
    }

    if category not in presets:
        return None

    preset_dict, create_func = presets[category]

    if preset_name not in preset_dict:
        return None

    preset = preset_dict[preset_name]
    mat_name = f"Cabinet_{category}_{preset_name}"

    return get_or_create_material(
        mat_name,
        lambda n: create_func(n, preset['color'], preset['roughness'])
    )


def create_all_presets():
    """Create all preset materials in the scene."""
    created = []

    for category, (preset_dict, _) in [
        ('WOOD', (WOOD_PRESETS, create_wood_material)),
        ('LAMINATE', (LAMINATE_PRESETS, create_laminate_material)),
        ('METAL', (METAL_PRESETS, create_metal_material)),
        ('GLASS', (GLASS_PRESETS, create_glass_material)),
    ]:
        for preset_name in preset_dict:
            mat = create_preset_material(category, preset_name)
            if mat:
                created.append(mat.name)

    return created


def get_preset_items(category):
    """Get enum items for a preset category.

    Args:
        category: 'WOOD', 'LAMINATE', 'METAL', or 'GLASS'

    Returns:
        List of (identifier, name, description) tuples for EnumProperty
    """
    presets = {
        'WOOD': WOOD_PRESETS,
        'LAMINATE': LAMINATE_PRESETS,
        'METAL': METAL_PRESETS,
        'GLASS': GLASS_PRESETS,
    }

    if category not in presets:
        return []

    items = []
    for key, value in presets[category].items():
        items.append((key, key.replace('_', ' ').title(), value['description']))

    return items


if __name__ == "__main__":
    # Test: create all presets
    materials = create_all_presets()
    print(f"Created {len(materials)} materials:")
    for name in materials:
        print(f"  - {name}")
