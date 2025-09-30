import sys
#import serial
from serial import Serial
import time
import argparse
import json
import logging, logging.config

class PiezoJenaEDS2Controller:
    """ PiezoJena EDS2 Controller object"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        self.debug = config["debug"]
        if not self.debug:
            self.logger.setLevel(logging.INFO)

        self.resp_delay_s = config["resp_delay_s"] if "resp_delay_s" in config else 0.02
        
        self.setup_status_register_values()
        
    def setup_status_register_values(self):
        self.actuator_plugged_shift = 0
        self.actuator_plugged_mask  = 0x1
        self.actuator_plugged_test  = 1
        self.actuator_measurement_shift = 1
        self.actuator_measurement_mask  = 0x3
        self.actuator_measurement_test_none   = 0
        self.actuator_measurement_test_strain = 2
        self.actuator_measurement_test_capacitive = 4
        self.actuator_measurement_test_inductive = 6
        self.actuator_measurement_type_dict = {
            0: "none",
            1: "strain",
            2: "capacitive",
            3: "inductive"
        }
        self.open_loop_system_shift = 4
        self.open_loop_system_mask  = 0x1
        self.open_loop_system_test  = 16
        self.piezo_voltage_enabled_shift = 6
        self.piezo_voltage_enabled_mask  = 0x1
        self.piezo_voltage_enabled_test  = 64
        self.open_loop_enabled_shift = 7
        self.open_loop_enabled_mask  = 0x1
        self.open_loop_enabled_test  = 128
        self.generator_type_shift = 9
        self.generator_type_mask  = 0x7
        self.generator_type_test_none      = 0
        self.generator_type_test_sine      = 512
        self.generator_type_test_triangle  = 1024
        self.generator_type_test_rectangle = 1536
        self.generator_type_test_noise     = 2048
        self.generator_type_test_sweep     = 2560
        self.generator_type_dict = {
            0: "none",
            1: "sine",
            2: "triangle",
            3: "rectangle",
            4: "noise",
            5: "sweep",
        }
        self.notch_filter_enabled_shift = 12
        self.notch_filter_enabled_mask  = 0x1
        self.notch_filter_enabled_test  = 4096
        self.low_pass_filter_enabled_shift = 13
        self.low_pass_filter_enabled_mask  = 0x1
        self.low_pass_filter_enabled_test  = 8192
        
    def decode_stat_reg(self, stat_reg):
        is_plugged = (stat_reg >> self.actuator_plugged_shift) & self.actuator_plugged_mask
        actuator_measurement_type = (stat_reg >> self.actuator_measurement_shift) & self.actuator_measurement_mask
        open_loop_system = (stat_reg >> self.open_loop_system_shift) & self.open_loop_system_mask
        piezo_voltage_enabled = (stat_reg >> self.piezo_voltage_enabled_shift) & self.piezo_voltage_enabled_mask
        open_loop_enabled = (stat_reg >> self.open_loop_enabled_shift) & self.open_loop_enabled_mask
        generator_type = (stat_reg >> self.generator_type_shift) & self.generator_type_mask
        notch_filter_enabled = (stat_reg >> self.notch_filter_enabled_shift) & self.notch_filter_enabled_mask
        low_pass_filter_enabled = (stat_reg >> self.low_pass_filter_enabled_shift) & self.low_pass_filter_enabled_mask
        print(f"For status register value {stat_reg}:")
        print(f" Actuator plugged (detected): {('yes' if is_plugged else 'no')}")
        print(f" Actuator measurmenent type: {self.actuator_measurement_type_dict[actuator_measurement_type]}")
        print(f" Open loop system: {('yes' if open_loop_system else 'no')}")
        print(f" Piezo voltage enabled: {('yes' if piezo_voltage_enabled else 'no')}")
        print(f" Closed loop enabled: {('yes' if open_loop_enabled else 'no')}")
        print(f" Generator type: {self.generator_type_dict[generator_type]}")
        print(f" Notch filter enabled: {('yes' if notch_filter_enabled else 'no')}")
        print(f" Low pass filter enabled: {('yes' if low_pass_filter_enabled else 'no')}")
        
        
    def sendCmd(self, cmd_str, noWait=False):
        len_sent = self.ser.write(cmd_str.encode())
        if noWait: return True, ""
        time.sleep(self.resp_delay_s)
        res_buf = ""
        cnt = self.ser.inWaiting()
        while (cnt > 0):
            res_buf += self.ser.read(cnt).decode("utf-8")
            if res_buf.find('\r'):
                break
            time.sleep(self.resp_delay_s)
            cnt = self.ser.inWaiting()
        res_buf = res_buf[:-1]
        return True, res_buf
    
    def getStat(self, chan):
        cmd = f"stat,{chan}"
        ok, resp = self.sendCmd(f"{cmd}\r")
        if not ok:
            self.logger.error("Error sending cmd to controller")
        print(f"stat cmd returned: {resp}")
        if len(resp.split(',')) == 3:
            self.decode_stat_reg(int(resp.split(',')[2]))
        elif resp.find('not present'):
            print(f"Controller not present in slot {chan}")

    def close(self):
        self.ser.close()

    def delay(self, delaytime=0.050):
        time.sleep(delaytime)

    def init(self):
        self.logger.info("Initializing PJ MotorController")

        self.logger.info(f" >> Opening comm port: {self.config['port']}")
        self.ser = Serial(timeout=1)
        self.ser.port     = self.config['port']
        self.ser.baudrate = self.config['baudrate']
        self.ser.open()
        if not self.ser.is_open:
            self.logger.info("Error: Could not open comm port! (port=", self.config['port'], ", baudrate=", self.config['baudrate'],")")
            return False

        ok, resp = self.sendCmd("ktemp\r")
        if not ok:
            self.logger.error("Error sending ktemp cmd to controller")
            return False
        
        self.logger.info(f"Rcv'd: {resp}")

        return True

    # def sendCmd(self, cmd):
    #     ok, resp = self.sendCmd(f"{cmd}\r")
    #     if not ok:
    #         self.logger.error(f"Error sending cmd: {cmd}")
    #         return False
    #     #self.logger.info(f"Rcv'd: {resp}")
    #     return resp


def main():
    parser = argparse.ArgumentParser(description='Utility for testing Piezo Jena EDS2 using Serial Interface')
    parser.add_argument("config_file_path", help='Full path to config file')
    args = parser.parse_args()

    if args.config_file_path:
        with open(args.config_file_path) as config_file:
            config = json.load(config_file)
    else:
        print(f"Config file not found: {args.config_file_path}")
        config = {
                "debug": True,
                "port" : '/dev/ttyUSB0',
                "baudrate" : 115200,
                "resp_delay_s": 0.020,
                "limits_mm": [[-250.0, 250.0]]
            }
        print(f"Using default data: \n{config}")

    LOGGING = { 'version': 1, 'disable_existing_loggers': False,
        'formatters': { 'simple': { 'format': '%(asctime)s.%(msecs)03d [%(name)s] (%(levelname)s): %(message)s', "datefmt": "%Y-%m-%d %H:%M:%S"} },
        'handlers': { 'console': {'class': 'logging.StreamHandler', 'level':'DEBUG', 'formatter': 'simple'} },
        'root': {'handlers': ['console'],'level': 'DEBUG'}
    }
    logging.config.dictConfig(LOGGING)

    logger = logging.getLogger("PJ_MC")

    pj = PiezoJenaEDS2Controller(config, logger)

    logger.info("MotorController started...starting initialization")
    if not pj.init():
        logger.error("Could not initialize Piezo Jena EDS2 Controller")
        sys.exit()

    while True:
        cmd = input(">>> ")
        if cmd == 'q' or cmd == 'quit':
            break
        cmd_pieces = cmd.split(',')
        if (cmd_pieces[0] == 'stat') and len(cmd_pieces) == 2:
            pj.getStat(int(cmd_pieces[1]))
        else:
            logger.info(f"Sending cmd: {cmd}")
            ok, resp = pj.sendCmd(f"{cmd}\r")
            if not ok:
                logger.error("Error sending cmd to controller")
            logger.info(f"Rcv'd: {resp}")

    logger.info("Closing MotorController...")
    pj.close()

if __name__ == '__main__':
    main()
