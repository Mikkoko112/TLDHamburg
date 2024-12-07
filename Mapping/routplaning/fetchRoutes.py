#!/usr/bin/env python3
import requests
import json


def getRoute(coordsStartEnd:list)->dict:

    body = {"coordinates": coordsStartEnd}
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf624884e5ad2d208a4ef2abb164f9f203b5b5",
        "Content-Type": "application/json; charset=utf-8",
    }
    call = requests.post(
        "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
        json=body,
        headers=headers,
        timeout=5,
    )

    return json.loads(call.text)

def getMultipleRoutes(coordsStartEnd:list)->dict:
    body = {"coordinates": coordsStartEnd,"alternative_routes":{"target_count":3}}
    
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf624884e5ad2d208a4ef2abb164f9f203b5b5",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    call = requests.post(
        "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
        json=body,
        headers=headers,
        timeout=5,
    )

    return json.loads(call.text)



