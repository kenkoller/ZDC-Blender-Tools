bl_info = {
    "name": "ZDC - Universal PBR Shader",
    "author": "Ziti Design & Creative",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "Properties > Material > ZDC",
    "description": "Full PBR shader with 10 texture maps and optional sparkle system",
    "category": "ZDC Tools",
}

from . import universal_pbr_shader


def register():
    universal_pbr_shader.register()


def unregister():
    universal_pbr_shader.unregister()


if __name__ == "__main__":
    register()
