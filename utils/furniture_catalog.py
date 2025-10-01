"""
Furniture catalog - dimensions and metadata for equipment IDs.
To be populated from SVG definitions.

Notes on coordinate system:
- Insert point in JSON = position in room coordinate system
- Insert point references top-left corner of furniture bbox
- Furniture can be rotated (angle) and scaled (x_scale, y_scale)
- SVG coordinates: 1px = 1cm (to be verified)
"""

# TODO: Extract from SVG catalog using svg_parser.py
FURNITURE_DIMS = {
    "b2": {"width": 2.05, "height": 1.5, "name": "double_bed", "category": "bed"},
    "sz": {"width": 0.6, "height": 0.6, "name": "nightstand", "category": "storage"},
    "sh": {"width": 0.9, "height": 0.9, "name": "shower", "category": "bathroom"},
    "wc": {"width": 0.6, "height": 0.7, "name": "toilet", "category": "bathroom"},
    # Add more as you extract from SVG
}

# Semantic rules: room_type -> allowed furniture
ROOM_FURNITURE_RULES = {
    "idBedroom": ["b2", "sz", "wardrobe", "desk", "chair"],
    "idBathroom": ["sh", "wc", "sink", "bathtub"],
    "idKitchen": ["fridge", "stove", "sink", "table", "chair"],
    "idLivingRoom": ["sofa", "tv", "table", "chair", "bookshelf"],
    # Add more room types
}


def get_furniture_dims(furniture_id: str) -> dict:
    """Get dimensions for a furniture ID."""
    return FURNITURE_DIMS.get(furniture_id, {"width": 1.0, "height": 1.0})


def validate_room_furniture(room_type: str, furniture_id: str) -> bool:
    """Check if furniture is semantically valid for room type."""
    allowed = ROOM_FURNITURE_RULES.get(room_type, [])
    return furniture_id in allowed


def extract_from_svg_catalog(svg_path: str) -> dict:
    """
    TODO: Parse SVG catalog and extract furniture definitions.
    
    Args:
        svg_path: Path to SVG file with furniture definitions
        
    Returns:
        Dictionary of {furniture_id: {width, height, paths, ...}}
    """
    raise NotImplementedError("Implement SVG parsing")
