import krpc
import time
import threading

orbitAltitude = 70000
# connect to KSP for telemetry
conn = krpc.connect(name="telemtry", address="192.168.1.174")
sc = conn.space_center
vessel = sc.active_vessel

flightParams = vessel.flight()
    
# determine pitch rate based on desired altitude. Want to be prograde at altitude
vessel.control.throttle = 1
vessel.control.sas = True

vessel.control.activate_next_stage()

desiredPitch = 80

def pitch_control():
    global desiredPitch
    while True:
        print(flightParams.pitch)
        if (flightParams.pitch < desiredPitch):
            vessel.control.pitch = -0.4
        elif (flightParams.pitch > desiredPitch):
            vessel.control.pitch = 0.4
        else:
            vessel.control.pitch = 0

def stage1_manager():
    global desiredPitch

    # 10,000 - 30
    while flightParams.mean_altitude < 2000:
        pass
    
    desiredPitch = 70

    # 40,000 - 60
    while flightParams.mean_altitude < 5000:
        pass

    desiredPitch = 60 

pitch_thread = threading.Thread(target=pitch_control)
pitch_thread.start()

pitch_mthread = threading.Thread(target=stage1_manager)
pitch_mthread.start()

# watch until apoapsis is at desired altitude
while (vessel.orbit.apoapsis_altitude < orbitAltitude):
    # determine pitch
    pass

# we'll now reach our altitude so we need to gain horizontal speed
vessel.control.throttle = 0
time.sleep(2)
vessel.control.activate_next_stage()
time.sleep(2)
vessel.control.activate_next_stage()

time.sleep(2)

desiredPitch = -10

while flightParams.pitch > 0:
    pass

vessel.control.throttle = 1
vessel.control.activate_next_stage()



# once at desired apoapsis, execute circularisation burn until periapsis is at desired altitude
while (vessel.orbit.speed < 2295):
    pass

vessel.control.throttle = 0


# to end flight, point retrograde

# perform burn

# wait until right time to arm parachute and arm