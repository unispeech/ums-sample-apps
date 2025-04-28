#!/usr/bin/python

"""
    Asterisk AGI OpenAI BS Application with functional call

    This script interacts with OpenAI API via UniMRCP server.
    * Revision: 1
    * Date: April 28, 2025
    * Vendor: Universal Speech Solutions LLC

exten => 755,1,Answer()
exten => 755,2,Set(LANGUAGE="en-US")
exten => 755,3,Set(VOICENAME="coral")
; The set of modalities the model can respond with. To disable audio, set this to ["text"].
exten => 755,4,Set(MODALITIES="text\,audio")
exten => 755,5,Set(TRANSCRIPTION_MODEL="gpt-4o-mini-transcribe")
exten => 755,6,agi(agi_openaibs.py)

"""

 

import sys
from asterisk.agi import *
import json
import os

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
        self.jsonpath=agi.get_variable("JSONPATH")
        self.prompt="Welocome to OpenAI. How can i help you?"
        


  
    def trigger_function_call(self, name, callid):
        """Triggers a function call"""

        grammar = 'builtin:speech/transcribe'
        separator = '?'
        

        if self.method:

            agi.verbose('got method to set %s' % self.method)

            grammar = self.append_option_parameter(
                grammar, "method", self.method, separator)


        if name == 'get_weather':
                separator = ';'
                agi.verbose('create conversation item')
                conversation_item = {}
                conversation_item['type'] = 'function_call_output'
                conversation_item['call_id'] = callid
                # Assuming we have temperature  
                conversation_item['output'] = '24C'
                grammar = self.append_grammar_parameter(
                    grammar, "conversation-item-json", json.dumps(conversation_item).replace('"', '\\\\\\"'), separator)
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

        if self.jsonpath:

            agi.verbose('got json path to set %s' % self.jsonpath)

            grammar = self.append_grammar_parameter(
                grammar, "tools-json", self.get_json_content(), separator)
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

    def get_json_content(self):
        json_file=None
        if os.path.isfile(self.jsonpath):
            with open(self.jsonpath, 'r') as file:
                json_file = json.load(file)
            return json.dumps(json_file, indent=None, separators=(',', ':')).replace('"', '\\\\\\"')

        agi.verbose('there is no json path specified. jsonpath is : %s' % json_file)
        

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""      
      

        processing = False
        
        if self.prompt:
            processing = True

        method_type = ''
        name = None
        arguments = None
        callid = None
        while processing:
            if method_type == 'function_call':
                self.trigger_function_call(name, callid)
            else:
                self.detect_intent()
            processing = True
            if self.status == 'OK':
                if self.cause == '000':
                    method_type = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/type)')
                    if method_type == 'function_call':
                        name = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/name)')
                        arguments = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/arguments)')
                        callid = agi.get_variable('RECOG_INSTANCE(0/0/response/output/0/call_id)')
                    else:
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
