from DataInput import DataStream
import requests



def main():
    data_stream = DataStream()

# Base URL for the API
base_url = "https://tld.iot.hamburg.de/v1.1/Datastreams"
# Initial filter to get primary signal datastreams
params = {
    '$filter': "properties/layerName eq 'primary_signal'",
    '$top': 1000  # Adjust as needed, but keep within API limits
}

# Initialize an empty list to store all results
all_datastreams = []

while True:
    print("hi")
    # Send GET request to the API
    response = requests.get(base_url, params=params)
    
    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()
        
        # Append current batch of results to the list
        all_datastreams.extend(data.get('value', []))
        
        # Check if there is a next link
        next_link = data.get('@iot.nextLink')
        if next_link:
            # If there's a next link, set the base_url to the next link for the next iteration
            base_url = next_link
        else:
            # If there is no next link, break the loop
            break
    else:
        # Handle errors (e.g., log the error, raise an exception, etc.)
        print(f"Error: {response.status_code} - {response.text}")
        break

# All results are now in the all_datastreams list
print(f"Retrieved {len(all_datastreams)} datastreams.")


if __name__ == "__main__":
    main()