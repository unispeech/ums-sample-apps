#!/usr/bin/python

"""
    Asterisk AGI OpenAI BS Application

    This script interacts with OpenAI API via UniMRCP server.
    * Revision: 1
    * Date: March 21, 2025
    * Vendor: Universal Speech Solutions LLC

asterisk extensions

exten=> 7649,1,Answer
exten=> 7649,2,agi(github/asterisk/agi/agi_openaibs.py)
exten=> 7649,3,Hangup()

"""

 

import sys
from asterisk.agi import *
import json


class OpenAIBS_APP:
    """A class representing OpenAI application"""

    def __init__(self, options):

        """Constructor"""

        self.options = options
        self.status = None
        self.cause = None
        self.prompt="Welcome to OpenAI. How can I help you?"
  

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


    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""
        grammar = 'builtin:speech/transcribe'
        separator = '?'

        return grammar

 
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

        agi.verbose('got result from openaibs %s' % agi.get_variable('RECOG_INSTANCE(0/0)'))

        promptType = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/content/0/type)')

        if promptType == 'input_audio':

            prompt = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/content/0/transcript)')

        elif promptType == 'uri':

            prompt = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/content/0/audio)')

        else:

            prompt = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/content/0/text)')

        # prompt = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/content/0/transcript)')

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

                elif self.cause != '001' and self.cause != '002':
                    processing = False
            elif self.cause != '001' and self.cause != '002':
                processing = False


        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)


agi = AGI()
options = 'plt=1&b=1&sct=1000&sint=15000&nit=15000&nif=json&gd=$'
app = OpenAIBS_APP(options)
app.run()
agi.verbose('exiting')
