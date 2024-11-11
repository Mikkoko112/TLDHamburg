import requests
import json

def get_directions(api_key, start_coords, end_coords, profile='driving-car'):
    url = f"https://api.openrouteservice.org/v2/directions/{profile}/geojson"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "coordinates": [
            start_coords,  # [longitude_start, latitude_start]
            end_coords     # [longitude_end, latitude_end]
        ],
        "format": "geojson"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        geojson_data = response.json()

        # Save to a .geojson file (optional)
        with open("route.geojson", "w") as file:
            json.dump(geojson_data, file, indent=4)

        return geojson_data

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

# Example usage
if __name__ == "__main__":
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    start_coords = [13.4050, 52.5200]  # Berlin (longitude, latitude)
    end_coords = [9.9937, 53.5511]     # Hamburg (longitude, latitude)

    directions = get_directions(api_key, start_coords, end_coords)
    if directions:
        print(json.dumps(directions, indent=4))  # Print the GeoJSON response
