import sys
import time
import argparse
import json
import logging, logging.config

from labjack import ljm

LOGGING = { 'version': 1, 'disable_existing_loggers': False,
    'formatters': { 'simple': { 'format': '%(asctime)s.%(msecs)03d [%(name)s] (%(levelname)s): %(message)s', "datefmt": "%Y-%m-%d %H:%M:%S"} },
    'handlers': { 'console': {'class': 'logging.StreamHandler', 'level':'DEBUG', 'formatter': 'simple'} },
    'root': {'handlers': ['console'],'level': 'DEBUG'}
}
logging.config.dictConfig(LOGGING)

logger = logging.getLogger("imgAPO_client")

DO_LOW, DO_HIGH = 0,1
PWM_DISABLE, PWM_ENABLE = 0,1

class LabJackDriver:
    """ LabJack driver object"""

    def __init__(self, config):
        self.config = config

        self.debug = config["debug"]
        if not self.debug:
            logger.setLevel(logging.INFO)

        self.lj_device = config["lj_device"] if "lj_device" in config else "T4"
        self.lj_conn = config["lj_conn"] if "lj_conn" in config else "ANY"
        self.lj_id = config["lj_id"] if "lj_id" in config else "ANY"

        self.lj_handle = None

    def connect(self):
        self.lj_handle = ljm.openS(self.lj_device, self.lj_conn, self.lj_id)  # T4 device, Any connection, Any identifier
        if self.lj_handle is None:
            logger.error("Could not connect to LabJack. Connected?")
            return False

        info = ljm.getHandleInfo(self.lj_handle)
        logger.info("Opened a LabJack with Device type: %i, Connection type: %i,\n"
            "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
            (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

        return True

    def stop(self):
        ljm.close(self.lj_handle)
        logger.info("Labjack disconnected")

    def setupDO(self, DO_name, set_low=True):
        # Reading from the digital line in case it was previously an analog input.
        ljm.eReadName(self.lj_handle, DO_name)
        if set_low:
            self.setDO(DO_name, DO_LOW)

    def setupDOMulti(self, DO_name_list, set_low=True):
        # Reading from the digital line in case it was previously an analog input.
        ljm.eReadNames(self.lj_handle, len(DO_name_list), DO_name_list)
        if set_low:
            self.setDOMulti(DO_name_list, [DO_LOW,  DO_LOW])

    def setDO(self, DO_name, state):
        ljm.eWriteName(self.lj_handle, DO_name, state)

    def setDOMulti(self, DO_name_list, state_list):
        ljm.eWriteNames(self.lj_handle, len(DO_name_list), DO_name_list, state_list)


    def setupPWM(self, DIO_num, freq_MHz ):
        '''
        For LJ T4, DIO_num can be either 6 or 7 (for DIO6, DIO7 (aka FIO6, FIO7))

        See https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pwm-out
        '''
        LJ_clock_MHz = 80    # LabJack Clock0's frequency
        LJ_divisor = 1       # default Clock0's divisor
        roll_value =  LJ_clock_MHz/(LJ_divisor * freq_MHz)  #calculated "roll value" to be used below

        logger.info(f"Setting up LabJack PWM for {freq_MHz}MHz on DIO{DIO_num}")
        logger.info(f"Calculated roll value: {roll_value}")

        # Configure Clock Registers:
        ljm.eWriteName(self.lj_handle, "DIO_EF_CLOCK0_ENABLE", 0); 	# Disable clock source
        # Set Clock0's divisor and roll value to configure frequency: 80MHz/1/2666.6666666666665 = 30kHz
        ljm.eWriteName(self.lj_handle, "DIO_EF_CLOCK0_DIVISOR", 1); 	# Configure Clock0's divisor
        ljm.eWriteName(self.lj_handle, "DIO_EF_CLOCK0_ROLL_VALUE", roll_value); 	# Configure Clock0's roll value
        ljm.eWriteName(self.lj_handle, "DIO_EF_CLOCK0_ENABLE", 1); 	# Enable the clock source

        # Configure EF Channel Registers:
        ljm.eWriteName(self.lj_handle, f"DIO{DIO_num}_EF_ENABLE", 0); 	# Disable the EF system for initial configuration
        ljm.eWriteName(self.lj_handle, f"DIO{DIO_num}_EF_INDEX", 0); 	# Configure EF system for PWM
        ljm.eWriteName(self.lj_handle, f"DIO{DIO_num}_EF_OPTIONS", 0); 	# Configure what clock source to use: Clock0
        ljm.eWriteName(self.lj_handle, f"DIO{DIO_num}_EF_CONFIG_A", (roll_value/2.0)); 	# Configure duty cycle to be: 50%

    def setPWMState(self, DIO_num, state):
        '''
            state = 1 (enable) or 0 (disable)
        '''
        ljm.eWriteName(self.handle, f"DIO{DIO_num}_EF_ENABLE", state); 	


def main():
    import getch                   # pip install getch
    from datetime import datetime

    def doLog(log_msg):
        print("%s: %s" % (datetime.now().strftime("%Y_%d_%m (%a) - %H:%M:%S.%f")[:-3], log_msg))

    parser = argparse.ArgumentParser(description='Labjack Driver')
    parser.add_argument('-f',  dest='freq_MHz', type=float, default=0.030, help='PWM freq in MHz (default: 0.030)')
    parser.add_argument('-t',  dest='time_s', type=float, default=1.0, help='amount of time for signal')
    args = parser.parse_args()

    config = {
            "debug": True,
            "lj_device": "T4",
            "lj_conn": "ANY",
            "lj_id": "ANY",
            "LED_name": "FIO6",
            "PWM_DIO_num": 7
        }

    LED_name = config["LED_name"]
    PWM_DIO_num = config["PWM_DIO_num"]

    lj = LabJackDriver(config)

    if not lj.connect():
        logger.error("Could not connect to Labjack...is it hooked up via USB?")
        sys.exit()

    lj.setupDO(LED_name, True)
    lj.setupPWM(PWM_DIO_num, args.freg_MHz)

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
            lj.setDO(LED_name, DO_HIGH)
            lj.setPWMState(PWM_DIO_num, PWM_ENABLE)         # Enable the EF system, PWM wave is now being outputted
            time.sleep(time_s)                              # wait desired time
            lj.setPWMState(PWM_DIO_num, PWM_DISABLE) 	    # Disable the EF system
            lj.setDO(LED_name, DO_LOW)
            doLog(f"PWM signal stopped...")

    lj.stop()
    doLog("all shut down.....")


if __name__ == '__main__':
    main()
