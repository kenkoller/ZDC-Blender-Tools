# Component Library Master Plan
## Kitchen & Cabinet Generator Toolset — Blender 5.0+

**Author:** ZDC / Ken Koller  
**Date:** February 2026  
**Status:** Planning Phase

---

## 1. Architecture Overview

### 1.1 Integration with Kitchen & Cabinet Generator

This component library is not a standalone product — it is a subsystem of the larger kitchen and cabinet generator toolset. The generators (cabinet-generator, kitchen-generator) are the orchestration layer that creates, places, and manages kitchen elements. This library provides the raw ingredients those generators consume: geometry assets, procedural material node groups, profile curves, and style definitions.

The relationship is one-directional: the generators depend on the library, but the library has no dependency on the generators. This means the library can be developed, tested, and expanded independently, and any generator (cabinet, kitchen, bathroom, closet) can pull from the same shared pool of assets. The library's API surface — how generators request and apply assets — must be designed with this flexibility in mind from the start.

Key integration points where the library interfaces with the generators:

**Geometry assets** (handles, sinks, faucets, appliances, fixtures) are stored as .blend objects that generators append/link into scenes and parent to generated cabinet/countertop geometry.

**Profile curves** (door styles, moulding, countertop edges) are consumed by generators that sweep or bevel them along computed paths to create 3D geometry.

**Procedural material node groups** are applied by generators to the surfaces they create. The generators need to be able to programmatically set exposed parameters on these node groups (e.g., wood species, stain color, grain scale) to enable one-click style changes.

**Style presets** are data definitions that map a named style (e.g., "Modern Farmhouse") to specific choices across every component category. The kitchen generator reads a preset and delegates to each sub-generator with the appropriate library selections.

### 1.2 Two-Tier Asset System

The toolset operates under a two-tier model that separates commercially distributable assets from private production assets. Every sourcing and creation decision must respect this boundary.

**Commercial Tier (Public Release)** — Assets that ship with the kitchen/cabinet generators when sold. Every asset in this tier must have a license that permits redistribution as part of a commercial software product where the end user can access the underlying .blend files. This is the strictest licensing requirement in the 3D asset world and eliminates most standard "royalty-free" marketplace models.

**Private Tier (ZDC Internal)** — Assets used exclusively for Rev-A-Shelf renders and other paid client work. Standard royalty-free licenses from any marketplace are fine here since the assets appear only in final rendered output, never redistributed as files. Rev-A-Shelf catalog items (drawer organizers, lazy susans, pull-outs, etc.) live here and are entirely separate from the generator toolset.

The addon codebase and library infrastructure must enforce this separation cleanly, likely through distinct library directories that can be toggled independently. The generators should be agnostic to which tier an asset comes from — they just query the library, and the library resolves to whichever tier is available and appropriate.

---

## 2. Critical Licensing Constraint

This is the single most important finding from the research phase and will shape every sourcing decision.

**The Problem:** Standard "royalty-free" licenses from TurboSquid, CGTrader, and similar marketplaces explicitly prohibit redistribution of 3D model files in formats that end users can extract. A Blender addon that ships .blend asset libraries gives end users direct access to the geometry — this violates those licenses regardless of whether the models are "incorporated into a larger product."

TurboSquid's license states that redistributed files "must be incorporated into a larger creation and not in an open format that others can be downloaded." CGTrader's license states that "the resale or redistribution by the Buyer of any Product, obtained from the Site is expressly prohibited unless it is an Incorporated Product" and specifically requires proprietary formats that prevent extraction.

A .blend file sitting in an addon's asset library directory is, by definition, extractable. Game engines get around this by compiling assets into proprietary binary formats — Blender addons do not have this luxury.

**What This Means for Sourcing:**

For the **commercial tier**, every asset must come from one of these sources:

1. **CC0 / Public Domain** — No restrictions whatsoever. Poly Haven is the gold standard here; everything is CC0 with Blender-native files and PBR textures. The limitation is that their catalog skews toward decorative/organic models rather than architectural hardware.

2. **Self-created (parametric or modeled)** — Full IP ownership. This is the most reliable path for core components like handles, moulding profiles, door panels, and anything that needs to be parametrically driven anyway.

3. **Commissioned with full IP transfer** — Hire a 3D artist to create specific assets under a work-for-hire agreement that transfers all intellectual property rights to you. This is the path for complex photorealistic assets that are too time-consuming to model yourself but don't exist in CC0 form.

4. **Direct licensing from individual artists** — Negotiate custom redistribution licenses with specific 3D artists. Some artists on CGTrader, Sketchfab, or personal portfolios will grant redistribution rights for a higher fee. This requires case-by-case negotiation.

For the **private/ZDC tier**, standard royalty-free marketplace purchases work fine since assets only appear in rendered output.

---

## 3. Complete Component Taxonomy

This section catalogs every component category the library needs to cover, organized by domain. Each entry specifies whether it should be parametric, sourced, or both, along with the recommended creation method for the commercial tier.

### 3.1 Cabinet Components

These are the core of the system and should be almost entirely parametric since they need to respond to dimensional changes, style swaps, and material reassignment.

#### 3.1.1 Cabinet Door Styles

The door front is the single most visible element in any kitchen render and the primary style differentiator. The commercial library needs broad coverage of the major architectural styles.

**Flat/Slab Styles** — Parametric (trivially generated as a single plane with optional edge bevel). Covers modern/contemporary kitchens.
- Flat slab (square edge)
- Flat slab with micro-bevel
- Flat slab with radius edge

**Shaker Styles** — Parametric (flat panel inset into a frame; frame dimensions and panel reveal are parameters). The most popular door style in North America.
- Standard Shaker (square inner edge)
- Shaker with beaded inner edge
- Shaker with beveled inner edge
- Shaker with radius inner edge
- Slim Shaker (narrow rails and stiles)

**Raised Panel Styles** — Parametric (frame + raised center panel with profiled edge; the profile curve is the swappable element).
- Cathedral arch raised panel
- Square raised panel
- Double raised panel
- Raised panel with applied moulding

