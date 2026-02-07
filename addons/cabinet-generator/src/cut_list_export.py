# Cut List Export functionality for Cabinet Generator
# Generates panel dimensions and cut lists for manufacturing

import bpy
import json
import csv
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Panel:
    """Represents a single panel with dimensions and metadata."""
    name: str
    width: float  # X dimension in mm
    height: float  # Y/Z dimension in mm
    thickness: float  # Material thickness in mm
    quantity: int = 1
    material: str = "Plywood"
    edge_banding: str = ""  # e.g., "L,R" for left and right edges
    grain_direction: str = "horizontal"  # or "vertical"
    notes: str = ""


@dataclass
class CutList:
    """Complete cut list for a cabinet."""
    name: str
    date: str
    panels: List[Panel] = field(default_factory=list)
    hardware: List[Dict] = field(default_factory=list)
    notes: str = ""

    def add_panel(self, panel: Panel):
        """Add a panel to the cut list."""
        self.panels.append(panel)

    def add_hardware(self, name: str, quantity: int, specs: str = ""):
        """Add hardware item to the list."""
        self.hardware.append({
            "name": name,
            "quantity": quantity,
            "specs": specs
        })

    def total_sheet_area(self) -> float:
        """Calculate total panel area in square meters."""
        return sum(
            (p.width / 1000) * (p.height / 1000) * p.quantity
            for p in self.panels
        )


