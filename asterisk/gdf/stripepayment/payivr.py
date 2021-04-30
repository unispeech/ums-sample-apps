#!/usr/bin/python
"""
    Asterisk AGI Dialogflow  sample Stripe payment Application
 
    This script interacts with mysql dtabase Google Dialogflow  API and Stripe API via UniMRCP server.
    * Revision: 1
    * Date: Apr 30, 2021
    * Vendor: Universal Speech Solutions LLC
"""
import sys
from datetime import datetime
from asterisk.agi import *
from payment import *
from store_transactions import *
from config import *

class GdfApp:

    """A class representing Dialogflow application"""

    def __init__(self, options):
        """Constructor"""
        self.options = options
        self.project_id = agi.get_variable('GDF_PROJECT_ID')
        self.status = None
        self.cause = None
        
        
    def trigger_payment_intent(self):
        """Triggers a welcome intent"""
        grammar = 'builtin:event/payment'
        separator = '?'

        if self.project_id:
            grammar = self.append_grammar_parameter(
                grammar, "projectid", self.project_id, separator)
            separator = ';'

        self.prompt = ' '
        self.grammars = grammar
        self.synth_and_recog()

    def detect_intent(self):
        """Performs a streaming intent detection"""
        self.grammars = "%s,%s" % (
            self.compose_speech_grammar(), self.compose_dtmf_grammar())
        self.synth_and_recog()

    def synth_and_recog(self):
        """This is an internal function which calls SynthAndRecog"""
        if not self.prompt:
            self.prompt = ' '
        args = "\\\"%s\\\",\\\"%s\\\",%s" % (
            self.prompt, self.grammars, self.options)
        agi.set_variable('RECOG_STATUS', '')
        agi.set_variable('RECOG_COMPLETION_CAUSE', '')
        self.action = None
        agi.appexec('SynthandRecog', args)
        self.status = agi.get_variable('RECOG_STATUS')
        agi.verbose('got status %s' % self.status)
        if self.status == 'OK':
            self.cause = agi.get_variable('RECOG_COMPLETION_CAUSE')
            agi.verbose('got completion cause %s' % self.cause)
        else:
            agi.verbose('Recognition completed abnormally')

    def compose_speech_grammar(self):
        """Composes a built-in speech grammar"""
        grammar = 'builtin:speech/transcribe'
        separator = '?'
        if self.project_id:
            grammar = self.append_grammar_parameter(
                grammar, "projectid", self.project_id, separator)
            separator = ';'
        return grammar

    def compose_dtmf_grammar(self):
        """Composes a built-in DTMF grammar"""
        grammar = 'builtin:dtmf/digits'
        separator = '?'
        if self.project_id:
            grammar = self.append_grammar_parameter(
                grammar, "projectid", self.project_id, separator)
            separator = ';'
        return grammar

    def compose_event_grammar(self, intent,value):
        """Composes a built-in event grammar"""
        grammar = 'builtin:event/%s' % intent
        separator = '?'
        if value:
            grammar = self.append_grammar_parameter(
                grammar, "value", value, separator)
            separator = ';'
        if self.project_id:
            grammar = self.append_grammar_parameter(
                grammar, "projectid", self.project_id, separator)
            separator = ';'
        return grammar

    def append_grammar_parameter(self, grammar, name, value, separator):
        """Appends a name/value parameter to the specified grammar"""
        grammar += "%s%s=%s" % (separator, name, value)
        return grammar

    def get_callerid(self):
        """Retrieves caller id from Asterisk"""
        return agi.env['agi_callerid']

    def get_callid(self):
        """Retrieves unique call id from Asterisk"""
        return agi.env['agi_uniqueid']


    def store_starttime(self):
        """Stores current time as starttime"""
        self.starttime = datetime.now()

    def store_endtime(self):
        """Stores current time as endtime"""
        self.endtime = datetime.now()

    def get_fulfillment_text(self):
        """Retrieves fulfillment text from the data returned by bot"""
        fulfillment_text = agi.get_variable(
            'RECOG_INSTANCE(0/0/fulfillment_text)')
        if isinstance(fulfillment_text, str):
            fulfillment_text = unicode(fulfillment_text, 'utf-8')
        agi.verbose('got fulfillment_text %s' % fulfillment_text)
        return fulfillment_text

    def get_query_text(self):
        """Retrieves query text from the data returned by bot"""
        query_text = agi.get_variable('RECOG_INSTANCE(0/0/query_text)')
        agi.verbose('got query_text %s' % query_text)
        return query_text

    def get_action(self):
        """Retrieves action from the data returned by bot"""
        action = agi.get_variable('RECOG_INSTANCE(0/0/action)')
        agi.verbose('got action %s' % action)
        return action

    def get_handover_target(self):
        """Retrieves handover target returned by bot"""
        handover_target = agi.get_variable(
            'RECOG_INSTANCE(0/0/parameters/handover_target)')
        agi.verbose('got handover_target %s' % handover_target)
        return handover_target

    def check_dialog_completion(self):
        """Checks wtether the dialog is complete"""
        end_of_conversation = agi.get_variable(
            'RECOG_INSTANCE(0/0/diagnostic_info/end_conversation)')
        complete = False
        if end_of_conversation == 'true':
            agi.verbose('got end_of_conversation %s' % end_of_conversation)
            complete = True
        return complete

   
    def collectcardinfo(self):
        """Collect card info from response"""
        all_present = agi.get_variable('RECOG_INSTANCE(0/0/all_required_params_present)')
        agi.verbose('got required params status %s'% all_present)
        if all_present:
            self.cardnumber = agi.get_variable( 'RECOG_INSTANCE(0/0/parameters/card_number)')
            self.exp_month = agi.get_variable( 'RECOG_INSTANCE(0/0/parameters/exp_month)')
            self.exp_year = agi.get_variable( 'RECOG_INSTANCE(0/0/parameters/exp_year)')
            self.cardcvc = agi.get_variable( 'RECOG_INSTANCE(0/0/parameters/cardcvc)')

            agi.verbose('got caller card number %s exp_month %s exp_year %s cardcvc %s' %(self.cardnumber,self.exp_month,self.exp_year,self.cardcvc))
        
        
    def chargeorredirect(self):
        """Charge and redirect to expected intent """
        value=None
        result = stripe.charge(self.cardnumber,self.exp_month,self.exp_year,self.cardcvc)
        if result['status'] == False:
            agi.verbose('got caller card result %s' %result)
            res = store_payment.storeResult(self.get_callerid(),self.get_callid(),result['error_cause'],None)
            if res['status']==True:
                agi.verbose('got database result %s' %res['string'])
            else:
                agi.verbose('got database result %s' %res['error_cause'])
            value = result['error_cause']
            intent = 'creditcard-check-failure'
            
            agi.verbose('failed to trigger %s intent' % self.get_query_text())
        else:
            res = store_payment.storeResult(self.get_callerid(),self.get_callid(),result['state'],result['transaction_id'])
            if res['status']==True:
                agi.verbose('got database result %s' %res['string'])
            else:
                agi.verbose('got database result %s' %res['error_cause'])
            intent = 'payment-success'

        self.transfer_to_intent(intent, value)
    

    def checkfailureandredirect(self):
        all_present = agi.get_variable('RECOG_INSTANCE(0/0/all_required_params_present)')
        if  all_present:
            value = agi.get_variable( 'RECOG_INSTANCE(0/0/parameters/card_number)') 
            intent = 'payment'
            self.transfer_to_intent(intent, value)

    def transfer_to_intent(self,intent,value):
        """Checks appointment date"""
        self.prompt = ' '
        self.grammars = self.compose_event_grammar(intent,value)
        self.synth_and_recog()

        if self.status != 'OK' or self.cause != '000':
            agi.verbose('failed to trigger %s intent' % intent)
            return

        self.prompt = self.get_fulfillment_text()

    def run(self):
       
        """Interacts with the caller in a loop until the dialog is complete"""
        self.trigger_payment_intent()
        if self.status != 'OK' or self.cause != '000':
            agi.verbose('failed to trigger welcome intent')
            return

        processing = False
        self.prompt = self.get_fulfillment_text()
        if self.prompt:
            processing = True

        while processing:
            self.detect_intent()
            processing = True
            if self.status == 'OK':
                if self.cause == '000':
                    self.prompt = self.get_fulfillment_text()
                    self.action = self.get_action()
                    
                    if self.check_dialog_completion():
                        processing = False
                    if self.action =='cardinfo':
                        self.collectcardinfo()
                    if self.action =='payment.payment-yes':
                        self.chargeorredirect()
                    if self.action =='payment.creditcard-check-failure':
                        self.checkfailureandredirect()
                    

                elif self.cause != '001' and self.cause != '002':
                    processing = False
            elif self.cause != '001' and self.cause != '002':
                processing = False

        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)



agi = AGI()
store_payment = storTransactions()
stripe = payment()
options = 'plt=1&b=1&sct=1000&sint=15000&nit=10000'
gdf_app = GdfApp(options)

gdf_app.run()

agi.verbose('exiting')
