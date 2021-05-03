#!/usr/bin/python2.7
"""
    Asterisk AGI Lex  Application

    This script interacts with Lex  API via UniMRCP server.

    * Revision: 1
    * Date: Apr 28, 2021
    * Vendor: Universal Speech Solutions LLC
"""

import sys
from asterisk.agi import *


class LexApp:

    """A class representing Amazon lex application"""

    def __init__(self, options):
        """Constructor"""
        self.options = options
        self.status = None
        self.cause = None
        self.prompt = 'Welcome to Amazon Lex.  How can i help you'

    def detect_intent(self):
        """Performs a streaming intent detection"""
        self.grammars = "builtin:speech/transcribe,builtin:dtmf/digits" 
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

   
    def get_message(self):
        """Retrieves message text from the data returned by bot"""
        message = agi.get_variable(
            'RECOG_INSTANCE(0/0/message)')
        if isinstance(message, str):
            message = unicode(message, 'utf-8')
        agi.verbose('got message %s' % message)
        return message

    def check_dialogstate(self):
        """Checks wtether the dialog is complete"""
        dialogstate = agi.get_variable(
            'RECOG_INSTANCE(0/0/dialogstate)')
        complete = False
        if dialogstate == 'ReadyForFulfillment':
            agi.verbose('got dialogstate %s' % dialogstate)
            complete = True
        return complete


    def run(self):
        processing = True
        while processing:
            self.detect_intent()
            processing = True
            if self.status == 'OK':
                if self.cause == '000':
                    self.prompt = self.get_message()
                    if self.check_dialogstate():
                        processing = False                  

                elif self.cause != '001' and self.cause != '002':
                    processing = False
            elif self.cause != '001' and self.cause != '002':
                processing = False

        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)



agi = AGI()
options = 'plt=1&b=1&sct=1000&sint=15000&nit=10000'
lex_app = LexApp(options)

lex_app.run()
agi.verbose('exiting')
 