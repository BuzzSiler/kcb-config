from __future__ import print_function
import sys
from time import sleep

from smartcard.CardConnectionObserver import CardConnectionObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from securechannelcomms import SecureChannelComms

from logger import logging


HUDSON_CARD_ATR = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 0A 00 1F 00 00 00 00 7D"

class OmnikeyCardConnectionObserver( CardConnectionObserver ):
    def update( self, cardconnection, ccevent ):
        if 'connect'==ccevent.type:
            print('connecting to ' + cardconnection.getReader())

        elif 'disconnect'==ccevent.type:
            pass

        elif 'command'==ccevent.type:
            pass

        elif 'response'==ccevent.type:
            pass

class ReadCardNumber(CardObserver):
    def __init__(self, key=""):
        self.key = key
        self.observer = OmnikeyCardConnectionObserver()

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            if HUDSON_CARD_ATR == toHexString(card.atr):
                logging.info("Card Inserted")

                try:
                    card.connection = card.createConnection()
                    card.connection.connect()
                    card.connection.addObserver(self.observer)
                except Exception as e:
                    logging.error("Error: failure making card connection")

                # Sanity Checking
                # Simple command that returns the card UID (no secure channel required)
                #apdu = [0xff, 0xca, 0x00, 0x00, 0x00]
                #response, sw1, sw2 = card.connection.transmit(apdu)
                #print(toHexString(response))

                
                secure_channel = SecureChannelComms(card, self.key)
                if secure_channel:
                    if secure_channel.Open():
                        card_number = secure_channel.GetCardNumber()
                        sys.stdout.write(card_number + '\n')
                        sys.stdout.flush()
                        secure_channel.Close()
            

        for card in removedcards:
            if HUDSON_CARD_ATR == toHexString(card.atr):
                logging.info("Card Removed")

#--------------------------------------------------------------------------------------------------
# Main
# Description: Creates a card monitor and observer
# 
#--------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    def sleep_forever():
        while True:
            sleep(1)

    logging.info(sys.argv)
    if len(sys.argv) > 1:
        key = sys.argv[1]
        
        while True:
            logging.info("Starting ...")
            try:
                cardmonitor = CardMonitor()
                selectobserver = ReadCardNumber(key)
                cardmonitor.addObserver(selectobserver)
                sleep_forever()
            except Exception as e:
                logging.error("Error: failure during card processing - {}".format(e.message), exc_info=True)

            finally:
                # don't forget to remove observer, or the
                # monitor will poll forever...
                cardmonitor.deleteObserver(selectobserver)
                del selectobserver
                del cardmonitor
                logging.info("Stopped")
    else:
        logging.error("Error: security failure - invalid key")



#--------------------------------------------------------------------------------------------------