"""
Location coordinate mappings for cities in the EV Concierge application.
Maps city names to (latitude, longitude) tuples for OpenChargeMap API queries.
"""

CITY_COORDINATES = {
    "Los Angeles, CA": (34.0522, -118.2437),
    "San Francisco, CA": (37.7749, -122.4194),
    "San Diego, CA": (32.7157, -117.1611),
    "Seattle, WA": (47.6062, -122.3321),
    "Las Vegas, NV": (36.1699, -115.1398),
}

def get_coordinates(city_name: str) -> tuple[float, float] | None:
    """
    Get coordinates for a city name.
    
    Args:
        city_name: City name (e.g., "Los Angeles, CA")
    
    Returns:
        Tuple of (latitude, longitude) or None if city not found
    """
    return CITY_COORDINATES.get(city_name)

def calculate_midpoint(coord1: tuple[float, float], coord2: tuple[float, float]) -> tuple[float, float]:
    """
    Calculate the midpoint between two coordinates.
    
    Args:
        coord1: First coordinate (lat, lon)
        coord2: Second coordinate (lat, lon)
    
    Returns:
        Midpoint coordinate (lat, lon)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return ((lat1 + lat2) / 2, (lon1 + lon2) / 2)

def calculate_distance_km(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """
    Calculate approximate distance between two coordinates in kilometers.
    Uses simple Euclidean distance (good enough for bounding box calculations).
    
    Args:
        coord1: First coordinate (lat, lon)
        coord2: Second coordinate (lat, lon)
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Approximate: 1 degree latitude ≈ 111 km, 1 degree longitude ≈ 111 km * cos(latitude)
    import math
    avg_lat = (lat1 + lat2) / 2
    lat_diff_km = (lat2 - lat1) * 111
    lon_diff_km = (lon2 - lon1) * 111 * math.cos(math.radians(avg_lat))
    
    return math.sqrt(lat_diff_km**2 + lon_diff_km**2)

def distance_from_line(point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]) -> float:
    """
    Calculate perpendicular distance from a point to a line segment in kilometers.
    This helps filter stations that are off the route.
    
    Args:
        point: Point coordinates (lat, lon)
        line_start: Start of line (lat, lon)
        line_end: End of line (lat, lon)
    
    Returns:
        Distance in kilometers
    """
    import math
    
    # Convert to approximate km coordinates
    lat, lon = point
    lat1, lon1 = line_start
    lat2, lon2 = line_end
    
    # Use average latitude for longitude scaling
    avg_lat = (lat1 + lat2) / 2
    lon_scale = math.cos(math.radians(avg_lat))
    
    # Convert to km
    px, py = lon * 111 * lon_scale, lat * 111
    x1, y1 = lon1 * 111 * lon_scale, lat1 * 111
    x2, y2 = lon2 * 111 * lon_scale, lat2 * 111
    
    # Calculate perpendicular distance to line
    line_len_sq = (x2 - x1)**2 + (y2 - y1)**2
    
    if line_len_sq == 0:
        # Line start and end are the same point
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    
    # Project point onto line
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len_sq))
    
    # Find closest point on line
    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)
    
    # Distance from point to closest point on line
    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
