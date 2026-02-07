#!/usr/bin/env python3
"""Validate bl_info metadata for all ZDC addons.

Checks that every addon in addons/ has a conforming bl_info dict:
  - name starts with "ZDC - "
  - author is "Ziti Design & Creative"
  - blender >= (5, 0, 0)
  - category is "ZDC Tools"

Usage:
    python scripts/validate_bl_info.py
"""

import ast
import sys
from pathlib import Path

# Addons that are third-party and should be skipped
SKIP_ADDONS = {"home-builder"}

REQUIRED = {
    "author": "Ziti Design & Creative",
    "category": "ZDC Tools",
}

MIN_BLENDER = (5, 0, 0)


def extract_bl_info(init_path: Path) -> dict | None:
    """Parse bl_info from an __init__.py without importing it."""
    try:
        tree = ast.parse(init_path.read_text())
    except SyntaxError as e:
        print(f"  PARSE ERROR: {e}")
        return None

    for node in ast.iter_child_nodes(tree):
        if (isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "bl_info"):
            return ast.literal_eval(node.value)
    return None


def validate_addon(addon_dir: Path) -> list[str]:
    """Validate a single addon, return list of issues."""
    issues = []
    init = addon_dir / "__init__.py"

    if not init.exists():
        issues.append("Missing __init__.py")
        return issues

    bl_info = extract_bl_info(init)
    if bl_info is None:
        issues.append("No bl_info found in __init__.py")
        return issues

    # Check name prefix
    name = bl_info.get("name", "")
    if not name.startswith("ZDC - "):
        issues.append(f'name "{name}" does not start with "ZDC - "')

    # Check required fields
    for key, expected in REQUIRED.items():
        actual = bl_info.get(key)
        if actual != expected:
            issues.append(f'{key}: expected "{expected}", got "{actual}"')

    # Check blender version
    blender = bl_info.get("blender")
    if blender is None:
        issues.append("Missing blender version")
    elif tuple(blender) < MIN_BLENDER:
        issues.append(f"blender {blender} < required {MIN_BLENDER}")

    return issues


def main():
    root = Path(__file__).resolve().parent.parent
    addons_dir = root / "addons"

    if not addons_dir.is_dir():
        print(f"Error: {addons_dir} not found")
        sys.exit(1)

    all_passed = True

    for addon_dir in sorted(addons_dir.iterdir()):
        if not addon_dir.is_dir():
            continue
        if addon_dir.name in SKIP_ADDONS:
            print(f"  SKIP  {addon_dir.name} (third-party)")
            continue

        issues = validate_addon(addon_dir)
        if issues:
            all_passed = False
            print(f"  FAIL  {addon_dir.name}")
            for issue in issues:
                print(f"        - {issue}")
        else:
            print(f"  OK    {addon_dir.name}")

    print()
    if all_passed:
        print("All ZDC addons passed bl_info validation.")
    else:
        print("Some addons have bl_info issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
