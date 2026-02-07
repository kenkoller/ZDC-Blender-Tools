#!/usr/bin/env python3
"""
Quick Test Script for Cabinet Generator
Clears all cached modules and runs fresh tests.

Run in Blender Python Console:
    exec(open('/Users/KK/My Drive/Assets-Cloud/Blender/Scripts/Development/blender-addons/cabinet-generator/quick_test.py').read())
"""

import sys
import importlib

# Project path
PROJECT_PATH = '/Users/KK/My Drive/Assets-Cloud/Blender/Scripts/Development/blender-addons/cabinet-generator'

# ========== STEP 1: Clear all cached modules ==========
print("\n" + "=" * 60)
print("CLEARING CACHED MODULES")
print("=" * 60)

modules_to_clear = [mod for mod in list(sys.modules.keys())
                    if 'cabinet' in mod.lower() or
                    'nodes' in mod.lower() or
                    'src.' in mod]

for mod_name in modules_to_clear:
    del sys.modules[mod_name]
    print(f"  Cleared: {mod_name}")

if modules_to_clear:
    print(f"\n  Cleared {len(modules_to_clear)} cached modules")
else:
    print("  No cached modules found")

# ========== STEP 2: Add project to path ==========
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# ========== STEP 3: Test Atomic Components ==========
print("\n" + "=" * 60)
print("TESTING ATOMIC COMPONENTS (14 total)")
print("=" * 60)

atomics = [
    ("Shelf", "src.nodes.atomic.shelf", "create_shelf_nodegroup"),
    ("DoorPanel", "src.nodes.atomic.door_panel", "create_door_panel_nodegroup"),
    ("Drawer", "src.nodes.atomic.drawer", "create_drawer_nodegroup"),
    ("Handle", "src.nodes.atomic.hardware", "create_handle_nodegroup"),
    ("ToeKick", "src.nodes.atomic.toe_kick", "create_toe_kick_nodegroup"),
    ("LazySusan", "src.nodes.atomic.lazy_susan", "create_lazy_susan_nodegroup"),
    ("Hinge", "src.nodes.atomic.hinges", "create_hinge_nodegroup"),
    ("DrawerSlides", "src.nodes.atomic.drawer_slides", "create_drawer_slides_nodegroup"),
    ("TrashPullout", "src.nodes.atomic.trash_pullout", "create_trash_pullout_nodegroup"),
    ("SpiceRack", "src.nodes.atomic.spice_rack", "create_spice_rack_nodegroup"),
    ("ShelfPins", "src.nodes.atomic.shelf_pins", "create_shelf_pins_nodegroup"),
    ("LEDStrip", "src.nodes.atomic.led_strip", "create_led_strip_nodegroup"),
    ("CrownMolding", "src.nodes.atomic.crown_molding", "create_crown_molding_nodegroup"),
    ("LightRail", "src.nodes.atomic.light_rail", "create_light_rail_nodegroup"),
]

atomic_passed, atomic_failed = 0, 0
atomic_errors = []

for name, mod_path, func_name in atomics:
    try:
        mod = importlib.import_module(mod_path)
        importlib.reload(mod)
        ng = getattr(mod, func_name)()
        print(f"  [PASS] {name}: {len(ng.nodes)} nodes")
        atomic_passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        atomic_failed += 1
        atomic_errors.append((name, str(e)))

print(f"\n  Atomic Results: {atomic_passed}/14 passed, {atomic_failed} failed")

# ========== STEP 4: Test System Components ==========
print("\n" + "=" * 60)
print("TESTING SYSTEM COMPONENTS (10 total)")
print("=" * 60)

systems = [
    ("CabinetBox", "src.nodes.systems.cabinet_box", "create_cabinet_box_nodegroup"),
    ("ShelfArray", "src.nodes.systems.shelf_array", "create_shelf_array_nodegroup"),
    ("DoorAssembly", "src.nodes.systems.door_assembly", "create_door_assembly_nodegroup"),
    ("DrawerStack", "src.nodes.systems.drawer_stack", "create_drawer_stack_nodegroup"),
    ("BlindCorner", "src.nodes.systems.blind_corner", "create_blind_corner_nodegroup"),
    ("SinkBase", "src.nodes.systems.sink_base", "create_sink_base_nodegroup"),
    ("ApplianceCabinet", "src.nodes.systems.appliance_cabinet", "create_appliance_cabinet_nodegroup"),
    ("OpenShelving", "src.nodes.systems.open_shelving", "create_open_shelving_nodegroup"),
    ("DiagonalCorner", "src.nodes.systems.diagonal_corner", "create_diagonal_corner_nodegroup"),
    ("PulloutPantry", "src.nodes.systems.pullout_pantry", "create_pullout_pantry_nodegroup"),
]

system_passed, system_failed = 0, 0
system_errors = []

for name, mod_path, func_name in systems:
    try:
        mod = importlib.import_module(mod_path)
        importlib.reload(mod)
        ng = getattr(mod, func_name)()
        print(f"  [PASS] {name}: {len(ng.nodes)} nodes")
        system_passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        system_failed += 1
        system_errors.append((name, str(e)))

print(f"\n  System Results: {system_passed}/10 passed, {system_failed} failed")

# ========== STEP 5: Test Master Orchestrator ==========
print("\n" + "=" * 60)
print("TESTING MASTER ORCHESTRATOR")
print("=" * 60)

master_passed = False
try:
    from src.nodes import master
    importlib.reload(master)
    ng = master.create_cabinet_master_nodegroup()
    print(f"  [PASS] CabinetMaster: {len(ng.nodes)} nodes")
    master_passed = True
except Exception as e:
    import traceback
    print(f"  [FAIL] CabinetMaster: {e}")
    traceback.print_exc()

# ========== STEP 6: Summary ==========
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

total_tests = 14 + 10 + 1  # atomics + systems + master
total_passed = atomic_passed + system_passed + (1 if master_passed else 0)
total_failed = atomic_failed + system_failed + (0 if master_passed else 1)

print(f"\n  Total: {total_passed}/{total_tests} passed, {total_failed} failed")

if total_failed == 0:
    print("\n  ALL TESTS PASSED!")
else:
    print("\n  ERRORS:")
    for name, error in atomic_errors + system_errors:
        print(f"    - {name}: {error}")
    if not master_passed:
        print(f"    - CabinetMaster: See traceback above")

print("\n" + "=" * 60)
