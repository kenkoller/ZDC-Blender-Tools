#!/usr/bin/env python3
"""
Visual Testing Script for Cabinet Generator

This script creates a grid of test cabinets in Blender so you can visually
inspect that geometry is correct. Run this in Blender's Python console.

Usage in Blender:
    import sys
    sys.path.insert(0, '/path/to/cabinet-generator')
    import visual_test
    visual_test.run_visual_tests()

    # Or run specific tests:
    visual_test.test_cabinet_types()
    visual_test.test_dimensions()
    visual_test.test_door_styles()
"""

import bpy
import math


def clear_test_objects():
    """Remove all test objects from the scene."""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith("Test_") or obj.name.startswith("Cabinet_Test"):
            obj.select_set(True)
    bpy.ops.object.delete()
    print("Cleared test objects")


def set_modifier_input(mod, name, value):
    """Helper to set geometry nodes modifier input."""
    for item in mod.node_group.interface.items_tree:
        if item.name == name and hasattr(item, 'identifier'):
            identifier = item.identifier
            if identifier in mod:
                mod[identifier] = value
                return True
    return False


def create_test_cabinet(name, location, settings):
    """Create a cabinet with specific settings for testing.

    Args:
        name: Object name
        location: (x, y, z) world position
        settings: Dict of modifier input values to set

    Returns:
        The created object
    """
    from src.nodes.master import create_cabinet_master_nodegroup

    # Ensure node group exists
    if "CabinetMaster" not in bpy.data.node_groups:
        create_cabinet_master_nodegroup()

    # Create object
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Add modifier
    mod = obj.modifiers.new("GeometryNodes", 'NODES')
    mod.node_group = bpy.data.node_groups["CabinetMaster"]

    # Apply settings
    for key, value in settings.items():
        set_modifier_input(mod, key, value)

    # Position
    obj.location = location

    return obj


