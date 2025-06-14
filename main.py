from dotenv import load_dotenv
import os
import requests
import pandas as pd
import xmltodict


load_dotenv()
API_KEY = os.getenv("CTA_BUS_KEY")


def get_bus_routes():
    """
    Gets all CTA bus routes using the Bus Tracker API
    Returns a response containing route data
    """
    base_url = "https://www.ctabustracker.com/bustime/api/v3/getroutes"

    # Set up parameters including the API key
    params = {"key": API_KEY, "format": "json"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        response = response.json()
        df = pd.DataFrame(response["bustime-response"]["routes"])
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching routes: {e}")
        return None


def get_bus_vehicles(vehicle_ids):
    """
    Gets real-time information for specific CTA buses using their vehicle IDs
    Args:
        vehicle_ids: List or comma-separated string of vehicle IDs to look up
    Returns:
        JSON response containing vehicle data or None if error occurs
    """
    base_url = "https://www.ctabustracker.com/bustime/api/v3/getvehicles"

    # Convert list to comma-separated string if needed
    if isinstance(vehicle_ids, list):
        vehicle_ids = ",".join(str(vid) for vid in vehicle_ids)

    # Set up parameters including API key and vehicle IDs
    params = {
        "key": API_KEY,
        "vid": vehicle_ids,
        "tmres": "s",  # Time resolution in seconds
        "format": "json",
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching vehicle data: {e}")
        return None


def get_bus_routes_with_key(api_key):
    """
    Gets all CTA bus routes using the Bus Tracker API with provided API key
    Args:
        api_key: API key for authentication
    Returns:
        pandas DataFrame containing route data or None if error occurs
        Columns: rt,rtnm,rtclr,rtdd
        rt: route number (Bus Number like 151, X9, 147, etc.)
        rtnm: route name
        rtclr: route color (Some Hex code)
        rtdd: route direction (Child element of the route element. Idk what this means I just copied it from the API documentation)
    """
    base_url = "https://www.ctabustracker.com/bustime/api/v3/getroutes"

    # Set up parameters with the provided API key - default format is XML
    params = {"key": api_key}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse XML to dictionary
        xml_dict = xmltodict.parse(response.text)

        # Check if there's an error in the response
        if "error" in xml_dict.get("bustime-response", {}):
            print(f"API Error: {xml_dict['bustime-response']['error']['msg']}")
            return None

        # Extract routes data - the routes are directly under bustime-response
        routes = xml_dict.get("bustime-response", {}).get("route", [])

        # If there's only one route, it won't be in a list
        if not isinstance(routes, list):
            routes = [routes]

        # Convert to DataFrame
        df = pd.DataFrame(routes)

        # Clean up column names (remove any whitespace)
        df.columns = df.columns.str.strip()

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching routes: {e}")
        return None
    except Exception as e:
        print(f"Error processing response: {e}")
        return None


def get_bus_stops_with_key(api_key, route, direction):
    """
    Gets all stops for a specific CTA bus route and direction using the Bus Tracker API
    Args:
        api_key: API key for authentication
        route: route number (e.g. '20', 'X9', etc.)
        direction: direction of travel (e.g. 'Eastbound', 'Westbound', etc.)
    Returns:
        pandas DataFrame containing stop data or None if error occurs
        Columns: stpid, stpnm, lat, lon
        stpid: stop ID
        stpnm: stop name/description
        lat: latitude
        lon: longitude
    """
    base_url = "https://www.ctabustracker.com/bustime/api/v3/getstops"

    # Set up parameters
    params = {"key": api_key, "rt": route, "dir": direction}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        # Parse XML to dictionary
        xml_dict = xmltodict.parse(response.text)

        # Check if there's an error in the response
        if "error" in xml_dict.get("bustime-response", {}):
            print(f"API Error: {xml_dict['bustime-response']['error']['msg']}")
            return None

        # Extract stops data
        stops = xml_dict.get("bustime-response", {}).get("stop", [])

        # If there's only one stop, it won't be in a list
        if not isinstance(stops, list):
            stops = [stops]

        # Convert to DataFrame
        df = pd.DataFrame(stops)

        # Clean up column names
        df.columns = df.columns.str.strip()

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching stops: {e}")
        return None
    except Exception as e:
        print(f"Error processing response: {e}")
        return None


# Example usage
if __name__ == "__main__":
    routes_df = get_bus_routes_with_key(API_KEY)
    if routes_df is not None:
        print("\nRoutes DataFrame:")
        print(routes_df)

    stops_df = get_bus_stops_with_key(API_KEY, "151", "Northbound")
    if stops_df is not None:
        print("\nStops DataFrame:")
        print(stops_df)
