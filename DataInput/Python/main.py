from DataInput import DataStream
import requests


def main():
    data_stream = DataStream()


base_url = "https://tld.iot.hamburg.de/v1.1/Datastreams"
params = {"$filter": "properties/layerName eq 'primary_signal'", "$top": 1000}
all_datastreams = []

while True:
    print("hi")
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        all_datastreams.extend(data.get("value", []))
        next_link = data.get("@iot.nextLink")
        if next_link:
            base_url = next_link
        else:
            break
    else:
        print(f"Error: {response.status_code} - {response.text}")
        break

print(f"Retrieved {len(all_datastreams)} datastreams.")

if __name__ == "__main__":
    main()
