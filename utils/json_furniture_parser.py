"""
JSON furniture catalog parser.
Replaces SVG parser - we have structured JSON files instead!

Furniture Schema:
- insert_point_type: ["wall_based", "universal", "opening", "standalone"]
- clash_detection_boundary: relative to insert_point
- access_area_boundary: relative to insert_point
- layer_index: vertical collision layer (e.g., chair can go under table)
"""

import json
from typing import Dict, List, Tuple
from pathlib import Path


# Constants
INSERT_POINT_TYPES = ["wall_based", "universal", "opening", "standalone"]

# Filter: Don't place these types (they're already in apartment JSON)
FURNITURE_TO_SKIP = ["opening"]  # doors, windows


def load_furniture_json(json_path: str) -> dict:
    """Load single furniture definition from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_furniture_dimensions(furniture_data: dict, 
                                scale_factor: float = 1.0) -> Dict[str, float]:
    """
    Extract furniture dimensions from JSON structure.
    
    Args:
        furniture_data: Furniture dict from JSON file
        scale_factor: Conversion factor (default 1.0 = cm, use 0.01 for meters)
        
    Returns:
        {"width": W, "height": H} in specified units
        
    Example:
        >>> data = {"default_x_length": 200, "default_y_length": 100}
        >>> parse_furniture_dimensions(data, scale_factor=0.01)
        {"width": 2.0, "height": 1.0}  # meters
    """
    # Default dimensions are in cm (from your example: 200cm x 100cm)
    width_cm = furniture_data.get("default_x_length", 0)
    height_cm = furniture_data.get("default_y_length", 0)
    
    return {
        "width": width_cm * scale_factor,
        "height": height_cm * scale_factor
    }


def parse_clash_boundary(furniture_data: dict) -> List[List[float]]:
    """
    Extract collision detection boundary.
    
    Returns:
        List of [x, y] points defining collision polygon
        
    Example:
        [[200,-100], [0,-100], [0,0], [200,0]]
    """
    return furniture_data.get("clash_detection_boundary", [])


def parse_access_areas(furniture_data: dict) -> List[List[List[float]]]:
    """
    Extract access area boundaries.
    
    Returns:
        List of polygons (each polygon is list of [x,y] points)
    """
    return furniture_data.get("access_area_boundary", [])


def extract_insert_point_from_svg(background_svg: str) -> Tuple[float, float]:
    """
    Extract insert point from SVG path 'M' command.
    Fallback for when insert_point_type is not clear.
    """
    import re
    m_match = re.search(r'M\s*(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)', 
                       background_svg, re.IGNORECASE)
    
    if m_match:
        return (float(m_match.group(1)), float(m_match.group(2)))
    
    return (0.0, 0.0)


def build_furniture_catalog_from_jsons(json_dir: str, 
                                       scale_factor: float = 0.01,
                                       skip_openings: bool = True) -> Dict[str, Dict]:
    """
    Build furniture catalog from directory of JSON files.
    
    Args:
        json_dir: Path to directory containing furniture JSON files
        scale_factor: Conversion factor (0.01 = cm to meters)
        skip_openings: Skip furniture with insert_point_type="opening" (doors/windows)
        
    Returns:
        Dictionary: {
            "furniture_id": {
                "name": "APLUS_LOZKO_POJEDYNCZE",
                "width": 2.0,  # meters
                "height": 1.0,
                "clash_boundary": [[x,y], ...],  # relative to insert point
                "access_areas": [[[x,y], ...], ...],  # relative to insert point
                "insert_point_type": "universal",  # wall_based/universal/opening/standalone
                "insert_point_offset": (x, y),  # from SVG M command
                "layer_index": 2,  # vertical collision layer
                "category": "basic",
                "background_svg": "M193 0A7..."
            }
        }
        
    Note:
        - clash_detection_boundary is RELATIVE to insert_point
        - Different insert_point_types have different placement logic:
          * wall_based: needs wall attachment
          * universal: can be anywhere
          * opening: doors/windows (usually skip)
          * standalone: free-standing objects
    """
    catalog = {}
    json_path = Path(json_dir)
    
    skipped_openings = 0
    
    for json_file in json_path.glob("*.json"):
        try:
            data = load_furniture_json(json_file)
            furniture_id = data.get("id")
            
            if not furniture_id:
                print(f"⚠️  Skipping {json_file.name}: no 'id' field")
                continue
            
            # Skip openings (doors/windows) if requested
            insert_type = data.get("insert_point_type", "unknown")
            if skip_openings and insert_type == "opening":
                skipped_openings += 1
                continue
            
            dims = parse_furniture_dimensions(data, scale_factor)
            clash_boundary = parse_clash_boundary(data)
            access_areas = parse_access_areas(data)
            
            # Try to get insert point
            background_svg = data.get("background_svg", "")
            insert_offset = extract_insert_point_from_svg(background_svg)
            
            catalog[furniture_id] = {
                "name": data.get("block_id", furniture_id),
                "width": dims["width"],
                "height": dims["height"],
                "clash_boundary": clash_boundary,
                "access_areas": access_areas,
                "insert_point_type": insert_type,
                "insert_point_offset": insert_offset,
                "layer_index": data.get("layer_index", 0),
                "category": data.get("category", "unknown"),
                "phase": data.get("phase", "unknown"),
                "background_svg": background_svg
            }
            
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            continue
    
    if skipped_openings > 0:
        print(f"ℹ️  Skipped {skipped_openings} 'opening' type furniture (doors/windows)")
    
    return catalog


def save_catalog_json(catalog: Dict, output_path: str):
    """Save furniture catalog to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(catalog)} furniture items to {output_path}")


