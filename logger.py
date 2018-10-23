from logging import handlers, getLogger, Formatter
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from os import getcwd
from config.config import device_name, logging_level

# TBD:  Move the logging configuration to a dictionary stored in a configuration file.
# On linux use tail -F (translates as tail --follow=name --retry) to follow the 
# rotating log. tail -f stops following when the log gets rotated out from under it.
#
# This logger currenlty rotates based upon file size. Python also supports timed based 
# rotation.
#

handler = None

def get_top_level_logger():

   global handler

   logger = getLogger(device_name)
   logger.setLevel(logging_level)

   handler = RotatingFileHandler(getcwd() + '/logs/mvp_iu.log', maxBytes=10*1000*1000,\
                                 backupCount=5)

   formatter = Formatter(fmt='%(asctime)s %(levelname)s %(name)s:%(message)s', 
                             datefmt='%Y-%m-%d %I:%M:%S %p %Z')
   handler.setFormatter(formatter)
   handler.setLevel(logging_level)

   logger.addHandler(handler)

   return logger

def get_sub_logger(name):
    return getLogger(device_name + '.' + name)
