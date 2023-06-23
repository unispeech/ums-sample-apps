#!/usr/bin/python3

"""

    Asterisk AGI NUANCE SR Application

    This script interacts with NUANCE SR/SS API via UniMRCP server.

    * Revision: 1
    * Date: June 14, 2023
    * Vendor: Universal Speech Solutions LLC

"""

 

import sys
from asterisk.agi import *
import random
VOICES=[
    {"name":"en-US-JennyNeural","model":"neural","language":"en-US","gender":"FEMALE","sampleRateHz":24000},
    {"name":"en-US-GuyNeural","model":"neural","language":"en-US","gender":"MALE","sampleRateHz":24000},
    {"name":"en-US-AriaNeural","model":"neural","language":"en-US","gender":"FEMALE","sampleRateHz":24000},
    {"name":"en-US-DavisNeural","model":"neural","language":"en-US","gender":"MALE","sampleRateHz":24000},
    {"name":"en-US-ElizabethNeural","model":"neural","language":"en-US","gender":"FEMALE","sampleRateHz":24000},
]

class NuanceSRAPP:


    """A class representing NUANCE SR  application"""

    def __init__(self, options):

        """Constructor"""
        self.options = options
        self.status = None
        self.cause = None
        self.prompt =" Welcome to Nuance speech transcription PLease speak "

 
    def detect_intent(self):
        """Performs a streaming intent detection"""
        self.compose_speech_options()
        self.grammars = "%s,%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())
        self.synth_and_recog()



    def synth_and_recog(self):

        """This is an internal function which calls SynthAndRecog"""

        if not self.prompt:
            self.prompt = ' '
        agi.verbose('got completion cause %s' % self.prompt)
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
            agi.verbose('recognition completed abnormally')

 

    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""

        grammar = 'builtin:speech/transcribe'
        separator = '?'

        return grammar

    def compose_speech_options(self):
        """Composes speech options"""
        index=random.randint(1,4)
        separator = '&'
        self.options = self.append_option_parameter(
            self.options, "vn", VOICES[index]['name'], separator)
        
        self.options = self.append_option_parameter(
            self.options, "vg", VOICES[index]['gender'], separator)        
        
        

    def append_option_parameter(self, options, name, value, separator):
        """Appends a name/value parameter to the specified grammar"""
        options += "%s%s=%s" % (separator, name, value)
        
        return options

    def compose_dtmf_grammar(self):

        """Composes a built-in DTMF grammar"""

        grammar = 'builtin:dtmf/digits'
        separator = '?'

        return grammar



    def append_grammar_parameter(self, grammar, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""
        grammar += "%s%s=%s" % (separator, name, value)
        return grammar


    def get_prompt(self):

        """Retrieves prompt from the data returned by bot"""
        prompt = agi.get_variable('RECOG_INSTANCE()')
        """Uncomment this line if your python version is 2.7"""
        # if isinstance(prompt, str):
           
        #     prompt = unicode(prompt, 'utf-8')
        agi.verbose('got prompt %s' % prompt)
        return prompt
 

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""      

        if self.prompt:
            processing = True

        while processing:
            self.detect_intent()
            processing = True
            if self.status == 'OK':
                if self.cause == '000':
                    self.prompt = self.get_prompt()

                elif self.cause != '001' and self.cause != '002':
                    processing = False

            elif self.cause != '001' and self.cause != '002':
                processing = False

 

        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)

 

agi = AGI()
options = 'plt=1&b=1&sct=1000&sint=15000&nit=10000&nif=json&p=ums'
nuance_sr_app = NuanceSRAPP(options)
nuance_sr_app.run()
agi.verbose('exiting')