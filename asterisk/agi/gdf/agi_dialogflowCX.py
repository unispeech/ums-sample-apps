#!/usr/bin/python2.7

"""

    Asterisk AGI Dialogflow CX Application

 

    This script interacts with Google Dialogflow CX API via UniMRCP server.

    * Revision: 1

    * Date: Apr 28, 2021

    * Vendor: Universal Speech Solutions LLC


"""

 

import sys
from asterisk.agi import *

 

class GdfCxApp:

 

    """A class representing DialogflowCX application"""

 

    def __init__(self, options):

        """Constructor"""

        self.options = options

        self.project_id = agi.get_variable('GDF_PROJECT_ID')

        self.agent_id = agi.get_variable('GDF_AGENT_ID')

        self.location = agi.get_variable('GDF_LOCATION')


        self.status = None

        self.cause = None

 

    def trigger_welcome_intent(self):

        """Triggers a welcome intent"""


        grammar = 'builtin:event/00000000-0000-0000-0000-000000000000'

        separator = '?'

        if self.project_id:

            grammar = self.append_grammar_parameter(grammar, "projectid", self.project_id, separator)

            separator = ';'

        if self.agent_id:

            grammar = self.append_grammar_parameter(grammar, "agent", self.agent_id, separator)

            separator = ';'

        if self.location:

            grammar = self.append_grammar_parameter(grammar, "location", self.location, separator)

            separator = ';'

 

        self.prompt = ' '

        self.grammars = grammar

        self.synth_and_recog()

 

    def detect_intent(self):

        """Performs a streaming intent detection"""

        self.grammars = "%s,%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())

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

            agi.verbose('recognition completed abnormally')

 

    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""

        grammar = 'builtin:speech/transcribe'

        separator = '?'

        if self.project_id:

            grammar = self.append_grammar_parameter(grammar, "projectid", self.project_id, separator)

            separator = ';'

        if self.agent_id:

            grammar = self.append_grammar_parameter(grammar, "agent", self.agent_id, separator)

            separator = ';'

        if self.location:

            grammar = self.append_grammar_parameter(grammar, "location", self.location, separator)

            separator = ';'

        return grammar

 

    def compose_dtmf_grammar(self):

        """Composes a built-in DTMF grammar"""

        grammar = 'builtin:dtmf/digits'

        separator = '?'

        if self.project_id:

            grammar = self.append_grammar_parameter(grammar, "projectid", self.project_id, separator)

            separator = ';'

        if self.agent_id:

            grammar = self.append_grammar_parameter(grammar, "agent", self.agent_id, separator)

            separator = ';'

        if self.location:

            grammar = self.append_grammar_parameter(grammar, "location", self.location, separator)

            separator = ';'

        return grammar

 

    def compose_event_grammar(self, intent, value):

        """Composes a built-in event grammar"""

        grammar = 'builtin:event/%s' % intent

        separator = '?'

        if value:

            grammar = self.append_grammar_parameter(grammar, "value", value, separator)

            separator = ';'

        if self.project_id:

            grammar = self.append_grammar_parameter(grammar, "projectid", self.project_id, separator)

            separator = ';'

        if self.agent_id:

            grammar = self.append_grammar_parameter(grammar, "agent", self.agent_id, separator)

            separator = ';'

        if self.location:

            grammar = self.append_grammar_parameter(grammar, "location", self.location, separator)

            separator = ';'

        return grammar

 

    def append_grammar_parameter(self, grammar, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""

        grammar += "%s%s=%s" % (separator, name, value)

        return grammar

 

    def get_prompt(self):

        """Retrieves prompt from the data returned by bot"""

        prompt = agi.get_variable('RECOG_INSTANCE(0/0/responseMessages/0/text/text/0)') + agi.get_variable('RECOG_INSTANCE(0/0/responseMessages/1/text/text/0)')
        

        if isinstance(prompt, str):
           
            prompt = unicode(prompt, 'utf-8')

        agi.verbose('got prompt %s' % prompt)

        return prompt

 

    def check_dialog_completion(self):

        """Checks wtether the dialog is complete"""
        
        current_page_display_name = agi.get_variable('RECOG_INSTANCE(0/0/current_page/display_name)')

        complete = False

        if current_page_display_name == "End Session":

            agi.verbose('got current_page current_page_display_name %s' % current_page_display_name)

            complete = True

        return complete

 

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""      
        
        self.trigger_welcome_intent()
        
        if self.status != 'OK' or self.cause != '000':

            agi.verbose('failed to trigger welcome intent')

            return

 

        processing = False

        self.prompt = self.get_prompt()

        if self.prompt:

            processing = True

 

        while processing:

            self.detect_intent()

            processing = True

            if self.status == 'OK':

                if self.cause == '000':

                    self.prompt = self.get_prompt()

                    if self.check_dialog_completion():

                        processing = False

 

                elif self.cause != '001' and self.cause != '002':

                    processing = False

            elif self.cause != '001' and self.cause != '002':

                processing = False

 

        if not self.prompt:

            self.prompt = 'Thank you. See you next time.'

        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)

 

agi = AGI()

options = 'plt=1&b=1&sct=1000&sint=15000&nit=10000&nif=json'

gdf_cx_app = GdfCxApp(options)

 

gdf_cx_app.run()

agi.verbose('exiting')