def test_cabinet_types():
    """Test all 10 cabinet types side by side."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Cabinet Types")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    cabinet_types = [
        (0, "Base", {"Width": 0.6, "Height": 0.72, "Depth": 0.55}),
        (1, "Wall", {"Width": 0.6, "Height": 0.72, "Depth": 0.35}),
        (2, "Tall", {"Width": 0.6, "Height": 2.1, "Depth": 0.55}),
        (3, "Drawer Base", {"Width": 0.6, "Height": 0.72, "Depth": 0.55, "Front Type": 1}),
        (4, "Blind Corner", {"Width": 0.9, "Height": 0.72, "Depth": 0.55, "Blind Width": 0.15}),
        (5, "Sink Base", {"Width": 0.9, "Height": 0.72, "Depth": 0.55}),
        (6, "Appliance", {"Width": 0.6, "Height": 1.8, "Depth": 0.55, "Appliance Opening Height": 0.5}),
        (7, "Open Shelving", {"Width": 0.8, "Height": 1.2, "Depth": 0.35}),
        (8, "Diagonal Corner", {"Width": 0.9, "Height": 0.72, "Depth": 0.9}),
        (9, "Pullout Pantry", {"Width": 0.3, "Height": 2.1, "Depth": 0.55}),
    ]

    spacing = 1.2

    for i, (type_id, type_name, extra_settings) in enumerate(cabinet_types):
        settings = {"Cabinet Type": type_id, "Has Toe Kick": True}
        settings.update(extra_settings)

        x = (i % 5) * spacing
        y = (i // 5) * -1.5

        obj = create_test_cabinet(f"Test_{type_name}", (x, y, 0), settings)
        print(f"  Created: {type_name} at ({x:.1f}, {y:.1f}, 0)")

    print(f"\nCreated {len(cabinet_types)} cabinet types")
    print("Inspect visually: All should stand upright, origin at floor level")


def test_dimensions():
    """Test dimension accuracy with ruler checks."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Dimension Accuracy")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    # Test specific dimensions
    test_cases = [
        ("300mm Wide", {"Width": 0.3, "Height": 0.72, "Depth": 0.55}),
        ("600mm Wide", {"Width": 0.6, "Height": 0.72, "Depth": 0.55}),
        ("900mm Wide", {"Width": 0.9, "Height": 0.72, "Depth": 0.55}),
        ("1200mm Wide", {"Width": 1.2, "Height": 0.72, "Depth": 0.55}),
        ("Wall Height 600mm", {"Width": 0.6, "Height": 0.6, "Depth": 0.35, "Cabinet Type": 1}),
        ("Tall 2100mm", {"Width": 0.6, "Height": 2.1, "Depth": 0.55, "Cabinet Type": 2}),
    ]

    for i, (name, settings) in enumerate(test_cases):
        settings["Cabinet Type"] = settings.get("Cabinet Type", 0)
        settings["Has Toe Kick"] = True

        x = (i % 3) * 1.5
        y = (i // 3) * -1.5

        obj = create_test_cabinet(f"Test_Dim_{name}", (x, y, 0), settings)

        # Calculate expected bounding box
        expected_width = settings["Width"]
        expected_height = settings["Height"]
        expected_depth = settings["Depth"]

        print(f"  {name}: Expected {expected_width*1000:.0f}x{expected_depth*1000:.0f}x{expected_height*1000:.0f}mm")

    print("\nUse Blender's measurement tools to verify dimensions")
    print("Press N > Item > Dimensions to see object bounds")


def test_door_styles():
    """Test all 5 door panel styles."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Door Panel Styles")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    styles = [
        (0, "Flat"),
        (1, "Shaker"),
        (2, "Raised"),
        (3, "Recessed"),
        (4, "Double Shaker"),
    ]

    for i, (style_id, style_name) in enumerate(styles):
        settings = {
            "Cabinet Type": 0,
            "Width": 0.6,
            "Height": 0.72,
            "Depth": 0.55,
            "Door Style": style_id,
            "Front Type": 0,  # Doors
            "Has Toe Kick": True,
        }

        obj = create_test_cabinet(f"Test_Door_{style_name}", (i * 0.8, 0, 0), settings)
        print(f"  Created: {style_name} door style")

    print("\nInspect door panel profiles - each should have distinct geometry")


def test_handle_styles():
    """Test all 5 handle styles."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Handle Styles")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    styles = [
        (0, "Bar"),
        (1, "Wire"),
        (2, "Knob"),
        (3, "Cup Pull"),
        (4, "Edge Pull"),
    ]

    for i, (style_id, style_name) in enumerate(styles):
        settings = {
            "Cabinet Type": 0,
            "Width": 0.6,
            "Height": 0.72,
            "Depth": 0.55,
            "Handle Style": style_id,
            "Has Toe Kick": True,
        }

        obj = create_test_cabinet(f"Test_Handle_{style_name}", (i * 0.8, 0, 0), settings)
        print(f"  Created: {style_name} handle")

    print("\nInspect handle geometry on each door")


