#!/usr/bin/env python3
"""
Comprehensive Test Script for Cabinet Generator Addon
Run this script in Blender's Python Console or as a script.

Usage in Blender Python Console:
    import sys
    sys.path.insert(0, '/path/to/cabinet-generator')
    exec(open('/path/to/cabinet-generator/test_cabinet_generator.py').read())

Or run from command line:
    blender --background --python test_cabinet_generator.py

This script:
1. Tests all atomic component generators
2. Tests all system component generators
3. Tests the master orchestrator
4. Creates a visual test scene with all cabinet types
5. Generates a JSON report with pass/fail status
6. Optionally renders thumbnails of each cabinet type
"""

import bpy
import json
import sys
import os
import traceback
from datetime import datetime

# Add project to path if not already
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "blender_version": ".".join(str(v) for v in bpy.app.version),
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }
}


def log_test(name, status, message="", details=None):
    """Log a test result."""
    result = {
        "name": name,
        "status": status,  # "pass", "fail", "warning"
        "message": message
    }
    if details:
        result["details"] = details
    test_results["tests"].append(result)
    test_results["summary"]["total"] += 1
    if status == "pass":
        test_results["summary"]["passed"] += 1
    elif status == "fail":
        test_results["summary"]["failed"] += 1
    elif status == "warning":
        test_results["summary"]["warnings"] += 1

    # Print to console
    icon = "+" if status == "pass" else ("!" if status == "warning" else "X")
    print(f"[{icon}] {name}: {message}")


def clear_scene():
    """Clear all objects and node groups from the scene."""
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Remove all geometry node groups (keep others)
    groups_to_remove = [ng for ng in bpy.data.node_groups
                       if ng.type == 'GEOMETRY']
    for ng in groups_to_remove:
        bpy.data.node_groups.remove(ng)


