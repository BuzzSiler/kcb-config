import sys

from smartcard.CardType import ATRCardType, AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes
from smartcard.Exceptions import CardRequestTimeoutException

from securechannelcomms import SecureChannelComms
from logger import logging

SCRIPT_ERROR_BASE = 100
APP_ERROR_BASE = 200

# One and only one argument is allowed, the key
if len(sys.argv) != 2:
    logging.fatal("incorrect arguments")
    sys.exit(SCRIPT_ERROR_BASE+1)

key = sys.argv[1]
if len(key) != 32:
    logging.fatal("invalid arguments")
    sys.exit(SCRIPT_ERROR_BASE+2)

cs = None
result = ""

try:
    ct = ATRCardType(toBytes("3B 8F 80 01 80 4F 0C A0 00 00 03 06 0A 00 1F 00 00 00 00 7D"))
    cr = CardRequest(timeout=1, cardType=ct)
    cs = cr.waitforcard()
    cs.connection.connect()
    logging.info("connected")
    scc = None
    try:
        scc = SecureChannelComms(cs, key)
        scc.Open()
        result = scc.GetCardNumber()
    except:
        logging.fatal("Error establishing secure channel")
    finally:
        if scc:
            scc.Close()

except CardRequestTimeoutException:
    logging.fatal("Card Request Timeout")
    sys.exit(APP_ERROR_BASE+1)
finally:
    if cs:
        cs.connection.disconnect()
        logging.info("disconnected")

sys.stdout.write(result)
sys.stdout.flush()