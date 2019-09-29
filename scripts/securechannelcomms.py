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
# Testing
#--------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    scc = SecureChannelComms(None)
    scc._SecureChannelComms__rmac = [0x50,0x3b,0x87,0xff,0xc8,0xc1,0xa0,0x83,0x7f,0x58,0x70,0x9a,0x80,0x54,0x8f,0x5e]
    scc._SecureChannelComms__smac1 = [0x47,0xb0,0xdd,0x5e,0x2d,0x91,0xd7,0xab,0x24,0x48,0x54,0x5c,0xec,0x62,0x59,0x7]
    scc._SecureChannelComms__smac2 = [0x79,0xf6,0xc6,0x3d,0x1c,0xdf,0x60,0x94,0x97,0xcf,0xe7,0xab,0x8b,0x28,0x9a,0x49]
    scc._SecureChannelComms__senc = [0x11,0x5d,0xe0,0xe5,0xa,0x15,0x4b,0x23,0x7,0x80,0x17,0x5,0xd2,0xce,0xdd,0xf0]
    command = scc._SecureChannelComms__CreatePacsBitsCommand()
    # FF 70 07 6B 30 A7 B4 5C 52 EA A9 2C 08 3E 3D 5D FF EB CE 5A 31
    #                A3 66 66 A1 F0 9A 7F AC 86 18 91 ED 27 E5 48 D0
    #                1E E5 CB BB 70 2B 4B B2 19 9F 69 69 84 6D FF 91 00

    scc = SecureChannelComms(None)
    response = [0x9d,0x20,0xb1,0xbc,0x4c,0x78,0x3a,0x13,0xbf,0xfd,0x71,0xaa,0x27,0x9c,0xaa,0x1a,0x68,0x71,0xc9,0xaf,0x9b,0x8,0xf5,0x4f,0x56,0xcb,0x9c,0x3c,0xcd,0xf5,0x42,0x37,0x75,0xc4]
    sw1 = 0x90
    sw2 = 0x00
    scc._SecureChannelComms__cmac = [0xbd,0x74,0xd6,0x59,0xd9,0x3f,0x0,0x6f,0xbd,0xa1,0x94,0x72,0xa5,0x74,0x5f,0xfd]
    scc._SecureChannelComms__senc = [0x87,0x98,0x82,0xb3,0xbd,0x65,0xcb,0x6a,0x79,0x58,0x55,0xf3,0x39,0xe4,0x37,0xf6]
    scc._SecureChannelComms__smac1 = [0x3,0x55,0xf,0x1a,0x3b,0x13,0x1c,0x71,0xa7,0x1d,0x25,0x9f,0xd6,0xd4,0x9a,0x7b]
    scc._SecureChannelComms__smac2 = [0xc0,0x85,0xc7,0x27,0xc4,0xe0,0x19,0x2f,0x27,0xb3,0x83,0xfe,0xbe,0xb3,0xb,0x2d]
    scc._SecureChannelComms__CheckPacsBitsCommandResponse(response, sw1, sw2)


    print("Test __ComputeSecureChannelBaseKey")
    '''
    [INPUT] 13 51 27 7E 0E 12 4A 22
    [DUMP] 9D E0 69 E0 22 0C 4E AC 45 CE 7C 4A 7D 5A FA 40
    '''
    scc = SecureChannelComms(None)
    scc._SecureChannelComms__serverUID = [0x13,0x51,0x27,0x7E,0x0E,0x12,0x4A,0x22]
    scc._SecureChannelComms__ComputeSecureChannelBaseKey()


    print("Test __DeriveSessionKeys")
    # [SCBK] 9D E0 69 E0 22 0C 4E AC 45 CE 7C 4A 7D 5A FA 40
    # [SRANDB] 64 4E DB D1 2A A0 57 F4
    scc = SecureChannelComms(None)
    scc._SecureChannelComms__SCBK = [0x9D,0xE0,0x69,0xE0,0x22,0x0C,0x4E,0xAC,0x45,0xCE,0x7C,0x4A,0x7D,0x5A,0xFA,0x40]
    scc._SecureChannelComms__serverChallengeRandB = [0x64,0x4E,0xDB,0xD1,0x2A,0xA0,0x57,0xF4]
    scc._SecureChannelComms__DeriveSessionKeys()


    print("Test __ComputeCryptogram")
    # [SENC] self.__senc
    # [CCRANDA] self.__clientChallengeRandA
    # [SCRANDB] 64 4E DB D1 2A A0 57 F4
    scc = SecureChannelComms(None)
    scc._SecureChannelComms__senc = [0x9C,0x7F,0x22,0xBA,0xE5,0x8A,0xDC,0x9F,0x07,0xFA,0xCA,0x9E,0x79,0x8A,0x7E,0x07]
    scc._SecureChannelComms__clientChallengeRandA = [0xE9,0xAA,0xE0,0xBE,0xA1,0x74,0x93,0x14]
    scc._SecureChannelComms__serverChallengeRandB = [0x64,0x4E,0xDB,0xD1,0x2A,0xA0,0x57,0xF4]
    cryptogram_input = scc._SecureChannelComms__clientChallengeRandA + scc._SecureChannelComms__serverChallengeRandB
    result = scc._SecureChannelComms__ComputeCryptogram(cryptogram_input)
    print(''.join(["{0:02X} ".format(i) for i in result]))

    print("Test __CheckServerAuthentication")
    # [CCRANDA] [0xE9,0xAA,0xE0,0xBE,0xA1,0x74,0x93,0x14]
    # [SUID] [0x13,0x51,0x27,0x7E,0x0E,0x12,0x4A,0x22]
    # [SCRANDB] [0x64,0x4E,0xDB,0xD1,0x2A,0xA0,0x57,0xF4]
    scc = SecureChannelComms(None)
    scc._SecureChannelComms__serverAuthenticationData = [0x13,0x51,0x27,0x7e,0xe,0x12,0x4a,0x22,0xd7,0x95,0xb8,0x92,0x92,0xe9,0xd0,0xb0,0xb3,0x21,0xb6,0xad,0x31,0x8a,0x3b,0x1d,0xbd,0x93,0x4,0x7f,0x31,0x4d,0x7f,0x70]
    #[0x13,0x51,0x27,0x7e,0xe,0x12,0x4a,0x22,0x84,0x10,0xac,0x42,0xa2,0x45,0xaa,0x5f,0x82,0x3f,0x15,0xc3,0x44,0xcb,0x62,0x7b,0x9c,0x70,0x8,0x84,0xb0,0x36,0x9a,0xa0]
    #[0x13,0x51,0x27,0x7E,0x0E,0x12,0x4A,0x22,0x64,0x4E,0xDB,0xD1,0x2A,0xA0,0x57,0xF4,0xD6,0xFC,0x2B,0x56,0x43,0xF5,0x1E,0x5B,0x5F,0x98,0x37,0xFC,0x39,0x4F,0x9D,0x18]
    scc._SecureChannelComms__serverUID = [0x13, 0x51, 0x27, 0x7E, 0x0E, 0x12, 0x4A, 0x22]
    scc._SecureChannelComms__clientChallengeRandA = [0xab,0xd4,0x2f,0x3a,0x82,0x52,0x24,0x69]
    #[0x9e,0x78,0x8b,0x8f,0x85,0xc1,0xd4,0x45]
    #[0xE9, 0xAA, 0xE0, 0xBE, 0xA1, 0x74, 0x93, 0x14]
    scc._SecureChannelComms__serverChallengeRandB = [0xd7,0x95,0xb8,0x92,0x92,0xe9,0xd0,0xb0]
    #[0x84,0x10,0xac,0x42,0xa2,0x45,0xaa,0x5f]
    #[0x64, 0x4E, 0xDB, 0xD1, 0x2A, 0xA0, 0x57, 0xF4]
    scc._SecureChannelComms__CheckServerAuthentication()

#--------------------------------------------------------------------------------------------------
# EOF