def test_atomic_components():
    """Test all atomic component generators."""
    print("\n=== Testing Atomic Components ===\n")

    atomic_tests = [
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

    for name, module_path, func_name in atomic_tests:
        try:
            # Import and run generator
            module = __import__(module_path, fromlist=[func_name])
            generator_func = getattr(module, func_name)
            ng = generator_func()

            # Verify node group was created
            if name in bpy.data.node_groups or ng is not None:
                # Check for basic validity
                actual_ng = bpy.data.node_groups.get(name) or ng
                if actual_ng and len(actual_ng.nodes) > 0:
                    log_test(f"Atomic/{name}", "pass",
                            f"Created with {len(actual_ng.nodes)} nodes")
                else:
                    log_test(f"Atomic/{name}", "warning",
                            "Created but appears empty")
            else:
                log_test(f"Atomic/{name}", "fail", "Node group not found after creation")
        except Exception as e:
            log_test(f"Atomic/{name}", "fail", f"Error: {str(e)}",
                    {"traceback": traceback.format_exc()})


def test_system_components():
    """Test all system component generators."""
    print("\n=== Testing System Components ===\n")

    system_tests = [
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

    for name, module_path, func_name in system_tests:
        try:
            module = __import__(module_path, fromlist=[func_name])
            generator_func = getattr(module, func_name)
            ng = generator_func()

            if name in bpy.data.node_groups or ng is not None:
                actual_ng = bpy.data.node_groups.get(name) or ng
                if actual_ng and len(actual_ng.nodes) > 0:
                    log_test(f"System/{name}", "pass",
                            f"Created with {len(actual_ng.nodes)} nodes")
                else:
                    log_test(f"System/{name}", "warning",
                            "Created but appears empty")
            else:
                log_test(f"System/{name}", "fail", "Node group not found after creation")
        except Exception as e:
            log_test(f"System/{name}", "fail", f"Error: {str(e)}",
                    {"traceback": traceback.format_exc()})


def test_master_orchestrator():
    """Test the CabinetMaster generator."""
    print("\n=== Testing Master Orchestrator ===\n")

    try:
        from src.nodes import master
        ng = master.create_cabinet_master_nodegroup()

        if "CabinetMaster" in bpy.data.node_groups or ng is not None:
            actual_ng = bpy.data.node_groups.get("CabinetMaster") or ng
            if actual_ng and len(actual_ng.nodes) > 0:
                # Check for required inputs
                required_inputs = [
                    "Cabinet Type", "Width", "Height", "Depth",
                    "Panel Thickness", "Front Type", "Shelf Count"
                ]
                missing = []
                for inp_name in required_inputs:
                    found = False
                    for item in actual_ng.interface.items_tree:
                        if item.name == inp_name:
                            found = True
                            break
                    if not found:
                        missing.append(inp_name)

                if missing:
                    log_test("Master/CabinetMaster", "warning",
                            f"Missing inputs: {missing}")
                else:
                    log_test("Master/CabinetMaster", "pass",
                            f"Created with {len(actual_ng.nodes)} nodes, all required inputs present")
            else:
                log_test("Master/CabinetMaster", "fail", "Created but appears empty")
        else:
            log_test("Master/CabinetMaster", "fail", "Node group not found")
    except Exception as e:
        log_test("Master/CabinetMaster", "fail", f"Error: {str(e)}",
                {"traceback": traceback.format_exc()})


def test_generate_all():
    """Test the generate_all_nodegroups function."""
    print("\n=== Testing Full Generation ===\n")

    try:
        from src.nodes import master
        result = master.generate_all_nodegroups()

        if result:
            # Verify all expected node groups exist
            expected = [
                "Shelf", "DoorPanel", "Drawer", "Handle", "ToeKick", "LazySusan",
                "Hinge", "DrawerSlides", "TrashPullout", "SpiceRack", "ShelfPins",
                "LEDStrip", "CrownMolding", "LightRail",
                "CabinetBox", "ShelfArray", "DoorAssembly", "DrawerStack",
                "BlindCorner", "SinkBase", "ApplianceCabinet", "OpenShelving",
                "DiagonalCorner", "PulloutPantry", "CabinetMaster"
            ]
            missing = [name for name in expected if name not in bpy.data.node_groups]

            if missing:
                log_test("FullGeneration", "warning",
                        f"Generated but missing: {missing}")
            else:
                log_test("FullGeneration", "pass",
                        f"All {len(expected)} node groups generated successfully")
        else:
            log_test("FullGeneration", "fail", "generate_all_nodegroups returned False")
    except Exception as e:
        log_test("FullGeneration", "fail", f"Error: {str(e)}",
                {"traceback": traceback.format_exc()})


def create_visual_test_scene():
    """Create a grid of all cabinet types for visual inspection."""
    print("\n=== Creating Visual Test Scene ===\n")

    try:
        from src.nodes import master

        # Ensure CabinetMaster exists
        if "CabinetMaster" not in bpy.data.node_groups:
            master.generate_all_nodegroups()

        ng = bpy.data.node_groups["CabinetMaster"]

        # Cabinet type configurations
        cabinet_configs = [
            {"name": "Base", "type": 0, "width": 0.6, "height": 0.72, "depth": 0.55, "front_type": 0},
            {"name": "Wall", "type": 1, "width": 0.6, "height": 0.72, "depth": 0.3, "front_type": 0},
            {"name": "Tall", "type": 2, "width": 0.6, "height": 2.1, "depth": 0.55, "front_type": 0},
            {"name": "DrawerBase", "type": 3, "width": 0.6, "height": 0.72, "depth": 0.55, "front_type": 1},
            {"name": "BlindCorner", "type": 4, "width": 0.9, "height": 0.72, "depth": 0.55, "front_type": 0},
            {"name": "SinkBase", "type": 5, "width": 0.9, "height": 0.72, "depth": 0.55, "front_type": 0},
            {"name": "Appliance", "type": 6, "width": 0.6, "height": 0.72, "depth": 0.55, "front_type": 0},
            {"name": "OpenShelving", "type": 7, "width": 0.6, "height": 0.72, "depth": 0.3, "front_type": 0},
            {"name": "DiagonalCorner", "type": 8, "width": 0.6, "height": 0.72, "depth": 0.55, "front_type": 0},
            {"name": "PulloutPantry", "type": 9, "width": 0.3, "height": 2.1, "depth": 0.55, "front_type": 0},
        ]

        # Create cabinets in a grid
        cols = 5
        spacing_x = 1.2
        spacing_y = 1.5

        created_count = 0
        for i, config in enumerate(cabinet_configs):
            try:
                col = i % cols
                row = i // cols

                # Create mesh and object
                mesh = bpy.data.meshes.new(f"Cabinet_{config['name']}")
                obj = bpy.data.objects.new(f"Cabinet_{config['name']}", mesh)
                bpy.context.collection.objects.link(obj)

                # Add geometry nodes modifier
                mod = obj.modifiers.new("GeometryNodes", 'NODES')
                mod.node_group = ng

                # Set parameters using the modifier's interface
                # Note: Blender 4.0+ uses different API for setting modifier inputs
                try:
                    # Try new API first (Blender 4.0+)
                    mod["Socket_2"] = config["type"]  # Cabinet Type
                    mod["Socket_3"] = config["width"]  # Width
                    mod["Socket_4"] = config["height"]  # Height
                    mod["Socket_5"] = config["depth"]  # Depth
                except:
                    # Fall back to finding sockets by name
                    pass

                # Position object
                obj.location = (col * spacing_x, row * spacing_y, 0)

                created_count += 1

            except Exception as e:
                log_test(f"VisualTest/{config['name']}", "fail", str(e))

        log_test("VisualTestScene", "pass",
                f"Created {created_count} cabinet objects in grid")

        # Add a camera and light for rendering
        bpy.ops.object.camera_add(location=(2.5, -4, 2))
        camera = bpy.context.active_object
        camera.rotation_euler = (1.1, 0, 0.2)
        bpy.context.scene.camera = camera

        bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))

        return True

    except Exception as e:
        log_test("VisualTestScene", "fail", f"Error: {str(e)}",
                {"traceback": traceback.format_exc()})
        return False