def test_animations():
    """Test door and drawer animations."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Animations")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    # Door opening angles
    door_angles = [0, 30, 60, 90, 120]
    for i, angle in enumerate(door_angles):
        settings = {
            "Cabinet Type": 0,
            "Width": 0.6,
            "Height": 0.72,
            "Depth": 0.55,
            "Front Type": 0,
            "Door Open Angle": math.radians(angle),
            "Has Toe Kick": True,
        }
        obj = create_test_cabinet(f"Test_Door_{angle}deg", (i * 0.8, 0, 0), settings)
        print(f"  Door open: {angle} degrees")

    # Drawer extension
    drawer_opens = [0, 0.25, 0.5, 0.75, 1.0]
    for i, amount in enumerate(drawer_opens):
        settings = {
            "Cabinet Type": 3,  # Drawer Base
            "Width": 0.6,
            "Height": 0.72,
            "Depth": 0.55,
            "Front Type": 1,
            "Drawer Open": amount,
            "Has Toe Kick": True,
        }
        obj = create_test_cabinet(f"Test_Drawer_{int(amount*100)}pct", (i * 0.8, -1.2, 0), settings)
        print(f"  Drawer open: {int(amount*100)}%")

    print("\nCheck door rotation pivots from hinge side")
    print("Check drawer slides out smoothly")


def test_construction_options():
    """Test face frame and other construction options."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Construction Options")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    # Frameless vs Face Frame
    settings_frameless = {
        "Cabinet Type": 0,
        "Width": 0.6,
        "Height": 0.72,
        "Depth": 0.55,
        "Has Face Frame": False,
        "Has Toe Kick": True,
    }
    obj1 = create_test_cabinet("Test_Frameless", (0, 0, 0), settings_frameless)
    print("  Created: Frameless cabinet")

    settings_faceframe = {
        "Cabinet Type": 0,
        "Width": 0.6,
        "Height": 0.72,
        "Depth": 0.55,
        "Has Face Frame": True,
        "Face Frame Width": 0.038,
        "Has Toe Kick": True,
    }
    obj2 = create_test_cabinet("Test_FaceFrame", (0.8, 0, 0), settings_faceframe)
    print("  Created: Face frame cabinet")

    # With/without back
    settings_noback = {
        "Cabinet Type": 0,
        "Width": 0.6,
        "Height": 0.72,
        "Depth": 0.55,
        "Has Back": False,
        "Has Toe Kick": True,
    }
    obj3 = create_test_cabinet("Test_NoBack", (1.6, 0, 0), settings_noback)
    print("  Created: Cabinet without back")

    print("\nCompare frameless vs face frame construction")
    print("Check face frame has stiles and rails at front")


def test_corner_cabinets():
    """Test corner cabinet configurations."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Corner Cabinets")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    # Blind corner left
    settings_bc_left = {
        "Cabinet Type": 4,
        "Width": 0.9,
        "Height": 0.72,
        "Depth": 0.55,
        "Corner Type": 0,  # Left
        "Blind Width": 0.15,
        "Has Toe Kick": True,
    }
    obj1 = create_test_cabinet("Test_BlindCorner_Left", (0, 0, 0), settings_bc_left)
    print("  Created: Blind corner (left)")

    # Blind corner right
    settings_bc_right = {
        "Cabinet Type": 4,
        "Width": 0.9,
        "Height": 0.72,
        "Depth": 0.55,
        "Corner Type": 1,  # Right
        "Blind Width": 0.15,
        "Has Toe Kick": True,
    }
    obj2 = create_test_cabinet("Test_BlindCorner_Right", (1.2, 0, 0), settings_bc_right)
    print("  Created: Blind corner (right)")

    # Diagonal corner
    settings_diag = {
        "Cabinet Type": 8,
        "Width": 0.9,
        "Height": 0.72,
        "Depth": 0.9,
        "Has Lazy Susan": True,
        "Lazy Susan Count": 2,
        "Has Toe Kick": True,
    }
    obj3 = create_test_cabinet("Test_DiagonalCorner", (2.4, 0, 0), settings_diag)
    print("  Created: Diagonal corner with lazy susan")

    print("\nCheck blind corners mirror correctly")
    print("Check diagonal has 45-degree angled front")


def test_glass_doors():
    """Test glass door option."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Glass Doors")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    settings_solid = {
        "Cabinet Type": 1,  # Wall
        "Width": 0.6,
        "Height": 0.72,
        "Depth": 0.35,
        "Is Glass Door": False,
    }
    obj1 = create_test_cabinet("Test_SolidDoor", (0, 0, 0), settings_solid)
    print("  Created: Solid door")

    settings_glass = {
        "Cabinet Type": 1,
        "Width": 0.6,
        "Height": 0.72,
        "Depth": 0.35,
        "Is Glass Door": True,
        "Glass Frame Width": 0.05,
    }
    obj2 = create_test_cabinet("Test_GlassDoor", (0.8, 0, 0), settings_glass)
    print("  Created: Glass door with frame")

    print("\nGlass door should have frame around transparent center")


