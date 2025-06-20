import sys
import serial
import time
import argparse
import json
import logging, logging.config

LOGGING = { 'version': 1, 'disable_existing_loggers': False,
    'formatters': { 'simple': { 'format': '%(asctime)s.%(msecs)03d [%(name)s] (%(levelname)s): %(message)s', "datefmt": "%Y-%m-%d %H:%M:%S"} },
    'handlers': { 'console': {'class': 'logging.StreamHandler', 'level':'DEBUG', 'formatter': 'simple'} },
    'root': {'handlers': ['console'],'level': 'DEBUG'}
}
logging.config.dictConfig(LOGGING)

logger = logging.getLogger("PJ_MC")

class PiezoJenaEDS2Controller:
    """ PiezoJena EDS2 Controller object"""

    def __init__(self, config):
        self.config = config

        self.debug = config["debug"]
        if not self.debug:
            logger.setLevel(logging.INFO)

        self.resp_delay_s = config["resp_delay_s"] if "resp_delay_s" in config else 0.02

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

    def close(self):
        self.ser.close()

    def delay(self, delaytime=0.050):
        time.sleep(delaytime)

    def init(self):
        logger.info("Initializing PJ MotorController")

        logger.info(" >> Opening comm port")
        self.ser = serial.Serial(timeout=1)
        self.ser.port     = self.config['port']
        self.ser.baudrate = self.config['baudrate']
        self.ser.open()
        if not self.ser.is_open:
            logger.info("Error: Could not open comm port! (port=", self.config['port'], ", baudrate=", self.config['baudrate'],")")
            return False

        ok, resp = self.sendCmd("ktemp\r")
        if not ok:
            logger.error("Error sending ktemp cmd to controller")
            return False
        
        logger.info(f"Rcv'd: {resp}")

        return True

    def setCmd(self, cmd):
        ok, resp = self.sendCmd(f"{cmd}\r")
        if not ok:
            logger.error(f"Error sending cmd: {cmd}")
            return False

def main():
    # parser = argparse.ArgumentParser(description='Utility for testing Copley Motor Controller using Serial Interface')
    # parser.add_argument("config_file_path", help='Full path to config file')
    # args = parser.parse_args()

    # if args.config_file_path:
    #     with open(args.config_file_path) as config_file:
    #         config = json.load(config_file)
    # else:
    #     parser.print_help()
    #     sys.exit(1)

    config = {
            "debug": True,
            "port" : '/dev/ttyUSB0',
            "baudrate" : 115200,
            "resp_delay_s": 0.020,
            "limits_mm": [[-250.0, 250.0]]
        }

    pj = PiezoJenaEDS2Controller(config)

    logger.info("MotorController started...starting initialization")
    if not pj.init():
        logger.error("Could not initialize Piezo Jena EDS2 Controller")
        sys.exit()


    logger.info("Closing MotorController...")
    pj.close()

if __name__ == '__main__':
    main()
