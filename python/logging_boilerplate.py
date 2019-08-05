#-------------------------------------------------
# Simple logging with file handler...

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d (%(name)16s) [%(levelname)7s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('my_log_file.log', mode='a')
    ])
logger = logging.getLogger()

host, port = '192.168.0.22', 200
logger.info("Starting loop cycle...")
logger.warning("High temp exceeding threshold!")
logger.error(f"Error connecting to {host}:{port}")
logger.critical("House is on fire, get out")
logger.debug("We are here...")

#-------------------------------------------------
# Colored logging:
import logging
import coloredlogs # pip install

fmt = "%(asctime)s.%(msecs)03d (%(name)16s) [%(levelname)7s]: %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=fmt,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('my_log_file.log', mode='a')
    ])
logger = logging.getLogger()
coloredlogs.install(level='DEBUG', fmt=fmt, 
    field_styles=coloredlogs.DEFAULT_FIELD_STYLES, level_styles=coloredlogs.DEFAULT_LEVEL_STYLES)

host, port = '192.168.0.22', 200
logger.info("Starting loop cycle...")
logger.warning("High temp exceeding threshold!")
logger.error(f"Error connecting to {host}:{port}")
logger.debug("We are here...")

#-------------------------------------------------
# Logging with config file:

import logging, logging.config
import coloredlogs

# open up and read the logging config file
try:
    with open(config["logger_config_path"], 'rt') as logger_config_file:
        logger_config = json.load(logger_config_file)
    if config["debug"] == True:
        logger_config["root"]["level"] = "DEBUG"
    logging.config.dictConfig(logger_config)
    try:
        fmt = logger_config["formatters"]["simple"]["format"]
        field_styles = logger_config["coloredlogs_field_styles"]
        level_styles = logger_config["coloredlogs_level_styles"]
    except:
        print("Using defaults for coloredlogs")
        fmt = "%(asctime)s.%(msecs)03d (%(name)16s) [%(levelname)s]: %(message)s"
        field_styles = coloredlogs.DEFAULT_FIELD_STYLES
        level_styles = coloredlogs.DEFAULT_LEVEL_STYLES
except Exception as e:
    print( str(e) )
    print("Warning! Problem with Logging config file: %s" % (config["logger_config_path"]))
    print("Creating logger with default settings")
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("dif_client")
coloredlogs.install(level='DEBUG', fmt=fmt, field_styles=field_styles, level_styles=level_styles)

logger.info('DIF Client started...')
logger.debug('>>>> Debug log level on...')

#————————————
# Logging config json:
{
"version": 1,
"disable_existing_loggers": false,
"formatters": {
    "simple": {
        "format": "%(asctime)s.%(msecs)03d (%(name)16s) [%(levelname)s]: %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"
    }
},

"handlers": {
    "console": {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "formatter": "simple",
        "stream": "ext://sys.stderr"
    },

    "rotating_file_handler": {
        "class": "logging.handlers.TimedRotatingFileHandler",
        "level": "DEBUG",
        "formatter": "simple",
        "filename": "../log/dif_client.log",
        "when": "midnight",
        "backupCount": 20,
        "encoding": "utf8",
        "utc": false
    }
},

"coloredlogs_field_styles": {"hostname": {"color": "magenta"}, "programname": {"color": "cyan"}, "name": {"color": "blue"}, "levelname": {"color": "magenta", "bold": false}, "asctime": {"color": "white"}},

"coloredlogs_level_styles":  {"info": {"color": "white", "bold": false}, "debug": {"color": "green"}, "warning": {"color": "yellow"}, "critical": {"color": "red", "bold": true}, "error": {"color": "red"}},

"root": {
    "level": "INFO",
    "handlers": ["console", "rotating_file_handler"]
}
}

