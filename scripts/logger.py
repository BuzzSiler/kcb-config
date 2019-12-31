import logging
from logging.handlers import RotatingFileHandler

LOG_FILE="/home/pi/kcb-config/logs/securecard.log"

# Setup logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=LOG_FILE)

handler = RotatingFileHandler(LOG_FILE, 
                              maxBytes=10*1024*1024, 
                              backupCount=10)

logging.getLogger().addHandler(handler)
