# Module for getting device input and talking to Maya to get model to update
import socket, time, json, random, argparse, re
import sys, os
sys.path.append(os.path.abspath("../"))

from utils.rotationMagic import RotationCorrector
from utils.streamUtils.StreamRead import StreamRead

def main(args):
    maya = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to Maya (Maya must be listening)
    maya.connect(("127.0.0.1", 7777))

    vals = {"tx" : 0, "ty" : 0, "tz" : 0, "rx" : 0, "ry" : 0, "rz" : 0}
    data = {"ANKLE_L" : vals.copy(), "TOE_L" : vals.copy(), "ANKLE_R" : vals.copy(), "TOE_R" : vals.copy()}

    startTime = time.time()
    duration = 60

    stream = StreamRead("/dev/input/smartshoes")

    # DEBUGGING (RUN WITHOUT DEVICE)
    if args.debug:
        while time.time() < startTime + duration:
            # Random rotation values
            data["ANKLE_L"]["rx"] = random.uniform(0,20)
            data["ANKLE_L"]["ry"] = random.uniform(0,20)
            data["ANKLE_L"]["rz"] = random.uniform(0,20)
            data["ANKLE_L"]["tx"] = random.uniform(0,10)
            data["ANKLE_L"]["ty"] = random.uniform(0,10)
            data["ANKLE_L"]["tz"] = random.uniform(0,10)
            data["ANKLE_R"]["rx"] = random.uniform(0,20)
            data["ANKLE_R"]["ry"] = random.uniform(0,20)
            data["ANKLE_R"]["rz"] = random.uniform(0,20)
            data["ANKLE_R"]["tx"] = random.uniform(0,10)
            data["ANKLE_R"]["ty"] = random.uniform(0,10)
            data["ANKLE_R"]["tz"] = random.uniform(0,10)
            jsonData = re.sub(r"\"", "\'", json.dumps(data))
            print(jsonData)
            maya.send(jsonData)
            time.sleep(0.1)
        return

    r_leg_rotation = RotationCorrector()
    while time.time() < startTime + duration:
        records = stream.readFromStream()
        if records and len(records[0]) == 10:
            records = map(float, records[0])

            angular_velocity, acceleration, magnetic_field = [records[x:x+3] for x in range(0, 9, 3)]

            # Switch axis orientations
            #angular_velocity[2], angular_velocity[0] = angular_velocity[0], angular_velocity[2]
            #acceleration[2], acceleration[0] = acceleration[0], acceleration[2]
            #magnetic_field[2], magnetic_field[0] = magnetic_field[0], magnetic_field[2]

            r_leg_rotation.rotationMagic(records[9], angular_velocity, acceleration, magnetic_field)

            data["ANKLE_R"]["ry"], data["ANKLE_R"]["rx"], data["ANKLE_R"]["rz"] = r_leg_rotation.getHpr()
            jsonData = re.sub(r"\"", "\'", json.dumps(data))
            maya.send(jsonData)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Capture device data and display on Maya")
    parser.add_argument("-d", action = "store_true", dest = "debug", help = "Turn debug mode on (run without hardware device)")
    args = parser.parse_args()
    if args.debug:
        print("DEBUG MODE ENABLED")
    main(args)
