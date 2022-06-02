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

logger = logging.getLogger("Copley_MC")

class CopleyMotorController:
    """ Copley Motor Controller object"""

    def __init__(self, config):
        self.config = config

        self.debug = config["debug"]
        if not self.debug:
            logger.setLevel(logging.INFO)

        self.resp_delay_s = config["resp_delay_s"] if "resp_delay_s" in config else 0.02
        self.counts_per_micron = config["counts_per_micron"] if "counts_per_micron" in config else 20
        self.default_max_velocity = config["default_max_velocity"]  if "default_max_velocity" in config else 10000000
        self.default_max_accel = config["default_max_accel"] if "default_max_accel" in config else 50000
        self.axis_list = config["axis_list"] if "axis_list" in config else ['a']
        self.limits_mm = config["limits_mm"] if "limits_mm" in config else [[-100.0,  100.0]]
        self.waitPollingTime_s = config["waitPollingTime_s"] if "waitPollingTime_s" in config else 0.01

        assert(len(self.limits_mm) == len(self.axis_list)), "Config Error: Length of axis_list is not the same as length of limits_mm"

        self.limits_min = {}
        self.limits_max = {}
        for idx, limits in enumerate(self.limits_mm):
            self.limits_min[ self.axis_list[idx] ] = limits[0] * 1000 * self.counts_per_micron
            self.limits_max[ self.axis_list[idx] ] = limits[1] * 1000 * self.counts_per_micron

        self.err_codes = {}
        self.err_codes[1 ]= "Too much data passed with command"
        self.err_codes[3 ]= "Unknown command code"
        self.err_codes[4 ]= "Not enough data was supplied with the command"
        self.err_codes[5 ]= "Too much data was supplied with the command"
        self.err_codes[9 ]= "Unknown parameter ID"
        self.err_codes[10]= " Data value out of range"
        self.err_codes[11]= " Attempt to modify read-only parameter"
        self.err_codes[14]= " Unknown axis state"
        self.err_codes[15]= " Parameter doesn’t exist on requested page"
        self.err_codes[16]= " Illegal serial port forwarding"
        self.err_codes[18]= " Illegal attempt to start a move while currently moving"
        self.err_codes[19]= " Illegal velocity limit for move"
        self.err_codes[20]= " Illegal acceleration limit for move"
        self.err_codes[21]= " Illegal deceleration limit for move"
        self.err_codes[22]= " Illegal jerk limit for move"
        self.err_codes[25]= " Invalid trajectory mode"
        self.err_codes[27]= " Command is not allowed while CVM is running"
        self.err_codes[31]= " Invalid node ID for serial port forwarding"
        self.err_codes[32]= " CAN Network communications failure"
        self.err_codes[33]= " ASCII command parsing error"
        self.err_codes[36]= " Bad axis letter specified"
        self.err_codes[46]= " Error sending command to encoder"
        self.err_codes[48]= " Unable to calculate filter"

    def print_err(self, code):
        logger.error("Error: %s" % self.err_codes[code])


    def sendCmdXXX(self, cmd_str, noWait=False):
        self.ser.reset_input_buffer()
        self.ser.flush()
        len_sent = self.ser.write(cmd_str.encode())
        if noWait: return True, ""
        time.sleep(self.resp_delay_s)
        res_buf = ""
        cnt = self.ser.inWaiting()
        if cnt == 0:
            return False, ""
        while (cnt > 0):
            res_buf += self.ser.read(cnt).decode("utf-8")
            if res_buf.find('\n'):
                cnt = 0
                break
            time.sleep(self.resp_delay_s)
            cnt = self.ser.inWaiting()
        if cnt > 0:
            logger.error(f"Error sending data to Copley Controller, cnt = {cnt}")
            return False, ""
        if len(res_buf[0]) > 0 and res_buf[0] == 'e':
            logger.error(int(res_buf[2:]))
            print_err(int(res_buf[2:]))
        res_buf = res_buf[:-1]
        return True, res_buf

    def sendCmd(self, cmd_str, noWait=False):
        len_sent = self.ser.write(cmd_str.encode())
        if noWait: return True, ""
        time.sleep(self.resp_delay_s)
        res_buf = ""
        cnt = self.ser.inWaiting()
        while (cnt > 0):
            res_buf += self.ser.read(cnt).decode("utf-8")
            if res_buf.find('\n'):
                break
            time.sleep(self.resp_delay_s)
            cnt = self.ser.inWaiting()
        if res_buf[0] == 'e':
            logger.error(int(res_buf[2:]))
        res_buf = res_buf[:-1]
        return True, res_buf

    def close(self):
        self.ser.close()

    def delay(self, delaytime=0.050):
        time.sleep(delaytime)

    def init(self):
        logger.info("Initializing MotorController")

        logger.info(" >> Opening comm port")
        self.ser = serial.Serial(timeout=1)
        self.ser.port     = self.config['port']
        self.ser.baudrate = self.config['baudrate']
        self.ser.open()
        if not self.ser.is_open:
            logger.info("Error: Could not open comm port! (port=", self.config['port'], ", baudrate=", self.config['baudrate'],")")
            return False

        ok, resp = self.sendCmd("g r0x90\n")
        if not ok:
            # Okay, if we got here, Copley controller may be at different
            # baud or maybe in error state.  Send break to reset comms
            logger.warning("Error with Copley comms...trying with baudrate = 9600")

            self.ser.send_break()
            time.sleep(0.2)
            self.ser.close()
            time.sleep(0.2)

            self.ser = serial.Serial(timeout=1)
            self.ser.port     = self.config['port']
            self.ser.baudrate = 9600
            self.ser.open()

            time.sleep(0.2)

            ok, resp = self.sendCmd("g r0x90\n")
            if not ok:
                logger.error("Error getting Copley baudrate")
                return False

            logger.info(f"Current Copley baudrate = 9600, ...now setting to {self.config['baudrate']}")

            self.sendCmd(f"s r0x90 {self.config['baudrate']}\n")
            self.ser.close()
            time.sleep(0.2)

            self.ser = serial.Serial(timeout=1)
            self.ser.port     = self.config['port']
            self.ser.baudrate = self.config['baudrate']
            self.ser.open()

            time.sleep(0.2)

            logger.info(f"Baudrate set to {self.config['baudrate']}...verifying")

            ok, resp = self.sendCmd("g r0x90\n")
            if not ok:
                logger.error("Error getting Copley baudrate")
                return False
            logger.info(f"Current Copley baudrate = {self.config['baudrate']}")
        else:
            logger.info(f"Current Copley baudrate = {self.config['baudrate']}")

        logger.info("Copley MotionController init complete.  Current Position = ")
        for axis in self.config['axis_list']:
            print(f"{axis}: {self.getCurPos(axis)}")

        self.setDefaultMoveParams()
        return True

    def setDefaultMoveParams(self):
        for axis in self.axis_list:
            logger.info(f"Set the trajectory generator to absolute move, trapezoidal profile for axis {axis}")
            ok, resp = self.sendCmd(f".{axis} s r0xc8 0\n")
            if not ok:
                logger.error(f"Error setting traj gen for axis {axis}")
                return False

            logger.info(f"Set maximum velocity to {self.default_max_velocity} for axis {axis}")
            ok, resp = self.sendCmd(f".{axis} s r0xcb {self.default_max_velocity}\n")
            if not ok:
                logger.error(f"Error setting maximum velocity for axis {axis}")
                return False

            logger.info(f"Set maximum accel to {self.default_max_accel} for axis {axis}")
            ok, resp = self.sendCmd(f".{axis} s r0xcc {self.default_max_accel}\n")
            if not ok:
                logger.error(f"Error setting maximum accel for axis {axis}")
                return False

            logger.info(f"Set maximum decel to {self.default_max_accel} for axis {axis}")
            ok, resp = self.sendCmd(f".{axis} s r0xcd {self.default_max_accel}\n")
            if not ok:
                logger.error(f"Error setting maximum decel for axis {axis}")
                return False

            logger.info(f"Enable the drive in Programmed Position (Trajectory Generator) Mode for axis {axis}")
            ok, resp = self.sendCmd(f".{axis} s r0x24 21\n")
            if not ok:
                logger.error(f"Error setting Programmed Position (Trajectory Generator) Mode for axis {axis}")
                return False

            return True

    def moveToPos(self, axis, pos, waitForStop=True, vel=-1, acc=-1):
        if pos < self.limits_min[axis] or pos >= self.limits_max[axis]:
            logger.error(f"Pos out of range. Axis: {axis}, Pos: {pos}");
            return -999;

        self.sendCmd(".%s s r0xc8 0\n" % (axis))
        self.sendCmd(".%s s r0xca %d\n" % (axis, pos))

        if vel > 0:
            self.sendCmd(".%s s r0xcb %d\n" % (axis, vel))
        if acc > 0:
            self.sendCmd(".%s s r0xcc %d\n" % (axis, acc))
            self.sendCmd(".%s s r0xcd %d\n" % (axis, acc))

        self.sendCmd(".%s s r0x24 21\n" % (axis))
        logger.debug("Staring pos = %d, starting move to %d" % (self.getCurPos(axis), pos))
        self.sendCmd(".%s t 1\n" % (axis))
        if waitForStop:
            self.waitForStop([axis])
            ok, cur_pos = self.sendCmd(".%s g r0x32\n" % (axis))
            final_pos = self.getCurPos(axis)
            logger.debug("\aMove complete.  Final pos = %d" % (final_pos))
            return final_pos
        else:
            return pos

    def moveToPos2(self, pos1, pos2, waitForStop=True, vel=-1, acc=-1):
        if pos1 < self.limits_min['a'] or pos1 >= self.limits_max['a']:
            logger.error(f"Pos1 out of range. Pos: {pos1}");
            return -999;
        if pos2 < self.limits_min['b'] or pos2 >= self.limits_max['b']:
            logger.error(f"Pos2 out of range. Pos: {pos2}");
            return -999;

        self.sendCmd(".a s r0xc8 0\n")
        self.sendCmd(".b s r0xc8 0\n")

        self.sendCmd(".a s r0xca %d\n" % (pos1))
        self.sendCmd(".b s r0xca %d\n" % (pos2))

        if vel > 0:
            self.sendCmd(".a s r0xcb %d\n" % (vel))
            self.sendCmd(".b s r0xcb %d\n" % (vel))
        if acc > 0:
            self.sendCmd(".a s r0xcc %d\n" % (acc))
            self.sendCmd(".a s r0xcd %d\n" % (acc))
            self.sendCmd(".b s r0xcc %d\n" % (acc))
            self.sendCmd(".b s r0xcd %d\n" % (acc))

        self.sendCmd(".a s r0x24 21\n" )
        self.sendCmd(".b s r0x24 21\n" )
        logger.debug("Staring pos = [%d, %d], starting move to [%d, %d]" % (self.getCurPos('a'), self.getCurPos('b'), pos1, pos2))
        self.sendCmd("t 0x3001\n")
        if waitForStop:
            self.waitForStop(['a', 'b'])
            final_pos1, final_pos2 = (self.getCurPos('a'), self.getCurPos('b'))
            logger.debug("\aMove complete.  Final pos = [%d, %d]" % (final_pos1, final_pos2))
            return (final_pos1, final_pos2)
        else:
            return pos1, pos2

    def moveToLoc(self, axis, loc_mm, waitForStop=True, vel=-1, acc=-1 ):
        return self.moveToPos(axis, (loc_mm * 1000 * self.counts_per_micron), waitForStop, vel, acc)
        
    def moveToLoc2(self, loc1_mm, loc2_mm, waitForStop=True, vel=-1, acc=-1 ):
        return self.moveToPos2((loc1_mm * 1000 * self.counts_per_micron), (loc2_mm * 1000 * self.counts_per_micron), waitForStop, vel, acc)

    def isMoving(self, axis_lst):
        moving = 0
        for axis in axis_lst:
            ok, ret = self.sendCmd(".%s g r0xa0\n" % (axis))
            moving += int(ret[2:])
        if moving > 0:
            return True
        else:
            return False

    def waitForStop(self, axis_lst):
        while self.isMoving(axis_lst):
            time.sleep(self.waitPollingTime_s)

    def getCurPos(self, axis):
        ok, ret = self.sendCmd(".%s g r0x32\n" % (axis))
        return int(ret[2:])

    def calc_vel_in_counts(self, mmps):
        return mmps*1000*self.counts_per_micron


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
            "port" : '/dev/tty.usbserial-21140',
            "baudrate" : 115200,
            "resp_delay_s": 0.020,
            "counts_per_micron": 20,
            "default_max_velocity": 10000000,
            "default_max_accel":    50000,
            "axis_list": ['a'],
            "limits_mm": [[-250.0, 250.0]]
        }

    mc = CopleyMotorController(config)

    logger.info("MotorController started...starting initialization")
    if not mc.init():
        logger.error("Could not initialize Copley Controller")
        sys.exit()

    if len(config['axis_list']) == 2:
        loc = (10,10)
        logger.info(f"Moving to {loc[0]}, {loc[1]}")
        mc.moveToLoc2(loc[0], loc[1])
    else:
        loc = (10)
        logger.info(f"Moving to {loc[0]}")
        mc.moveToLoc(loc[0])

    logger.info("Closing MotorController...")
    mc.close()

if __name__ == '__main__':
    main()
