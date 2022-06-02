#!/usr/bin/python

import time
import sys
from datetime import datetime
import argparse
from labjack import ljm
import signal
import getch                   # pip install getch


LOW,HIGH = 0,1

def doLog(log_msg):
    print("%s: %s" % (datetime.now().strftime("%Y_%d_%m (%a) - %H:%M:%S.%f")[:-3], log_msg))


if __name__ == "__main__":
    done = False
    def sigint_handler(signal, frame):
        global done
        doLog( "\nShutting down...")
        done = True
    signal.signal(signal.SIGINT, sigint_handler)
    
    parser = argparse.ArgumentParser(description='Trigger Linscan: send trigger signal for n pages with delay between')
    parser.add_argument('-f',  dest='freq_MHz', type=float, default=0.030, help='PWM freq in MHz (default: 0.030)')
    parser.add_argument('-t',  dest='time_s', type=float, default=1.0, help='amount of time for signal')

    args = parser.parse_args()
    freq_MHz = args.freq_MHz
    time_s = args.time_s

    handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
    if handle is None:
        doLog("Could not connect to LabJack. Connected?")
        sys.exit()

    info = ljm.getHandleInfo(handle)
    doLog("Opened a LabJack with Device type: %i, Connection type: %i,\n"
          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    # Let's use an output to turn on/off an LED for debug
    LED_name = "FIO6"
    # Reading from the digital line in case it was previously an analog input.
    ljm.eReadName(handle, LED_name)
    # set output low to begin with
    ljm.eWriteName(handle, LED_name, LOW)

    # 
    #  Here's where we setup the LJ for PWM
    # 
    #  See https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pwm-out
    #
    LJ_clock_MHz = 80    # LabJack Clock0's frequency
    LJ_divisor = 1       # default Clock0's divisor
    roll_value =  LJ_clock_MHz/(LJ_divisor * freq_MHz)  #calculated "roll value" to be used below

    doLog(f"Setting up LabJack PWM for {freq_MHz}MHz for {time_s}s on DIO7")
    doLog(f"Calculated roll value: {roll_value}")

    # Configure Clock Registers:
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 0); 	# Disable clock source
    # Set Clock0's divisor and roll value to configure frequency: 80MHz/1/2666.6666666666665 = 30kHz
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", 1); 	# Configure Clock0's divisor
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", roll_value); 	# Configure Clock0's roll value
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1); 	# Enable the clock source

    # Configure EF Channel Registers:
    ljm.eWriteName(handle, "DIO7_EF_ENABLE", 0); 	# Disable the EF system for initial configuration
    ljm.eWriteName(handle, "DIO7_EF_INDEX", 0); 	# Configure EF system for PWM
    ljm.eWriteName(handle, "DIO7_EF_OPTIONS", 0); 	# Configure what clock source to use: Clock0
    ljm.eWriteName(handle, "DIO7_EF_CONFIG_A", (roll_value/2.0)); 	# Configure duty cycle to be: 50%

    #
    #  PWM setup complete
    #
    doLog("Starting loop...")
    while True:
        #cmd = input("'q' to Quit, 'p' for product detect")
        print("'q' to Quit, 't' to set PWM time, space or any other key for trigger output:")
        cmd = getch.getch()
        if cmd == 't':
            i = input("Enter new PWM time (s): ")
            try:
                time_s = float(i)
            except ValueError as error:
                doLog(f"Error: {i} not a number or out of range")
                continue
            doLog(f"Trigger PWM time set to {time_s} sec")

        elif cmd == 'q':
            break

        elif cmd == '?':
            print("\nCommands:\n")
            print("\tspace or any key: Trigger output")
            print("\tt:                Set PWM time")
            print("\tq:                Quit program\n")
            print("\th:                This help")

        else:
            #  Now turn on channel for desired time:
            doLog(f"Starting PWM signal...")
            ljm.eWriteName(handle, LED_name, HIGH)
            ljm.eWriteName(handle, "DIO7_EF_ENABLE", 1); 	# Enable the EF system, PWM wave is now being outputted
            time.sleep(time_s)                              # wait desired time
            ljm.eWriteName(handle, "DIO7_EF_ENABLE", 0); 	# Disable the EF system
            ljm.eWriteName(handle, LED_name, LOW)
            doLog(f"PWM signal stopped...")

    ljm.close(handle)
    doLog("all shut down.....")