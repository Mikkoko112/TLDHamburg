class Trafficlight:
    """
    This class represents a traffic light and any data that you want to store.
    In the current status it is used to store the status and some static data.
    """
    things_id = None            # id
    _lat = None
    _lon = None
    object_type = None          # signal type

    status = None                


    def __init__(self, things_id, lat, lon, object_type):
        self.things_id = things_id
        self._lat = lat
        self._lon = lon
        self.object_type = object_type
        pass

    def get_coordinates(self, option=["latlon", "lonlat"]):
        if option == "latlon":
            return self._lat, self._lon
        if option == "lonlat":
            return self._lon, self._lat
        
    def set_status(self, status):
        self.status = status
        return status

    def get_status(self):
        return self.status   