def generate_cut_list_from_settings(settings) -> CutList:
    """Generate a cut list from cabinet settings.

    Args:
        settings: CABINET_PG_Settings property group

    Returns:
        CutList with all panels and hardware
    """
    # Convert from meters to mm
    width_mm = settings.width * 1000
    height_mm = settings.height * 1000
    depth_mm = settings.depth * 1000
    panel_thick_mm = settings.panel_thickness * 1000
    shelf_thick_mm = settings.shelf_thickness * 1000

    # Effective interior dimensions
    interior_width = width_mm - (2 * panel_thick_mm)
    interior_height = height_mm - (2 * panel_thick_mm)

    cut_list = CutList(
        name=f"{settings.cabinet_type} Cabinet",
        date=datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    # ========== CARCASS PANELS ==========

    # Side panels (2x)
    cut_list.add_panel(Panel(
        name="Side Panel",
        width=depth_mm,
        height=height_mm,
        thickness=panel_thick_mm,
        quantity=2,
        edge_banding="F",  # Front edge
        grain_direction="vertical",
        notes="Left and right sides"
    ))

    # Top panel
    cut_list.add_panel(Panel(
        name="Top Panel",
        width=interior_width,
        height=depth_mm,
        thickness=panel_thick_mm,
        quantity=1,
        edge_banding="F",
        grain_direction="horizontal"
    ))

    # Bottom panel
    cut_list.add_panel(Panel(
        name="Bottom Panel",
        width=interior_width,
        height=depth_mm,
        thickness=panel_thick_mm,
        quantity=1,
        edge_banding="F",
        grain_direction="horizontal"
    ))

    # Back panel (if enabled)
    if settings.has_back:
        back_thick_mm = 6  # Standard back thickness
        cut_list.add_panel(Panel(
            name="Back Panel",
            width=interior_width,
            height=interior_height,
            thickness=back_thick_mm,
            quantity=1,
            material="HDF/MDF",
            notes="Fits in rabbet or overlay"
        ))

    # ========== SHELVES ==========
    if settings.has_shelves and settings.shelf_count > 0:
        shelf_depth = depth_mm - 20  # 20mm setback from front
        if settings.has_back:
            shelf_depth -= 6  # Account for back panel

        cut_list.add_panel(Panel(
            name="Adjustable Shelf",
            width=interior_width - 2,  # 1mm clearance each side
            height=shelf_depth,
            thickness=shelf_thick_mm,
            quantity=settings.shelf_count,
            edge_banding="F",
            grain_direction="horizontal",
            notes="Adjustable shelf"
        ))

    # ========== TOE KICK ==========
    if settings.has_toe_kick:
        toe_kick_height_mm = settings.toe_kick_height * 1000
        toe_kick_depth_mm = settings.toe_kick_depth * 1000

        cut_list.add_panel(Panel(
            name="Toe Kick Panel",
            width=interior_width,
            height=toe_kick_height_mm,
            thickness=panel_thick_mm,
            quantity=1,
            notes="Front toe kick cover"
        ))

        cut_list.add_panel(Panel(
            name="Toe Kick Support",
            width=depth_mm - toe_kick_depth_mm,
            height=toe_kick_height_mm,
            thickness=panel_thick_mm,
            quantity=2,
            notes="Side supports"
        ))

    # ========== FACE FRAME ==========
    if settings.has_face_frame:
        frame_width_mm = settings.face_frame_width * 1000

        # Stiles (vertical)
        cut_list.add_panel(Panel(
            name="Face Frame Stile",
            width=frame_width_mm,
            height=height_mm,
            thickness=panel_thick_mm,
            quantity=2,
            material="Solid Wood",
            grain_direction="vertical",
            notes="Left and right stiles"
        ))

        # Rails (horizontal)
        rail_width = width_mm - (2 * frame_width_mm)
        cut_list.add_panel(Panel(
            name="Face Frame Rail",
            width=rail_width,
            height=frame_width_mm,
            thickness=panel_thick_mm,
            quantity=2,
            material="Solid Wood",
            grain_direction="horizontal",
            notes="Top and bottom rails"
        ))

    # ========== DOORS ==========
    if settings.front_type == 'DOORS':
        door_gap = 3  # 3mm gap between doors and frame

        if settings.double_doors:
            door_width = (width_mm / 2) - (door_gap * 1.5)
            door_qty = 2
        else:
            door_width = width_mm - (door_gap * 2)
            door_qty = 1

        door_height = height_mm - (door_gap * 2)
        if settings.has_toe_kick:
            door_height -= settings.toe_kick_height * 1000

        cut_list.add_panel(Panel(
            name="Door Panel",
            width=door_width,
            height=door_height,
            thickness=panel_thick_mm,
            quantity=door_qty,
            edge_banding="L,R,T,B",  # All edges
            grain_direction="vertical"
        ))

        # Hardware for doors
        hinges_per_door = 2 if door_height < 600 else 3
        cut_list.add_hardware("European Cup Hinge", hinges_per_door * door_qty, "35mm cup, soft-close")
        cut_list.add_hardware("Door Handle", door_qty, settings.handle_style)

    # ========== DRAWERS ==========
    if settings.front_type == 'DRAWERS':
        drawer_height_mm = (height_mm - (settings.has_toe_kick and settings.toe_kick_height * 1000 or 0)) / settings.drawer_count
        drawer_front_height = drawer_height_mm - 3  # 3mm gap

        # Drawer fronts
        cut_list.add_panel(Panel(
            name="Drawer Front",
            width=width_mm - 6,  # 3mm gap each side
            height=drawer_front_height,
            thickness=panel_thick_mm,
            quantity=settings.drawer_count,
            edge_banding="L,R,T,B",
            grain_direction="horizontal"
        ))

        # Drawer box sides
        drawer_box_height = drawer_front_height - 50  # Allow for front overhang
        cut_list.add_panel(Panel(
            name="Drawer Side",
            width=depth_mm - 80,  # Leave space for slides
            height=drawer_box_height,
            thickness=12,  # Standard drawer side thickness
            quantity=settings.drawer_count * 2,
            material="Baltic Birch",
            notes="Drawer box sides"
        ))

        # Drawer box front/back
        cut_list.add_panel(Panel(
            name="Drawer Box F/B",
            width=interior_width - 50,  # Allow for slides
            height=drawer_box_height,
            thickness=12,
            quantity=settings.drawer_count * 2,
            material="Baltic Birch",
            notes="Drawer box front and back"
        ))

        # Drawer bottoms
        cut_list.add_panel(Panel(
            name="Drawer Bottom",
            width=interior_width - 52,
            height=depth_mm - 82,
            thickness=6,
            quantity=settings.drawer_count,
            material="HDF",
            notes="Fits in groove"
        ))

        # Hardware for drawers
        cut_list.add_hardware("Drawer Slide Pair", settings.drawer_count, "Full extension, soft-close")
        cut_list.add_hardware("Drawer Handle", settings.drawer_count, settings.handle_style)

    # ========== ADJUSTABLE SHELF HARDWARE ==========
    if settings.has_adjustable_shelves:
        pins_per_shelf = 4  # 4 pins per shelf
        cut_list.add_hardware("Shelf Pin", settings.shelf_count * pins_per_shelf, "5mm, nickel")

    return cut_list


def export_to_csv(cut_list: CutList, filepath: str):
    """Export cut list to CSV file.

    Args:
        cut_list: The cut list to export
        filepath: Path to save the CSV file
    """
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header info
        writer.writerow(["Cut List:", cut_list.name])
        writer.writerow(["Generated:", cut_list.date])
        writer.writerow([])

        # Panel section
        writer.writerow(["PANELS"])
        writer.writerow(["Name", "Width (mm)", "Height (mm)", "Thickness (mm)",
                         "Qty", "Material", "Edge Banding", "Grain", "Notes"])

        for panel in cut_list.panels:
            writer.writerow([
                panel.name,
                f"{panel.width:.1f}",
                f"{panel.height:.1f}",
                f"{panel.thickness:.1f}",
                panel.quantity,
                panel.material,
                panel.edge_banding,
                panel.grain_direction,
                panel.notes
            ])

        writer.writerow([])
        writer.writerow(["Total Panel Area (m²):", f"{cut_list.total_sheet_area():.2f}"])

        # Hardware section
        if cut_list.hardware:
            writer.writerow([])
            writer.writerow(["HARDWARE"])
            writer.writerow(["Item", "Quantity", "Specifications"])
            for hw in cut_list.hardware:
                writer.writerow([hw["name"], hw["quantity"], hw["specs"]])

        # Notes
        if cut_list.notes:
            writer.writerow([])
            writer.writerow(["NOTES:", cut_list.notes])


def export_to_json(cut_list: CutList, filepath: str):
    """Export cut list to JSON file.

    Args:
        cut_list: The cut list to export
        filepath: Path to save the JSON file
    """
    data = {
        "name": cut_list.name,
        "date": cut_list.date,
        "panels": [asdict(p) for p in cut_list.panels],
        "hardware": cut_list.hardware,
        "notes": cut_list.notes,
        "summary": {
            "total_panels": sum(p.quantity for p in cut_list.panels),
            "total_area_m2": cut_list.total_sheet_area(),
            "total_hardware_items": sum(h["quantity"] for h in cut_list.hardware)
        }
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def format_cut_list_text(cut_list: CutList) -> str:
    """Format cut list as readable text.

    Args:
        cut_list: The cut list to format

    Returns:
        Formatted string representation
    """
    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"CUT LIST: {cut_list.name}")
    lines.append(f"Generated: {cut_list.date}")
    lines.append(f"{'=' * 60}")
    lines.append("")
    lines.append("PANELS:")
    lines.append("-" * 60)
    lines.append(f"{'Name':<20} {'W (mm)':<10} {'H (mm)':<10} {'T':<6} {'Qty':<4}")
    lines.append("-" * 60)

    for panel in cut_list.panels:
        lines.append(
            f"{panel.name:<20} {panel.width:<10.1f} {panel.height:<10.1f} "
            f"{panel.thickness:<6.1f} {panel.quantity:<4}"
        )

    lines.append("-" * 60)
    lines.append(f"Total Area: {cut_list.total_sheet_area():.2f} m²")
    lines.append("")

    if cut_list.hardware:
        lines.append("HARDWARE:")
        lines.append("-" * 60)
        for hw in cut_list.hardware:
            lines.append(f"  {hw['quantity']}x {hw['name']} ({hw['specs']})")

    return "\n".join(lines)


# Blender Operator for exporting
class CABINET_OT_ExportCutList(bpy.types.Operator):
    """Export cabinet cut list"""
    bl_idname = "cabinet.export_cut_list"
    bl_label = "Export Cut List"
    bl_description = "Export panel dimensions and cut list for manufacturing"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH',
        default="cabinet_cutlist"
    )

    format: bpy.props.EnumProperty(
        name="Format",
        items=[
            ('CSV', "CSV", "Comma-separated values"),
            ('JSON', "JSON", "JSON format"),
            ('TEXT', "Text", "Plain text to clipboard"),
        ],
        default='CSV'
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        settings = context.scene.cabinet_settings
        cut_list = generate_cut_list_from_settings(settings)

        if self.format == 'CSV':
            filepath = self.filepath if self.filepath.endswith('.csv') else self.filepath + '.csv'
            export_to_csv(cut_list, filepath)
            self.report({'INFO'}, f"Exported cut list to {filepath}")

        elif self.format == 'JSON':
            filepath = self.filepath if self.filepath.endswith('.json') else self.filepath + '.json'
            export_to_json(cut_list, filepath)
            self.report({'INFO'}, f"Exported cut list to {filepath}")

        elif self.format == 'TEXT':
            text = format_cut_list_text(cut_list)
            context.window_manager.clipboard = text
            self.report({'INFO'}, "Cut list copied to clipboard")

        return {'FINISHED'}


class CABINET_OT_ShowCutList(bpy.types.Operator):
    """Show cabinet cut list in popup"""
    bl_idname = "cabinet.show_cut_list"
    bl_label = "Show Cut List"
    bl_description = "Display cut list in a popup window"
    bl_options = {'REGISTER'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=500)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cabinet_settings
        cut_list = generate_cut_list_from_settings(settings)

        box = layout.box()
        box.label(text=f"Cut List: {cut_list.name}", icon='FILE_TEXT')
        box.label(text=f"Generated: {cut_list.date}")

        # Panels
        layout.label(text="Panels:", icon='MESH_PLANE')
        for panel in cut_list.panels:
            row = layout.row()
            row.label(text=f"{panel.quantity}x {panel.name}")
            row.label(text=f"{panel.width:.0f} x {panel.height:.0f} x {panel.thickness:.0f} mm")

        layout.separator()
        layout.label(text=f"Total Area: {cut_list.total_sheet_area():.2f} m²")

        # Hardware
        if cut_list.hardware:
            layout.separator()
            layout.label(text="Hardware:", icon='TOOL_SETTINGS')
            for hw in cut_list.hardware:
                layout.label(text=f"  {hw['quantity']}x {hw['name']}")


# Registration
classes = (
    CABINET_OT_ExportCutList,
    CABINET_OT_ShowCutList,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
