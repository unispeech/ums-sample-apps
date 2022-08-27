#!/usr/bin/python3
"""
    Asterisk AGI Lex V2 Application

    This script interacts with Lex V2 API via UniMRCP server.

    This script demonstrates passing session attributes from asterisk agi  to lexv2 api via unimrcp server.
    Note this script can't work without lambda script and lexv2 bot.You can find both in the same directory 

    To invoke this WeatherNow intent use phrases 'I would like to get weather' or Weather and pass your prefered Longitude and Latitude
    Weatherbot zip passord is weatherbot

    * Revision: 1
    * Date: Aug 10, 2022
    * Vendor: Universal Speech Solutions LLC

    * asterisk extension with aws credentials
    exten => 7533,1,Answer();
    exten => 7533,2,Set(AWS_REGION="")
    exten => 7533,3,Set(AWS_BOT_ID="")
    exten => 7533,4,Set(AWS_ALIAS_ID="")
    exten => 7533,5,agi(agi_lexv2_weather.py)

"""

import sys
from asterisk.agi import *

class LexV2App:

    """A class representing LexV2 application"""

    def __init__(self, options):
        """Constructor"""
        self.options = options
        self.region = agi.get_variable('AWS_REGION')
        self.bot_id = agi.get_variable('AWS_BOT_ID')
        self.alias_id = agi.get_variable('AWS_ALIAS_ID')
        self.message = None
        
        """Specify intent name if you want to trigger and intent"""
        self.intent_name = None
        
        self.Longitude='44.4454'
        self.Latitude='40.1797'
        self.status = None
        self.cause = None

    def trigger_WeatherNow_intent(self):
        """Triggers a welcome intent"""
        grammar = 'builtin:speech/transcribe'
        separator = '?'
        if self.bot_id:
            grammar = self.append_grammar_parameter(grammar, "bot-name", self.bot_id, separator)
            separator = ';'
        if self.alias_id:
            grammar = self.append_grammar_parameter(grammar, "alias", self.alias_id, separator)
            separator = ';'
        if self.message:
            grammar = self.append_grammar_parameter(grammar, "message", self.message, separator)
            separator = ';'
        if self.intent_name:
            grammar = self.append_grammar_parameter(grammar, "intent-name", self.intent_name, separator)
            separator = ';'
        
        grammar = self.append_grammar_parameter(grammar, "lex.Longitude", self.Longitude, separator)
        separator = ';'
        grammar = self.append_grammar_parameter(grammar, "lex.Latitude", self.Latitude, separator)
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
        if self.bot_id:
            grammar = self.append_grammar_parameter(grammar, "bot-name", self.bot_id, separator)
            separator = ';'
        if self.alias_id:
            grammar = self.append_grammar_parameter(grammar, "alias", self.alias_id, separator)
            separator = ';'
        
        return grammar

    def compose_dtmf_grammar(self):
        """Composes a built-in DTMF grammar"""
        grammar = 'builtin:dtmf/digits'
        separator = '?'
        if self.bot_id:
            grammar = self.append_grammar_parameter(grammar, "bot-name", self.bot_id, separator)
            separator = ';'
        if self.alias_id:
            grammar = self.append_grammar_parameter(grammar, "alias", self.alias_id, separator)
            separator = ';'
        grammar = self.append_grammar_parameter(grammar, "lex.Longitude", self.Longitude, separator)
        separator = ';'
        grammar = self.append_grammar_parameter(grammar, "lex.Latitude", self.Latitude, separator)
        separator = ';'
        return grammar

    def compose_event_grammar(self, intent, value):
        """Composes a built-in event grammar"""
        grammar = 'builtin:event/%s' % intent
        separator = '?'
        if value:
            grammar = self.append_grammar_parameter(grammar, "value", value, separator)
            separator = ';'
        if self.bot_id:
            grammar = self.append_grammar_parameter(grammar, "bot-name", self.bot_id, separator)
            separator = ';'
        if self.alias_id:
            grammar = self.append_grammar_parameter(grammar, "alias", self.alias_id, separator)
            separator = ';'
        return grammar

    def append_grammar_parameter(self, grammar, name, value, separator):
        """Appends a name/value parameter to the specified grammar"""
        grammar += "%s%s=%s" % (separator, name, value)
        return grammar

    def get_prompt(self):
        """Retrieves prompt from the data returned by bot"""
        prompt = agi.get_variable('RECOG_INSTANCE(0/0/textResponse/messages/0/content)')

        """Uncomment this line if your python version is 2.7"""
        # if isinstance(prompt, str):
        #     prompt = unicode(prompt, 'utf-8')
        
        agi.verbose('got prompt %s' % prompt)
        return prompt

    def check_dialog_completion(self):
        """Checks wtether the dialog is complete"""
        dialog_action_type = agi.get_variable('RECOG_INSTANCE(0/0/intentResult/sessionState/dialogAction/type)')
        agi.verbose('got dialog_action_type %s' % dialog_action_type)
        complete = False
        if dialog_action_type == 'Close':
            complete = True
        return complete

    def run(self):
        """Interacts with the caller in a loop until the dialog is complete"""
        self.trigger_WeatherNow_intent()
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
options = 'plt=1&b=1&sct=1500&sint=15000&nit=10000&nif=json&p=uni3_amazon'
lex_v2_app = LexV2App(options)

lex_v2_app.run()
agi.verbose('exiting')
