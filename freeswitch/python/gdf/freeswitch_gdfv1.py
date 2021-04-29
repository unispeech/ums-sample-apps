from freeswitch import *
import json
"""

    Freeswitch Dialogflow  Application

    This script interacts with Google Dialogflow  API via UniMRCP server.

    * Revision: 1
    * Date: Apr 28, 2021
    * Vendor: Universal Speech Solutions LLC

"""

class GdfApp:
    
    """A class representing DialogflowV1 application"""

 

    def __init__(self,session,options):

        """Constructor"""
        self.options = options
        self.session = session
        self.asr_engine = "unimrcp:gdf_mrcp-v2"
        self.tts_engine = "unimrcp:gdf_mrcp-v2"
        self.project_id = self.session.getVariable('GDF_PROJECT_ID')
        self.result = None



    def trigger_welcome_intent(self):

        """Triggers a welcome intent"""
        grammar = 'builtin:event/welcome?'
        self.prompt = ' '
        self.grammars = grammar
        self.play_and_detect_speech()

 

    def detect_intent(self):

        """Performs a streaming intent detection"""
        self.grammars = "%s,%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())
        self.play_and_detect_speech()



    def play_and_detect_speech(self):

        """This is an internal function which calls play_and_detect_speech"""
        data = "say:%s detect:%s %s%s" %(self.prompt,self.asr_engine,self.options,self.grammars)
        self.session.execute("play_and_detect_speech", data)
        self.get_and_process_result()

       
 

    def compose_speech_grammar(self):

        """Composes a built-in speech grammar"""
        grammar = 'builtin:speech/transcribe'
        separator = '?'
        if self.project_id:
            grammar = self.append_grammar_parameter(
                grammar, "projectid", self.project_id, separator)
            separator = ';'
        return grammar

 

    def compose_dtmf_grammar(self):

        """Composes a built-in DTMF grammar"""
        grammar = 'builtin:dtmf/digits'
        separator = '?'
        if self.project_id:
            grammar = self.append_grammar_parameter(
                grammar, "projectid", self.project_id, separator)
            separator = ';'
        return grammar

 
    def append_grammar_parameter(self, grammar, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""

        grammar += "%s%s=%s" % (separator, name, value)
        return grammar
    

    def get_prompt(self):

        """Retrieves prompt from the data returned by bot"""
        prompt = str(self.result['fulfillmentText'])
        console_log("info",'got prompt %s\n' % prompt)
        return prompt

 

    def check_dialog_completion(self):

        """Checks wtether the dialog is complete"""
        allPresent = False
        if 'allRequiredParamsPresent' in str(self.result):
            if str(self.result['allRequiredParamsPresent']) == "true":
                allPresent = True
            console_log("info",'got allPresent %s' % allPresent)
        return allPresent


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
        self.trigger_welcome_intent()
        if self.result:
            self.prompt = self.get_prompt()
        while (self.session.ready()):

            self.detect_intent()
            if self.result:
                self.prompt = self.get_prompt()

                if self.check_dialog_completion():
                    break
            else:
                console_log("ERR",'no result %s\n' % result)
                break

        self.session.set_tts_params(self.tts_engine, ' ')
        self.session.speak("Thank you.See you next time. ")
        
        



def handler(session, args):
    session.answer()
    session.setAutoHangup(False)
    options ="{start-input-timers=false,define-grammar=false,no-input-timeout=10000}"
    gdf_app = GdfApp(session,options)
    gdf_app.run()
    session.hangup()