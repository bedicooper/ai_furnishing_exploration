# Furniture Schema Reference

Quick reference for furniture JSON structure.

## Schema Overview

```json
{
  "id": "b1",
  "block_id": "APLUS_LOZKO_POJEDYNCZE",
  "category": "basic",
  "phase": "Phase 0",
  "layer_index": 2,
  "insert_point_type": "universal",
  "default_x_length": 200,
  "default_y_length": 100,
  "background_svg": "M193 0A7 7...",
  "contour_svg": "M5 -13v-74...",
  "clash_detection_boundary": [[200,-100],[0,-100],[0,0],[200,0]],
  "access_area_boundary": [
    [[130,0],[130,60],[70,60],[70,0]],
    [[130,-100],[130,-160],[70,-160],[70,-100]]
  ]
}
```

---

## Fields

### `id` (string)
- Unique furniture identifier
- Used in apartment JSON equipments/caseworks
- Examples: `"b1"`, `"b2"`, `"sz"`, `"wc"`

### `block_id` (string)
- Human-readable furniture name
- Examples: `"APLUS_LOZKO_POJEDYNCZE"` (single bed)

### `category` (string)
- Furniture category/group
- **Enum values**: `["sanitary", "basic", "additional", "accessory", "door", "window", "greenery", "symbol"]`
- Examples: `"basic"` (bed), `"sanitary"` (toilet), `"door"`, `"window"`
- Use: Filtering, organization, semantic rules

### `phase` (string)
- Project phase identifier
- Examples: `"Phase 0"`, `"Phase 1"`
- Use: Version control, rollout stages

### `layer_index` (int)
- **Vertical collision layer / SVG render priority**
- **Official levels**:
  - `1` - floor (e.g., carpet)
  - `2` - under counter (e.g., chairs)
  - `3` - countertop (e.g., table top)
  - `4` - on counter (e.g., stove, fridge, sink, dishwasher)
  - `5` - above counter (e.g., upper cabinets, wardrobe, paintings)
  - `6` - ceiling (e.g., ceiling lighting)
- **Rule**: Lower layer can be underneath higher layer (chair {2} under table {3})
- Use: 3D collision detection, SVG rendering order

### `insert_point_type` (enum)
- **Values**: `["wall_based", "universal", "opening", "standalone"]`
- **Defines placement logic**:

| Type | Description | Examples | Placement Logic |
|------|-------------|----------|-----------------|
| `wall_based` | Needs wall | Wall cabinets, radiators | Find wall, attach |
| `universal` | Anywhere | Beds, tables, sofas | Free placement |
| `opening` | Doors/windows | Doors, windows | **Skip! Don't place** |
| `standalone` | Free-standing | Chairs, lamps | Center/near furniture |

### `default_x_length` (float)
- **Width in centimeters**
- Example: `200` = 200cm = 2.0m

### `default_y_length` (float)
- **Height/depth in centimeters**
- Example: `100` = 100cm = 1.0m

### `background_svg` (string)
- SVG path for furniture outline
- Example: `"M193 0A7 7 0 0 0 200 -7v-86..."`
- Use: Visualization, detailed geometry

### `contour_svg` (string)
- SVG path for furniture contour/details
- Example: `"M5 -13v-74h42v74z..."`
- Use: Visualization

### `clash_detection_boundary` (array)
- **Collision polygon**
- **Coordinates RELATIVE to insert point**
- Format: `[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]`
- Example: `[[200,-100],[0,-100],[0,0],[200,0]]`
- Use: **Stage 2 collision detection** 🎯

