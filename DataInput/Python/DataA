class DataAcquisition:
    def get_location_selflink(data: dict[str, any]):

        if "value" not in data:
            print("Missing key: The key 'value' is missing from the data.")
            return None

        if not isinstance(data["value"], list):
            print("Invalid type: The 'value' key is not associated with a list.")
            return None

        if not data["value"]:
            print("Empty list: The 'value' list is empty.")
            return None

        location_values = data["value"][0]
        return location_values.get("@iot.selfLink")
