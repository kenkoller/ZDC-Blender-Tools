# ZDC - Universal PBR Shader

Full PBR shader with support for 10 texture map inputs and an optional sparkle/flake system. Blender 5.0+ (Cycles).

## Features

- Complete PBR workflow: Base Color, Metallic, Roughness, Normal, Bump, Displacement, AO, Emission, Opacity, Subsurface
- Optional sparkle/flake overlay system
- Image texture loading with automatic colorspace detection
- Non-destructive parameter control

## Usage

1. Select an object
2. Open **Properties > Material > ZDC**
3. Apply the Universal PBR material
4. Load texture maps or use procedural defaults

## Structure

```
universal-pbr-shader/
├── __init__.py                ← Registration and bl_info
└── universal_pbr_shader.py    ← Full shader system
```

## Notes

Originally extracted from the metallic-flake-shader addon where it was unused dead code. Now maintained as a standalone addon.
