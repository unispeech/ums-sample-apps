"""

    FreeSWITCH Dialogflow CX Application
    This script interacts with Google Dialogflow CX API via UniMRCP server.
    * Revision: 1
    * Date: May 7, 2021
    * Vendor: Universal Speech Solutions LLC


"""


import json
from freeswitch import *
      

class GdfCxApp:
    
    """A class representing Dialogflow application"""

 

    def __init__(self,session,options):

        """Constructor"""

        self.options = options
        self.session = session
        self.asr_engine = self.session.getVariable("asr_engine")
        self.tts_engine = self.session.getVariable("tts_engine")
        self.project_id = self.session.getVariable('GDF_PROJECT_ID')
        self.agent_id = self.session.getVariable('GDF_AGENT_ID')
        self.location = self.session.getVariable('GDF_LOCATION')
        self.result= None 
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
        self.play_and_detect_speech()

 

    def detect_intent(self):

        """Performs a streaming intent detection"""

        self.grammars = "%s\n%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())
        self.play_and_detect_speech()



    def play_and_detect_speech(self):

        """This is an internal function which calls play_and_detect_speech"""

        data = "say:%s detect:%s %s%s" %(self.prompt,self.asr_engine,self.options,self.grammars)
        self.session.execute("play_and_detect_speech", data)
        self.result=self.session.getVariable("detect_speech_result")
        
        
        
        

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
        prompt=''
        result=json.loads(self.result)
        responseMessages=result['responseMessages']
        for message in responseMessages:
            if 'text' in message:
                prompt += message['text']['text'][0]   
        prompt = str(prompt)
        console_log("INFO",'got next prompt %s\n' % prompt)
        return prompt

 

    def check_dialog_completion(self):

        """Checks wtether the dialog is complete"""
        result=json.loads(self.result)
        current_page_display_name =result['currentPage']['displayName']
        complete = False
        if current_page_display_name == "End Session":
            console_log("INFO",'got current page display name: %s\n' % str(current_page_display_name))
            complete = True
        return complete
          

        

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""
        
        self.trigger_welcome_intent()

        if 'Completion-Cause' in str(self.result):
            console_log("ERR",'failed to trigger welcome intent')
            return

        processing = False

        self.prompt = self.get_prompt()

        if self.prompt:
            processing = True
    
        while processing:
            
            self.detect_intent()
            processing = True
            
            if 'Completion-Cause' not in str(self.result):
                
                if self.check_dialog_completion():
                    processing = False
                    
                self.prompt = self.get_prompt()    

            elif '001' not in str(self.result) and '002' not in str(self.result):
                    processing == False

        self.session.set_tts_params(self.tts_engine, ' ')
        self.session.speak("Thank you.See you next time. ")
        



def handler(session, args):

    """Freeswitch handler function.Without it can't work anything"""

    session.answer()
    session.setAutoHangup(False)
    options ="{start-input-timers=false,define-grammar=false,no-input-timeout=5000,recognition-timeout=5000}"
    gdf_cx_app = GdfCxApp(session,options)
    gdf_cx_app.run()
    session.hangup()