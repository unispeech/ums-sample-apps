#!/usr/bin/python

"""
    Asterisk AGI OpenAI BS Application

    This script interacts with OpenAI API via UniMRCP server.
    * Revision: 1
    * Date: April 28, 2025
    * Vendor: Universal Speech Solutions LLC

exten => 757,1,Answer()
exten => 757,2,Set(LANGUAGE="en-US")
exten => 757,3,Set(VOICENAME="coral")
exten => 757,4,Set(INSTRUCTIONS=You are a WHeather companie agent that uses tool_choice get_weather)
exten => 757,5,set(METHOD=create-response)
exten => 757,6,Set(MODALITIES="text\,audio")
exten => 757,7,Set(TRANSCRIPTION_MODEL="gpt-4o-mini-transcribe")
exten => 757,8,agi(agi_openaibs_instructions.py)

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
        self.language=agi.get_variable("LANGUAGE")
        self.voice_name=agi.get_variable("VOICENAME")
        self.method=agi.get_variable("METHOD")
        self.transcription_model=agi.get_variable("TRANSCRIPTION_MODEL")
        self.modalities=agi.get_variable("MODALITIES")
        self.instructions=agi.get_variable("INSTRUCTIONS")

    def trigger_welcome_state(self):
        """Triggers a function call"""

        grammar = 'builtin:speech/transcribe'
        separator = '?'

        if self.method:

            agi.verbose('got method to set %s' % self.method)

            grammar = self.append_grammar_parameter(
                grammar, "method", self.method, separator)
            separator = ';'

        if self.instructions:

            agi.verbose('got instructions to set %s' % self.instructions)

            grammar = self.append_grammar_parameter(
                grammar, "instructions", self.instructions, separator)
            separator = ';'
            
        if self.transcription_model:
            grammar = self.append_grammar_parameter(
                grammar, "transcription-model", self.transcription_model, separator)
            separator = ';'

        if self.modalities:
            grammar = self.append_grammar_parameter(
                grammar, "modalities", self.modalities, separator)
            separator = ';'


        self.prompt = ' '
        self.grammars = grammar
        self.synth_and_recog()

    def detect_intent(self):

        """Performs a streaming intent detection"""
        self.grammars = "%s$%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())
        self.synth_and_recog()


    def synth_and_recog(self):

        """This is an internal function which calls SynthAndRecog"""
        if not self.prompt:
            self.prompt = ' '

        args = "\\\"%s\\\",\\\"%s\\\",%s" % (
            self.prompt, self.grammars, self.compose_speech_options(self.options))
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


    def compose_speech_options(self,options):
        """Composes speech options """
        separator = '&'
        if self.language:

            agi.verbose('got language  to set %s' % self.language)

            options = self.append_option_parameter(
                options, "spl",self.language, separator)

        if self.voice_name:

            agi.verbose('got voice name to set %s' % self.voice_name)

            options = self.append_option_parameter(
                options, "vn", self.voice_name, separator)


        return options

    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""
        grammar = 'builtin:speech/transcribe'
        separator = '?'
        if self.transcription_model:
            grammar = self.append_grammar_parameter(
                grammar, "transcription-model", self.transcription_model, separator)
            separator = ';'

        if self.modalities:
            grammar = self.append_grammar_parameter(
                grammar, "modalities", self.modalities, separator)
            separator = ';'
            
        return grammar

 
    def compose_dtmf_grammar(self):

        """Composes a built-in DTMF grammar"""
        grammar = 'builtin:dtmf/digits'

        separator = '?'
        
        if self.transcription_model:
        
            grammar = self.append_grammar_parameter(
                grammar, "transcription-model", self.transcription_model, separator)
        
            separator = ';'

        if self.modalities:

            grammar = self.append_grammar_parameter(
                grammar, "modalities", self.modalities, separator)
            separator = ';'
        
        return grammar

    def append_option_parameter(self, options, name, value, separator):
        """Appends a name/value parameter to the specified grammar"""
        options += "%s%s=%s" % (separator, name, value)
        
        return options


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

        self.trigger_welcome_state()
        
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
