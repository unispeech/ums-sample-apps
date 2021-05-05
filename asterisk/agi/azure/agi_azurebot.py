#!/usr/bin/python2.7
"""
    Asterisk AGI Azure Echo bot  Demo Application
    This script interacts with Azure echo bot via UniMRCP server.

    * Revision: 1
    * Date: May 5, 2021
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

    def detect_intent(self):
        """Performs a streaming intent detection"""
        self.grammar = "builtin:speech/transcribe?" 
        self.synth_and_recog()
        

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
        if isinstance(speak, str):
            speak = unicode(speak, 'utf-8')
        agi.verbose('got message %s' % speak)
        return speak


    def run(self):
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