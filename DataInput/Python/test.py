import requests
import json
from DataFetcher import DataFetcher

data_fetcher = DataFetcher()

endpoint = "Datastreams"

params = {
    "$top" : 3
}

data_fetcher.fetch_data(endpoint,params)

data_fetcher.print_raw_data()