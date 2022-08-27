#!/usr/bin/python3

"""

    Asterisk AGI Soundhound BS Application

    This script interacts with Soundhound BS API via UniMRCP server.
    * Revision: 1
    * Date: July  30, 2022
    * Vendor: Universal Speech Solutions LLC

asterisk Soundhound BS example  extensions

with domains

exten=> 7649,1,Answer
exten=> 7649,2,Set(SOUNDHOUNDBSDOMAINS=Query Glue,Map Data,Weather)
exten=> 7649,3,Verbose(${SOUNDHOUNDBSDOMAINS} )
exten=> 7649,4,agi(agi_soundhoundbs.py)
exten=> 7649,5,Hangup()

without domains

exten=> 7649,1,Answer
exten=> 7649,2,agi(agi_soundhoundbs.py)
exten=> 7649,3,Hangup()

"""

 

import sys
from asterisk.agi import *
import json
import re

REQUEST_INFO={}
CONVERSATION_STATE={}

class SoundhoundBS_APP:

    """A class representing SoundhoundBS application"""
    def __init__(self, options):
        """Constructor"""
        self.options = options
        self.domains = agi.get_variable('SOUNDHOUNDBSDOMAINS')
        self.status = None
        self.cause = None
        self.prompt="Welcome to soundhound bot services"
 


 

    def detect_intent(self):

        """Performs a streaming intent detection"""
        self.grammars = "%s$%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())
        self.synth_and_recog()



    def synth_and_recog(self):

        """This is an internal function which calls SynthAndRecog"""
        if not self.prompt:
            self.prompt = ' '

        args = "\\\"%s\\\",\\\"%s\\\",%s" % (
            self.prompt, self.grammars, self.options)
        agi.verbose('got args %s' % args)
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
            agi.verbose('recognition completed abnormally')

    


    def compose_request_info(self):

        """This is an internal function which composes request info"""
        domains=self.domains.split(',')
        agi.verbose('got domains %s' % domains)
            
        REQUEST_INFO["Domains"]={"Only":{"DomainNames":domains}}
            
        

        """for more parameters go to https://docs.houndify.com/reference/RequestInfo"""
        # if self.InputLanguageEnglishName:
        #     REQUEST_INFO["InputLanguageEnglishName"]="English"

        # if self.InputLanguageIETFTag:
        #     REQUEST_INFO["InputLanguageIETFTag"]="en"

        # if self.TimeZone:
        #     REQUEST_INFO["TimeZone"]="Asia/Yerevan"

        # if self.Latitude:
        #     REQUEST_INFO["Latitude"]=40.1797

        # if self.Longitude:
        #     REQUEST_INFO["Longitude"]=44.4454
        agi.verbose('got request info %s' % REQUEST_INFO)
        
    def escape(self,data):
        """This is an internal function which escape/unescape request info fields"""
        return json.dumps(data).replace('"', '\\\\\\"')


    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""
        grammar = 'builtin:speech/transcribe'
        separator = '?'
        
        """Uncomment this if need to use with a domains predefined in asterisk extension"""
        # if self.domains:
        #     self.compose_request_info()

        if REQUEST_INFO:
            agi.verbose('got request info %s' % self.escape(REQUEST_INFO))
            grammar = self.append_grammar_parameter(grammar, "request-info-json",self.escape(REQUEST_INFO) , separator) 
            separator = ';'

        """Comment this if need to use conversation state as an object""" 
        if CONVERSATION_STATE:
            for x in CONVERSATION_STATE.keys():
                grammar = self.append_grammar_parameter(grammar, re.sub(r"(\w)([A-Z])", r"\1-\2", x).lower() ,CONVERSATION_STATE[x] , separator)
                separator = ';'

        """Uncomment this if need to use conversation state as an object"""
        # if CONVERSATION_STATE:
        #     grammar = self.append_grammar_parameter(grammar, "conversation-state-json", self.escape(CONVERSATION_STATE) , separator)
        #     separator = ';'
            
        return grammar

 
    def compose_dtmf_grammar(self):

        """Composes a built-in DTMF grammar"""
        grammar = 'builtin:dtmf/digits'
        separator = '?'
        
        if REQUEST_INFO:
            grammar = self.append_grammar_parameter(grammar, "request-info-json", self.escape(REQUEST_INFO) , separator)
            separator = ';'

        """Comment this if need to use conversation state as an object""" 
        if CONVERSATION_STATE:
            for x in CONVERSATION_STATE.keys():
                grammar = self.append_grammar_parameter(grammar, re.sub(r"(\w)([A-Z])", r"\1-\2", x).lower() ,CONVERSATION_STATE[x] , separator)
                separator = ';'

        """Uncomment this if need to use conversation state as an object"""
        # if CONVERSATION_STATE:
        #     grammar = self.append_grammar_parameter(grammar, "conversation-state-json", self.escape(CONVERSATION_STATE) , separator)
        #     separator = ';'
        return grammar

 

    def append_grammar_parameter(self, grammar, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""
        grammar += "%s%s=%s" % (separator, name, value)
        return grammar

    def trigger_conversation_state(self,field):
        """Retrieves conversationState field from the data returned by bot"""

        data=agi.get_variable('RECOG_INSTANCE(0/0/AllResults/0/ConversationState/%s)' %field)
        agi.verbose('got %s: %s' % (field,data))
        CONVERSATION_STATE[field]=data
       
            


    def get_prompt(self):

        """Retrieves prompt from the data returned by bot"""
        
        prompt = agi.get_variable('RECOG_INSTANCE(0/0/AllResults/0/SpokenResponseLong)') 

        """Uncomment this line if your python version is 2.7"""
        # if isinstance(prompt, str):
           
        #     prompt = unicode(prompt, 'utf-8')
        agi.verbose('got prompt %s' % prompt)
        return prompt

 


 

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""      
     
        processing = False
        if self.prompt:
            processing = True

        while processing:

            self.detect_intent()
            processing = True
            if self.status == 'OK':
                if self.cause == '000':
                    self.prompt = self.get_prompt()
                    self.trigger_conversation_state('ConversationStateTime')
                elif self.cause != '001' and self.cause != '002':
                    processing = False
            elif self.cause != '001' and self.cause != '002':
                processing = False

 

        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)

 

agi = AGI()
options = 'plt=1&b=1&sct=1000&sint=15000&nit=15000&nif=json&gd=$&p=unihoundify-bot'
soundhoundbs_app = SoundhoundBS_APP(options)
soundhoundbs_app.run()
agi.verbose('exiting')