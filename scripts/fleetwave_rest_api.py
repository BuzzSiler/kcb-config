import requests
import xmltodict
from xml.parsers.expat import ExpatError
from logger import logging


# Chevin URLs
reservation2_base = 'https://fw2.fleetwave.com/dev/script/webservices/safepak_interface.asmx/Reservation2?'
reservation2_params = 'clientName={client}&reservationNumber=&authMethod=&HIDcode=&kioskNumber={kiosk_number}&payrollNumber={payroll_number}'
reservation2_url = '{base}{params}'.format(base=reservation2_base, params=reservation2_params)

transaction_complete2_base = 'https://fw2.fleetwave.com/dev/script/webservices/safepak_interface.asmx/TransactionComplete2?'
transaction_complete2_params = 'clientName={client}&transactionNumber={transaction_number}&reservationNumber=&status={status}&question1={question_1}&question2={question_2}&question3={question_3}&UDF1=&UDF2=&UDF3=&UDF4=&UDF5=&UDF6=&authMethod=&HIDcode=&payrollNumber={payroll_number}'
transaction_complete2_url = '{base}{params}'.format(base=transaction_complete2_base, params=transaction_complete2_params)

chevin_rest = { 'Reservation2' : reservation2_url,
                'transactionComplete2' : transaction_complete2_url
              }

# Perform the Rest Request and return the return code and response document
def DoRestRequest(url):
    
    logging.debug("DoRestRequest URL: %s", url)
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: %s", errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: %s", errc)
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: %s", errt)
    except requests.exceptions.RequestException as err:
        logging.error("Oops: Something Else: %s", err)
        
    logging.debug(r.headers)
    logging.debug(r.text)
    
    try:
        doc = xmltodict.parse(r.text)
    except xmltodict.expat.ExpatError as errx:
        logging.error("Unable to create dict from xml", errx)
        return 0, None

    try:
        return_code = int(doc['Result']['ReturnCode'])
    except ValueError:
        return_code = 0
    
    logging.debug("DoRestRequest Returned: %s %s", return_code, str(doc))

    return return_code, doc

# Perform a Reservation query, return the return code, box and transaction number
def DoReservation(client_name, kiosk_number, payroll_number, action):
    '''
    Sent from FleetWave to Keybox:
        <?xml version="1.0" encoding="UTF-8"?>
        <Result xmlns="Chevin.WebServices.SafePak" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <ReturnCode>1</ReturnCode>
            <TransactionNumber>000022</TransactionNumber>
            <Box>1</Box>
            <action>ACTION</action>
            <Payrollnumber>10307</Payrollnumber>
        </Result> 
    '''
    logging.debug("ClientName: %s", client_name)
    logging.debug("KioskNumber: %s", kiosk_number)
    logging.debug("PayrollNumber: %s", payroll_number)

    return_code, doc = DoRestRequest(chevin_rest['Reservation2'].format(client=client_name, 
                                                                kiosk_number=kiosk_number, 
                                                                payroll_number=payroll_number))
    
    if return_code == 0 or doc is None:
        logging.error("Invalid return code or xml document")
        return -1, "", ""
    
    response_payrollnumber = doc['Result']['Payrollnumber']
    response_action = doc['Result']['action']
    
    if payroll_number != response_payrollnumber:
        logging.error("Invalid payroll number (expected %s, got %s)", payroll_number, response_payrollnumber)
        return -1, "", ""
        
    if  action != response_action:
        logging.error("Invalid action (expected %s, got %s)", action, response_action)
        return -1, "", ""

    box = doc['Result']['Box']
    transaction_number = doc['Result']['TransactionNumber']
    
    logging.debug("ReturnCode: %d", return_code)
    logging.debug("Box: %s", box)
    logging.debug("TransactionNumber: %s", transaction_number)
    
    return return_code, box, transaction_number

# Perform the 'Take' request
def TakeKeyReservation(client_name, kiosk_number, payroll_number):
    '''
    To retrieve keys from the keybox on an existing reservation with the Employee Payroll Number (Reservation2)
    Sent from Keybox to FleetWave using Reservation2
        clientName = HUDSON
        kioskNumber = 1
        payrollNumber = Received from HID card
    '''
    return DoReservation(client_name, kiosk_number, payroll_number, action="COLLECTING")

# Perform the 'Return' request
def ReturnKeyReservation(client_name, kiosk_number, payroll_number):
    '''
    To return keys to the keybox on an existing reservation with the Employee Payroll Number (Reservation2):
    Sent from Keybox to FleetWave using Reservation2
        clientName = HUDSON
        kioskNumber = 1
        payrollNumber = Received from HID card
    '''
    return DoReservation(client_name, kiosk_number, payroll_number, action="RETURNING")

# Peform a Transaction Complete query, return the return code
def DoTransactionComplete(client_name, transaction_number, payroll_number, answer1="", answer2="", answer3=""):
    '''
    Sent from FleetWave to Keybox
        <?xml version="1.0" encoding="UTF-8"?>
        <Result xmlns="Chevin.WebServices.SafePak" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <ReturnCode>1</ReturnCode>
            <TransactionNumber>000023</TransactionNumber>
            <Payrollnumber>10307</Payrollnumber>
            </Result>
    '''
    logging.debug("ClientName: %s", client_name)
    logging.debug("TransactionNumber: %s", transaction_number)
    logging.debug("PayrollNumber: %s", payroll_number)
    logging.debug("Answer1: %s", answer1)
    logging.debug("Answer2: %s", answer2)
    logging.debug("Answer3: %s", answer3)

    return_code, doc = DoRestRequest(chevin_rest['transactionComplete2'].format(client=client_name, 
                                                                                transaction_number=transaction_number, 
                                                                                status="SUCCESS", 
                                                                                question_1=answer1, 
                                                                                question_2=answer2, 
                                                                                question_3=answer3, 
                                                                                payroll_number=payroll_number))

    if return_code == 0 or doc is None:
        logging.error("Invalid return code or xml document")
        return -1

    response_transactionnumber = doc['Result']['TransactionNumber']
    response_payrollnumber = doc['Result']['Payrollnumber']

    if  transaction_number != response_transactionnumber:
        logging.error("Invalid transaction number (expected %s, got %s)", transaction_number, response_transactionnumber)
        return -1
    
    if payroll_number != response_payrollnumber:
        logging.error("Invalid payroll number (expected %s, got %s)", payroll_number, response_payrollnumber)
        return -1

    logging.debug("ReturnCode: %d", return_code)
    logging.debug("TransactionNumber: %s", transaction_number)
    logging.debug("PayrollNumber: %s", payroll_number)
    
    return return_code

# Perform a 'Take' transaction complete
def TakeKeyTransactionComplete(client_name, transaction_number, payroll_number):
    '''
    Sent from Keybox to FleetWave using TransactionComplete2
        clientName = HUDSON
        transactionNumber = Received from TakeKeyReservation2
        status = SUCCESS
        payrollNumber = Received from HID card
    '''
    return DoTransactionComplete(client_name, transaction_number, payroll_number)

# Perform a 'Return' transaction complete
def ReturnKeyTransactionComplete(client_name, transaction_number, payroll_number, answer1, answer2, answer3):
    '''
    Sent from Keybox to FleetWave using TransactionComplete2
        clientName = HUDSON
        transactionNumber = Received from ReturnKeyReservation2
        status = SUCCESS
        question1 = answer to question 1
        question2 = answer to question 2
        question3 = answer to question 3
        payrollNumber = Receieved from HID card
    '''
    return DoTransactionComplete(client_name, transaction_number, payroll_number, answer1, answer2, answer3)
