#!/usr/bin/env python3
"""Install ZDC addons into Blender by creating symlinks.

Creates symbolic links from each addon directory in addons/ to the
user's Blender addons directory, making them available in Blender's
preferences without copying files.

Supports macOS and Windows. Auto-detects the latest Blender version
directory found on the system.

Usage:
    python scripts/install_addons.py
    python scripts/install_addons.py --blender-version 5.0
    python scripts/install_addons.py --uninstall
"""

import argparse
import os
import platform
import sys
from pathlib import Path


def get_blender_addons_dir(version: str | None = None) -> Path | None:
    """Find the Blender user addons directory for this platform.

    Args:
        version: Explicit Blender version (e.g. "5.0"). If None,
                 auto-detects the latest version found.

    Returns:
        Path to the addons directory, or None if not found.
    """
    system = platform.system()

    if system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / "Blender"
    elif system == "Windows":
        base = Path(os.environ.get("APPDATA", "")) / "Blender Foundation" / "Blender"
    elif system == "Linux":
        base = Path.home() / ".config" / "blender"
    else:
        return None

    if not base.exists():
        return None

    if version:
        target = base / version / "scripts" / "addons"
    else:
        # Find the latest version directory
        versions = []
        for d in base.iterdir():
            if d.is_dir():
                try:
                    versions.append((tuple(int(x) for x in d.name.split(".")), d.name))
                except ValueError:
                    continue
        if not versions:
            return None
        versions.sort(reverse=True)
        target = base / versions[0][1] / "scripts" / "addons"

    return target


def install(addons_src: Path, addons_dest: Path, dry_run: bool = False):
    """Create symlinks for all addons."""
    addons_dest.mkdir(parents=True, exist_ok=True)

    for addon_dir in sorted(addons_src.iterdir()):
        if not addon_dir.is_dir():
            continue
        if not (addon_dir / "__init__.py").exists():
            continue

        link = addons_dest / addon_dir.name
        if link.exists() or link.is_symlink():
            if link.is_symlink() and link.resolve() == addon_dir.resolve():
                print(f"  OK    {addon_dir.name} (already linked)")
                continue
            else:
                print(f"  SKIP  {addon_dir.name} (path exists, not our symlink)")
                continue

        if dry_run:
            print(f"  WOULD {addon_dir.name} -> {link}")
        else:
            link.symlink_to(addon_dir)
            print(f"  LINK  {addon_dir.name} -> {link}")


def uninstall(addons_src: Path, addons_dest: Path, dry_run: bool = False):
    """Remove symlinks for all addons."""
    for addon_dir in sorted(addons_src.iterdir()):
        if not addon_dir.is_dir():
            continue

        link = addons_dest / addon_dir.name
        if link.is_symlink() and link.resolve() == addon_dir.resolve():
            if dry_run:
                print(f"  WOULD REMOVE {link}")
            else:
                link.unlink()
                print(f"  REMOVED {addon_dir.name}")
        else:
            print(f"  SKIP    {addon_dir.name} (not a ZDC symlink)")


def main():
    parser = argparse.ArgumentParser(description="Install ZDC addons into Blender")
    parser.add_argument("--blender-version", help="Blender version (e.g. 5.0)")
    parser.add_argument("--uninstall", action="store_true", help="Remove addon symlinks")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    addons_src = root / "addons"

    if not addons_src.is_dir():
        print(f"Error: {addons_src} not found")
        sys.exit(1)

    addons_dest = get_blender_addons_dir(args.blender_version)
    if addons_dest is None:
        print("Error: Could not find Blender user addons directory.")
        print("Use --blender-version to specify the version explicitly.")
        sys.exit(1)

    print(f"Blender addons dir: {addons_dest}")
    print()

    if args.uninstall:
        uninstall(addons_src, addons_dest, args.dry_run)
    else:
        install(addons_src, addons_dest, args.dry_run)

    print()
    print("Done. Restart Blender and enable addons in Preferences > Add-ons.")


if __name__ == "__main__":
    main()
