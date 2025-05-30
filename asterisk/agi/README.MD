Asterisk python agi scripts for interacting with unimrcp servers 

## NOTE

For using this script you must  have a working instance of unimrcp server and asterisk unimrcp module installed

Use the web page  [unimrcp](http://www.unimrcp.org/) to explore documentations.

## Installation

install python-asterisk.

Using apt

```bash
apt-get install python-asterisk
```

Using yum

```bash
yum install python-asterisk
```



Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pyst2.

```bash
pip install pyst2
```

## Usage

Put this extentions to your /etc/asterisk/extensions.conf
```bash

;dialogflow cx
exten => 751,1,Answer()
exten => 751,2,Set(GDF_PROJECT_ID="your_project_id")
exten => 751,3,Set(GDF_AGENT_ID="your_agent_id")
exten => 751,4,Set(GDF_LOCATION="your_agent_location")
exten => 751,5,agi(/gdf/sample/agi_dialogflowCX.py)
;azurebot
exten => 752,1,Answer()
exten => 752,2,agi(/azure/sample/agi_azurebot.py)
;aws lex
exten => 753,1,Answer()
exten => 753,2,agi(/lex/sample/agi_lex.py)
;aws lexv2
exten => 753,1,Answer()
exten => 753,2,Set(AWS_BOT_ID="your_bot_id")
exten => 753,3,Set(AWS_ALIAS_ID="your_bot_alias_id")
exten => 753,4,agi(/lex/sample/agi_lexv2.py)


;openaibs 
exten => 755,1,Answer()
exten => 755,2,Set(LANGUAGE="en-US")
exten => 755,3,Set(VOICENAME="coral")
; The set of modalities the model can respond with. To disable audio, set this to "text".
exten => 755,4,Set(MODALITIES="text\,audio")
exten => 755,5,Set(TRANSCRIPTION_MODEL="gpt-4o-mini-transcribe")
exten => 755,6,agi(agi_openaibs.py)


;openaibs functioncall
exten => 756,1,Answer()
exten => 756,2,Set(LANGUAGE="en-US")
exten => 756,3,Set(VOICENAME="coral")
exten => 756,4,set(METHOD=create-response)
exten => 756,5,set(JSONPATH=/var/lib/asterisk/agi-bin/tools.json)
exten => 756,6,Set(MODALITIES="text\,audio")
exten => 756,7,Set(TRANSCRIPTION_MODEL="gpt-4o-mini-transcribe")
exten => 756,8,agi(agi_openaibs_functioncall.py)

;openaibs instructions
exten => 757,1,Answer()
exten => 757,2,Set(LANGUAGE="en-US")
exten => 757,3,Set(VOICENAME="coral")
exten => 757,4,Set(INSTRUCTIONS=You are Car Rental Agent)
exten => 757,5,set(METHOD=create-response)
exten => 757,6,Set(MODALITIES="text\,audio")
exten => 757,7,Set(TRANSCRIPTION_MODEL="gpt-4o-mini-transcribe")
exten => 757,8,agi(agi_openaibs_instructions.py)


;open ai chatgpt
exten => 756,1,Answer()
exten => 756,2,agi(agi_chatgpt.py)
```



Note that if your expected NLSML INSTANCE FORMAT  from unimrcp-server is json you must add nif=json to options or delete it if you want to use default xml format

```bash
options = 'plt=1&b=1&sct=1000&sint=15000&nit=10000&nif=json'
```

for geting xml/json object string value  you must set full path of  element

json example

```bash
prompt = agi.get_variable('RECOG_INSTANCE(0/0/responseMessages/0/text/text/0)')
```
xml example
```bash
prompt = agi.get_variable('RECOG_INSTANCE(0/0/response_Messages/0/text/text/0)')
```
 
Uncomment this line if your python version is 2.7 

```python
        if isinstance(prompt, str):
        prompt = unicode(prompt, 'utf-8')
```
