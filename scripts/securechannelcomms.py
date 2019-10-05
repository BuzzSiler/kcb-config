from Crypto.Util.number import long_to_bytes, getRandomInteger
from Crypto.Cipher import AES
from smartcard.Exceptions import CardConnectionException

secureChannelKeyReference = "80"
clientChallengeRandALen = 8
clientChallengeRandA = getRandomInteger(64)


from logger import logging

class SecureChannelComms():
    def __init__(self, card, key=""):
        self.__card = card
        # Convert the string into a list
        self.__key = list(bytes.fromhex(key))
        self.__secureChannel_ID = 0
        self.__serverAuthenticationData = []
        self.__serverUIDLen = 0
        self.__serverUID = []
        self.__serverChallengeRandBLen = 0
        self.__serverChallengeRandB = []
        self.__serverCryptogramLen = 0
        self.__serverCryptogram = []
        self.__SCBK = []
        self.__smac1 = []
        self.__smac2 = []
        self.__senc = []
        
        self.__clientChallengeRandA = list(bytearray(long_to_bytes(getRandomInteger(64))))

    def __list_to_hexstring(self, data):
        return ''.join(['{0:02X} '.format(i) for i in data])
        
    def __RoundUp(self, n, val):
        return ((val + (n-1)) & (~(n-1)))

    def __Pad(self, data, length):
        output = [0] * self.__RoundUp(16, length + 1)
        output[:len(data)] = list(data)
        output[length] = 0x80
        return output

    def __transmit(self, message):
        try:
            #logging.debug("Sent: %s" % str(message))
            response, sw1, sw2 = self.__card.connection.transmit(message)
            #logging.debug("Recv: %s %d %d" % (response, sw1, sw2))
        except CardConnectionException as e:
            logging.error("Card Connection Exception: {}".format(str(e)), exc_info=True)
            raise e

        return response, sw1, sw2

    def __init_auth(self):
        CLA = 0xFF
        INS = 0x70
        P1 = 0x07
        P2 = 0x6B
        LC = 0x14
        LE = 0x00
        DATA = [0xA1, 0x12]
        DATA += [0xA0, 0x10]
        DATA += [0x80, 0x01, 0x00]
        DATA += [0x81, 0x01]
        DATA += [0x80]
        DATA += [0x82]
        DATA += [0x08]
        DATA += self.__clientChallengeRandA

        message = [CLA, INS, P1, P2, LC] + DATA + [LE]
        return message
        
    def __verify_init_auth(self, response, sw1, sw2):
        #* Strip response into parts:                                                   
        #* 9D 20                                                                        
        #* uu uu uu uu uu uu uu uu      // 8 byte UID                                   
        #* rr rr rr rr rr rr rr rr      // 8 byte RND.B                                 
        #* xx xx xx xx xx xx xx xx      // 16 byte Reader Cryptogram                    
        #* xx xx xx xx xx xx xx xx                                                      
        if sw1 == 0x90 and sw2 == 0x00:
            if response[0] == 0x9D:
                self.__secureChannel_ID = 0x81
                self.__serverAuthenticationData = response[2:2+32]
                self.__serverUIDLen = 8
                self.__serverUID = response[2:2+8]
                self.__serverChallengeRandBLen = 8
                self.__serverChallengeRandB = response[2+8:2+8+8]
                self.__serverCryptogramLen = 16
                self.__serverCryptogram = response[2+8+8:2+8+8+16]
                logging.debug("verify init auth ok")
                return True

        logging.info("verify init auth failed")
        return False
    
    def __ComputeSecureChannelBaseKey(self):
        # Complement the serverUID
        complimentUID = [ (~i & 0xff) for i in self.__serverUID ]
        inputData = self.__serverUID + complimentUID
        self.__SCBK = AES.new(bytes(self.__key), AES.MODE_ECB).encrypt(bytes(inputData))

    def __DeriveSessionKeys(self):
        inputData = [0]*16

        aes = AES.new(bytes(self.__SCBK), AES.MODE_ECB)
        inputData[0] = 0x01
        inputData[2] = self.__serverChallengeRandB[0]
        inputData[3] = self.__serverChallengeRandB[1]
        inputData[1] = 0x01
        self.__smac1 = aes.encrypt(bytes(inputData[0:16]))
        inputData[1] = 0x02
        self.__smac2 = aes.encrypt(bytes(inputData[0:16]))
        inputData[1] = 0x82
        self.__senc = aes.encrypt(bytes(inputData[0:16]))

    def __ComputeCryptogram(self, inputData):
        return AES.new(bytes(self.__senc), AES.MODE_ECB).encrypt(bytes(inputData[0:16]))

    def __CheckServerAuthentication(self):
        self.__ComputeSecureChannelBaseKey()
        self.__DeriveSessionKeys()
        cryptogramInput = self.__clientChallengeRandA + self.__serverChallengeRandB
        self.__clientCryptogram = self.__ComputeCryptogram(cryptogramInput)
        serverAuthenticationDataCheck = self.__serverUID
        serverAuthenticationDataCheck += self.__serverChallengeRandB
        serverAuthenticationDataCheck += self.__clientCryptogram
        result = serverAuthenticationDataCheck == self.__serverAuthenticationData
        return result

    def __ComputeMAC(self, iv, data, offset=0, length=0):
        if length == 0 or length % 16 != 0:
            data = self.__Pad(data, length)

        iv2 = [0]*16
        if length > 16:
            encryption = AES.new(bytes(self.__smac1), AES.MODE_CBC, bytes(iv)).encrypt(bytes(data[:len(data)-16]))
            if len(encryption) > 0:
                start = len(encryption) - 16
                iv2 = encryption[start:start+16]
        else:
            iv2 = iv

        start = len(data) - 16
        value = AES.new(bytes(self.__smac2), AES.MODE_CBC, bytes(iv2)).encrypt(bytes(data[start:start+16]))
        return value


    def __Wrap(self, data):
        data = self.__Pad(data, len(data))
        iv = self.__rmac
        comp_iv = [(~i & 0xFF) for i in iv]
        enc_payload = AES.new(bytes(self.__senc), AES.MODE_CBC, bytes(comp_iv)).encrypt(bytes(data))
        self.__cmac = self.__ComputeMAC(self.__rmac, enc_payload, length=len(enc_payload))
        mac = list(self.__cmac)
        result = list(enc_payload) + mac
        return result

    def __Unwrap(self, data):
        if len(data) % 16 != 0 or len(data) < 16:
            return None

        iv = self.__cmac
        length = len(data) - 16
        mac = self.__ComputeMAC(iv, data[:length], length=length)
        mac_matches = list(mac) == data[length:length+len(mac)]

        if not mac_matches:
            return None

        output = None
        if len(data) > 16:
            iv = self.__cmac
            comp_iv = [(~i & 0xFF) for i in iv]
            decrypted_data = AES.new(bytes(self.__senc), AES.MODE_CBC, bytes(comp_iv)).decrypt(bytes(data[:len(data)-16]))

            # Strip off padding
            # xx xx xx xx xx xx xx xx xx 80 00 00 00 00 00 00
            # The 80 is a marker, find the 80 and keep everything before it
            # Im not sure how 80 will never be part of the data though
            found_terminator = [i for i, j in enumerate(list(decrypted_data)) if j == 128]
            if found_terminator and len(found_terminator) > 0:
                index = max(found_terminator)
                output = decrypted_data[:index]

        self.__rmac = mac
        return output

    def __ComputeClientAuthenticationData(self):
        cryptogramInput = self.__serverChallengeRandB
        cryptogramInput += self.__clientChallengeRandA
        self.__clientCryptogram = self.__ComputeCryptogram(cryptogramInput)
        iv = [0] * 16
        self.__cmac = self.__ComputeMAC(iv, self.__clientCryptogram, length=len(self.__clientCryptogram))
        self.__clientAuthenticationData = self.__clientCryptogram
        self.__clientAuthenticationData += self.__cmac


    def __CreateAuth2Message(self):
        CLA = 0xff
        INS = 0x70
        P1 = 0x07
        P2 = 0x6B
        LC = 0x28
        LE = 0x00
        message = [CLA, INS, P1, P2, LC]
        DATA = [0xA1,0x26]
        DATA += [0xA1,0x24]
        DATA += [0x80,0x10]
        DATA += self.__clientCryptogram
        DATA += [0x81,0x10]
        DATA += self.__cmac
        message += DATA
        message += [LE]
        return message

    def __cont_auth1(self):
        if self.__CheckServerAuthentication():
            self.__ComputeClientAuthenticationData()
            return True
        return False

    def __cont_auth2(self, response):
        if response[0] == 0x9D: # iClass SE "SAM Response" subtype
            self.__rmac = response[2:]
            iv = self.__cmac
            blankArray = [0]*1
            rmaCheck = self.__ComputeMAC(iv, blankArray)
            success = rmaCheck == bytes(self.__rmac)

            return success

    def __GetTerminateCommand(self):
        CLA  = 0xFF
        INS  = 0x70
        P1 = 0x07
        P2 = 0x6B
        LE = 0x00
        DATA = [0x04, 0xA1, 0x02, 0xA2]
        data = [CLA, INS, P1, P2] + DATA + [LE]
        enc_data_len = (len(data) >> 4) * 16 # wouldn't 0xF0 work the same?
        if len(data) % 16 != 0:
            enc_data_len += 16
        enc_data_len += 16
        ENC_DATA = self.__Wrap(data)
        LC = enc_data_len
        message = [CLA, INS, P1, P2, LC] + list(ENC_DATA) + [LE]
        return message

    def __CheckTerminateResponse(self, response, sw1, sw2):
        return sw1 == 0x90 and sw2 == 0x00 and response[0] == 0x9D

    def __CreatePacsBitsCommand(self):
        CLA = 0xFF
        INS = 0x70
        P1 = 0x07
        P2 = 0x6B
        LE = 0x00
        DATA = [0x15,0xa0,0x13,0xa1,0x11,0x80,0x1,0x4,0x84,0xc,0x2b,0x6,0x1,0x4,0x1,0x81,0xe4,0x38,0x1,0x1,0x2,0x4]
        data = [CLA, INS, P1, P2] + DATA + [LE]
        enc_data_len = (len(data) >> 4) * 16 # wouldn't 0xF0 work the same?
        if len(data) % 16 != 0:
            enc_data_len += 16
        enc_data_len += 16
        ENC_DATA = self.__Wrap(data)
        LC = enc_data_len
        message = [CLA, INS, P1, P2, LC] + list(ENC_DATA) + [LE]
        return message

    def __CheckPacsBitsCommandResponse(self, response, sw1, sw2):
        if sw1 == 0x90 and sw2 == 0x00:
            # Strip off the first two bytes of the response: 9D 20
            enc_data = response[2:]
            pacs_bits = self.__Unwrap(enc_data)
            return pacs_bits

        return None

    #----------------------------------------------------------------------------------------------

    def Open(self):
        logging.info("Opening secure channel")
        init_auth_msg = self.__init_auth()

        try:
            response, sw1, sw2 = self.__transmit(init_auth_msg)
        except Exception as e:
            logging.error("Error: sending auth message - {}".format(str(e)), exc_info=True)
            return False

        logging.debug("calling verify init auth")
        go_nogo = self.__verify_init_auth(response, sw1, sw2)
        if go_nogo:
            logging.debug("calling cont auth 1")
            if self.__cont_auth1():
                auth2_msg = self.__CreateAuth2Message()
                try:
                    response, sw1, sw2 = self.__transmit(auth2_msg)
                except Exception as e:
                    logging.error("Error: establishing secure comms - {}".format(str(e)), exc_info=True)
                    return False

                if (sw1 == 0x90 and sw2 == 0x00):
                    if self.__cont_auth2(response):
                        logging.info("secure channel open")
                        return True
                else:
                    logging.warn("Error in auth2 message response")
                return False
        else:
            logging.warn("verify init auth failed")
            return False

    def Close(self):
        command = self.__GetTerminateCommand()
        try:
            response, sw1, sw2 = self.__transmit(command)
        except Exception as e:
            logging.error("Error: sending terminate command - {}".format(str(e)), exc_info=True)
            return False

        if self.__CheckTerminateResponse(response, sw1, sw2):
            logging.info("Secure session closed")
            return True
        else:
            logging.warn("Failed to terminate secure session")
            return False

    def GetPacsBits(self):
        command = self.__CreatePacsBitsCommand()
        try:
            response, sw1, sw2 = self.__transmit(command)
        except Exception as e:
            logging.error("Error: sending PACS command - {}".format(str(e)), exc_info=True)
            return None

        pacs_bits = self.__CheckPacsBitsCommandResponse(response, sw1, sw2)
        if pacs_bits is not None:
            return pacs_bits
        return None

    def GetCardNumber(self):
        pacs_bits = self.GetPacsBits()
        if pacs_bits is not None and len(pacs_bits) == 10 and pacs_bits[1] == 0x06:
            # Bytes 4 through 7 contain the card number
            card_number_bytes = list(pacs_bits[4:8])
            if card_number_bytes is not None and len(card_number_bytes) == 4:
                card_number_bytes[0] = card_number_bytes[0] & 0x03
                str_value = ''.join(["{0:02X}".format(i) for i in card_number_bytes])
                card_number = str(int(str_value, 16) >> 6)
                logging.info("Read card number: %s" % card_number)
                return card_number

        return None
#--------------------------------------------------------------------------------------------------
# EOF
