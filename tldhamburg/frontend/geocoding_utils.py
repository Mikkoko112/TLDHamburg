
from geopy.geocoders import Nominatim
from geopy.point import Point
from loguru import logger
import sys

# Geocoding
# the API Nominatim (OpenStreetMap) that gets a street address and will 
# changes it to the associated coordinates

#https://geopy.readthedocs.io/en/stable/#nominatim
# Using Nominatim with the default user_agent is strongly discouraged, as it 
# violates Nominatim’s Usage Policy https://operations.osmfoundation.org/policies/nominatim/ 
# and may possibly cause 403 and 429 HTTP errors. 
# Please make sure to specify a custom user_agent with Nominatim(user_agent="my-application") 
# or by overriding the default user_agent: geopy.geocoders.options.default_user_agent = "my-application". 
# An exception will be thrown if a custom user_agent is not specified.

#Initialize logging
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

def return_coordinates(address: str, geolocator = Nominatim):
    """
    Fetches the latitude and longitude of a given address using geocoding.
    
    Parameters:
    address (str): The full street address.
    geolocator (Nominate): An instance of a geocoding class.
    
    Returns:
    Tuple[Optional[float], Optional[float]]: Latitude and Longitude as a tuple, or (None, None) if unsuccessful.
    """

    geolocator = Nominatim(user_agent="http")

    # initialize variables
    lat, lon = None, None
    # parameters for viewbox for hamburg
    viewbox_hh = [Point(53.781807,9.675926),Point(53.366671,10.426862)]

    try:
        geocode_info = geolocator.geocode(query=address, country_codes="de", viewbox=viewbox_hh, bounded=True)
        lat = float(geocode_info.latitude)
        lon = float(geocode_info.longitude)
        logger.info(f"Fetched coordinates {lat}, {lon} for {address}.")
    except AttributeError:
        logger.warning(f"Geocoding returned no results for {address}.")
    except Exception as e:
        logger.warning(f"Could not fetch geocode information for {address} because of {e}.")
    return lat,lon

def convert_to_lat_lon(lonlat):
    """
    Since it seems as if there is no industry standard, we are going for lat,lon
    """
    return lonlat[1], lonlat[0]  # Swap the order
