import krpc
import time
import threading

orbitAltitude = 70000
# connect to KSP for telemetry
conn = krpc.connect(name="telemtry", address="192.168.1.174")
sc = conn.space_center
vessel = sc.active_vessel

flightParams = vessel.flight(vessel.orbit.body.reference_frame)
pitchRate = 90 / orbitAltitude
    

# select altitude

# determine pitch rate based on desired altitude. Want to be prograde at altitude
vessel.control.throttle = 1
vessel.control.sas = True

vessel.control.activate_next_stage()

def pitch_control():
    # 10,000 - 30
    while flightParams.mean_altitude < 2000:
        pass

    while flightParams.pitch < 40:
        print(flightParams.pitch)
        vessel.control.pitch = 1
    vessel.control.pitch = 0

    # 40,000 - 60
    while flightParams.mean_altitude < 10000:
        pass

    while flightParams.pitch < 60:
        print(flightParams.pitch)
        vessel.control.pitch = 1
    vessel.control.pitch = 0
    

pitch_thread = threading.Thread(target=pitch_control)
pitch_thread.start()

# watch until apoapsis is at desired altitude
while (vessel.orbit.apoapsis_altitude < orbitAltitude):
    # determine pitch
    pass
    
vessel.control.activate_next_stage()
time.sleep(2)
vessel.control.throttle = 0
vessel.control.activate_next_stage()

while vessel.flight().pitch > 0:
    print(vessel.flight().pitch)
    vessel.control.pitch = 1
vessel.control.pitch = 0


while flightParams.mean_altitude < orbitAltitude:
    # determine pitch
    pass

vessel.control.throttle = 1
vessel.control.activate_next_stage()

# once at desired apoapsis, execute circularisation burn until periapsis is at desired altitude
while (vessel.orbit.periapsis_altitude < orbitAltitude):
    pass

vessel.control.throttle = 0


# to end flight, point retrograde

# perform burn

# wait until right time to arm parachute and arm