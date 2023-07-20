Freeswitch python scripts for interacting with unimrcp servers 


## Usage

freeswitch dialplan extensions
```bash

;nuance-bot
    <extension name="493">
      <condition field="destination_number" expression="^493$">

          <action application="answer"/>
          <action application="set" data="tts_engine=unimrcp:ums-v2"/>
          <action application="set" data="asr_engine=unimrcp:ums-v2"/>
          <action application="set" data="MODEL=urn:nuance-mix:tag:model/A7315_C150290/mix.dialog"/>
          <action application="set" data="SSML=True"/>
          <action application="set" data="SELECTOR_CHANNEL= IVR channel"/>
          <action application="python" data="freeswitch_nuance_bot"/>

      </condition>
    </extension> 

```
