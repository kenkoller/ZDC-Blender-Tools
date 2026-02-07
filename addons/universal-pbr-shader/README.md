# ZDC - Universal PBR Shader

Comprehensive PBR material system for Blender 5.0+ (Cycles) with full texture map support and metallic flake sparkle system.

This is the single shader addon for ZDC tools.

## Features

- Full PBR workflow: Base Color, Metallic, Roughness, Normal, Bump, Displacement, AO, Emission, Opacity, Gloss (10 texture map slots)
- Shared UV mapping controls (scale, rotation, offset, projection mode)
- Optional three-layer sparkle system for metallic flake materials
- Surface grain, anisotropic grain, SSS, and clearcoat effects
- 13 built-in presets including 7 metallic flake material presets
- User preset save/load (persisted as JSON)

## Built-in Presets

**General Materials:**
- Default (Standard Plastic)
- Brushed Steel
- Wood Base
- Glazed Ceramic
- Soft Rubber
- Frosted Glass

**Metallic Flake Materials** (sparkle system enabled):
- Silver Automotive
- Gold
- Midnight Blue Pearl
- Candy Apple Red
- Gunmetal Gray
- Champagne
- Plastic Toy (Coarse)

## Usage

1. Select an object
2. Open **Properties > Material > ZDC**
3. Click "Create Universal PBR Material"
4. Choose a preset or adjust parameters manually
5. Load texture maps via the Textures panel, or use procedural settings
6. Enable the Sparkle System panel for metallic flake effects

## Structure

```
universal-pbr-shader/
├── __init__.py                ← Registration and bl_info
└── universal_pbr_shader.py    ← Full shader system
```
