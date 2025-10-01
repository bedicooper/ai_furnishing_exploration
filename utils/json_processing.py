"""
Utility functions for processing apartment JSONs.
"""

import json
from typing import Dict, List, Tuple


def load_apartment_json(json_path: str) -> dict:
    """Load apartment JSON from file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_empty_apartment(apartment_json: dict) -> dict:
    """
    Create empty version of apartment (remove all furniture).
    
    Args:
        apartment_json: Full apartment JSON with furniture
        
    Returns:
        Same JSON but with empty equipments[] and caseworks[]
    """
    empty = apartment_json.copy()
    
    for apartment in empty.get("apartments", []):
        for compartment in apartment.get("compartments", []):
            compartment["equipments"] = []
            compartment["caseworks"] = []
    
    return empty


def extract_furniture_ids(apartment_json: dict) -> Dict[str, List[str]]:
    """
    Extract all furniture IDs from apartment, grouped by room.
    
    Returns:
        {room_name: [furniture_id1, furniture_id2, ...]}
    """
    furniture_by_room = {}
    
    for apartment in apartment_json.get("apartments", []):
        for compartment in apartment.get("compartments", []):
            room_name = compartment.get("name_cad", "unknown")
            
            furniture_ids = []
            
            # Collect equipment IDs
            for eq in compartment.get("equipments", []):
                furniture_ids.append(eq.get("id"))
            
            # Collect casework IDs
            for cw in compartment.get("caseworks", []):
                furniture_ids.append(cw.get("id"))
            
            furniture_by_room[room_name] = furniture_ids
    
    return furniture_by_room


def create_training_pair(apartment_json: dict) -> Tuple[dict, dict]:
    """
    Create (input, output) pair for training.
    
    Returns:
        (empty_apartment, furnished_apartment)
    """
    empty = create_empty_apartment(apartment_json)
    furnished = apartment_json
    
    return (empty, furnished)


def extract_room_features(compartment: dict) -> dict:
    """
    Extract simplified features from a room for model input.
    
    Args:
        compartment: Room dict from apartment JSON
        
    Returns:
        Simplified feature dict
    """
    return {
        "room_type": compartment.get("name_cad", "unknown"),
        "area": compartment.get("area", 0.0),
        "perimeter": compartment.get("perimeter", 0.0),
        "window_area": compartment.get("window_area", 0.0),
        "exposition": compartment.get("exposition", []),
        "boundary": compartment.get("boundary", {})
    }


def normalize_coordinates(coordinates: List[List[float]], 
                          bbox: Tuple[float, float, float, float]) -> List[List[float]]:
    """
    Normalize coordinates to [0, 1] range based on bounding box.
    
    Args:
        coordinates: List of [x, y] points
        bbox: (min_x, min_y, max_x, max_y)
        
    Returns:
        Normalized coordinates
    """
    min_x, min_y, max_x, max_y = bbox
    width = max_x - min_x
    height = max_y - min_y
    
    normalized = []
    for x, y in coordinates:
        norm_x = (x - min_x) / width if width > 0 else 0
        norm_y = (y - min_y) / height if height > 0 else 0
        normalized.append([norm_x, norm_y])
    
    return normalized
