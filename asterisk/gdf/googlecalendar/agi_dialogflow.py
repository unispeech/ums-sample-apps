#!/usr/bin/python2.7
"""

    Asterisk AGI Dialogflow  sample Calendar Application

 

    This script interacts with Google Dialogflow  API and Calendar API via UniMRCP server.

    * Revision: 1
    * Date: Apr 29, 2021
    * Vendor: Universal Speech Solutions LLC
"""



import sys
import dateutil.parser
from datetime import datetime
from asterisk.agi import *
from config import *
from gcalendar import *


class GdfApp:

    """A class representing Dialogflow application"""

    def __init__(self, options):
        """Constructor"""
        self.options = options
        self.project_id = agi.get_variable('GDF_PROJECT_ID')
        self.status = None
        self.cause = None
        self.callerid = self.get_callerid()
        self.callid = self.get_callid()
        self.starttime = None
        self.endtime = None
        

    def trigger_welcome_intent(self):
        """Triggers a welcome intent"""
        grammar = 'builtin:event/welcome'
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

    def compose_event_grammar(self, intent, value):
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

    def check_dialog_completion(self):
        """Checks wtether the dialog is complete"""
        end_of_conversation = agi.get_variable(
            'RECOG_INSTANCE(0/0/diagnostic_info/end_conversation)')
        complete = False
        if end_of_conversation == 'true':
            agi.verbose('got end_of_conversation %s' % end_of_conversation)
            complete = True
        return complete



    def get_event_dates(self):
        """Retreives event date time and duration from agent"""
        start_date_str = agi.get_variable('RECOG_INSTANCE(0/0/parameters/start_date_time)')
        if "date_time" in start_date_str:
            start_date_str = agi.get_variable('RECOG_INSTANCE(0/0/parameters/start_date_time/date_time)')

        duration_amount = agi.get_variable('RECOG_INSTANCE(0/0/parameters/duration/amount)')
        duration_unit = agi.get_variable('RECOG_INSTANCE(0/0/parameters/duration/unit)')

        end_date_str = None
        if start_date_str and duration_amount and duration_unit:
            amount = int(duration_amount)
            start_date = dateutil.parser.parse(start_date_str)
            if duration_unit == "s":
                end_date = start_date + timedelta(seconds=amount)
            elif duration_unit == "min":
                end_date = start_date + timedelta(minutes=amount)
            elif duration_unit == "h":
                end_date = start_date + timedelta(hours=amount)
            elif duration_unit == "day":
                end_date = start_date + timedelta(days=amount)
            end_date_str = end_date.isoformat()

        dates = dict()
        dates['startDateTime'] = start_date_str
        dates['endDateTime'] = end_date_str
        return dates
    
    def create_event(self):
        """Creates an event in Google Calendar"""
        all_present = agi.get_variable('RECOG_INSTANCE(0/0/all_required_params_present)')
        agi.verbose('got required params status %s'% all_present)

        if all_present:
            dates = self.get_event_dates()
            email = agi.get_variable('RECOG_INSTANCE(0/0/parameters/email)')
            agi.verbose('create event: dates %s,  call-id %s, caller-id %s, email %s' % (dates, self.callerid, self.callid, email))
            result = calendar.create_event(dates,self.callerid,self.callid,email)
            
            if result['status'] == True:
                agi.verbose('event is successfuly created for %s ' % dates)
                value = "succeeded"
            else:
                agi.verbose('failed to create event: %s ' % result['error_cause'])
                value = "failed"
            
            self.transfer_to_intent('GoogleCalendarQueryStatus', value)

    def check_event(self):
        """Checks an event in Google Calendar"""
        intent = None
        grammar = 'builtin:event/'
        separator = '?'

        email = None
        all_present = agi.get_variable('RECOG_INSTANCE(0/0/all_required_params_present)')
        agi.verbose('got required params status %s'% all_present)
        if all_present:
            email = agi.get_variable('RECOG_INSTANCE(0/0/parameters/email)')
            agi.verbose('retrieve google calendar event date for  email %s' % email)
            result = calendar.get_event_by_mail(email)
            if result['status'] == True:
                if "appointment_date" in result:
                    appointment_date = result['appointment_date']
                    agi.verbose('got google calendar event date: %s' % appointment_date)
                    intent = "EventCheckSuccess"
                    grammar += intent
                    grammar = self.append_grammar_parameter(
                        grammar, "date", appointment_date,separator)
                    separator = ';'

                else:
                    intent = 'EventCheckNone'
                    grammar += intent
            else:
                agi.verbose('failed to get event date: %s' % result['error_cause'])
                intent = 'EventCheckFailure'
                grammar += intent

            if self.project_id:
                grammar = self.append_grammar_parameter(
                    grammar, "projectid", self.project_id, separator)
                separator = ';'

            self.prompt = ' '
            self.grammars = grammar
            self.synth_and_recog()

            if self.status != 'OK' or self.cause != '000':
                agi.verbose('failed to trigger %s intent' % intent)
                return
            self.prompt = self.get_fulfillment_text()


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
        self.trigger_welcome_intent()
        
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

                    elif self.action == 'EventCheck':
                        self.check_event()
                    elif self.action == 'EventCreate':
                        self.create_event()


                elif self.cause != '001' and self.cause != '002':
                    processing = False
            elif self.cause != '001' and self.cause != '002':
                processing = False

        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)


agi = AGI()
calendar = GoogleCalendarConnector()
options = 'plt=1&nif=xml&b=1&sct=1000&sint=15000&nit=10000'
gdf_app = GdfApp(options)

gdf_app.run()
agi.verbose('exiting')
