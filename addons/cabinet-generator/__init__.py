bl_info = {
    "name": "ZDC - Cabinet Generator",
    "author": "Ziti Design & Creative",
    "version": (4, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > ZDC",
    "description": "Parametric cabinet generation system using Geometry Nodes",
    "category": "ZDC Tools",
}

import bpy
import importlib
import sys
from pathlib import Path

# Add addon directory to path for src imports
addon_dir = Path(__file__).parent
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))

# Import submodules
from . import properties
from . import operators
from . import panels
from .src import cut_list_export
from .src import cabinet_presets
from .src import batch_generation
from .src import batch_lazy_susan

# Support reloading
if "bpy" in locals():
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(cut_list_export)
    importlib.reload(cabinet_presets)
    importlib.reload(batch_generation)
    importlib.reload(batch_lazy_susan)


def register():
    """Register addon classes."""
    print("Cabinet Generator: Registering...")
    properties.register()
    operators.register()
    panels.register()
    cut_list_export.register()
    cabinet_presets.register()
    batch_generation.register()
    batch_lazy_susan.register()
    print("Cabinet Generator: Registered successfully")


def unregister():
    """Unregister addon classes."""
    print("Cabinet Generator: Unregistering...")
    batch_lazy_susan.unregister()
    batch_generation.unregister()
    cabinet_presets.unregister()
    cut_list_export.unregister()
    panels.unregister()
    operators.unregister()
    properties.unregister()
    print("Cabinet Generator: Unregistered")


if __name__ == "__main__":
    register()
