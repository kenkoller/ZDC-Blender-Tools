#!/usr/bin/env python3
"""
Validation script for Cabinet Generator addon.

This script can be run in two ways:
1. Standalone (without Blender): Validates imports and syntax
2. In Blender's Python console: Validates full functionality

Usage in Blender:
    import sys
    sys.path.insert(0, '/path/to/cabinet-generator')
    import validate_addon
    validate_addon.run_all_tests()
"""

import sys
import os
from pathlib import Path

# Add addon directory to path
addon_dir = Path(__file__).parent
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))


def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "=" * 60)
    print("Testing Module Imports")
    print("=" * 60)

    errors = []

    # Core addon modules
    core_modules = [
        ('properties', 'from . import properties'),
        ('operators', 'from . import operators'),
        ('panels', 'from . import panels'),
    ]

    # New utility modules
    utility_modules = [
        ('cut_list_export', 'from .src import cut_list_export'),
        ('cabinet_presets', 'from .src import cabinet_presets'),
        ('batch_generation', 'from .src import batch_generation'),
    ]

    # Node utility modules
    node_modules = [
        ('nodes.utils', 'from src.nodes import utils'),
        ('nodes.master', 'from src.nodes import master'),
        ('nodes.material_presets', 'from src.nodes import material_presets'),
    ]

    # Atomic components
    atomic_modules = [
        ('atomic.shelf', 'from src.nodes.atomic import shelf'),
        ('atomic.door_panel', 'from src.nodes.atomic import door_panel'),
        ('atomic.drawer', 'from src.nodes.atomic import drawer'),
        ('atomic.hardware', 'from src.nodes.atomic import hardware'),
        ('atomic.toe_kick', 'from src.nodes.atomic import toe_kick'),
        ('atomic.lazy_susan', 'from src.nodes.atomic import lazy_susan'),
        ('atomic.hinges', 'from src.nodes.atomic import hinges'),
        ('atomic.drawer_slides', 'from src.nodes.atomic import drawer_slides'),
        ('atomic.trash_pullout', 'from src.nodes.atomic import trash_pullout'),
        ('atomic.spice_rack', 'from src.nodes.atomic import spice_rack'),
        ('atomic.shelf_pins', 'from src.nodes.atomic import shelf_pins'),
        ('atomic.led_strip', 'from src.nodes.atomic import led_strip'),
        ('atomic.crown_molding', 'from src.nodes.atomic import crown_molding'),
        ('atomic.light_rail', 'from src.nodes.atomic import light_rail'),
    ]

    # System components
    system_modules = [
        ('systems.cabinet_box', 'from src.nodes.systems import cabinet_box'),
        ('systems.shelf_array', 'from src.nodes.systems import shelf_array'),
        ('systems.door_assembly', 'from src.nodes.systems import door_assembly'),
        ('systems.drawer_stack', 'from src.nodes.systems import drawer_stack'),
        ('systems.blind_corner', 'from src.nodes.systems import blind_corner'),
        ('systems.sink_base', 'from src.nodes.systems import sink_base'),
        ('systems.appliance_cabinet', 'from src.nodes.systems import appliance_cabinet'),
        ('systems.open_shelving', 'from src.nodes.systems import open_shelving'),
        ('systems.diagonal_corner', 'from src.nodes.systems import diagonal_corner'),
        ('systems.pullout_pantry', 'from src.nodes.systems import pullout_pantry'),
    ]

    all_modules = node_modules + atomic_modules + system_modules

    for name, _ in all_modules:
        try:
            # Try importing the module
            parts = name.split('.')
            if len(parts) == 1:
                __import__(f'src.nodes.{name}')
            elif parts[0] == 'atomic':
                __import__(f'src.nodes.atomic.{parts[1]}')
            elif parts[0] == 'systems':
                __import__(f'src.nodes.systems.{parts[1]}')
            elif parts[0] == 'nodes':
                __import__(f'src.nodes.{parts[1]}')
            print(f"  [OK] {name}")
        except ImportError as e:
            print(f"  [FAIL] {name}: {e}")
            errors.append((name, str(e)))
        except Exception as e:
            print(f"  [ERROR] {name}: {type(e).__name__}: {e}")
            errors.append((name, str(e)))

    return errors


