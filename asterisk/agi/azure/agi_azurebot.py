#!/usr/bin/python3
"""
    Asterisk AGI Azure Echo bot  Demo Application
    This script interacts with Azure echo bot via UniMRCP server.

    * Revision: 2
    * Date: Jun 27, 2022
    * Vendor: Universal Speech Solutions LLC
"""

import sys
from asterisk.agi import *


class AzurebotApp:

    """A class representing Azure bot application"""

    def __init__(self, options):
        """Constructor"""
        self.options = options
        self.status = None
        self.cause = None
        self.prompt = 'Welcome to Azure Echo bot. Say something i will repeat your phrase?'
        self.method=None



    def detect_intent(self):
        """Performs a streaming intent detection"""
        self.grammar = self.compose_speech_grammar()
        self.synth_and_recog()
        
    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""

        grammar = 'builtin:speech/transcribe'
        separator = '?'
        if self.method:
            grammar = self.append_grammar_parameter(grammar, "method", self.method, separator)
            separator = ';'
        return grammar

    def append_grammar_parameter(self, grammar, name, value, separator):
        """Appends a name/value parameter to the specified grammar"""
        grammar += "%s%s=%s" % (separator, name, value)
        return grammar

    def synth_and_recog(self):
        """This is an internal function which calls SynthAndRecog"""
        if not self.prompt:
            self.prompt = ' '
        args = "\\\"%s\\\",\\\"%s\\\",%s" % (
            self.prompt, self.grammar, self.options)
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

   
    def get_speak(self):
        """Retrieves message text from the data returned by bot"""
        speak = agi.get_variable(
            'RECOG_INSTANCE(0/0/speak)')
            
        """Uncomment this line if your python version is 2.7"""
        # if isinstance(speak, str):
        #     speak = unicode(speak, 'utf-8')
        agi.verbose('got message %s' % speak)
        return speak


    def run(self):
        self.method="listen"
        processing = True
        while processing:
            self.detect_intent()
            processing = True
            if self.status == 'OK':
                if self.cause == '000':
                    self.prompt = self.get_speak()               

                elif self.cause != '001' and self.cause != '002':
                    processing = False
            elif self.cause != '001' and self.cause != '002':
                processing = False

        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)



agi = AGI()
options = 'nif=json&plt=1&b=1&sct=1000&sint=15000&nit=10000'
botApp = AzurebotApp(options)

botApp.run()
agi.verbose('exiting')