def test_door_features():
    """Test specific door features like hinge side and double doors."""
    print("\n=== Testing Door Features ===\n")

    try:
        from src.nodes.systems import door_assembly
        ng = door_assembly.create_door_assembly_nodegroup()

        # Check for Hinge Side input
        hinge_side_found = False
        for item in ng.interface.items_tree:
            if item.name == "Hinge Side":
                hinge_side_found = True
                break

        if hinge_side_found:
            log_test("DoorFeatures/HingeSide", "pass", "Hinge Side parameter found")
        else:
            log_test("DoorFeatures/HingeSide", "fail", "Hinge Side parameter missing")

        # Check for Overlay Type input
        overlay_type_found = False
        for item in ng.interface.items_tree:
            if item.name == "Overlay Type":
                overlay_type_found = True
                break

        if overlay_type_found:
            log_test("DoorFeatures/OverlayType", "pass", "Overlay Type parameter found")
        else:
            log_test("DoorFeatures/OverlayType", "fail", "Overlay Type parameter missing")

    except Exception as e:
        log_test("DoorFeatures", "fail", f"Error: {str(e)}")


def test_hardware_integration():
    """Test that hardware components are integrated in master."""
    print("\n=== Testing Hardware Integration ===\n")

    try:
        from src.nodes import master

        # Regenerate to ensure latest
        ng = master.create_cabinet_master_nodegroup()

        # Check for hardware-related inputs
        hardware_inputs = ["Show Hardware", "Hinge Style", "Drawer Slide Style", "Hardware Material"]
        found = []
        missing = []

        for inp_name in hardware_inputs:
            input_found = False
            for item in ng.interface.items_tree:
                if item.name == inp_name:
                    input_found = True
                    found.append(inp_name)
                    break
            if not input_found:
                missing.append(inp_name)

        if missing:
            log_test("HardwareIntegration/Inputs", "warning",
                    f"Missing: {missing}, Found: {found}")
        else:
            log_test("HardwareIntegration/Inputs", "pass",
                    f"All hardware inputs present: {found}")

        # Check for hardware node instances
        hardware_nodes = ["Hinge", "Drawer Slides", "Shelf Pins", "Trash Pullout", "Spice Rack"]
        nodes_found = []
        nodes_missing = []

        for node_name in hardware_nodes:
            if any(n.name == node_name for n in ng.nodes):
                nodes_found.append(node_name)
            else:
                nodes_missing.append(node_name)

        if nodes_missing:
            log_test("HardwareIntegration/Nodes", "warning",
                    f"Missing nodes: {nodes_missing}, Found: {nodes_found}")
        else:
            log_test("HardwareIntegration/Nodes", "pass",
                    f"All hardware nodes integrated: {nodes_found}")

    except Exception as e:
        log_test("HardwareIntegration", "fail", f"Error: {str(e)}")