**Recessed/Flat Panel Styles** — Parametric (frame + flat inset panel).
- Mission style (square frame, flat panel)
- Beadboard inset panel
- V-groove inset panel

**Glass Front Styles** — Parametric (frame with glass panel insert; mullion pattern is the variable).
- Single glass panel
- Mullion grid (adjustable divisions)
- Leaded glass pattern
- Seeded/textured glass (material variant)

**Specialty Styles** — Mix of parametric + sourced depending on complexity.
- Louvered/slatted
- Open frame (no panel)
- Tambour/roll-up (appliance garages)
- Curved/radius doors (for lazy susan corners)

**Implementation approach:** Build a DoorGenerator class that takes a profile curve, frame dimensions, and panel type as inputs. The curve profiles define the decorative moulding detail on the frame's inner edge and the panel's raised edge. Swapping curves = swapping styles. Store profile curves as Blender curve objects in the library.

#### 3.1.2 Cabinet Hardware — Handles & Knobs

This is the category you specifically asked about. For the commercial tier, the recommended approach is parametric generation for geometric styles and self-modeled or commissioned work for ornate styles.

**Bar/Pull Handles (Parametric)** — These are the most common modern handle type and are geometrically simple enough to generate procedurally. Parameters: length, diameter/cross-section, standoff height, mounting hole spacing.
- Round bar pull (straight)
- Square bar pull (straight)
- D-shaped bar pull (curved)
- Flat bar pull (rectangular cross-section)
- T-bar pull
- Bow/arched pull
- Wire pull
- Oversized/appliance pull (12–24")

**Cup/Bin Pulls (Parametric + Modeled)** — The basic shell shape can be parametric, but ornate cast designs need modeling.
- Classic bin pull (half-cylinder shell)
- Mission-style cup pull
- Decorative cast cup pull (modeled)

**Knobs (Mostly Modeled)** — Knobs have more organic/decorative form so most benefit from hand modeling or lathe-style curve revolution.
- Round mushroom knob (parametric — revolve a half-circle profile)
- Square knob (parametric)
- Faceted/geometric knob (parametric)
- Turned/traditional knob (modeled — revolve a custom profile curve)
- Porcelain/ceramic knob (modeled)
- Crystal/glass knob (modeled + material)
- Ring pull / drop ring (modeled)
- Backplate + knob combos (modeled)

**Edge/Finger Pulls (Parametric)** — Minimal profile handles for handleless modern kitchens.
- Routed finger pull (integrated into door edge)
- Channel pull (aluminum extrusion profile)
- J-pull / lip pull
- Push-to-open (no visible hardware — just a mechanism)

**Hinges (Parametric)** — Rarely visible in renders but needed for realism when doors are shown open.
- European concealed hinge (standard 35mm cup)
- Exposed decorative hinge (modeled)
- Pivot hinge

**Recommended CC0 sources for handles:** Poly Haven has very limited cabinet hardware. For the commercial tier, the most practical approach is to self-create the parametric handles (bar pulls, edge pulls, simple knobs) and commission a 3D artist for a set of 10–15 ornate knob/pull designs under a work-for-hire IP transfer agreement. Budget estimate: $30–80 per model for detailed photorealistic hardware, so roughly $300–1,200 for a complete ornate set.

**For the private/ZDC tier:** TurboSquid has excellent handle sets. The "Knobs and cup handles set" at $39 for 23 models is a strong option for immediate production use. CGTrader has similar bundles. These work perfectly for your Rev-A-Shelf renders.

#### 3.1.3 Cabinet Box Construction

All parametric. The box itself is generated by the cabinet generator's Python code.

- Face frame construction (traditional US)
- Frameless/European construction (32mm system)
- Inset door construction
- Overlay options (full, half, variable)
- Toe kick (height, profile, material)
- Interior shelving (adjustable, fixed)
- Drawer box construction (dovetail visual, standard)
- Drawer slides (undermount, side-mount — simplified visual representation)

#### 3.1.4 Cabinet Types

All parametric, generated by the cabinet/kitchen generator.

**Base Cabinets** — Single door, double door, drawer bank (3/4/5 drawer), sink base (false front), tray divider, pull-out waste, corner base (blind corner, lazy susan, diagonal), peninsula/island end panel.

**Wall Cabinets** — Single door, double door, open shelf, plate rack, microwave cabinet, corner wall (blind, diagonal), range hood surround, glass-front, appliance garage.

**Tall Cabinets** — Pantry (single/double door), oven cabinet, utility cabinet, broom closet.

**Specialty** — Island cabinet, bookcase end, wine rack insert, desk/workstation base, refrigerator surround panels.

### 3.2 Countertops

#### 3.2.1 Edge Profiles (Parametric)

These are 2D curve profiles extruded/swept along the countertop perimeter. Store as Blender curve objects, swap them to change the look instantly.

- Square/straight edge
- Eased/slightly rounded edge
- Bullnose (half-round)
- Half bullnose
- Ogee (S-curve)
- Double ogee
- Beveled/chamfered
- Waterfall (mitered 90° down sides)
- Dupont
- Cove
- Laminate with build-up edge

#### 3.2.2 Countertop Forms (Parametric)

Generated based on cabinet layout footprint, with parameters for overhang, thickness, and backsplash integration.

- Standard straight run
- L-shaped
- U-shaped
- Island/peninsula
- Bar-height raised section
- Integrated sink cutout
- Cooktop cutout

### 3.3 Backsplash

#### 3.3.1 Patterns (Parametric via Geometry Nodes or Shader)

- Subway tile (standard brick pattern with adjustable grout width, tile dimensions)
- Herringbone
- Chevron
- Stacked vertical
- Hexagonal
- Mosaic (small square grid)
- Large format slab (no pattern, just material)
- Penny round
- Arabesque/lantern
- Basketweave

Implementation: These work best as shader-based patterns with displacement, or Geometry Nodes that instance tile geometry. The actual 3D geometry approach gives better realism at close range; shader-only is faster for distant shots.

### 3.4 Sinks & Faucets

#### 3.4.1 Kitchen Sinks (Mix — parametric base, modeled details)

- Undermount single bowl
- Undermount double bowl
- Farmhouse/apron-front single bowl
- Farmhouse double bowl
- Drop-in/top-mount single
- Drop-in double
- Workstation sink (with accessories ledge)
- Bar/prep sink (small)
- Integrated sink (same material as countertop)

**For the commercial tier:** The basic rectangular/bowl shapes can be parametric (revolve/loft profiles). Farmhouse sinks with fireclay texture and detailed drain fittings benefit from hand modeling. Consider commissioning 4–6 high-quality sink models.

#### 3.4.2 Faucets (Modeled or Sourced)

Faucets are complex organic forms with tight radii, knurled surfaces, and mechanical joints. Parametric generation is impractical — these should be modeled or sourced.

- Single-handle pull-down (most common modern)
- Single-handle pull-out
- Bridge faucet (traditional)
- Wall-mounted pot filler
- Bar faucet
- Touchless/motion sensor
- Two-handle widespread

**Commercial tier strategy:** Commission a set of 6–8 faucet models under work-for-hire. Budget: $50–120 per model depending on complexity.

### 3.5 Appliances

Appliances are the second-biggest visual element after cabinets. For photorealistic renders they need to look convincing.

#### 3.5.1 Major Appliances (Modeled or Sourced)

- Refrigerator: French door, side-by-side, single door with bottom freezer, counter-depth, panel-ready
- Range/oven: Freestanding gas, freestanding electric, slide-in gas, slide-in electric, pro-style range (36"/48")
- Cooktop: Gas 4-burner, gas 5-burner, electric smooth-top, induction
- Wall oven: Single, double, microwave combo
- Microwave: Over-the-range, built-in, countertop
- Dishwasher: Standard panel, integrated panel-ready, visible controls, hidden controls
- Range hood: Under-cabinet, wall-mount chimney, island chimney, downdraft, custom insert

**Critical licensing note:** Brand-specific appliance models (Sub-Zero, Wolf, Viking, etc.) are almost always trademarked. For the commercial tier, create "generic inspired" versions that capture the proportions and functional elements without replicating branded details. For the private tier, use brand-specific models from marketplaces as needed.

#### 3.5.2 Small Appliances / Countertop Items (Decorative — Sourced CC0)

These are scene-dressing items. Poly Haven and similar CC0 sources are appropriate here.

- Coffee maker
- Toaster
- Stand mixer
- Knife block
- Cutting board
- Fruit bowl
- Cookbook/tablet stand
- Paper towel holder
- Utensil crock

### 3.6 Doors & Windows (Architectural)

Home Builder 4 covers these, and your fork/rebuild needs equivalents. These are primarily parametric since they're driven by dimensional inputs and style variants.

#### 3.6.1 Interior Doors (Parametric)

- Flat/flush door
- 1-panel Shaker
- 2-panel
- 3-panel
- 4-panel (colonial)
- 5-panel
- 6-panel (classic colonial)
- Glass panel (French door)
- Barn door (flat + track hardware)
- Pocket door

**Components:** Door slab, frame/jamb, casing/trim (profile curve), hinges, handle sets (lever, knob, deadbolt).

#### 3.6.2 Exterior Doors (Parametric + Modeled details)

- Panel door with sidelights
- Panel door with transom
- Full glass/French
- Sliding patio door
- Bifold patio door

#### 3.6.3 Windows (Parametric)

All window types share a common parametric framework: frame, sash, glazing, with variable grid/muntin patterns.

- Single-hung
- Double-hung
- Casement (single, double)
- Sliding
- Awning
- Fixed/picture
- Bay window (3-section angled)
- Bow window (curved multi-section)
- Garden window (box/greenhouse)
- Transom
- Arched/radius top

**Muntin patterns (parametric grid):** Colonial (even grid), Prairie (border only), Craftsman (top section only), Diamond, None.

#### 3.6.4 Window Treatments (Mix)

- Blinds (horizontal, vertical — parametric via array modifier)
- Roman shade (modeled draped fabric)
- Curtain rod + panels (cloth sim or modeled)
- Plantation shutters (parametric — array of louvers)
- Roller shade (parametric)

### 3.7 Moulding & Trim Profiles

This is one of the most critical parametric library categories. Moulding profiles are 2D curves that get swept along paths (wall intersections, cabinet tops, door frames, etc.). The library is essentially a catalog of curve profiles.

#### 3.7.1 Crown Moulding

- Cove (simple concave arc)
- Ogee (S-curve)
- Dentil crown (requires geometry nodes for repeating blocks)
- Egg-and-dart (complex — modeled repeating element + array)
- Federal/colonial (multi-step profile)
- Contemporary (simple angular profile)
- Stepped/stacked (multiple pieces combined)

#### 3.7.2 Base Moulding / Baseboard

- Ranch (flat with slight top relief)
- Colonial (multi-curve top profile)
- Craftsman (simple flat with square cap)
- Victorian (ornate multi-curve)
- Modern (square/flat, tall)
- Shoe moulding (small quarter-round at floor line)

#### 3.7.3 Chair Rail / Wainscoting

- Simple cap moulding
- Traditional chair rail profile
- Wainscot panel frame (raised panel below chair rail)
- Shiplap/beadboard (horizontal or vertical planking)

#### 3.7.4 Cabinet-Specific Trim

- Light rail moulding (under wall cabinets)
- Scribe moulding (filler strips)
- Cabinet crown moulding (smaller scale than room crown)
- Decorative corbels (modeled brackets under countertop overhangs)
- Turned posts / pilasters (modeled, placed at cabinet run ends)
- Valance (above sink window, between wall cabinets)
- Toe kick cap moulding

#### 3.7.5 Casing & Trim

- Door/window casing profiles (multiple styles matching the moulding family)
- Rosette blocks (corner blocks where casing meets — modeled)
- Plinth blocks (base of door casing — parametric)

**Implementation approach:** Create a MouldingProfile library as a collection of Blender curve objects. Each profile is a 2D cross-section curve. The generator creates a sweep path (along wall-ceiling intersection for crown, along wall-floor for base, etc.) and uses Blender's curve bevel/taper or Geometry Nodes Curve to Mesh to generate the 3D geometry. Swapping profiles = swapping the entire moulding style. Consider organizing into "style families" (Colonial, Craftsman, Modern, Traditional) where each family is a coordinated set of crown + base + casing + cabinet trim profiles.

### 3.8 Walls, Floors & Ceilings

#### 3.8.1 Wall Construction (Parametric)

Inherited from Home Builder's wall system, with enhancements:
- Standard stud wall with drywall
- Half-wall / pony wall (with optional cap)
- Accent wall (material variant)
- Wainscoted wall (lower panel + upper surface)
- Open shelving wall section

#### 3.8.2 Flooring (Material Library — Shader Based)

Flooring is primarily a materials/shader problem rather than a geometry problem, except for individual plank/tile geometry when close-up shots need parallax.

- Hardwood planks (various species, plank widths, patterns: straight, herringbone, chevron)
- Tile (ceramic/porcelain — square, rectangular, hexagonal)
- Natural stone (marble, slate, travertine — larger format)
- Luxury vinyl plank (LVP)
- Concrete (polished, stained)
- Brick (running bond, herringbone)

#### 3.8.3 Ceiling

- Flat drywall (standard)
- Tray ceiling (stepped)
- Coffered ceiling (grid of beams — parametric)
- Exposed beam ceiling (parametric beam spacing/dimensions)
- Tongue-and-groove plank ceiling
- Vaulted/cathedral (wall angle parameter)

### 3.9 Lighting Fixtures

Lighting has dual importance: the fixture as a visible object, and the light it emits affecting the render.

#### 3.9.1 Kitchen-Specific (Modeled or Sourced)

- Under-cabinet LED strip (parametric — length adjustable)
- Under-cabinet puck lights (parametric — array)
- Pendant lights (over island — modeled, 5–8 style variants)
- Recessed can lights (parametric — simple cylinder + trim ring)
- Track lighting (parametric rail + modeled heads)
- Flush-mount ceiling fixture
- Semi-flush-mount

#### 3.9.2 General Interior

- Chandelier (2–3 styles, modeled)
- Sconce / wall-mounted (2–3 styles)
- Table/floor lamp (decorative, sourced CC0)

**Commercial tier strategy for pendants/chandeliers:** Commission 5–8 pendant light designs that span modern, transitional, and traditional styles. These are high-visibility items that sell the scene realism. Alternatively, Poly Haven occasionally publishes light fixture models under CC0.

### 3.10 Bathroom Fixtures

Home Builder includes these, so your system should match at minimum.

- Toilet (one-piece, two-piece, wall-hung)
- Vanity (essentially a cabinet variant with sink cutout — handled by cabinet generator)
- Bathroom sink (undermount, vessel, pedestal, wall-hung)
- Bathtub (alcove, freestanding, corner)
- Shower (walk-in, tub/shower combo, corner)
- Shower fixtures (head, handle, door/glass panel)
- Bathroom faucets (widespread, single-hole, wall-mount)
- Mirror (framed, frameless — parametric)
- Towel bar / ring / hook
- Toilet paper holder

### 3.11 Decorative / Scene-Dressing

These are the items that make renders look lived-in and realistic. They don't need to be parametric — static mesh with good materials is sufficient. Poly Haven CC0 models are excellent for this category.

- Plants / potted herbs
- Books / cookbooks
- Vases
- Fruit / food items
- Dishes / plates / bowls
- Glassware
- Candles
- Picture frames
- Clocks
- Rugs / runners
- Bar stools / dining chairs
- Dining table

---

## 4. PBR Material Library — Procedural-First Approach

### 4.0 Core Philosophy: Everything Lives Inside Blender

The material library is built on a procedural-first principle: every material should be a Blender shader node group with exposed parameters, not an external image texture file that Blender references. This approach provides several critical advantages for a parametric generator system.

**Why procedural over texture maps:**

Procedural materials are resolution-independent — they look sharp at any zoom level without needing 4K or 8K texture files. They carry zero file size overhead beyond the node group definition itself, which means the addon stays small and distributable. Their parameters (color, grain scale, vein intensity, roughness, etc.) can be driven programmatically by the generators via Python, enabling the one-click style swap functionality where the kitchen generator changes a wood species or stain color across every cabinet in the scene by updating node group inputs. They also avoid the UV dependency problem: parametrically generated geometry doesn't always have clean UV maps, but procedural shaders work with object-space or generated coordinates and don't care.

**Where image textures are still acceptable:**

Some materials are genuinely difficult to replicate procedurally with photorealistic results, particularly natural stone with complex organic veining (marble, granite), exotic wood species with highly specific character, and any material where a specific real-world product match is needed. For these cases, the private/ZDC tier can use captured or sourced image textures freely. For the commercial tier, image textures should only be used when procedural results are demonstrably insufficient, and they must come from CC0 sources or be self-captured. Even then, wrapping image textures inside a node group with exposed parameters (tint, scale, rotation, roughness adjustment) keeps the interface consistent with the rest of the procedural library.

**Node group as the universal interface:**

Every material in the library — whether fully procedural or image-backed — should be packaged as a Blender node group with a standardized set of exposed inputs. This is the API contract between the library and the generators. The generators don't need to know or care whether a material is procedural or texture-based; they just set parameters on the node group.

Standard exposed inputs for all material node groups:
- **Color / Tint** (Color) — Base color or tint multiplier
- **Roughness Adjust** (Float, 0–1) — Global roughness offset
- **Scale** (Float) — Pattern/grain scale factor
- **Rotation** (Float, 0–360) — Pattern/grain rotation
- **Bump Strength** (Float) — Surface detail intensity
- **Object Info Random** (Boolean) — Per-object variation toggle

### 4.1 Material Categories

#### 4.1.1 Wood Species (Cabinet Primary)

Wood is the most important material category for the kitchen generator and the one that benefits most from the procedural approach. Blender's Noise, Musgrave (in 4.x) / Gabor Noise (in 5.0), and Wave textures can produce convincing wood grain when properly layered.

**Procedural wood shader architecture:**
The core wood shader should be a single master node group with parameters that control species-specific characteristics: grain tightness, ray fleck presence (for quarter-sawn oak), knot frequency, color variation range, heartwood/sapwood contrast, and figure pattern. Individual "species presets" are then just saved parameter combinations applied to this one master shader, not separate node groups.

**Natural/Stained Woods (all procedural, parameter-driven from a single master wood shader):**
- White Oak (quarter-sawn, plain-sawn)
- Red Oak
- Maple (hard)
- Cherry
- Walnut
- Hickory
- Birch
- Alder
- Ash
- Pine / Knotty Pine
- Bamboo

**Finish variants for each species:**
- Natural/clear coat
- Light stain
- Medium stain
- Dark stain
- Whitewashed/cerused
- Gray stain
- Ebonized

**Painted finishes (no grain — flat or slight texture):**
- White (multiple shades — pure, antique, linen)
- Black
- Navy
- Sage green
- Gray (multiple values)
- Cream/warm white
- Custom color (HSV adjustable)

#### 4.1.2 Countertop Materials

Countertops are the most challenging category for the procedural-first approach because natural stone veining has organic complexity that's difficult to replicate purely with noise functions. The strategy here is to push procedural as far as possible and flag specific materials that may need Tier 2/3 image supplements.

**Natural Stone (Tier 2–3 — procedural base with possible image supplement for hero renders):**
- Carrara marble (white with gray veining) — Voronoi + Noise combo can approximate veining; Tier 2 for close-ups
- Calacatta marble (white with gold veining) — similar approach, color ramp adjustment
- Granite — multiple colors (absolute black, giallo ornamental, bianco antico, blue pearl, ubatuba) — Voronoi at multiple scales replicates speckle well; most granites are achievable as Tier 1 procedural
- Soapstone (dark gray-green) — subtle veining, very achievable procedurally
- Quartzite (Taj Mahal, Super White) — complex veining, likely Tier 2

**Engineered/Manufactured (Tier 1 — fully procedural):**
- Quartz (Caesarstone/Silestone inspired — solid colors, veined patterns) — engineered quartz is actually easier to replicate procedurally than natural stone since patterns are more uniform
- Solid surface (Corian-like — uniform matte) — trivially procedural, nearly flat color
- Laminate (various patterns) — procedural for solid colors; patterned laminates may need images
- Concrete (polished, matte, various colors) — Noise + subtle speckle, fully procedural

**Wood Countertops:**
- Butcher block (end-grain, edge-grain)
- Live edge slab

**Metal:**
- Stainless steel (brushed)
- Zinc (patina)
- Copper (patina stages)

#### 4.1.3 Metal Finishes (Hardware & Fixtures)

All metal finishes are Tier 1 — fully procedural. Metals are among the easiest materials to create procedurally because they're defined primarily by their Metallic (1.0), base color, and roughness values, with subtle anisotropic scratching patterns generated by noise nodes. A single master metal shader node group with exposed Color, Roughness, and Scratch Pattern parameters covers every variant below.

- Brushed nickel
- Polished chrome
- Satin brass
- Antique brass
- Oil-rubbed bronze
- Matte black
- Polished gold
- Copper (polished, patina)
- Stainless steel (brushed, polished)
- Pewter/gunmetal
- Champagne bronze

These are applied to any handle, faucet, or fixture geometry by the generators. The generator selects a metal preset from `metal_presets.py` and applies the parameters to the master metal node group.

#### 4.1.4 Glass

All glass variants are Tier 1 — fully procedural. Blender's Glass/Principled BSDF with Transmission handles these natively. A single master glass node group with Tint Color, Roughness (frosted), and Seed Pattern (for seeded glass via noise displacement) parameters covers all variants.

- Clear
- Frosted
- Seeded
- Textured/reeded
- Tinted (gray, bronze, blue)
- Leaded (with mullion geometry — the geometry is separate; glass shader stays simple)

#### 4.1.5 Tile / Ceramic

- Glazed ceramic (various colors, gloss levels)
- Porcelain (matte, polished)
- Natural stone tile (marble, travertine, slate)
- Glass tile
- Handmade/zellige (irregular surface)
- Cement/encaustic (patterned)

#### 4.1.6 Wall Finishes

- Painted drywall (matte, eggshell, semi-gloss — various colors)
- Wallpaper/textured wall (2–3 subtle patterns)
- Shiplap/beadboard (white painted wood)
- Exposed brick
- Plaster (smooth, Venetian/textured)

#### 4.1.7 Flooring (Expanded from 3.8.2)

- Hardwood (species from wood list above, in plank format)
- Tile patterns (from backsplash list, scaled for floor)
- Stone
- Concrete
- LVP

### 4.2 Material Organization Principles

**Naming Convention:** `{Category}_{Material}_{Variant}_{Finish}`  
Examples: `Wood_Oak_QuarterSawn_NaturalClear`, `Stone_Marble_Carrara_Polished`, `Metal_Brass_Satin`

**Node Group Packaging:**
Every material ships as a Blender node group stored in a .blend library file. Generators append/link these node groups by name. The naming convention above doubles as the node group name, making programmatic access straightforward: `bpy.data.node_groups["Wood_Oak_QuarterSawn_NaturalClear"]`.

**Procedural Feasibility Tiers:**

Tier 1 — Fully Procedural (no external files): Painted finishes, metals, glass, solid colors, concrete, simple fabrics, and most wood species. These should compose the majority of the commercial library.

Tier 2 — Procedural with Enhancement (optional image overlay): Complex wood species where grain character is very specific, handmade/artisanal tile with irregular glaze. The procedural base gets you 80% there; an optional image texture layer adds the last 20% of realism for hero close-ups. The shader should still work and look good without the image layer present.

Tier 3 — Image-Dependent (private tier, or CC0 images for commercial): Natural stone with complex veining (marble, granite), exotic or photomatched materials, wallpaper patterns, encaustic/patterned tile. These genuinely need image data to be convincing. For the commercial tier, source images from CC0 libraries (Poly Haven, AmbientCG) and embed them in the .blend library file. For the private tier, use your cross-polarized captures or sourced textures freely.

**Material Preset System:**
For the master wood shader and similar parameterized materials, store species/variant presets as Python dictionaries or JSON that the generator reads and applies. This keeps the node group count manageable (one master wood shader instead of 77 individual node groups for every species × finish combination) and makes adding new presets trivial.

```python
# Example: Wood species presets consumed by generators
WOOD_PRESETS = {
    "oak_quartersawn_natural": {
        "grain_scale": 12.0,
        "grain_tightness": 0.7,
        "ray_fleck": 0.8,
        "base_color": (0.45, 0.32, 0.18),
        "color_variation": 0.15,
        "roughness": 0.4,
        "knot_frequency": 0.02,
    },
    "walnut_natural": {
        "grain_scale": 8.0,
        "grain_tightness": 0.5,
        "ray_fleck": 0.0,
        "base_color": (0.25, 0.15, 0.08),
        "color_variation": 0.25,
        "roughness": 0.35,
        "knot_frequency": 0.01,
    },
    # ... etc
}
```

### 4.3 Material Sourcing Strategy

**Primary approach: Build procedural shaders in Blender.** This is the default for every material category. The effort invested in building a strong master wood shader, master stone shader, master metal shader, etc. pays compounding returns as new presets are just parameter tuning rather than new development.

**CC0 image textures as procedural supplements (commercial tier):** When a procedural shader needs an image layer for added realism (Tier 2 and Tier 3 materials), source from Poly Haven, AmbientCG (ambientcg.com), or cgbookcase.com. These are all CC0 with no restrictions. Pack the image into the .blend library file so there are no external file dependencies. Use these sparingly — each packed image adds to the addon file size, and the procedural-first philosophy means they should be the exception rather than the rule.

**Self-captured materials (competitive advantage):** Your cross-polarized photography setup and material capture workflow can produce reference photos that inform procedural shader tuning, or in cases where photorealism demands it, can be processed into texture maps for the private tier. For the commercial tier, captures can serve as reference targets that you tune your procedural shaders to match — "this procedural walnut shader was tuned to match a real walnut sample" is a quality differentiator without any image file dependency.

**Procedural shader development resources:** The Blender community has extensive documentation on procedural material techniques. Key references include: Ryan King Art's procedural material tutorials (YouTube), Blender Guru's shader fundamentals, and the Blender Manual's shader nodes documentation. The Cycles shader node set provides everything needed: Noise, Voronoi, Wave, Gabor Noise (5.0+), Musgrave (4.x), and math nodes for combining them.

---

## 5. Sourcing Summary by Strategy

### 5.1 Self-Created / Parametric (Highest Priority)

These components are the core value proposition and differentiation. They also carry zero licensing risk.

- All cabinet box types and construction variants
- All cabinet door styles (curve profile library)
- Simple/geometric handle styles (bar pulls, edge pulls, square knobs)
- All moulding/trim profiles (2D curve library)
- Countertop edge profiles (2D curve library)
- All window types and variants
- All interior door types
- Backsplash tile patterns (GN or shader)
- Under-cabinet lighting, recessed cans
- All procedural materials: wood species master shader + presets, painted finishes, metal finishes, glass, concrete, solid surface, tile glaze, drywall/plaster, basic fabric
- Procedural stone shaders (marble veining, granite speckle — may need Tier 2 image supplement for hero close-ups)

### 5.2 CC0 Sources (Supplement)

Free, no licensing risk. Used primarily for decorative geometry and as optional image texture supplements for Tier 2/3 procedural materials.

- **Poly Haven Models:** Decorative objects, select furniture, HDRIs for lighting
- **Poly Haven / AmbientCG / cgbookcase Textures:** CC0 image textures for packing into Tier 2/3 material node groups where procedural alone isn't sufficient. Used sparingly and packed into .blend files — no external file dependencies.
- **Poly Haven HDRIs:** Environment lighting presets for the kitchen generator's rendering setup

### 5.3 Commissioned (Fill Gaps for Commercial Tier)

Budget these as a product development cost. Target assets that are high-visibility, complex geometry that can't be parametrically generated, and would significantly elevate the library quality.

**Priority commissions (estimated budget: $1,500–3,000 total):**
- 10–15 ornate cabinet knobs and decorative pulls ($30–80 each)
- 6–8 faucet models spanning modern/traditional ($50–120 each)
- 5–8 pendant light fixtures ($40–80 each)
- 4–6 kitchen sink variants including farmhouse ($40–80 each)
- 2–3 pro-style range/range hood combos ($80–150 each)

**Where to commission:**
- Fiverr / Upwork (budget tier, quality varies — vet portfolios carefully)
- CGTrader "Custom Order" feature (mid-tier, artists already understand commercial 3D)
- ArtStation / Blender Artists Forum (higher tier, find archviz specialists)
- Direct outreach to Blender archviz artists on social media

**Contract requirements:** Work-for-hire agreement with full IP transfer. The deliverable must include source .blend files with clean topology, proper UV unwrapping, and real-world scale. Materials on commissioned models should either be procedural node groups or use the library's standard material node groups applied to the geometry — avoid baked texture maps that would need to ship with the addon. You must own all rights to redistribute.

### 5.4 Marketplace Purchases (Private/ZDC Tier Only)

For immediate production use on Rev-A-Shelf and client work. These assets never ship with the public addon.

- TurboSquid handle/knob bundles for variety in client renders
- CGTrader appliance models (brand-specific where needed)
- Evermotion archviz asset packs (kitchen scenes, props)

---

## 6. Implementation Priority

The goal is to get functional libraries operational as quickly as possible while building the long-term parametric system. This priority order front-loads the components that make the biggest visual impact with the least development time.

### Phase 1: Foundation (Weeks 1–4)

**Goal:** Basic functional kitchen generation with style-swappable procedural materials. Library infrastructure integrates with the kitchen/cabinet generator repos.

1. **Library infrastructure & generator integration** — Set up the asset library directory structure and .blend library file format. Define the interface contract between generators and the library: how generators query for assets, how material node groups are applied, how profile curves are consumed. Establish the commercial/private tier separation with `.gitignore` rules. Ensure the library repo can be cloned/symlinked as a dependency of both cabinet-generator and kitchen-generator.

2. **Cabinet door profile curve library** — Create 10–15 2D curve profiles covering Shaker, flat slab, raised panel, and recessed panel styles. These curves feed the cabinet generator's door creation functions.

3. **Core procedural materials** — Build the foundational shader node groups inside Blender:
   - Master wood shader node group with exposed species/stain parameters, plus 8–10 initial species presets (stored as Python dicts that generators apply)
   - 5+ painted finish node group (single parameterized shader — color, sheen, texture)
   - Master metal finish node group with presets for brushed nickel, chrome, matte black, satin brass, oil-rubbed bronze, champagne bronze
   - Basic stone node group (initial version — may need image supplement later for marble)
   - Glass shader node group (clear, frosted, seeded variants via parameters)

4. **Basic parametric handles** — Create 5–6 bar pull variants and 2–3 knob shapes that cover 80% of modern/transitional kitchens. Apply the metal finish node group to demonstrate the material swap workflow.

### Phase 2: Completeness (Weeks 5–8)

**Goal:** Cover all major kitchen elements. Scene renders look complete and professional. Generator-to-library API is proven and stable.

5. **Moulding profile library** — Create curve profiles for crown, base, cabinet trim. Organize into 3 style families (Modern, Transitional, Traditional). Ensure the moulding generator can consume these profiles via the library API.

6. **Countertop edge profiles** — 8–10 profile curves, consumed by the kitchen generator's countertop creation logic.

7. **Window and door parametric system** — Build the generators with initial style variants.

8. **Appliances (generic)** — Model or source 5–6 core appliances: refrigerator, range, dishwasher, microwave, range hood. These can be simpler initially and refined later.

9. **Sink + basic faucet** — At minimum one undermount sink and one pull-down faucet for functional kitchen renders.

### Phase 3: Polish & Depth (Weeks 9–16)

**Goal:** Library depth approaches professional archviz toolset quality. Ready for commercial release consideration. Generators can produce complete, style-consistent kitchens.

10. **Commission ornate hardware** — Get the decorative knobs, faucets, and pendant lights from contracted artists. Ensure delivered models use the library's procedural material node groups rather than baked textures.

11. **Backsplash pattern system** — Implement tile patterns via GN or shader, integrated with the kitchen generator's backsplash placement logic.

12. **Expand procedural materials** — Deepen the master wood shader with more species presets and refine realism. Develop a dedicated procedural marble/granite shader or evaluate whether CC0 image supplements (packed into .blend) are needed for Tier 3 stone materials. Add more stain, glaze, and patina variants to the metal shader.

13. **Decorative/scene-dressing items** — Curate CC0 models from Poly Haven, organize into the decoration library.

14. **Bathroom fixtures** — Extend the system to handle bathroom vanities, toilets, tubs.

15. **Flooring system** — Material-based flooring with optional geometry for close-up shots.

16. **Window treatments** — Blinds, shades, basic curtains.

### Phase 4: Differentiation (Ongoing)

**Goal:** Features and library depth that exceed Home Builder and competing tools. The generator + library system is a polished, sellable product.

17. **Advanced procedural materials** — Leverage your cross-polarized photography setup to capture reference samples, then tune procedural shaders to match real-world materials. This "procedural-matched-to-real" approach is a strong differentiator — no texture files ship, but the results are tuned against real samples.

18. **Advanced lighting** — More fixture variety, IES light profiles for accurate fixture-specific light distribution. Integrate with the kitchen generator's lighting placement logic.

19. **Specialty cabinets** — Corner solutions, appliance garages, butler's pantry configurations. These extend the cabinet generator's vocabulary using library profile curves and hardware.

20. **Style presets** — One-click "kitchen style" presets that coordinate door style + hardware + moulding + countertop + backsplash into curated combinations (e.g., "Modern Farmhouse," "Contemporary Minimalist," "Traditional Colonial"). These are the capstone feature that ties the generators and library together — the kitchen generator reads a preset definition, then pulls the correct profile curves, geometry assets, and material presets from the library to build a cohesive kitchen in one operation.

---

## 7. Handle Styles Reference — Complete Taxonomy

Since handles were your original question, here's the exhaustive reference list organized by type. This is the full scope of what the handle library should eventually cover.

### 7.1 Bar / Pull Handles
1. Round bar pull — straight, round cross-section
2. Square bar pull — straight, square cross-section
3. Flat bar pull — straight, rectangular/flat cross-section
4. D-ring pull — curved D-shape, round cross-section
5. D-ring flat pull — curved D-shape, flat cross-section
6. Bow pull — gentle arc, round cross-section
7. Wire pull — thin gauge wire, various curves
8. T-bar pull — horizontal T with vertical post mount
9. Oversized/appliance pull — 12", 18", 24" lengths
10. Tubular pull — hollow tube, visible end caps
11. Tapered pull — thicker at center, thinner at mounts
12. Arch pull — pronounced arch shape

### 7.2 Cup / Bin Pulls
13. Classic bin pull — half-cylinder shell
14. Flat-bottom cup pull — squared-off bottom
15. Mission cup pull — simple angular form
16. Decorative cup pull — scrollwork or cast detail

### 7.3 Knobs
17. Round mushroom knob — hemisphere
18. Round ball knob — full sphere
19. Flattened/disc knob — low-profile round
20. Square knob — cubic/rectangular
21. Faceted knob — geometric faces (hex, octagonal)
22. Turned/traditional knob — lathe-turned profile with rings
23. Porcelain round knob — smooth ceramic look
24. Crystal/glass knob — transparent with facets
25. Acorn knob — tapered dome shape
26. Cabinet ring pull with backplate — hanging ring

### 7.4 Edge / Integrated Pulls
27. Routed finger pull — groove milled into door edge
28. Tab pull — small protruding tab at door top/bottom
29. Channel/J-pull — aluminum channel along door edge
30. Lip pull — small angled lip at door bottom
31. Recessed pull — flush rectangular cutout in door face
32. Push-to-open — no visible hardware, mechanism only

### 7.5 Specialty / Decorative
33. Ring pull — hanging ring with decorative backplate
34. Drop pull — hanging teardrop/pendant shape
35. Bail pull — curved wire bail with post mounts (dresser-style)
36. Latch pull — thumb latch / catch style
37. Backplate + knob combo — ornate backplate behind simple knob
38. Leather strap pull — leather loop with metal mounts

---

## 8. Directory Structure Recommendation

The library is structured as an independent repository that the kitchen-generator and cabinet-generator repos reference as a dependency (via git submodule, symlink, or Blender addon dependency). This keeps the library versioned and distributable separately from the generators while ensuring both generators draw from the same asset pool.

```
component-library/                     # Standalone repo, dependency of generators
├── README.md
├── CLAUDE.md                          # Agent context for development
├── __init__.py                        # Blender addon registration (library browser UI)
├── library_api.py                     # Python interface for generators to query assets
├── presets/                           # Parameter preset definitions (Python/JSON)
│   ├── wood_presets.py                # Species + finish parameter combos
│   ├── metal_presets.py               # Hardware finish parameter combos
│   ├── stone_presets.py               # Countertop stone parameter combos
│   └── style_presets.py               # Full kitchen style definitions
├── blend_libraries/                   # .blend files containing node groups & assets
│   ├── materials.blend                # All procedural material node groups
│   ├── handles.blend                  # Handle geometry assets
│   ├── sinks_faucets.blend
│   ├── appliances.blend
│   ├── lighting.blend
│   ├── bathroom.blend
│   └── decorations.blend
├── profiles/                          # .blend files containing 2D curve profiles
│   ├── door_profiles.blend            # Cabinet door style curves
│   ├── moulding_profiles.blend        # Crown, base, casing, cabinet trim curves
│   └── countertop_edges.blend         # Countertop edge profile curves
├── commercial/                        # Clean-licensed assets for public release
│   ├── (mirrors blend_libraries/ and profiles/ structure above)
│   └── ...
└── private/                           # ZDC internal only, .gitignored
    ├── rev_a_shelf/
    ├── branded_appliances/
    ├── marketplace_purchases/
    ├── image_textures/                # Tier 3 image-backed materials for ZDC renders
    └── client_specific/

# In the generator repos:
cabinet-generator/
├── ...
├── deps/
│   └── component-library/             # Git submodule or symlink
└── ...

kitchen-generator/
├── ...
├── deps/
│   └── component-library/             # Git submodule or symlink
└── ...
```

The `private/` directory should be in `.gitignore` and never committed to the public repository.

**Note on .blend library files:** Rather than hundreds of individual .blend files, group related assets into consolidated library files (e.g., all handles in one `handles.blend`, all procedural material node groups in one `materials.blend`). This reduces file count, simplifies distribution, and makes append/link operations faster. The generators query assets by name within these library files via `library_api.py`.

---

## 9. Open Questions / Future Decisions

1. **Asset Browser vs. Custom Panel** — Blender 5.0's asset browser is maturing but has limitations for parametric assets. A custom sidebar panel (like Home Builder's approach) gives more control over the UI/UX but requires more development. This choice affects how the library presents assets to users and how the generators' UI exposes library selections.

