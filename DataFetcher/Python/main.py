from DataFetcher import DataFetcher

def main():
    data_fetcher = DataFetcher()
    endpoint = "Datastreams"
    params = {
        "$filter" : "properties/layerName eq 'primary_signal'"
    }

    data_fetcher.fetch_data(endpoint,params)
    print(f"fetched {len(data_fetcher.get_data())} entries")

if __name__ == "__main__":
    main()