def test_file_structure():
    """Verify all expected files exist."""
    print("\n" + "=" * 60)
    print("Testing File Structure")
    print("=" * 60)

    expected_files = [
        # Root files
        '__init__.py',
        'properties.py',
        'operators.py',
        'panels.py',

        # Utility modules
        'src/cut_list_export.py',
        'src/cabinet_presets.py',
        'src/batch_generation.py',

        # Node modules
        'src/nodes/__init__.py',
        'src/nodes/utils.py',
        'src/nodes/master.py',
        'src/nodes/material_presets.py',

        # Atomic components
        'src/nodes/atomic/__init__.py',
        'src/nodes/atomic/shelf.py',
        'src/nodes/atomic/door_panel.py',
        'src/nodes/atomic/drawer.py',
        'src/nodes/atomic/hardware.py',
        'src/nodes/atomic/toe_kick.py',
        'src/nodes/atomic/lazy_susan.py',
        'src/nodes/atomic/hinges.py',
        'src/nodes/atomic/drawer_slides.py',
        'src/nodes/atomic/trash_pullout.py',
        'src/nodes/atomic/spice_rack.py',
        'src/nodes/atomic/shelf_pins.py',
        'src/nodes/atomic/led_strip.py',
        'src/nodes/atomic/crown_molding.py',
        'src/nodes/atomic/light_rail.py',

        # System components
        'src/nodes/systems/__init__.py',
        'src/nodes/systems/cabinet_box.py',
        'src/nodes/systems/shelf_array.py',
        'src/nodes/systems/door_assembly.py',
        'src/nodes/systems/drawer_stack.py',
        'src/nodes/systems/blind_corner.py',
        'src/nodes/systems/sink_base.py',
        'src/nodes/systems/appliance_cabinet.py',
        'src/nodes/systems/open_shelving.py',
        'src/nodes/systems/diagonal_corner.py',
        'src/nodes/systems/pullout_pantry.py',
    ]

    missing = []
    for filepath in expected_files:
        full_path = addon_dir / filepath
        if full_path.exists():
            print(f"  [OK] {filepath}")
        else:
            print(f"  [MISSING] {filepath}")
            missing.append(filepath)

    return missing


def test_syntax():
    """Check Python syntax of all files."""
    print("\n" + "=" * 60)
    print("Testing Python Syntax")
    print("=" * 60)

    import ast

    errors = []

    for py_file in addon_dir.rglob('*.py'):
        # Skip __pycache__
        if '__pycache__' in str(py_file):
            continue

        rel_path = py_file.relative_to(addon_dir)
        try:
            with open(py_file, 'r') as f:
                source = f.read()
            ast.parse(source)
            print(f"  [OK] {rel_path}")
        except SyntaxError as e:
            print(f"  [SYNTAX ERROR] {rel_path}: Line {e.lineno}: {e.msg}")
            errors.append((str(rel_path), f"Line {e.lineno}: {e.msg}"))

    return errors


def test_blender_available():
    """Check if running inside Blender."""
    try:
        import bpy
        print("\n  Running inside Blender: YES")
        print(f"  Blender version: {bpy.app.version_string}")
        return True
    except ImportError:
        print("\n  Running inside Blender: NO")
        print("  (Some tests will be skipped)")
        return False


def test_node_generators():
    """Test node group generation (requires Blender)."""
    print("\n" + "=" * 60)
    print("Testing Node Group Generators")
    print("=" * 60)

    try:
        import bpy
    except ImportError:
        print("  [SKIP] Blender not available")
        return []

    errors = []

    # Test atomic generators
    atomic_tests = [
        ('Shelf', 'src.nodes.atomic.shelf', 'create_shelf_nodegroup'),
        ('DoorPanel', 'src.nodes.atomic.door_panel', 'create_door_panel_nodegroup'),
        ('Drawer', 'src.nodes.atomic.drawer', 'create_drawer_nodegroup'),
        ('Handle', 'src.nodes.atomic.hardware', 'create_handle_nodegroup'),
        ('ToeKick', 'src.nodes.atomic.toe_kick', 'create_toe_kick_nodegroup'),
        ('LazySusan', 'src.nodes.atomic.lazy_susan', 'create_lazy_susan_nodegroup'),
        ('Hinge', 'src.nodes.atomic.hinges', 'create_hinge_nodegroup'),
        ('DrawerSlides', 'src.nodes.atomic.drawer_slides', 'create_drawer_slides_nodegroup'),
        ('TrashPullout', 'src.nodes.atomic.trash_pullout', 'create_trash_pullout_nodegroup'),
        ('SpiceRack', 'src.nodes.atomic.spice_rack', 'create_spice_rack_nodegroup'),
        ('ShelfPins', 'src.nodes.atomic.shelf_pins', 'create_shelf_pins_nodegroup'),
        ('LEDStrip', 'src.nodes.atomic.led_strip', 'create_led_strip_nodegroup'),
        ('CrownMolding', 'src.nodes.atomic.crown_molding', 'create_crown_molding_nodegroup'),
        ('LightRail', 'src.nodes.atomic.light_rail', 'create_light_rail_nodegroup'),
    ]

    # Test system generators
    system_tests = [
        ('CabinetBox', 'src.nodes.systems.cabinet_box', 'create_cabinet_box_nodegroup'),
        ('ShelfArray', 'src.nodes.systems.shelf_array', 'create_shelf_array_nodegroup'),
        ('DoorAssembly', 'src.nodes.systems.door_assembly', 'create_door_assembly_nodegroup'),
        ('DrawerStack', 'src.nodes.systems.drawer_stack', 'create_drawer_stack_nodegroup'),
        ('BlindCorner', 'src.nodes.systems.blind_corner', 'create_blind_corner_nodegroup'),
        ('SinkBase', 'src.nodes.systems.sink_base', 'create_sink_base_nodegroup'),
        ('ApplianceCabinet', 'src.nodes.systems.appliance_cabinet', 'create_appliance_cabinet_nodegroup'),
        ('OpenShelving', 'src.nodes.systems.open_shelving', 'create_open_shelving_nodegroup'),
        ('DiagonalCorner', 'src.nodes.systems.diagonal_corner', 'create_diagonal_corner_nodegroup'),
        ('PulloutPantry', 'src.nodes.systems.pullout_pantry', 'create_pullout_pantry_nodegroup'),
    ]

    # Master generator
    master_test = [
        ('CabinetMaster', 'src.nodes.master', 'create_cabinet_master_nodegroup'),
    ]

    all_tests = atomic_tests + system_tests + master_test

    for name, module_path, func_name in all_tests:
        try:
            module = __import__(module_path, fromlist=[func_name])
            func = getattr(module, func_name)
            ng = func()

            if ng and ng.name:
                print(f"  [OK] {name} - created '{ng.name}'")
            else:
                print(f"  [WARN] {name} - returned None or invalid")
                errors.append((name, "Generator returned None"))
        except Exception as e:
            print(f"  [FAIL] {name}: {type(e).__name__}: {e}")
            errors.append((name, str(e)))

    return errors


