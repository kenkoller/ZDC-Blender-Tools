"""ZDC naming conventions and ID prefix mapping.

All ZDC addons follow a consistent naming scheme for Blender classes:

  Operators:      ZDC_OT_{AddonName}_{action}
  Panels:         ZDC_PT_{AddonName}_{section}
  PropertyGroups: ZDC_PG_{AddonName}_{name}
  Menus:          ZDC_MT_{AddonName}_{name}

The bl_idname for operators uses dots: zdc.addonname_action

Node groups use the ZDC_ prefix: ZDC_{GroupName}_v{N}
"""

# Addon short names used in class prefixes
ADDON_PREFIXES = {
    "auto-batch-renderer": "BatchRender",
    "cabinet-generator": "CabinetGen",
    "kitchen-generator": "KitchenGen",
    "universal-pbr-shader": "UniversalPBR",
}

# Node group prefix
NODE_GROUP_PREFIX = "ZDC_"


def operator_idname(addon_key: str, action: str) -> str:
    """Build a ZDC operator bl_idname from addon key and action.

    Args:
        addon_key: Addon directory name (e.g. "cabinet-generator")
        action: Action verb (e.g. "generate")

    Returns:
        Dot-separated bl_idname (e.g. "zdc.cabinetgen_generate")
    """
    prefix = ADDON_PREFIXES.get(addon_key, addon_key.replace("-", ""))
    return f"zdc.{prefix.lower()}_{action}"


def class_name(kind: str, addon_key: str, name: str) -> str:
    """Build a ZDC class name.

    Args:
        kind: One of "OT", "PT", "PG", "MT"
        addon_key: Addon directory name
        name: Descriptive suffix

    Returns:
        Class name (e.g. "ZDC_OT_CabinetGen_generate")
    """
    prefix = ADDON_PREFIXES.get(addon_key, addon_key.replace("-", ""))
    return f"ZDC_{kind}_{prefix}_{name}"