def test_bevel_options():
    """Test edge bevel settings."""
    print("\n" + "=" * 60)
    print("VISUAL TEST: Edge Bevels")
    print("=" * 60)

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    bevel_widths = [0.0, 0.001, 0.003, 0.005]

    for i, width in enumerate(bevel_widths):
        settings = {
            "Cabinet Type": 0,
            "Width": 0.6,
            "Height": 0.72,
            "Depth": 0.55,
            "Bevel Width": width,
            "Bevel Segments": 2,
            "Has Toe Kick": True,
        }
        obj = create_test_cabinet(f"Test_Bevel_{width*1000:.0f}mm", (i * 0.8, 0, 0), settings)
        print(f"  Created: Bevel width {width*1000:.1f}mm")

    print("\nCompare edge softness - larger bevel = more rounded")


def generate_test_report():
    """Generate a test report of what needs visual inspection."""
    report = """
============================================================
CABINET GENERATOR - VISUAL TEST CHECKLIST
============================================================

After running visual_test.run_visual_tests(), check the following:

CABINET TYPES:
[ ] Base cabinet - 720mm height, toe kick at bottom
[ ] Wall cabinet - No toe kick, shorter depth
[ ] Tall cabinet - Full height (2100mm)
[ ] Drawer Base - Drawer fronts instead of doors
[ ] Blind Corner - L-shape with blind panel
[ ] Sink Base - Open interior, false fronts
[ ] Appliance - Opening for appliance
[ ] Open Shelving - No doors, visible shelves
[ ] Diagonal Corner - 45-degree angled front
[ ] Pullout Pantry - Narrow, pull-out rack

DIMENSIONS:
[ ] 300mm, 600mm, 900mm, 1200mm widths are accurate
[ ] Heights match specified values
[ ] Depths match specified values
[ ] Use Blender's N-panel > Dimensions to verify

DOOR STYLES:
[ ] Flat - Completely flat panel
[ ] Shaker - Recessed center panel with frame
[ ] Raised - Center panel raised above frame
[ ] Recessed - Deep groove around center
[ ] Double Shaker - Two-tier frame detail

HANDLES:
[ ] Bar - Horizontal bar handle
[ ] Wire - Wire pull handle
[ ] Knob - Round knob
[ ] Cup Pull - Cup/bin pull
[ ] Edge Pull - Edge-mounted finger pull

ANIMATIONS:
[ ] Door opens 0-120 degrees smoothly
[ ] Door pivots from hinge side (not center)
[ ] Drawer extends 0-100% of depth
[ ] Drawer slides forward (positive Y direction)

CONSTRUCTION:
[ ] Frameless has full-overlay doors
[ ] Face frame has visible stiles/rails at front
[ ] Back panel toggles on/off
[ ] Toe kick has correct height/depth

CORNER CABINETS:
[ ] Blind corner left/right are mirrored
[ ] Diagonal corner has 45-degree face
[ ] Lazy susan rotates correctly

KNOWN ISSUES TO VERIFY:
- Door hinge side (should be outer edge, not always left)
- Double doors for wide cabinets (not implemented)
- Gap between drawer fronts (may be missing)
- Hardware components (hinges, slides) not visible in master

============================================================
    """
    print(report)
    return report


def run_visual_tests():
    """Run all visual tests."""
    print("\n" + "=" * 60)
    print("CABINET GENERATOR - VISUAL TEST SUITE")
    print("=" * 60)

    clear_test_objects()

    # Run each test category
    test_cabinet_types()

    # Generate report
    generate_test_report()

    print("\n" + "=" * 60)
    print("Visual tests complete!")
    print("Navigate through the scene to inspect each cabinet")
    print("=" * 60)


def run_quick_test():
    """Run a quick single-cabinet test."""
    print("Quick test - creating single base cabinet...")

    from src.nodes.master import generate_all_nodegroups
    generate_all_nodegroups()

    settings = {
        "Cabinet Type": 0,
        "Width": 0.6,
        "Height": 0.72,
        "Depth": 0.55,
        "Has Toe Kick": True,
        "Door Style": 1,  # Shaker
    }

    obj = create_test_cabinet("Test_QuickTest", (0, 0, 0), settings)

    # Select and frame
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print(f"Created: {obj.name}")
    print("Check: Should be 600x550x720mm base cabinet with shaker doors")


if __name__ == "__main__":
    run_visual_tests()