### `access_area_boundary` (array of arrays OR null)
- **Required clearance zones**
- **Can be null** (some furniture doesn't require access zones)
- **Coordinates RELATIVE to insert point** (cardinal system)
- Format: `[[[x1,y1],...], [[x1,y1],...]]` (multiple zones)
- Example: Access on both sides of bed
- Use: Validate human can reach furniture (advanced feature)

### `in_compartments` (array of strings OR null)
- **Room restriction list**
- Furniture appears only in specified compartment IDs
- Can be null (no restriction)
- Example: `["idBathroom", "idWC"]` - toilet only in bathrooms
- Use: Semantic validation, filter furniture by room type

---

## Important Notes

### 1. Relative Coordinates & Cardinal System
⚠️ **All boundaries are RELATIVE to insert_point!**
⚠️ **Cardinal coordinates**: +x right, -x left, +y up, -y down

```
In room JSON:
  "insert_point": [1086, 190]

In furniture JSON (cardinal coords):
  "clash_detection_boundary": [[200,-100],[0,-100],[0,0],[200,0]]
  # 0,0 is at insert_point
  # +x = right, -x = left, +y = up, -y = down
  
Actual position in room:
  boundary_in_room = translate(clash_boundary, insert_point)
  = [[1286, 90], [1086, 90], [1086, 190], [1286, 190]]

Note: SVG rendering uses transform="scaleY(-1)" for browser display
```

### 2. Filter Openings
```python
# Don't place furniture with type="opening"
if furniture["insert_point_type"] == "opening":
    skip()  # Already in apartment (doors/windows)
```

### 3. Layer Index (Future)
```python
# Advanced: Layer-aware collision
def check_collision(furn1, furn2):
    if furn1["layer_index"] == furn2["layer_index"]:
        return check_polygon_overlap(furn1, furn2)
    else:
        return False  # Different layers, no collision

# Example: chair (2) can go under table (3)
chair = {"id": "k", "layer_index": 2}  # under counter
table = {"id": "st", "layer_index": 3}  # countertop
check_collision(chair, table)  # False - different layers OK!

# Official layer mapping:
# 1=floor, 2=under counter, 3=countertop, 
# 4=on counter, 5=above counter, 6=ceiling
```

---

## Usage in Project

### Stage 1 (Semantic Model)
```python
# Only needs ID
furniture_ids = ["b1", "sz", "wardrobe"]
```

### Stage 2 (Geometric Placement)
```python
# Full furniture info needed
furniture = catalog["b1"]

# Get dimensions
width = furniture["width"]   # meters
height = furniture["height"]

# Get collision boundary (relative to insert_point)
clash_boundary = furniture["clash_boundary"]

# Transform to room coordinates
# Step 1: Translate - move furniture to room position
room_insert = apartment_json["insert_point"]  # [1086, 190]
angle = apartment_json["angle"]  # 90
x_scale = apartment_json.get("x_scale", 1)  # 1.0
y_scale = apartment_json.get("y_scale", 1)  # 0.89

# Step 2: Apply transformations (order matters!)
# 1. Scale (if x_scale/y_scale != 1)
# 2. Rotate (around insert_point)
# 3. Translate (to room_insert position)
boundary_in_room = transform(
    clash_boundary,
    scale=(x_scale, y_scale),
    rotate=angle,
    translate=room_insert
)

# Check collision
if not collides(boundary_in_room, room_walls):
    place_furniture(furniture, room_insert, angle, x_scale, y_scale)
```

**Transformation order is critical**:
1. **Scale first** - resize furniture if needed
2. **Rotate** - around local origin (0,0)
3. **Translate** - move to final position in room

**Note**: All furniture boundaries are defined relative to insert_point (0,0), so transformations are straightforward.

---

## Examples by Type

### Universal (b1 - Bed)
```json
{
  "insert_point_type": "universal",
  "default_x_length": 200,
  "default_y_length": 100
}
```
- Can place anywhere in room
- Check walls, doors, windows
- Consider access areas

### Wall Based (hypothetical - wall cabinet)
```json
{
  "insert_point_type": "wall_based",
  "default_x_length": 80,
  "default_y_length": 30
}
```
- MUST attach to wall
- Find suitable wall segment
- Check height clearance

### Opening (skip)
```json
{
  "insert_point_type": "opening"
}
```
- ❌ Filter out from placeable catalog
- Already in apartment JSON as doors/windows

### Standalone (hypothetical - chair)
```json
{
  "insert_point_type": "standalone",
  "layer_index": 2
}
```
- Can place in center
- Higher layer_index = can go under table
- Often placed near other furniture

---

## Data Constraints

⚠️ **Confidentiality**: Full furniture catalog not shareable
- Have: Schema + 1 example (`b1.json`)
- Don't have: Complete catalog of all furniture IDs
- Workaround: Work with available apartment data to infer used IDs

---

## Related Files

- `samples/b1.json` - Example furniture definition
- `utils/json_furniture_parser.py` - Parser implementation
- `NOTES_2025_10_02_furniture_jsons.md` - Detailed analysis
- `PRD.md` - Project requirements with constraints


<!--
furniture definition schema 
"equipment": {
    "title": "Equipment",
    "description": "Definiton of equipment in data",
    "type": "object",
    "additionalProperties": false,
    "properties": {
        "id": {
            "title": "Equipment ID",
            "description": "Equipment ID (SVG)",
            "type":"string"
        },
        "block_id": {
            "title": "Autocad Block ID",
            "description": "Autocad Block ID (Name)",
            "type":"string"
        },
        "category": {
            "title": "Equipment category",
            "description": "Equipment category",
            "type": "string",
            "enum": ["sanitary", "basic", "additional", "accessory", "door", "window", "greenery", "symbol"]
        },
        "insert_point_type": {
            "title": "Insert point type",
            "description": "Insert point type
                {standalone}    most cases in bounding-box centroid, eg. table, chair;
                {wall based}    in b-box edge midpoint or corner, eg. sanitary, kitchen;
                {universal}     a catch-all for others, mostly on b-box edge but can be placed against a wall or standalone, eg. some beds, sofas, desks;
                {opening}       mostly for windows in slated roofs(appearing on the plan (above) not in walls);
            ",      
            "type": "string",
            "enum": ["standalone", "wall based", "universal", "opening"]
        },
        "default_x_length": {
            "title": "Default X length",
            "description": "Default X length, b-box dimension",
            "type" : "number",
            "minimum": 0,
            "multipleOf" : 0.01
        },
        "default_y_length": {
            "title": "Default Y length, b-box dimension",
            "description": "Default Y length",
            "type" : "number",
            "minimum": 0,
            "multipleOf" : 0.01
        },
        "layer_index": {
            "title": "Layer index (SVG)",
            "description": "Layer index / element priority on SVG renders.
                floor           {1}    e.g. carpet;
                under counter   {2}    e.g. chairs;
                countertop      {3}    e.g. table top;
                on counter      {4}    e.g. stove, fridge, sink (even under-counter equipment like dishwasher are drawn above in svg);
                above counter   {5}    e.g. upper cabinets, wardrobe, paintings;
                ceiling         {6}    e.g. ceiling lighting;
            ",
            "type": "integer"
        },
        "background_svg": {
            "title": "Equipment background (SVG path)",
            "description": "Equipment background as SVG path (string)
                ATTENTION! this is polyline representation as a svg 'd' string,
                but its not in web browser coordinate system! This still uses
                cardinal coordinates (+x to the right, -x to the left, +y up, -y down)
                For this object to render correctly in browser `transform="scaleY(-1)" is applied
            ",
            "type": "string"
        },
        "clash_detection_boundary": {
            "title": "Equipment clash detection boundary",
            "description": "Equipment clash detection boundary
                boundary point vertices with 0,0 in "insert_point" 
                cardinal coordinates (+x to the right, -x to the left, +y up, -y down)
            ",
            "type": "array",
            "minItems": 3,
            "uniqueItems": true,
            "items": {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "items": {
                    "type": "number",
                    "multipleOf" : 0.01
                }
            }
        },
        },
        "access_area_boundary": {
            "title": "Equipment access area boundary",
            "description": "Equipment access area boundary
                boundary point vertices with 0,0 in "insert_point" 
                cardinal coordinates (+x to the right, -x to the left, +y up, -y down)
            ",
            "oneOf": [
                {"type": "null"},
                {
                    "type": "array",
                    "minItems": 3,
                    "uniqueItems": true,
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "number",
                            "multipleOf" : 0.01
                        }
                    }
                }
            ]
        },
        "in_compartments": {
            "title": "In compartments (IDs) (TODO null???)",
            "description": "Appears only in the specified compartment id.",
            "oneOf": [
                {"type": "null"},
                {
                    "type": "array",
                    "items": {
                        "type":"string"
                    }
                }
            ]
        },
    }
}

-->