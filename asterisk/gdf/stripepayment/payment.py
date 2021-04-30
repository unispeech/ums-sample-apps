#!/usr/bin/python

"""
    Asterisk AGI Dialogflow  sample Stripe payment Application
 
    This script interacts with mysql dtabase Google Dialogflow  API and Stripe API via UniMRCP server.
    * Revision: 1
    * Date: Apr 30, 2021
    * Vendor: Universal Speech Solutions LLC
"""
import requests
import json
from config import *


class payment:

    def __init__(self):

        self.result = dict()
        self.result['status'] = False

    def createtoken(
        self,
        cardnumber,
        exp_month,
        exp_year,
        cvc,
        ):
        creditcard = {
            'card[number]': cardnumber,
            'card[exp_month]': exp_month,
            'card[exp_year]': exp_year,
            'card[cvc]': cvc,
            }

        tok = requests.post('https://api.stripe.com/v1/tokens',
                            headers={'Authorization': 'Bearer %s' % ACCESS_TOKEN}, data=creditcard)
        result = json.loads(tok.content)
        # print(result)
        return result

    def charge(
        self,
        cardnumber,
        exp_month,
        exp_year,
        cvc,
        ):
        # result = dict()
        # result['status'] = False
        charged = None
        data = self.createtoken(cardnumber, exp_month, exp_year, cvc)
        if 'error' in data:
            self.result['error_cause'] = data['error']['message']
            

        if 'id' in data:
            # print (data['id'])
            charged = {
                'amount': '100',
                'currency': 'usd',
                'source': data['id'],
                'description': 'charge without stripe module',
                
                }

            req = requests.post('https://api.stripe.com/v1/charges',headers={'Authorization': 'Bearer %s'% ACCESS_TOKEN}, data=charged)
           
            if req.content:
                content= json.loads(req.content)
                if 'error' in content:
                    self.result['error_cause'] = content['error']['message']
                else:
                    self.result['status']=True
                    self.result['state']=content['status']
                    self.result['transaction_id']=content['id']
                # print(req.content)
       
        return self.result

    def generate_response(self, result):
        # print(result)
        client_secret = None
        if result['status'] == 'requires_action':

            self.result['requires_action'] = True
            self.result['payment_client_secret'] = client_secret
        elif result['status'] == 'succeeded':

            self.result['status'] = True
        else:
            self.result['error_cause'] = 'Invalid Payment status'

        return self.result



# print(json.dumps(payment().charge("4242424242424242",6,2021,314), indent=4, sort_keys=True))
