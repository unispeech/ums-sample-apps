#!/usr/bin/python3

"""
    Asterisk AGI Nuance bot Application
 
    This script interacts with Nuance bot API via UniMRCP server.
    * Revision: 1
    * Date: Apr 15, 2023
    * Vendor: Universal Speech Solutions LLC
"""

 

import sys
import json
from asterisk.agi import *



class NuanceBotApp:


    """A class representing NUANCE BOT application"""

    def __init__(self, options):

        """Constructor"""

        self.options = options

        self.model = agi.get_variable('MODEL')

        self.tag_format="semantics/json"

        self.status = None

        self.cause = None

        self.recognitionSettings=None
        
        self.ssml = agi.get_variable('SSML')

    def set_method(self,grammar,method):

        """Sets method """

        separator = '?'

        grammar = self.append_grammar_parameter(grammar, "method", method, separator)

        return grammar

    def set_model(self,grammar):

        """Sets model uri """

        if self.model:

            separator = ';'

            grammar = self.append_grammar_parameter(grammar, "model-uri", self.model, separator)

        return grammar

    def set_tag_format(self,grammar):

        """Sets tag format """

        if self.tag_format:

            separator = ';'

            grammar=self.append_grammar_parameter(grammar, "tag-format", self.tag_format, separator)

        return grammar
    
    def set_collection_settings(self):

        """Sets collection/timeouts settings"""

        if self.recognitionSettings["collectionSettings"]:

            timeout=self.recognitionSettings["collectionSettings"]["timeout"]

            maxSpeechTimeout=self.recognitionSettings["collectionSettings"]["maxSpeechTimeout"]

            # incompleteTimeout = self.recognitionSettings["collectionSettings"]["incompleteTimeout"]
            # completeTimeout=self.recognitionSettings["collectionSettings"]["completeTimeout"]
            if timeout:

                separator = '&'

                self.options = self.append_option_parameter(self.options, "t", timeout, separator)
            # if incompleteTimeout:
            #     self.options = self.append_option_parameter(self.options, "sint", incompleteTimeout, separator)
            # if completeTimeout:
            #     self.options = self.append_option_parameter(self.options, "sct", completeTimeout, separator)
            if maxSpeechTimeout:

                separator = '&'

                self.options = self.append_option_parameter(self.options, "nit", maxSpeechTimeout, separator)


    def set_speech_settings(self):

        """Sets speech settings"""

        if self.recognitionSettings["speechSettings"]:

            bargeInType=self.recognitionSettings["speechSettings"]["bargeInType"]

            if bargeInType:

                separator = '&'

                self.options = self.append_option_parameter(self.options, "b", '1', separator)

            
    def set_dtmf_settings(self):

        """Sets dtmf settings"""

        if self.recognitionSettings["dtmfSettings"]: 

            interDigitTimeout=self.recognitionSettings["dtmfSettings"]["interDigitTimeout"]

            termTimeout=self.recognitionSettings["dtmfSettings"]["termTimeout"]

            termChar=self.recognitionSettings["dtmfSettings"]["termChar"]

            if interDigitTimeout:

                separator = '&'

                self.options = self.append_option_parameter(self.options, "dit", interDigitTimeout, separator)

            if termTimeout:

                separator = '&'

                self.options = self.append_option_parameter(self.options, "dtt", termTimeout, separator)

            if termChar:

                separator = '&'

                self.options = self.append_option_parameter(self.options, "dttc", termChar, separator)


    def get_recognitionSettings(self):
        
        """Retrieves recognition settings from the data returned by bot"""

        agi.verbose('got recognitionSettings2 %s' % agi.get_variable('RECOG_INSTANCE(0/0/response/payload/qaAction/recognitionSettings)'))
        
        rec_settings= agi.get_variable('RECOG_INSTANCE(0/0/response/payload/qaAction/recognitionSettings)')
        
        return json.loads(rec_settings)


    def trigger_welcome_intent(self):

        """Triggers a welcome intent"""


        grammar = 'builtin:speech/transcribe'

        grammar = self.set_method(grammar,"Execute")

        grammar = self.set_model(grammar)

        grammar = self.set_tag_format(grammar)


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

        if self.recognitionSettings:

            self.compose_speech_options()

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

        grammar = self.set_method(grammar,"ExecuteStream")

        grammar = self.set_model(grammar)

        grammar = self.set_tag_format(grammar)


        return grammar

 

    def compose_dtmf_grammar(self):

        """Composes a built-in DTMF grammar"""

        grammar = 'builtin:dtmf/digits'

        grammar +="?"

        grammar = self.set_model(grammar)

        grammar = self.set_tag_format(grammar)



        return grammar


    def compose_speech_options(self):

        """Composes a built-in speech grammar options"""

        self.set_collection_settings()

        self.set_speech_settings()

        self.set_dtmf_settings()


 
    def append_option_parameter(self, options, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""

        options += "%s%s=%s" % (separator, name, value)
        
        return options

 

    def append_grammar_parameter(self, grammar, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""

        grammar += "%s%s=%s" % (separator, name, value)

        return grammar

    def str_to_json(self,string):
        
        return json.loads(string)

    def compose_ssml(self,prompts):

        """composes ssml"""

        ssml="<speak version='\"1.0'\" xmlns='\"http://www.w3.org/2001/10/synthesis'\"> %s </speak>" % prompts

        agi.verbose('got ssml %s' % ssml)
        
        return ssml

 

    def get_nlg(self,path):

        """Retrieves prompt from the data returned by bot"""

        nlg=agi.get_variable('RECOG_INSTANCE(0/0/response/payload/%s)' % path)
        
        agi.verbose('got nlg %s' % nlg)

        return self.str_to_json(nlg)

    def get_prompts(self,data):

        """Retrieves prompt from the data returned by bot"""

        prompts=''
        
        if data:
            
            for i in range(len(data)):
               
                agi.verbose('got %s prompt %s' % (i,data[i]['text']))
               
                prompts += f"{str(data[i]['text'])}"
        
        return prompts

    def compose_prompt(self):

        """Concatenates prompts"""

        prompts=''

        nlg1 = self.get_nlg("messages/0/nlg")

        agi.verbose('got nlg 1 %s'  % nlg1)

        prompts += self.get_prompts(nlg1)

        nlg2 = self.get_nlg("qaAction/message/nlg")

        agi.verbose('got nlg 2 %s' % nlg2)

        prompts += self.get_prompts(nlg2)

        agi.verbose('got ssml %s ' % self.ssml)

        if self.ssml:

           agi.verbose('got ssml %s ' % self.ssml)
            
           prompts=self.compose_ssml(prompts)

        return prompts

    
    def dialog_escalation_action(self):

        """Checks whether the dialog is transfered and perform transfer"""

        result= False

        actionid=nlg=agi.get_variable('RECOG_INSTANCE(0/0/response/payload/endAction/escalationAction/id)')

        if "Transfer" in actionid:

            result=True
        
        return result

    def dialog_end_action(self):

        """Checks whether the dialog is complete"""

        result= False

        actionid=nlg=agi.get_variable('RECOG_INSTANCE(0/0/response/payload/endAction/id)')

        if "EndCall" in actionid:

            result=True
        
        return result



 

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""      
        
        self.trigger_welcome_intent()
        
        if self.status != 'OK' or self.cause != '000':

            agi.verbose('failed to trigger welcome intent')

            return

 

        processing = False

        self.prompt = self.compose_prompt()

        if self.prompt:

            processing = True

 

        while processing:

            self.detect_intent()

            processing = True

            if self.status == 'OK':

                if self.cause == '000':

                    self.recognitionSettings=self.get_recognitionSettings()

                    self.prompt = self.compose_prompt()

                    if self.dialog_escalation_action():

                        processing=False

                    if self.dialog_end_action():

                        processing=False

 

                elif self.cause != '001' and self.cause != '002':

                    processing = False

            elif self.cause != '001' and self.cause != '002':

                processing = False

 

        if not self.prompt:

            self.prompt = 'Thank you. See you next time.'

        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)

 

agi = AGI()

options = 'plt=1&nif=json'

nuance_bot_app = NuanceBotApp(options)

 

nuance_bot_app.run()

agi.verbose('exiting')