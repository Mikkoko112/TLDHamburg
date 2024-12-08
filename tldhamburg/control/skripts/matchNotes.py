#!/usr/bin/env python3
import json
import os
import math
import requests

from tldhamburg.control.skripts.models import ORSNode, OSMNode

body = {"bbox": [[9.98, 53.54], [10.0, 53.56]]}

headers = {
    "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
    "Authorization": "5b3ce3597851110001cf6248803978b4d3c14162a51793eab41b47c1",
    "Content-Type": "application/json; charset=utf-8",
}
call = requests.post(
    "https://api.openrouteservice.org/v2/export/driving-car",
    json=body,
    headers=headers,
    timeout=5,
)

ors_data = json.loads(call.text)

with open("ors_graph.json", "w", encoding="utf-8") as fp:
    json.dump(ors_data, fp, indent=4)



def matchNotes(ORSNotes,traficLights)->list:
    pass