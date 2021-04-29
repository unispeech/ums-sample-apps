from freeswitch import *
import json
      
"""
    Freswitch Lex V2 Application

    This script interacts with Lex V2 API via UniMRCP server.

    * Revision: 1
    * Date: apr 28, 2021
    * Vendor: Universal Speech Solutions LLC
""" 

class LexV2App:
    
    """A class representing LexV2 application"""
    def __init__(self,session,options):

        """Constructor"""

        self.options = options
        self.session = session
        self.asr_engine = self.session.getVariable("asr_engine")
        self.tts_engine = self.session.getVariable("tts_engine")
        self.bot_id = self.session.getVariable('AWS_BOT_ID')
        self.alias_id = self.session.getVariable('AWS_ALIAS_ID')
        self.intent_name = None
        self.message = "Welcome to orderflowers bot.How can i help you?"
        self.result= None 
        



    def trigger_welcome_intent(self):

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
        
        prompt = str(self.result['textResponse']['messages'][0]['content'])
        return prompt

 

    def check_dialog_completion(self):

        """Checks wtether the dialog is complete"""

        complete = False
        if str(self.result['intentResult']['sessionState']['dialogAction']['type']) == "Close":
            complete = True
            console_log("info",'got end of conversation %s' % complete)
        return complete


    def get_and_process_result(self):

        """Get and process result from bot"""

        result = self.session.getVariable("detect_speech_result")
        if result:
            if 'Completion-Cause' not in str(result):
                result = json.loads(result)
                if len(result)>1:
                    self.result = result
        
            

        

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""
        
        self.trigger_welcome_intent()
        if self.result:
           self.prompt = self.get_prompt()
        while (self.session.ready()):
            
            self.detect_intent()
            if self.result:
                if self.check_dialog_completion():
                    break
                
                self.prompt = self.get_prompt()

            else:
                console_log("ERR",'no result %s\n' % self.result)
                break

        self.session.set_tts_params(self.tts_engine, ' ')
        self.session.speak("Thank you.See you next time. ")
        



def handler(session, args):

    """Freeswitch handler function.Without it can't work anything"""

    session.answer()
    session.setAutoHangup(False)
    options ="{start-input-timers=true,define-grammar=false,no-input-timeout=10000,recognition-timeout=5000}"
    gdf_app = LexV2App(session,options)
    gdf_app.run()
    session.hangup()