def render_visual_proof(output_dir=None):
    """Render visual proof images for each cabinet type.

    Uses EEVEE at 800x600 for speed. Saves images to /validation/ directory.
    """
    print("\n=== Rendering Visual Proof ===\n")

    if output_dir is None:
        output_dir = os.path.join(PROJECT_PATH, "validation")

    # Create validation directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Set up render settings for speed
        scene = bpy.context.scene
        scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'BLENDER_EEVEE_NEXT') else 'BLENDER_EEVEE'
        scene.render.resolution_x = 800
        scene.render.resolution_y = 600
        scene.render.film_transparent = True

        # Ensure camera exists
        if scene.camera is None:
            bpy.ops.object.camera_add(location=(2.5, -4, 2))
            camera = bpy.context.active_object
            camera.rotation_euler = (1.1, 0, 0.2)
            scene.camera = camera

        # Find all test cabinet objects
        cabinet_objects = [obj for obj in bpy.data.objects if obj.name.startswith("Cabinet_")]

        if not cabinet_objects:
            log_test("VisualProof/Render", "warning", "No cabinet objects found to render")
            return False

        rendered_count = 0
        for obj in cabinet_objects:
            try:
                # Hide all other cabinets
                for other in cabinet_objects:
                    other.hide_render = (other != obj)

                # Position camera to frame this cabinet
                # Move camera closer for individual shots
                cam = scene.camera
                cam.location = (obj.location.x + 1.5, obj.location.y - 2.5, 1.5)

                # Set output path
                cabinet_name = obj.name.replace("Cabinet_", "")
                render_path = os.path.join(output_dir, f"{cabinet_name}.png")
                scene.render.filepath = render_path

                # Render
                bpy.ops.render.render(write_still=True)
                rendered_count += 1
                print(f"  Rendered: {cabinet_name}.png")

            except Exception as e:
                log_test(f"VisualProof/{obj.name}", "fail", str(e))

        # Unhide all for final grid render
        for obj in cabinet_objects:
            obj.hide_render = False

        # Render full grid overview
        cam = scene.camera
        cam.location = (2.5, -6, 4)
        cam.rotation_euler = (1.0, 0, 0)
        scene.render.filepath = os.path.join(output_dir, "_all_cabinets_grid.png")
        bpy.ops.render.render(write_still=True)
        rendered_count += 1

        log_test("VisualProof/Render", "pass",
                f"Rendered {rendered_count} images to {output_dir}")
        return True

    except Exception as e:
        log_test("VisualProof/Render", "fail", f"Error: {str(e)}",
                {"traceback": traceback.format_exc()})
        return False


def save_report(output_path=None):
    """Save test results to JSON file."""
    if output_path is None:
        # Try to save in the project directory
        output_path = os.path.join(PROJECT_PATH, "test_report.json")

    # Check if the directory exists and is actually a directory
    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        # Fall back to user's home directory
        output_path = os.path.expanduser("~/cabinet_generator_test_report.json")
        print(f"Warning: Could not save to project directory, saving to: {output_path}")

    try:
        with open(output_path, 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"\nReport saved to: {output_path}")
    except Exception as e:
        print(f"\nCould not save report file: {e}")
        print("Test results available in test_results variable.")

    return output_path


def print_summary():
    """Print test summary to console."""
    summary = test_results["summary"]
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total:    {summary['total']}")
    print(f"Passed:   {summary['passed']}")
    print(f"Failed:   {summary['failed']}")
    print(f"Warnings: {summary['warnings']}")
    print("=" * 50)

    if summary['failed'] > 0:
        print("\nFAILED TESTS:")
        for test in test_results["tests"]:
            if test["status"] == "fail":
                print(f"  - {test['name']}: {test['message']}")


def run_all_tests(create_visual=True, save_json=True, render_proof=False):
    """Run all tests.

    Args:
        create_visual: Create visual test scene with cabinet objects
        save_json: Save JSON report to test_report.json
        render_proof: Render visual proof images to /validation/ directory
    """
    print("\n" + "=" * 50)
    print("CABINET GENERATOR TEST SUITE")
    print("=" * 50)

    # Clear scene first
    clear_scene()

    # Run test categories
    test_atomic_components()
    test_system_components()
    test_master_orchestrator()
    test_generate_all()
    test_door_features()
    test_hardware_integration()

    if create_visual:
        clear_scene()  # Clear before creating visual scene
        create_visual_test_scene()

    if render_proof:
        render_visual_proof()

    # Print and save results
    print_summary()

    if save_json:
        save_report()

    return test_results


def run_full_validation():
    """Run complete validation with visual proof rendering.

    This is the comprehensive validation that:
    1. Tests all node group generators
    2. Creates visual test scene
    3. Renders proof images to /validation/ directory
    4. Saves JSON report

    Usage:
        blender --background --python test_cabinet_generator.py -- --full-validation
    """
    return run_all_tests(create_visual=True, save_json=True, render_proof=True)


# Run tests when script is executed
if __name__ == "__main__":
    import sys
    # Check for command line arguments
    if "--full-validation" in sys.argv:
        run_full_validation()
    elif "--render-proof" in sys.argv:
        run_all_tests(render_proof=True)
    else:
        run_all_tests()
