from tldhamburg.backend.DataFetcher import DataFetcher
import json
from datetime import datetime

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