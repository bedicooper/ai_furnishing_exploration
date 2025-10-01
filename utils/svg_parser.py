"""
SVG parser for furniture catalog extraction.
Extracts furniture definitions from SVG file with background paths.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Tuple


# SVG scale factor: 1px = X cm
SVG_SCALE_FACTOR = 1.0  # TODO: Verify this value from your SVG files


def parse_svg_path_bbox(path_d: str) -> Tuple[float, float, float, float]:
    """
    Parse SVG path 'd' attribute and calculate bounding box.
    
    Args:
        path_d: SVG path 'd' attribute string (e.g., "M193 0A7 7...")
        
    Returns:
        (min_x, min_y, max_x, max_y) bounding box
        
    Example:
        >>> parse_svg_path_bbox("M193 0A7 7 0 0 0 200 -7v-86...")
        (0, -100, 200, 0)
    """
    # Extract all coordinate pairs from path commands
    # This is simplified - for production use a proper SVG path parser
    coords = []
    
    # Find M (moveto) and subsequent coordinates
    # Pattern matches numbers (including negatives and decimals)
    numbers = re.findall(r'-?\d+\.?\d*', path_d)
    
    # Convert to floats and pair them (x, y)
    for i in range(0, len(numbers), 2):
        if i + 1 < len(numbers):
            x, y = float(numbers[i]), float(numbers[i + 1])
            coords.append((x, y))
    
    if not coords:
        return (0, 0, 0, 0)
    
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_to_dimensions(bbox: Tuple[float, float, float, float], 
                       scale_factor: float = SVG_SCALE_FACTOR) -> Dict[str, float]:
    """
    Convert bounding box to width/height in centimeters.
    
    Args:
        bbox: (min_x, min_y, max_x, max_y)
        scale_factor: Conversion factor from SVG units to cm
        
    Returns:
        {"width": W, "height": H} in cm
    """
    min_x, min_y, max_x, max_y = bbox
    width_px = max_x - min_x
    height_px = max_y - min_y
    
    return {
        "width": abs(width_px) * scale_factor / 100,  # Convert to meters
        "height": abs(height_px) * scale_factor / 100
    }


def extract_furniture_from_svg(svg_path: str) -> Dict[str, Dict]:
    """
    Extract furniture catalog from SVG file.
    
    Expected SVG structure:
    <svg>
        <g id="b2">  <!-- furniture ID -->
            <path d="..." class="bg" />  <!-- background/outline path -->
            <!-- other elements -->
        </g>
        <g id="sz">
            ...
        </g>
    </svg>
    
    Args:
        svg_path: Path to SVG file with furniture definitions
        
    Returns:
        Dictionary: {
            "furniture_id": {
                "width": float (meters),
                "height": float (meters),
                "bbox": (min_x, min_y, max_x, max_y),
                "path_d": str (original SVG path)
            }
        }
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Handle SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    furniture_catalog = {}
    
    # Find all <g> elements with id attribute (furniture definitions)
    for group in root.findall('.//svg:g[@id]', ns) or root.findall('.//g[@id]'):
        furniture_id = group.get('id')
        
        # Find path with class="bg" (background/outline)
        bg_path = None
        for path in group.findall('.//svg:path[@class="bg"]', ns) or group.findall('.//path[@class="bg"]'):
            bg_path = path.get('d')
            break
        
        # Fallback: use first path if no bg class
        if not bg_path:
            path_elem = group.find('.//svg:path', ns) or group.find('.//path')
            if path_elem is not None:
                bg_path = path_elem.get('d')
        
        if bg_path:
            bbox = parse_svg_path_bbox(bg_path)
            dims = bbox_to_dimensions(bbox)
            
            furniture_catalog[furniture_id] = {
                "width": dims["width"],
                "height": dims["height"],
                "bbox": bbox,
                "path_d": bg_path
            }
    
    return furniture_catalog


def save_catalog_json(catalog: Dict, output_path: str):
    """Save furniture catalog to JSON file."""
    import json
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(catalog)} furniture items to {output_path}")


# Example usage
if __name__ == "__main__":
    # TODO: Update path to your SVG catalog
    svg_file = "path/to/furniture_catalog.svg"
    output_file = "furniture_catalog.json"
    
    catalog = extract_furniture_from_svg(svg_file)
    
    print(f"Extracted {len(catalog)} furniture items:")
    for furn_id, data in list(catalog.items())[:5]:
        print(f"  {furn_id}: {data['width']:.2f}m x {data['height']:.2f}m")
    
    save_catalog_json(catalog, output_file)
