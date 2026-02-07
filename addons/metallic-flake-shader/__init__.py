bl_info = {
    "name": "ZDC - Metallic Flake Shader",
    "author": "Ziti Design & Creative",
    "version": (4, 0, 0),
    "blender": (5, 0, 0),
    "location": "Properties > Material > ZDC",
    "description": "Procedural metallic paint flake material system",
    "category": "ZDC Tools",
}

from . import metallic_flake_shader


def register():
    metallic_flake_shader.register()


def unregister():
    metallic_flake_shader.unregister()


if __name__ == "__main__":
    register()
