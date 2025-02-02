from tldhamburg.backend.DataFetcher import DataFetcher
import json
from datetime import datetime


'''
This script generates static data which might be used for statically evalueating
possible routes and grouping simultaneous traffic lights for more complex pre-
diction algorithms. The structure of the generated files is as follows:
    ../data/struct.json: This lists all classes of simultaneously switching traffic
                         lights for each scrossing where the trafficLightsID is used
                         as a key for which the entry is a list cotaining lists of 
                         Things identified by their @iot.id as well as their name.
    ../data/structRev.json: This allows to access the equivallence classes from struct.json
                            quickly by listing the name and the trafficLightsID for each Thing,
                            usinf the @iot.id as a key, as well as the classIndex which is the 
                            index of the equivalence class in the relevant crossing the Thing is
                            part of.
    ../data/weights.json: This contains the expected wait time for the primary signal of each Thing,
                          using the @iot.id as a key.

Autor: Caspar Kiehn
'''


def getWeight(Observations):
    weightCurr=0
    for i, data in enumerate(Observations):
        if i==0:
            lastGreen=datetime.fromisoformat(data["phenomenonTime"])
            end=lastGreen
            continue
        if data["result"]==3:
            lastGreen=datetime.fromisoformat(data["phenomenonTime"])
            continue
        if data["result"]==1:
            timeRed=(lastGreen-datetime.fromisoformat(data["phenomenonTime"])).total_seconds()
            weightCurr+=timeRed**2/2
    return weightCurr/(end-datetime.fromisoformat(Observations[-1]["phenomenonTime"])).total_seconds()

TIME_CHECK="2025-01-21T11:11:11Z"
NUM_OBSERVATIONS=100

getter=DataFetcher()
print("start fetch")
getter.fetch_data("Things",{"$expand":f"Datastreams($filter=properties/layerName eq 'primary_signal';$expand=Observations($orderby=phenomenonTime desc;$filter=phenomenonTime lt {TIME_CHECK};$top={NUM_OBSERVATIONS};$select=phenomenonTime,result);$select=Observations)","$select":"name,@iot.id,Datastreams"})
print("end fetch")
dataFetched=getter.get_data()


struct={}
for data in dataFetched:
    if len(data["Datastreams"])==0 or len(data["Datastreams"][0]["Observations"])<NUM_OBSERVATIONS:
        continue
    tl=data["name"].split("_")[0]
    if tl not in struct:
        struct[tl]={}
    key=tuple([(x["phenomenonTime"],x["result"]) for x in data["Datastreams"][0]["Observations"]])
    val={"name":data["name"],"id":data["@iot.id"]}
    if key not in struct[tl]:
        struct[tl][key]=[]
    struct[tl][key].append(val)
for tl in struct.keys():
    struct[tl]=list(struct[tl].values())

structRev={}
for tl in struct.keys():
    for i,lanes in enumerate(struct[tl]):
        for lane in lanes:
            structRev[lane["id"]]={"name":lane["name"],"intersection":tl,"classIndex":i}

weights={}
for data in dataFetched:
    id=data["@iot.id"]
    if id not in structRev:
        continue
    if len(data["Datastreams"])==0 or len(data["Datastreams"][0]["Observations"])<NUM_OBSERVATIONS:
        print(id)
        continue
    weights[id]=getWeight(data["Datastreams"][0]["Observations"])

with open("../data/struct.json","w") as out:
    json.dump(struct,out,indent=4)
with open("../data/structRev.json","w") as out:
    json.dump(structRev,out,indent=4)
with open("../data/weights.json","w") as out:
    json.dump(weights,out,indent=4)