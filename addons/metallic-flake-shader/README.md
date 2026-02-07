# ZDC - Metallic Flake Shader

Procedural metallic paint flake material system for Blender 5.0+ (Cycles).

## Features

- Multi-layer metallic flake shader (base coat, flake layer, clear coat)
- Procedural flake generation with configurable size, density, and orientation
- Color-accurate metallic finishes for product visualization
- Non-destructive parameter control via material properties panel

## Usage

1. Select an object
2. Open **Properties > Material > ZDC**
3. Apply the metallic flake material
4. Adjust parameters (base color, flake color, flake density, clear coat IOR, etc.)

## Structure

```
metallic-flake-shader/
├── __init__.py                ← Registration and bl_info
└── metallic_flake_shader.py   ← Full shader system (operators, panels, node creation)
```
