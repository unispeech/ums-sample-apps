#!/usr/bin/python3.8
from config import *
from asterisk.agi import *
from openai import OpenAI
import os

class SpeechTranscriptionApp:

    """A class representing speech transcription application"""

    def __init__(self, options):

        """Constructor"""

        self.options = options

        self.status = None

        self.cause = None
        
        self.prompt = None

        self.messages=[]

 
  




    def compose_chat_messages(self,content,role):

        """Composes a built-in speech grammar"""
        agi.verbose('got content %s' % content)
        agi.verbose('got role %s' % role)
        self.messages.append({"role": role, "content": content}),


    def create_chat(self):
        client = OpenAI(
            api_key=OPENAI_KEY
        )
        result = dict()

        result['status'] = False

        try:

            agi.verbose('got model %s got messages %s' %(OPENAI_MODEL,self.messages))

            response = client.chat.completions.create(
                model= OPENAI_MODEL,
                messages=self.messages
            )

            agi.verbose('got messages %s' % response.choices[0].message.content)
            result['response'] = response.choices[0].message.content

            if result:
                result['status'] = True

        except Error as e:
            result['error_cause'] = 'connection Error [%d]: %s' % (
                e.args[0], e.args[1])
        except:
            result['error_cause'] = 'Unknown error occurred'

       
        agi.verbose('got result %s' % result)

        return result


  

       
    

    def detect_intent(self):

        """Performs a streaming intent detection"""

        # self.compose_speech_options()

        self.grammars = "%s,%s" % (self.compose_speech_grammar(), self.compose_dtmf_grammar())

        self.synth_and_recog()



    def synth_and_recog(self):

        """This is an internal function which calls SynthAndRecog"""

        if not self.prompt:
            self.prompt = ' '
        agi.verbose('got completion cause %s' % self.prompt)
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

        return grammar

        
        
        

    def append_option_parameter(self, options, name, value, separator):
        """Appends a name/value parameter to the specified grammar"""
        options += "%s%s=%s" % (separator, name, value)
        
        return options

    def compose_dtmf_grammar(self):

        """Composes a built-in DTMF grammar"""

        grammar = 'builtin:dtmf/digits'
        separator = '?'

        return grammar



    def append_grammar_parameter(self, grammar, name, value, separator):

        """Appends a name/value parameter to the specified grammar"""
        grammar += "%s%s=%s" % (separator, name, value)
        return grammar


    def get_prompt(self):

        """Retrieves prompt from the data returned by bot"""
        prompt = agi.get_variable('RECOG_INSTANCE(0/0/StreamingRecognitionResult/alternatives/transcript)')
        """Uncomment this line if your python version is 2.7"""
        # if isinstance(prompt, str):
           
        #     prompt = unicode(prompt, 'utf-8')
        agi.verbose('got prompt %s' % prompt)
        return prompt
 

    def run(self):

        """Interacts with the caller in a loop until the dialog is complete"""      
        
        processing = False

        content="You are a helpful assistant on a phone call."

        self.compose_chat_messages(content,"system")


        result = self.create_chat()

        if result['status']==True:

            self.prompt=result['response']


        if self.prompt:
            processing = True

        while processing:
            self.detect_intent()

            processing = True
            if self.status == 'OK':
                if self.cause == '000':
                    self.compose_chat_messages(self.get_prompt(),"user")
                    result = self.create_chat()
                    if result['status']==True:
                        self.prompt=result['response']
                    
                elif self.cause != '001' and self.cause != '002':
                    processing = False

            elif self.cause != '001' and self.cause != '002':
                processing = False

 

        if not self.prompt:
            self.prompt = 'Thank you. See you next time.'
        agi.appexec('MRCPSynth', "\\\"%s\\\"" % self.prompt)

 

agi = AGI()
options = 'plt=1&b=1&sct=3000&sint=15000&nit=10000&p=ums2'
chatgpt_app_gsr = SpeechTranscriptionApp(options)
chatgpt_app_gsr.run()
agi.verbose('exiting')