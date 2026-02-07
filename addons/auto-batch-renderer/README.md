# ZDC - Auto Batch Renderer

Automated batch rendering system for high-volume product visualization in Blender 5.0+.

## Features

- Multi-view camera system with configurable angles
- Turntable animation with segments and hold points
- Orthographic and perspective camera support
- Automatic camera framing (object bounding box fitting)
- Batch render all views in sequence with cancel support
- Timeline marker integration

## Usage

1. Open the **ZDC** sidebar tab in the 3D Viewport
2. Click **Initialize Scene** to set up camera rig and lighting
3. Add views with desired angles, camera types, and render settings
4. Configure turntable segments if animation is needed
5. Click **Render All** to batch-render every configured view

## Module Structure

```
auto-batch-renderer/
├── __init__.py       ← Registration and bl_info
├── properties.py     ← Settings, view configs, turntable segments
├── operators.py      ← All operator classes (add/remove views, render, etc.)
├── panels.py         ← UI panel
├── handlers.py       ← Timeline update handler, deferred data check
└── src/
    └── framing.py    ← Camera framing algorithm (pure computation)
```

## Known Issues

- First render in a session may take longer due to shader compilation
- Cancelling mid-render leaves partial output files
