import sys
import time
import argparse
import json
import logging, logging.config

from client_socket import ClientSocket

LOGGING = { 'version': 1, 'disable_existing_loggers': False,
    'formatters': { 'simple': { 'format': '%(asctime)s.%(msecs)03d [%(name)s] (%(levelname)s): %(message)s', "datefmt": "%Y-%m-%d %H:%M:%S"} },
    'handlers': { 'console': {'class': 'logging.StreamHandler', 'level':'DEBUG', 'formatter': 'simple'} },
    'root': {'handlers': ['console'],'level': 'DEBUG'}
}
logging.config.dictConfig(LOGGING)

logger = logging.getLogger("imgAPO_client")

class ImgAPO_client:
    """ ImageAPO client object"""

    def __init__(self, config):
        self.config = config

        self.debug = config["debug"]
        if not self.debug:
            logger.setLevel(logging.INFO)

        self.resp_delay_s = config["resp_delay_s"] if "resp_delay_s" in config else 0.02
        self.ipAddress = config["ipAddress"] if "ipAddress" in config else "127.0.0.1"
        self.port = config["port"] if "port" in config else 12070
        self.active_cam_idx = config["active_cam_idx"] if "active_cam_idx" in config else 0

        self.targetType = "name"
        self.active_cam_idx = 0
        self.target_found_pts = []
        self.cmd_idx = 0
        self.connected = False

        if config["auto_connect"]:
            self.connect()

    def callback_func(self, msg):
        logger.info("Rec'd: " + msg)
        if msg.find('result') >= 0:
            resp_dict = json.loads(msg)
            if "result" in resp_dict:
                result_dict = resp_dict["result"]
                if result_dict["success"] == False:
                    if 'error_str' in result_dict:
                        logger.info(f"Error! {result_dict['error_str']}")
                    else:
                        logger.info(f"Error with command!")
                else:        
                    if result_dict["result_type"] == "locate_target":
                        self.update_locate_results(result_dict)
                    elif result_dict["result_type"] == "check_targets":
                        if 'misc' in result_dict:
                            self.update_target_names(result_dict['misc'])

    def send_msg(self, msg):
        if not self.connected or not self.client.connected:
            logger.info("Client not connected; could not send msg")
            return False
        else:
            try:
                self.client.write(msg)
                return True
            except BrokenPipeError:
                logger.info("Error sending msg, connection lost")
                return False
                
    def connect(self):
        logger.info("Connecting to imgAPO server...")
        if self.connected and self.client.connected:
            logger.info("Stopping current connection")
            self.client.stop()
            time.sleep(0.1)
        self.client = ClientSocket('ClientSocket', (self.ipAddress, int(self.port)))
        logger.info("setting callback")
        self.client.setCallback(self.callback_func)
        logger.info("starting...")
        self.client.start()
        time.sleep(0.1)
        if self.client.connected:
            self.connected = True
            logger.info("Connect successful")
            return True
        else:
            self.connected = False
            logger.info("Connect failed...")
            return False

    def stop(self):
        if self.connected and self.client.connected:
            logger.info("Stopping client")
            self.client.stop()

    def select_target(self, target_name):
        cmd_dict = { "id": self.getCmdIdx(), "type": "IP",  "method": "select_target", "target_name": target_name, "buffer_type": "live", "cam_idx": self.active_cam_idx }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def check_targets(self):
        cmd_dict = { "id": self.getCmdIdx(), "type": "IP",  "method": "check_targets" }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def reload_target_library(self):
        cmd_dict = { "id": self.getCmdIdx(), "type": "IP",  "method": "reload_target_library" }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def locate_target(self, target_name):
        cmd_dict = { "id": self.getCmdIdx(), "type": "IP",  "method": "locate_target", "target_name": target_name, "buffer_type": "live", "cam_idx": self.active_cam_idx }
        cmd_str = json.dumps(cmd_dict)
        self.locates_needed = 1
        self.locates_cnt = 0

    def save_image(self, image_filename, cmd_type="IP"):
        cmd_dict = { "id": self.getCmdIdx(), "type": cmd_type,  "method": "save_image", "cam_idx": self.active_cam_idx, "image_filename": image_filename }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        ret = self.send_msg(cmd_str)

    def smt_start(self):
        cmd_dict = { "id": self.getCmdIdx(), "type": "SMT",  "method": "smt_start" }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def smt_stop(self):
        cmd_dict = { "id": self.getCmdIdx(), "type": "SMT",  "method": "smt_stop" }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def smt_query(self):
        cmd_dict = { "id": self.getCmdIdx(), "type": "SMT",  "method": "smt_query" }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def smt_set_strategy(self, strategy_name):
        cmd_dict = { "id": self.getCmdIdx(), "type": "SMT",  "method": "set_smt_strategy", "strategy_name": strategy_name }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def bufferImg(self):
        cmd_dict = { "id": self.getCmdIdx(), "type": "NOTCH_PP",  "method": "buffer_current_image", "cam_idx": self.active_cam_idx }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def find_notch_pp_dist(self, imgBufferType):
        cmd_dict = { "id": self.getCmdIdx(), "type": "NOTCH_PP",  "method": "notch_pushpin_dist", "cam_idx": self.active_cam_idx, "buffer_type": imgBufferType }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def locate_notch(self, imgBufferType):
        cmd_dict = { "id": self.getCmdIdx(), "type": "NOTCH_PP",  "method": "locate_notch", "cam_idx": self.active_cam_idx, "buffer_type": imgBufferType }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

    def clear_list(self):
        self.target_found_pts = []

    def getCmdIdx(self):
        self.cmd_idx += 1
        return self.cmd_idx

    def setupDropDetection(self, SeqLength_mm, PageLength_Ln, ScanVel_mmps):
        cmd_dict = { "id": self.getCmdIdx(), "type": "DD",  "method": "setupDD", "SeqLength_mm": SeqLength_mm, "PageLength_Ln": PageLength_Ln, "ScanVel_mmps":ScanVel_mmps }
        cmd_str = json.dumps(cmd_dict)
        logger.info(f"sending: {cmd_str}")
        self.send_msg(cmd_str)

def main():
    parser = argparse.ArgumentParser(description='Image APO GUI')
    parser.add_argument('-i', '--ip_address', type=str, default='localhost:12070', help='IPAddress:Port to connect to (def: localhost:12070)', required=False)
    args = parser.parse_args()

    ip, port = args.ip_address.split(':')

    config = {
            "debug": True,
            "ipAddress": ip,
            "port": int(port),
            "auto_connect": False
        }

    imgAPO = ImgAPO_client(config)

    if not imgAPO.connect():
        logger.error("Could not connect to imgAPO")
        sys.exit()

    imgAPO.locate_notch("live")
    time.sleep(0.5)

    imgAPO.find_notch_pp_dist("live")
    time.sleep(0.5)
    
    imgAPO.stop()

if __name__ == '__main__':
    main()
