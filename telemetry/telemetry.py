import krpc
import time
from elasticsearch import Elasticsearch
from datetime import datetime
import sys

# connect to Elasticsearch
es = Elasticsearch([
    'https://elastic:' + sys.argv[1] + '@64acb284c1c042259d4f4ec4fa5a6c5f.eu-west-2.aws.cloud.es.io:9243'
])

# create an Index for the flight
indexName = "telemetry-" + str(datetime.now()).replace(' ','').replace(':','')

mapping = {
    "mappings": {
        "properties": {
            "type": {
                "type": "keyword"
            },
            "time": {
                "type": "date"
            },
            "vessel": {
                "type": "keyword"
            },
            "partName": {
                "type": "keyword"
            },
            "value": {
                "type": "float"
            },
            "location": {
                "type": "geo_point"
            }
        }
    }
}

ci = es.indices.create(indexName,mapping)

print("Telemetry created with name " + indexName)
input("Press any key to continue")

# connect to KSP for telemetry
conn = krpc.connect(name="telemtry", address="192.168.1.174")
sc = conn.space_center

parts = []

class Vessel:
    def __init__(self,v):
        self.v = v
        self.streams = []

def configureVesselStreams(v):
    newVessel = Vessel(v)
    parts.append(newVessel)

    refframe = v.orbit.body.reference_frame

    newVessel.streams.append({
        'metric': 'altitude',
        'stream': conn.add_stream(getattr,v.flight(refframe),'mean_altitude')
    })

    newVessel.streams.append({
        'metric': 'speed',
        'stream': conn.add_stream(getattr,v.flight(refframe),'speed')
    })

    newVessel.streams.append({
        'metric': 'pitch',
        'stream': conn.add_stream(getattr,v.flight(refframe),'pitch')
    })
    
    newVessel.streams.append({
        'metric': 'heading',
        'stream': conn.add_stream(getattr,v.flight(refframe),'heading')
    })

    newVessel.streams.append({
        'metric': 'roll',
        'stream': conn.add_stream(getattr,v.flight(refframe),'roll')
    })

    newVessel.streams.append({
        'metric': 'g_force',
        'stream': conn.add_stream(getattr,v.flight(refframe),'g_force')
    })

    newVessel.streams.append({
        'metric': 'dynamic_pressure',
        'stream': conn.add_stream(getattr,v.flight(refframe),'dynamic_pressure')
    })

    newVessel.streams.append({
        'metric': 'location',
        'lat_stream': conn.add_stream(getattr,v.flight(refframe),'latitude'),
        'lon_stream': conn.add_stream(getattr,v.flight(refframe),'longitude')
    })

    for e in v.parts.engines:
        for p in e.propellants:
            newVessel.streams.append({
                'metric': 'available_propellant',
                'part': e.part.name + "-" + p.name,
                'stream': conn.add_stream(getattr,p,'current_amount')
            })

def inVessels(v):
    
    for ve in parts:
        try:
            if v.name == ve.v.name:
                return True
        except:
            print("removing vessel")
            parts.remove(ve)

    return False

while (True):
    # find all the vessels and configure them
    for v in conn.space_center.vessels:
        if not inVessels(v):
            configureVesselStreams(v)

    for v in parts:
        for s in v.streams:    
            try:
                if (s['metric'] == 'location'):
                    ind = es.index(index=ci['index'],body={
                        'type': s['metric'],
                        'vessel': v.v.name,
                        'time': datetime.now(),
                        "location": {
                            'lat': s['lat_stream'](),
                            'lon': s['lon_stream']()
                        }
                    })
                elif (not 'part' in s):
                    ind = es.index(index=ci['index'],body={
                        'type': s['metric'], 
                        'vessel': v.v.name,
                        'time': datetime.now(),
                        "value": s['stream']()
                    })
                else:
                    ind = es.index(index=ci['index'],body={
                        'type': s['metric'],
                        'vessel': v.v.name,
                        'partName': s['part'],
                        'time': datetime.now(),
                        "value": s['stream']()
                    })

            except:
                pass

    time.sleep(1)


