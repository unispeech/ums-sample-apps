Freeswitch python scripts for interacting with unimrcp servers 

## Use Javascript with mod_v8 mode_python is not stabil. this is only demonstration

## NOTE

For using this script you must  have a working instance of unimrcp server.

Use the web page  [unimrcp](http://www.unimrcp.org/) to explore documentations and guids.



FreeSwitchDemoGDF.py is for NLSML JSON format
set up your umsgdf.xml
```xml

    <results
      format="json"
      indent="0"
      replace-dots="true"
      confidence-format="auto"
      tag-format="semantics/json"
   />
```
## NOTE
applicable freeswitch version is 1.8(if you build from source) or 1.10.5.release.8-1.el7 

## freeswitch deployment on centos with rpms
```bash
    yum install -y http://files.freeswitch.org/freeswitch-release-1-6.noarch.rpm epel-release
    yum install -y freeswitch-config-vanilla freeswitch-lang-* freeswitch-sounds-*
    
    systemctl enable freeswitch

    yum install freeswitch-asrtts-unimrcp.x86_64

    yum install freeswitch-python.x86_64


```

enable mod_unimrcp and mod_python in modules.conf and disable mod_opus
configure sip profile  sip-ext-ip ind rtp-ext-ip 
change permissions of /var/run/freeswitch from freeswitch to root if you want to run freeswitch with root user

start 
```bash
    freeswitch -ncwait

    fs_cli
```

## NOTE
python site-packages must contain 
```python
    freeswitch.py
```

## Put following extentions to your dialplan xml
for lex
```
    <extension name="493">
      <condition field="destination_number" expression="^493$">

          <action application="answer"/>
          <action application="set" data="tts_engine=unimrcp:lex_mrcp-v2"/>
          <action application="set" data="asr_engine=unimrcp:lex_mrcp-v2"/>
          <action application="set" data="AWS_BOT_ID=QL2JKXN9BI"/>
          <action application="set" data="AWS_ALIAS_ID=TSTALIASID"/>
          <action application="python" data="FreeSwitchDemoLEXV2"/>

      </condition>
    </extension> 
```
for gdf
```
    <extension name="494">
      <condition field="destination_number" expression="^494$">

          <action application="answer"/>
          <action application="set" data="tts_engine=unimrcp:gdf_mrcp-v2"/>
          <action application="python" data="FreeSwitchDemoGDF"/>

      </condition>
    </extension> 
```
