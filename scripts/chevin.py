#--------------------------------------------------------------------------------------------------
# Description: This program interfaces to the Chevin Fleetwave web interface.  It is expected to be
# invoked from the the KeyCodeBox application.
#
# Persistent Date: This program stores the transaction number in a pickle file named, transaction.pkl.
# The transaction number is used to link a 'request' with a 'complete'.  The request/complete calls
# are back-to-back so there is no concern about intervening transactions.
#
# Invocation:
#    chevin.py take request <payroll number> -> returns <box>
#    chevin.py take complete <box> -> returns <box>
#    chevin.py return request <payroll number> -> returns <box>,<question1>,<question2>,<question3>
#    chevin.py return complete <box>,<answer1>,<answer2>,<answer3> -> returns <box>
#--------------------------------------------------------------------------------------------------

import sys
import pickle
from xml.parsers.expat import ExpatError
import json
import fleetwave_rest_api as fleetwave
from logger import logging

TRANSACTION_FILE="/home/pi/kcb-config/scripts/chevin.pkl"
SETTINGS_FILE="/home/pi/kcb-config/settings/chevin.json"

# Read the questions from a json configuration file
doc = None
client = ''
kiosk = ''
question1 = ''
question2 = ''
question3 = ''

with open(SETTINGS_FILE, 'r') as fh:
    doc = json.load(fh)
    client = doc[u'client']
    kiosk = doc[u'kiosk']
    question1 = doc[u'question1']
    question2 = doc[u'question2']
    question3 = doc[u'question3']


# Take Request, return box or None
def DoTakeRequest(card_id, filename):
    try:
        return_code, box, transaction_number, payroll_number = fleetwave.TakeKeyReservation(client, 
                                                                            kiosk, 
                                                                            card_id)
        if return_code == 1:
            transaction = {'state' : 'take', 
                           'payroll number': payroll_number,
                           'box': box,
                           'transaction number': transaction_number}
            
            pickle.dump( transaction, open( filename, "wb" ) )
            return box
        else:
            return "error"
            
    except Exception as e:
        logging.info("DoTakeRequest failed", e)
        return "failed"

# Take Complete, return box or None
def DoTakeComplete(box, filename):
    try:
        transaction  = pickle.load( open( filename, "rb" ) )
        
        if box == transaction['box']:
            transaction_number = transaction['transaction number']
            payroll_number = transaction['payroll number']
            
            return_code = fleetwave.TakeKeyTransactionComplete(client, 
                                                               transaction_number, 
                                                               payroll_number)
            return box if return_code == 1 else "error"
        else:
            return "failed"

    except Exception as e:
        logging.info("DoTakeComplete failed", e)
        return "failed"

# Return Request, return box or None
def DoReturnRequest(card_id, filename):
    try:
        return_code, box, transaction_number, payroll_number = fleetwave.ReturnKeyReservation(client, 
                                                                              kiosk, 
                                                                              card_id)
        if return_code == 1:
            transaction = {'state' : 'return', 
                           'payroll number': payroll_number,
                           'box': box,
                           'transaction number': transaction_number}
        
            pickle.dump( transaction, open( filename, "wb" ) )
            return box
        else:
            return "error"

    except Exception as e:
        logging.info("DoReturnRequest failed", e)
        return "failed"

# Return Complete, return box or None
def DoReturnComplete(box, answer1, answer2, answer3, filename):
    
    try:
        transaction = pickle.load( open( filename, "rb" ) )
        
        if box == transaction['box']:
            transaction_number = transaction['transaction number']
            payroll_number = transaction['payroll number']
            
            return_code = fleetwave.ReturnKeyTransactionComplete(client, 
                                                                 transaction_number, 
                                                                 payroll_number, 
                                                                 answer1, 
                                                                 answer2, 
                                                                 answer3)
            return box if return_code > 0 else "error"
        else:
            return "failed"
            
    except Exception as e:
        logging.info("DoReturnComplete failed", e)
        return "failed"

#--------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    
    logging.info("Inputs: %s", args)
    
    try:
        take_return, request_complete = args[:2]
    except ValueError:
        sys.stdout.write("failed")
        sys.exit(1)
    
    # chevin.py take request <code>
    #   On success, return <box>
    #   On failure, return "failed"
    if take_return == 'take' and request_complete == 'request':
        card_id = args[2]
        result = DoTakeRequest(card_id, TRANSACTION_FILE)
        sys.stdout.write(result)
        if result == "failed":
            sys.exit(1)
        
    # chevin.py take complete <box>
    #   On success, return <box>
    #   On failure, return "failed"
    elif take_return == 'take' and request_complete == 'complete':
        box = args[2]
        result = DoTakeComplete(box, TRANSACTION_FILE)
        sys.stdout.write(result)
        if result == "failed":
            sys.exit(1)
            
    # chevin.py return request 10307
    #   On success, return <box> "<question1>" "<question2>" "<question3>"
    #   On failure, return nothing
    elif take_return == 'return' and request_complete == 'request':
        card_id = args[2]
        result = DoReturnRequest(card_id, TRANSACTION_FILE)
        if result == "failed":
            sys.stdout.write(result)
            sys.exit(1)
        elif result == "error":
            sys.stdout.write(result)
        else:
            sys.stdout.write('{},{},{},{}'.format(result, question1, question2, question3))
            
    # chevin.py return complete <box> "<answer1>" "<answer2>" "<answer3>"
    #   On success, return <box>
    #   On failure, return "failed"
    elif take_return == 'return' and request_complete == 'complete':
        try:
            box, answer1, answer2, answer3 = args[2].split(',')
        except ValueError:
            sys.stdout.write("failed")
        
        result = DoReturnComplete(box, answer1, answer2, answer3, TRANSACTION_FILE)
        sys.stdout.write(result)
        if result == "failed":
            sys.exit(1)
            
    else:
        sys.stdout.write("failed")
        sys.exit(1)

#--------------------------------------------------------------------------------------------------
# EOF
