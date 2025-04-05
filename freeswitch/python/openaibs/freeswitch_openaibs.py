from freeswitch import *
import json
"""

Freeswitch python script OpenAI BS Application

    This script interacts with OpenAI API via UniMRCP server.
    * Revision: 1
    * Date: March 21, 2025
    * Vendor: Universal Speech Solutions LLC

"""

class OpenAIBS_APP:
    
    """A class representing DialogflowV1 application"""

 

    def __init__(self,session,options):

        """Constructor"""
        self.options = options
        self.session = session
        self.asr_engine = "unimrcp:transcribe_mrcp-v2"
        self.tts_engine = "unimrcp:transcribe_mrcp-v2"
        self.language = self.session.getVariable("LANGUAGE")
        # self.voice_name = self.session.getVariable("VOICENAME")
        self.transcription_model = self.session.getVariable("TRANSCRIPTION_MODEL")
        self.MODALITIES = self.session.getVariable("MODALITIES")
        self.prompt="Welcome to OpenAI. How can I help you?"
        self.result = None
        


    def detect_intent(self):

        """Performs a streaming intent detection"""
        self.grammars = "%s\n%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())
        self.play_and_detect_speech()



    def play_and_detect_speech(self):

        """This is an internal function which calls play_and_detect_speech"""
        data = "say:%s detect:%s {%s}%s" %(self.prompt,self.asr_engine,self.compose_speech_options(self.options),self.grammars)
        self.session.execute("play_and_detect_speech", data)
        self.get_and_process_result()

       
    def compose_speech_options(self,options):
        """Composes speech options """
        separator = ','
        if self.language:
            options = self.append_option_parameter(
                options, "speech-language",self.language, separator)

        return options

    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""
        grammar = 'builtin:speech/transcribe'
        separator = '?'
        if self.transcription_model:
            grammar = self.append_grammar_parameter(
                grammar, "transcription_model", self.transcription_model, separator)
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
                grammar, "transcription_model", self.transcription_model, separator)
            separator = ';'

        if self.modalities:
            grammar = self.append_grammar_parameter(
                grammar, "modalities", self.modalities, separator)
            separator = ';'
            
        return grammar

 
    def append_grammar_parameter(self, grammar, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""
        grammar += "%s%s=%s" % (separator, name, value)

        return grammar
    
    def append_option_parameter(self, options, name, value, separator):
        """Appends a name/value parameter to the specified grammar"""
        options += "%s%s=%s" % (separator, name, value)
        
        return options

    def get_prompt(self):

        """Retrieves prompt from the data returned by bot"""
        promptType = str(self.result['response']['output'][0]['content'][0]['type'])

        if promptType == 'input_audio':

            prompt = str(self.result['response']['output'][0]['content'][0]['transcript'])

        elif promptType == 'uri':

            prompt = str(self.result['response']['output'][0]['content'][0]['audio'])

        else:

            prompt =str(self.result['response']['output'][0]['content'][0]['text']) 


        """Uncomment this line if your python version is 2.7"""
        # if isinstance(prompt, str):
        #     prompt = unicode(prompt, 'utf-8')

        console_log("info",'got prompt %s\n' % prompt)
        return prompt




    def get_and_process_result(self):

        result = self.session.getVariable("detect_speech_result")
        if result:
            if 'Completion-Cause' not in str(result):
                result = json.loads(result)
                if len(result)>1:
                    console_log("info",'got  result  %s\n' % result)
                    self.result = result


        

    def run(self):
        """Interacts with the caller in a loop until the dialog is complete"""
        while (self.session.ready()):

            self.detect_intent()
            if self.result:
                self.prompt = self.get_prompt()

             
            else:
                console_log("ERR",'no result %s\n' % self.result)
                break

        self.session.set_tts_params(self.tts_engine, ' ')
        self.session.speak("Thank you.See you next time. ")
        
        



def handler(session, args):
    session.answer()
    session.setAutoHangup(False)
    options ="start-input-timers=false,define-grammar=false,no-input-timeout=10000"
    gdf_app = OpenAIBS_APP(session,options)
    gdf_app.run()
    session.hangup()