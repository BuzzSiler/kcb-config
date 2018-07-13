import logging

LOG_FILE="/home/pi/kcb-config/logs/chevin.log"

# Setup logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=LOG_FILE)
