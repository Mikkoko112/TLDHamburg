import requests
import json
import folium
import time
from DataFetcher import DataFetcher

data_fetcher = DataFetcher()

endpoint = "Things(23229)"

params = {
    "$expand" : "Locations"
}
start = time.time()
data_fetcher.fetch_data(endpoint,params)
end = time.time()

data_fetcher.print_raw_data()

print(f"finished in {end-start}")