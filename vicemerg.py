import json, requests, gzip, base64

URL = "https://www.emergency.vic.gov.au/public/events-geojson.json"
USED_FEAT_ATTRIBS = ["geometry"]
USED_PROP_ATTIRBS = [
    "id", "name", "sourceTitle", "status",
    "resources", "sizeFmt", "updated", "location",
    "feedType", "category1", "action", "statewide",
    "text"
]

def getData(compressed=False):
    req = requests.get(URL)
    if req.status_code != 200:
        return False
    
    data = req.json()
    newData = {}
    newData.update({"properties": {"conditions": data["properties"]["conditions"]}})
    features = []
    for feat in data["features"]:
        newFeat = {}
        newProp = {}
        for x in USED_FEAT_ATTRIBS:
            newFeat.update({x: feat[x]})
        for x in USED_PROP_ATTIRBS:
            if x in feat["properties"].keys():
                newProp.update({x: feat["properties"][x]})
        newFeat.update({"properties": newProp})
        features.append(newFeat)
    
    newData.update({"features": features})
    if compressed:
        dataBytes = json.dumps(newData).encode("utf-8")
        compressedBytes = gzip.compress(dataBytes)
        b64 = base64.b64encode(compressedBytes)
        return b64
    else:
        return json.dumps(newData)

if __name__ == "__main__":
    data = getData()
    f = open("data.json", "w")
    f.write(data)
    f.close()