def test_operator_registration():
    """Test that operators can be registered (requires Blender)."""
    print("\n" + "=" * 60)
    print("Testing Operator Registration")
    print("=" * 60)

    try:
        import bpy
    except ImportError:
        print("  [SKIP] Blender not available")
        return []

    # Expected operators
    expected_operators = [
        'cabinet.create_cabinet',
        'cabinet.generate_nodegroups',
        'cabinet.create_shelf',
        'cabinet.create_door_panel',
        'cabinet.create_drawer',
        'cabinet.create_handle',
        'cabinet.create_cabinet_box',
        'cabinet.create_toe_kick',
        'cabinet.create_lazy_susan',
        'cabinet.create_blind_corner',
        'cabinet.create_hinges',
        'cabinet.create_drawer_slides',
        'cabinet.create_shelf_pins',
        'cabinet.create_trash_pullout',
        'cabinet.create_spice_rack',
        'cabinet.create_sink_base',
        'cabinet.create_appliance_cabinet',
        'cabinet.create_open_shelving',
        'cabinet.create_diagonal_corner',
        'cabinet.create_pullout_pantry',
        'cabinet.apply_material_presets',
        'cabinet.reload_generators',
        'cabinet.export_cut_list',
        'cabinet.show_cut_list',
        'cabinet.save_preset',
        'cabinet.load_preset',
        'cabinet.apply_builtin_preset',
        'cabinet.batch_generate',
        'cabinet.batch_from_json',
        'cabinet.generate_kitchen_run',
    ]

    errors = []

    for op_id in expected_operators:
        try:
            if hasattr(bpy.ops, op_id.split('.')[0]):
                op_group = getattr(bpy.ops, op_id.split('.')[0])
                if hasattr(op_group, op_id.split('.')[1]):
                    print(f"  [OK] {op_id}")
                else:
                    print(f"  [NOT FOUND] {op_id}")
                    errors.append((op_id, "Operator not registered"))
            else:
                print(f"  [NOT FOUND] {op_id}")
                errors.append((op_id, "Operator group not found"))
        except Exception as e:
            print(f"  [ERROR] {op_id}: {e}")
            errors.append((op_id, str(e)))

    return errors


def run_all_tests():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("CABINET GENERATOR ADDON VALIDATION")
    print("=" * 60)

    all_errors = []

    # Check if in Blender
    in_blender = test_blender_available()

    # File structure
    missing = test_file_structure()
    if missing:
        all_errors.extend([('File Missing', f) for f in missing])

    # Syntax check
    syntax_errors = test_syntax()
    all_errors.extend(syntax_errors)

    # Import tests (requires proper setup)
    if in_blender:
        import_errors = test_imports()
        all_errors.extend(import_errors)

        # Node generators
        node_errors = test_node_generators()
        all_errors.extend(node_errors)

        # Operator registration (only if addon is enabled)
        op_errors = test_operator_registration()
        all_errors.extend(op_errors)

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if all_errors:
        print(f"\n  ERRORS FOUND: {len(all_errors)}")
        for category, msg in all_errors:
            print(f"    - {category}: {msg}")
        return False
    else:
        print("\n  ALL TESTS PASSED!")
        return True


def quick_validate():
    """Quick validation without Blender - checks files and syntax only."""
    print("\n" + "=" * 60)
    print("QUICK VALIDATION (No Blender Required)")
    print("=" * 60)

    all_errors = []

    # File structure
    missing = test_file_structure()
    if missing:
        all_errors.extend([('File Missing', f) for f in missing])

    # Syntax check
    syntax_errors = test_syntax()
    all_errors.extend(syntax_errors)

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if all_errors:
        print(f"\n  ERRORS FOUND: {len(all_errors)}")
        for category, msg in all_errors:
            print(f"    - {category}: {msg}")
        return False
    else:
        print("\n  ALL TESTS PASSED!")
        print("\n  Note: Run in Blender for full validation")
        return True


if __name__ == '__main__':
    # When run standalone, do quick validation
    quick_validate()