# Quick validation
def validate_furniture_catalog(catalog: Dict):
    """Run basic validation checks on catalog."""
    print("\n" + "=" * 80)
    print("FURNITURE CATALOG VALIDATION")
    print("=" * 80)
    
    print(f"\nTotal furniture items: {len(catalog)}")
    
    # Check dimensions
    valid_dims = sum(1 for f in catalog.values() if f['width'] > 0 and f['height'] > 0)
    print(f"Items with valid dimensions: {valid_dims}/{len(catalog)}")
    
    # Check clash boundaries
    with_clash = sum(1 for f in catalog.values() if f['clash_boundary'])
    print(f"Items with clash_detection_boundary: {with_clash}/{len(catalog)}")
    
    # Check insert point types
    from collections import Counter
    insert_types = Counter(f['insert_point_type'] for f in catalog.values())
    print("\nInsert point types:")
    for itype, count in insert_types.most_common():
        desc = {
            "wall_based": "(needs wall)",
            "universal": "(anywhere)",
            "opening": "(doors/windows)",
            "standalone": "(free-standing)"
        }.get(itype, "")
        print(f"  {itype:15s} {desc:20s}: {count}")
    
    # Check layer indices
    layer_indices = Counter(f['layer_index'] for f in catalog.values())
    print("\nLayer indices (vertical collision layers):")
    for layer, count in sorted(layer_indices.items()):
        print(f"  Layer {layer}: {count} items")
    
    # Size distribution
    widths = [f['width'] for f in catalog.values() if f['width'] > 0]
    heights = [f['height'] for f in catalog.values() if f['height'] > 0]
    
    if widths and heights:
        print("\nDimensions (meters):")
        print(f"  Width:  {min(widths):.2f}m - {max(widths):.2f}m")
        print(f"  Height: {min(heights):.2f}m - {max(heights):.2f}m")
    
    # Categories
    categories = Counter(f['category'] for f in catalog.values())
    print("\nCategories:")
    for cat, count in categories.most_common():
        print(f"  {cat}: {count}")
    
    print("=" * 80)


# Example usage
if __name__ == "__main__":
    # Build catalog from JSON files
    catalog = build_furniture_catalog_from_jsons("../samples/furniture_jsons/")
    
    # Validate
    validate_furniture_catalog(catalog)
    
    # Save
    save_catalog_json(catalog, "../samples/furniture_catalog.json")