2. **Geometry Nodes version management** — GN trees stored in .blend files are difficult to version-control. Consider storing them in dedicated .blend library files with a clear naming convention, and using Python scripts to link/append them at runtime. The same concern applies to procedural material node groups — all node groups live in .blend files, so the `materials.blend` library file becomes a critical versioned artifact.

3. **Library dependency management** — How should the cabinet-generator and kitchen-generator repos reference the component-library repo? Options include git submodules (explicit versioning but sometimes painful UX), git subtree (embedded copy), symlinks (development convenience but not portable), or a Python package-style install. The choice affects how updates to the library propagate to both generators and how end users install the commercial product.

4. **Style preset system** — The one-click kitchen style swap is a major selling feature and the primary integration point between generators and library. Needs a data structure that maps a style name to specific choices for every component category (door profile + hardware + moulding + countertop material preset + backsplash + metal finish preset, etc.). This should be designed early even if fully populated later, because it defines the contract between generators and library.

5. **Procedural material quality benchmarking** — The procedural-first approach is architecturally superior but needs quality validation. Early in Phase 1, build the master wood shader and compare it side-by-side against image-textured wood at typical kitchen render distances and close-ups. Establish a quality bar that determines when procedural is "good enough" vs. when an image supplement is warranted. This benchmarking informs how much effort to invest in Tier 2/3 image supplements.

6. **ComfyUI integration** — Your existing ComfyUI work could potentially be used for AI-assisted procedural shader development (generating reference images to tune shaders against) or for post-render enhancement, but that's a later-phase consideration.

7. **Home Builder fork scope** — Clarify the boundary between what lives in the Home Builder fork (wall system, room layout, asset browser UI, placement logic) versus what lives in the generator repos and component library. The fork handles the architectural shell and user interaction; the generators handle parametric creation of specific element types; the library provides the raw ingredients. This three-layer separation needs to be explicit so development effort isn't duplicated.
