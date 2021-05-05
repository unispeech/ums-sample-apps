from freeswitch import *
import json
"""

    Freeswitch Azure bot Application

    This script interacts with Azure echo bot  API via UniMRCP server.

    * Revision: 1
    * Date: May 5, 2021
    * Vendor: Universal Speech Solutions LLC

"""

class AzureBotApp:
    
    """A class representing Azure echo bot application"""

 

    def __init__(self,session,options):

        """Constructor"""
        self.options = options
        self.session = session
        self.engine = "unimrcp:azurebot_mrcp-v2"
        self.result = None
        self.grammar="builtin:speech/transcribe?"
        self.prompt="Welcome to Azure Echo bot.Say something i will repeat your phrase."


    def play_and_detect_speech(self):

        """This is an internal function which calls play_and_detect_speech"""
        data = "say:%s detect:%s %s%s" %(self.prompt,self.engine,self.options,self.grammar)
        self.session.execute("play_and_detect_speech", data)

        result = self.session.getVariable("detect_speech_result")
        if result:
            if 'Completion-Cause' not in str(result):
                result = json.loads(result)
                if len(result)>1:
                    console_log("info",'got  result  %s\n' % result)
                    self.result = result
    

    def get_prompt(self):

        """Retrieves prompt from the data returned by bot"""
        prompt = str(self.result['speak'])
        console_log("info",'got prompt %s\n' % prompt)
        return prompt
  

    def run(self):
        """Interacts with the caller in a loop until the dialog is complete"""
        while (self.session.ready()):

            self.play_and_detect_speech()
            if self.result:
                self.prompt = self.get_prompt()

            else:
                console_log("ERR",'no result %s\n' % self.result)
                break

        self.session.set_tts_params(self.engine, ' ')
        self.session.speak("Thank you.See you next time. ")
        
        



def handler(session, args):
    session.answer()
    session.setAutoHangup(False)
    options ="{start-input-timers=false,no-input-timeout=5000,recognition-timeout=5000}"
    azure_bot_app = AzureBotApp(session,options)
    azure_bot_app.run()
    session.hangup()