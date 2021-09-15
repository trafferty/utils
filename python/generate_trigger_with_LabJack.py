#!/usr/bin/env python
import time
import sys
import argparse
from datetime import datetime

from labjack import ljm        # pip install labjack-ljm
import getch                   # pip install getch

LOW,HIGH = 0,1

def doLog(log_msg):
    print("%s: %s" % (datetime.now().strftime("%Y_%d_%m (%a) - %H:%M:%S.%f")[:-3], log_msg))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produce trigger signal when any key is pressed; except: 'q' for quit and 'p' to set pulse time" )
    parser.add_argument(dest='pulse_time_ms', nargs='?', type=int, default=5, help='Interval in ms to hold trigger signal high. Default: 5ms')

    args = parser.parse_args()
    pulse_time_ms = args.pulse_time_ms

    # connect to the LabJack T4 (assumes only one connected to computer)
    handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
    if handle is None:
        logger.error("Could not connect to LabJack. Connected?")
        sys.exit()

    # Query Labjack, get some info...
    info = ljm.getHandleInfo(handle)
    deviceType = info[0]
    doLog("Opened a LabJack with Device type: %i, Connection type: %i,\n"
          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    # Setting FIO4 and 05 on the LabJack T4. FIO0-FIO3 are reserved for AIN0-AIN3.
    trigger_name = "FIO4"
    LED_name     = "FIO5"

    # setup vars for reading/writing multiple I/Os in parallel (eReadNames, eWriteName)
    trig_names = [trigger_name, LED_name]
    num_frames = len(trig_names)
    trig_high_values = [HIGH, HIGH]
    trig_low_values  = [LOW,  LOW]

    # Reading from the digital line in case it was previously an analog input.
    results = ljm.eReadNames(handle, num_frames, trig_names)

    # set both outputs low to begin with
    ljm.eWriteNames(handle, num_frames, trig_names, trig_low_values)

    doLog(f"Trigger pulse time set to {pulse_time_ms} ms")
    doLog("Starting loop...")
    while True:
        #cmd = input("'q' to Quit, 'p' for product detect")
        print("'q' to Quit, 'p' to set pulse time, space or any other key for trigger output:")
        cmd = getch.getch()
        if cmd == 'p':
            i = input("Enter new pulse time (ms): ")
            i = i.strip()
            if not i.isdigit() or int(i) < 0:
                doLog(f"Error: {i} not a number or out of range")
                continue
            pulse_time_ms = int(i)
            doLog(f"Trigger pulse time set to {pulse_time_ms} ms")

        elif cmd == 'q':
            break

        elif cmd == '?':
            print("\nCommands:\n")
            print("\tspace or any key: Trigger output")
            print("\tp:                Set pulse time")
            print("\tq:                Quit program\n")
            print("\th:                This help")

        else:
            # Set both inputs high
            ljm.eWriteNames(handle, num_frames, trig_names, trig_high_values)
            # sleep for pulse time
            time.sleep(pulse_time_ms / 1e3)
            # set both inputs low
            ljm.eWriteNames(handle, num_frames, trig_names, trig_low_values)
            doLog(f"Triggered for {pulse_time_ms} ms")

    ljm.close(handle)