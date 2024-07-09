from datetime import datetime
import json, requests

__areas_url = "https://www.emergency.vic.gov.au/public/impact-areas-geojson.json?_="
__events_url = "https://www.emergency.vic.gov.au/public/events-geojson.json?_="
    
def __getAllEvents():
    ts = int(datetime.now().timestamp()*1000)
    resp = requests.get(__events_url + str(ts))
    if resp.status_code == 200:
        return resp.json()
    return None

def __getAllAreas():
    ts = int(datetime.now().timestamp()*1000)
    resp = requests.get(__areas_url + str(ts))
    if resp.status_code == 200:
        return resp.json()
    return None

def getNearbyEvents(lat, long, range):
    #range: Range in km
    pass