from strands import tool  
import requests

@tool 
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@tool
def get_nearby_places(location_name, radius=3000):
    # Step 1: Geocode location name -> lat/lng
    geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={location_name}"
    geo_data = requests.get(geo_url, headers={"User-Agent": "NearbyPlacesAgent"}).json()
    
    if not geo_data:
        return f"Could not find location: {location_name}"
    
    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

    # Step 2: Use Overpass API to fetch nearby "tourism" tagged places
    query = f"""
    [out:json];
    node(around:{radius},{lat},{lon})["tourism"];
    out;
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    response = requests.post(overpass_url, data={"data": query})
    data = response.json()

    # Step 3: Extract place names
    places = []
    for element in data["elements"]:
        if "tags" in element and "name" in element["tags"]:
            places.append(element["tags"]["name"])
    
    return places if places else "No famous places found nearby."


