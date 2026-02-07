# ZDC Blender Tools

Blender 5.0+ add-ons for professional 3D product visualization, developed by **Ziti Design & Creative**.

## Add-ons

| Add-on | Description | Status |
|--------|-------------|--------|
| [auto-batch-renderer](addons/auto-batch-renderer/) | Automated batch rendering pipeline for high-volume product shots | Production |
| [cabinet-generator](addons/cabinet-generator/) | Parametric cabinet generation via Geometry Nodes | Production |
| [metallic-flake-shader](addons/metallic-flake-shader/) | Procedural metallic paint flake material system | Production |
| [universal-pbr-shader](addons/universal-pbr-shader/) | Full PBR shader with 10 texture maps and sparkle system | Production |
| [kitchen-generator](addons/kitchen-generator/) | Kitchen scene/layout generation | Stub |
| [home-builder](addons/home-builder/) | Room/house construction system (Andrew Peel, GPLv3) | Integrated |

## Requirements

- **Blender 5.0+** (Python 3.11+)
- GPU rendering recommended (Cycles)

## Installation

### Quick Install (symlinks)

```bash
python scripts/install_addons.py
```

This creates symlinks from each addon into your Blender user addons directory. Restart Blender and enable each addon in **Preferences > Add-ons** (search "ZDC").

To remove:
```bash
python scripts/install_addons.py --uninstall
```

### Manual Install

Copy or symlink individual addon folders from `addons/` into your Blender addons directory:

- **macOS:** `~/Library/Application Support/Blender/5.0/scripts/addons/`
- **Windows:** `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`
- **Linux:** `~/.config/blender/5.0/scripts/addons/`

## Project Structure

```
ZDC-Blender-Tools/
├── addons/          ← Installable Blender add-ons
├── common/          ← Shared utilities across addons
├── scripts/         ← Development and installation scripts
├── tests/           ← Test scenes and runners
├── docs/            ← Design specifications
├── mcp/             ← BlenderMCP integration docs
└── reference/       ← Local-only reference files (gitignored)
```

## Development

### Validation

```bash
python scripts/validate_bl_info.py
```

### BlenderMCP

See [mcp/README.md](mcp/README.md) for instructions on connecting Claude Desktop to a running Blender instance for interactive development.

## License

GPLv3 — see [LICENSE](LICENSE).

Add-ons authored by Ziti Design & Creative. Home Builder by Andrew Peel (GPLv3).
