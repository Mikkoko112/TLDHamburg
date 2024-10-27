
from geopy.geocoders import Nominatim
from geopy.point import Point
from loguru import logger
#import pandas as pd
import sys

#https://geopy.readthedocs.io/en/stable/#nominatim

# Data handling
# The spreadsheet was in CSV form, so that Pandas is a good choice
# to manipulate the dataframe and add columns

# Geocoding
# I need an API that can get a street address and will change it to 
# the associated coordinates
# I use Nominatim (OpenStreetMap) because it is free 

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

    try:
        geocode_info = geolocator.geocode(query=address, country_codes="de", viewbox=[Point(53.781807,9.675926),Point(53.366671,10.426862)], bounded=True)
        #points = Nominatim.reverse(self = Nominatim, query=address)
        lat = float(geocode_info.latitude)
        lon = float(geocode_info.longitude)
        logger.info(f"Fetched coordinates {lat}, {lon} for {address}.")
    except AttributeError:
        logger.warning(f"Geocoding returned no results for {address}.")
    except Exception as e:
        logger.warning(f"Could not fetch geocode information for {address} because of {e}.")
    return lat,lon

#geolocator = Nominatim(user_agent="http")
x = return_coordinates("Lehmweg 9 Hamburg")
print(x)