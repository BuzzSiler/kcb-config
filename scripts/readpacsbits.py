from __future__ import print_function
from time import sleep

from smartcard.CardConnectionObserver import CardConnectionObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from securechannelcomms import SecureChannelComms

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

class ReadPacsBits(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def __init__(self):
        self.observer = OmnikeyCardConnectionObserver()

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            if HUDSON_CARD_ATR == toHexString(card.atr):
                print("Card Inserted")

            card.connection = card.createConnection()
            card.connection.connect()
            card.connection.addObserver(self.observer)

            secure_channel = SecureChannelComms(card)
            if secure_channel:
                if secure_channel.Open():
                    card_number = secure_channel.GetCardNumber()
                    print(card_number)
                    secure_channel.Close()

        for card in removedcards:
            if HUDSON_CARD_ATR == toHexString(card.atr):
                print("Card Removed")

if __name__ == '__main__':
    def sleep_forever():
        while True:
            sleep(1)

    while True:
        print("Starting ...")
        try:
            cardmonitor = CardMonitor()
            selectobserver = ReadPacsBits()
            cardmonitor.addObserver(selectobserver)
            sleep_forever()
        except Exception:
            print("Error: failure during card processing")

        finally:
            # don't forget to remove observer, or the
            # monitor will poll forever...
            cardmonitor.deleteObserver(selectobserver)
            del selectobserver
            del cardmonitor
            print("Stopped")

    #import sys
    #if 'win32' == sys.platform:
    #    print('press Enter to continue')
    #    sys.stdin.read(1)