"""Calibrated color accuracy constants and utilities.

This module is the single source of truth for color values used across
ZDC addons. Colors are derived from cross-polarized photography captures
of physical product samples under standardized lighting.

Client-specific color values should be added to a local (gitignored)
extension of this module or to CLAUDE.local.md — never committed to the
public repository.

All color values are stored as linear RGB tuples (0.0–1.0) for direct
use in Blender shader nodes. Use srgb_to_linear() when converting from
measured sRGB values.
"""

import math
from typing import Tuple

# Type alias for RGB color tuples
LinearRGB = Tuple[float, float, float]


def srgb_to_linear(value: float) -> float:
    """Convert a single sRGB channel value (0–1) to linear.

    Uses the standard IEC 61966-2-1 transfer function.
    """
    if value <= 0.04045:
        return value / 12.92
    return math.pow((value + 0.055) / 1.055, 2.4)


def linear_to_srgb(value: float) -> float:
    """Convert a single linear channel value (0–1) to sRGB."""
    if value <= 0.0031308:
        return value * 12.92
    return 1.055 * math.pow(value, 1.0 / 2.4) - 0.055


def srgb_tuple_to_linear(srgb: Tuple[float, float, float]) -> LinearRGB:
    """Convert an sRGB color tuple to linear RGB.

    Args:
        srgb: (R, G, B) values in sRGB space (0–1 range)

    Returns:
        (R, G, B) in linear space
    """
    return (srgb_to_linear(srgb[0]),
            srgb_to_linear(srgb[1]),
            srgb_to_linear(srgb[2]))


def hex_to_linear(hex_color: str) -> LinearRGB:
    """Convert a hex color string to linear RGB.

    Args:
        hex_color: Color string like "#FF8800" or "FF8800"

    Returns:
        (R, G, B) in linear space
    """
    h = hex_color.lstrip('#')
    srgb = (int(h[0:2], 16) / 255.0,
            int(h[2:4], 16) / 255.0,
            int(h[4:6], 16) / 255.0)
    return srgb_tuple_to_linear(srgb)


# ---------------------------------------------------------------------------
# Standard material colors (generic, non-client-specific)
# ---------------------------------------------------------------------------

# Common metallic finishes (approximate linear RGB)
CHROME_BASE = srgb_tuple_to_linear((0.863, 0.863, 0.863))
BRUSHED_NICKEL_BASE = srgb_tuple_to_linear((0.753, 0.733, 0.710))
OIL_RUBBED_BRONZE_BASE = srgb_tuple_to_linear((0.220, 0.176, 0.145))
MATTE_BLACK_BASE = srgb_tuple_to_linear((0.067, 0.067, 0.067))

# Common wood tones (approximate linear RGB)
NATURAL_MAPLE = srgb_tuple_to_linear((0.878, 0.773, 0.620))
NATURAL_WALNUT = srgb_tuple_to_linear((0.396, 0.263, 0.176))
WHITE_OAK = srgb_tuple_to_linear((0.827, 0.761, 0.659))
