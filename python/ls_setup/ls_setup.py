#!/usr/bin/env python3

import sys
import os
import argparse
import signal
import time
import json
# from datetime import datetime
import logging, logging.config
from collections import deque
import getch                   # pip install getch

from Copley_motorController import CopleyMotorController
from imgAPO_client import ImgAPO_client
from labjack_driver import LabJackDriver

DO_LOW, DO_HIGH = 0,1
PWM_DISABLE, PWM_ENABLE = 0,1

def main():
    done = False
    def sigint_handler(signal, frame):
        global done
        print( "\nShutting down...")
        done = True
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(description='TCS App')
    parser.add_argument('-c', '--config_file_path', action="store", default='dif_client_config.json', help='path to config file')

    args = parser.parse_args()

    # open up and read the config file
    try:
        with open(args.config_file_path) as config_file:
            try:
                config = json.load(config_file)
            except ValueError:
                print("Error parsing config file: %s" % (args.config_file_path))
                raise
                sys.exit()
    except FileNotFoundError:
        print("Error! Config file not found: %s" % (args.config_file_path))
        raise
        sys.exit()

    LOGGING = { 'version': 1, 'disable_existing_loggers': False,
        'formatters': { 'simple': { 'format': '%(asctime)s.%(msecs)03d [%(name)s] (%(levelname)s): %(message)s', "datefmt": "%Y-%m-%d %H:%M:%S"} },
        'handlers': { 'console': {'class': 'logging.StreamHandler', 'level':'DEBUG', 'formatter': 'simple'} },
        'root': {'handlers': ['console'],'level': 'DEBUG'}
    }
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger("main")

    logger.info('Linescan setup started...')

    logger.info("Creating Copley MC and starting initialization")
    mc = CopleyMotorController(config["copley_mc"])
    if not mc.init():
        logger.error("Could not initialize Copley Controller")
        sys.exit()

    logger.info("Creating connection to imgAPO...")
    imgAPO = ImgAPO_client(config["imgAPO"])

    if not imgAPO.connect():
        logger.error("Could not connect to imgAPO")
        sys.exit()

    LED_name    = config["labjack"]["LED_name"]
    PWM_DIO_num = config["labjack"]["PWM_DIO_num"]
    freq_MHz    = config["labjack"]["freq_MHz"]
    PWM_time_s  = config["labjack"]["PWM_time_s"]

    lj = LabJackDriver(config)

    if not lj.connect():
        logger.error("Could not connect to Labjack...is it hooked up via USB?")
        sys.exit()

    lj.setupDO(LED_name, True)
    lj.setupPWM(PWM_DIO_num, freq_MHz)

    start_loc_mm = config["start_loc_mm"]
    end_loc_mm = config["end_loc_mm"]
    PWM_start_delay_s = config["PWM_start_delay_s"]
    SeqLength_mm = config["SeqLength_mm"]
    PageLength_Ln = config["PageLength_Ln"]
    ScanVel_mmps = config["ScanVel_mmps"]

    vel_counts_per_sec = mc.calc_vel_in_counts(ScanVel_mmps)
    stage_accel_counts_per_sec2 = config["stage_accel_counts_per_sec2"]

    axis = 'a'

    logger.info("Starting loop...")
    while True:
        #cmd = input("'q' to Quit, 'p' for product detect")
        print("'q' to Quit, 't' to set PWM time, space or any other key for trigger output:")
        cmd = getch.getch()
        if cmd == 't':
            i = input("Enter new PWM time (s): ")
            try:
                PWM_time_s = float(i)
            except ValueError as error:
                logger.info(f"Error: {i} not a number or out of range")
                continue
            logger.info(f"Trigger PWM time set to {PWM_time_s} sec")

        elif cmd == 'q':
            break

        elif cmd == '?':
            print("\nCommands:\n")
            print("\tspace or any key: Trigger output")
            print("\tt:                Set PWM time")
            print("\tq:                Quit program\n")
            print("\th:                This help")

        elif cmd == 'g':
            logger.info("Slewing to start location...")
            mc.moveToLoc(axis, start_loc_mm, False)

            imgAPO.setupDropDetection(SeqLength_mm, PageLength_Ln, ScanVel_mmps)

            mc.waitForStop([axis])
            time.sleep(0.5)

            logger.info("Starting scan dispense move...")
            mc.moveToLoc(axis, end_loc_mm, False, vel_counts_per_sec, stage_accel_counts_per_sec2)

            time.sleep(PWM_start_delay_s)

            #  Now turn on channel for desired time:
            logger.info(f"Starting PWM signal...")
            lj.setPWMState(PWM_DIO_num, PWM_ENABLE)         # Enable the EF system, PWM wave is now being outputted
            lj.setDO(LED_name, DO_HIGH)
            time.sleep(PWM_time_s)                          # wait desired time
            lj.setPWMState(PWM_DIO_num, PWM_DISABLE) 	    # Disable the EF system
            lj.setDO(LED_name, DO_LOW)

            mc.waitForStop([axis])

            logger.info(f"Scan complete...")

    logger.info("Closing MotorController...")
    mc.close()

    logger.info("Closing labJack...")
    lj.stop()

    logger.info("Disconnecting from imgAPO...")
    imgAPO.stop()

    logger.info("all shut down.....")

    if __name__ == '__main__':
        main()
