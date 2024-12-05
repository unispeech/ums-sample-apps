Freeswitch python scripts for interacting with unimrcp servers 

## NOTE

For using this script you must  have a working instance of unimrcp server.

Use the web page  [unimrcp](http://www.unimrcp.org/) to explore documentations and guids.



## NOTE
applicable freeswitch version is 1.8(if you build from source) or 1.10.5.release.8-1.el7 

## freeswitch deployment on centos with rpms
```bash
    yum install -y http://files.freeswitch.org/freeswitch-release-1-6.noarch.rpm epel-release
    yum install -y freeswitch-config-vanilla freeswitch-lang-* freeswitch-sounds-*
    
    systemctl enable freeswitch

    yum install freeswitch-asrtts-unimrcp.x86_64

    yum install freeswitch-python.x86_64

    yum install sofia-sip

```

Enable mod_unimrcp and mod_python in modules.conf and disable mod_opus
configure sip profile  sip external ip  and rtp external ip 
change permissions of /var/run/freeswitch from freeswitch to root if you want to run freeswitch with root user



## Configuring UniMRCP profile

Create a new UniMRCP profile for example ums-v2.xml, located in /usr/local/freeswitch/etc/freeswitch/mrcp_profiles, and pointing to the UniMRCP server configured in the previous step. In the example below, the IP address of UniMRCP Server is 10.128.0.4, and the IP address of FreeSWITCH is 10.128.0.5.
```xml
<include>
  <!-- UniMRCP Server MRCPv2 -->
  <profile name="ums-v2" version="2">
    <param name="client-ip" value="10.128.0.5"/>
    <param name="client-port" value="16092"/>
    <param name="server-ip" value="10.128.0.4"/>
    <param name="server-port" value="8060"/>
    <!--param name="force-destination" value="1"/-->
    <param name="sip-transport" value="udp"/>
    <!--param name="ua-name" value="FreeSWITCH"/-->
    <!--param name="sdp-origin" value="FreeSWITCH"/-->
    <!--param name="rtp-ext-ip" value="auto"/-->
    <param name="rtp-ip" value="10.128.0.5"/>
    <param name="rtp-port-min" value="15000"/>
    <param name="rtp-port-max" value="16000"/>
    <!-- enable/disable rtcp support -->
    <param name="rtcp" value="0"/>
    <!-- rtcp bye policies (rtcp must be enabled first)
             0 - disable rtcp bye
             1 - send rtcp bye at the end of session
             2 - send rtcp bye also at the end of each talkspurt (input)
    -->
    <param name="rtcp-bye" value="2"/>
    <!-- rtcp transmission interval in msec (set 0 to disable) -->
    <param name="rtcp-tx-interval" value="5000"/>
    <!-- period (timeout) to check for new rtcp messages in msec (set 0 to disable) -->
    <param name="rtcp-rx-resolution" value="1000"/>
    <!--param name="playout-delay" value="50"/-->
    <!--param name="max-playout-delay" value="200"/-->
    <!--param name="ptime" value="20"/-->
    <param name="codecs" value="PCMU PCMA L16/96/8000 telephone-event/101/8000"/>

    <!-- Add any default MRCP params for SPEAK requests here -->
    <synthparams>
    </synthparams>

    <!-- Add any default MRCP params for RECOGNIZE requests here -->
    <recogparams>
      <!--param name="start-input-timers" value="false"/-->
    </recogparams>
  </profile>
</include>

```
Remove all other sample profiles located in the same directory.
Afterwards, in the configuration file unimrcp.conf.xml, located in /usr/local/freeswitch/etc/freeswitch/autoload_configs directory, set the name of the configured profile.

```xml
<configuration name="unimrcp.conf" description="UniMRCP Client">
  <settings>
    <!-- UniMRCP profile to use for TTS -->
    <param name="default-tts-profile" value="ums-v2"/>
    <!-- UniMRCP profile to use for ASR -->
    <param name="default-asr-profile" value="ums-v2"/>
    <!-- UniMRCP logging level to appear in freeswitch.log.  Options are:
         EMERGENCY|ALERT|CRITICAL|ERROR|WARNING|NOTICE|INFO|DEBUG -->
    <param name="log-level" value="DEBUG"/>
    <!-- Enable events for profile creation, open, and close -->
    <param name="enable-profile-events" value="false"/>

    <param name="max-connection-count" value="100"/>
    <param name="offer-new-connection" value="1"/>
    <param name="request-timeout" value="3000"/>
  </settings>

  <profiles>
    <X-PRE-PROCESS cmd="include" data="../mrcp_profiles/*.xml"/>
  </profiles>

</configuration>

```
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

## Aws Lex V2 instructions

Configure expected NLSML format from unimrcp server on umslex.xml

```xml

    <results
      format="json"
      indent="0"
      replace-dots="true"
      confidence-format="auto"
      tag-format="semantics/json"
   />
```
Put following extentions to your dialplan xml 
```xml
    <extension name="493">
      <condition field="destination_number" expression="^493$">

          <action application="answer"/>
          <action application="set" data="tts_engine=unimrcp:lex_mrcp-v2"/>
          <action application="set" data="asr_engine=unimrcp:lex_mrcp-v2"/>
          <action application="set" data="AWS_BOT_ID=your_bot_id"/>
          <action application="set" data="AWS_ALIAS_ID=your_alias_id"/>
          <action application="python" data="freeswitch_lexv2"/>

      </condition>
    </extension> 
```
## Dialogflow instructions
Configure expected NLSML format of unimrcp server on umsgdf.xml
```xml

    <results
      format="json"
      indent="0"
      replace-dots="true"
      confidence-format="auto"
      tag-format="semantics/json"
   />
```
Put following extentions to your dialplan xml 
```xml
    <extension name="494">
      <condition field="destination_number" expression="^494$">

          <action application="answer"/>
          <action application="set" data="tts_engine=unimrcp:gdf_mrcp-v2"/>
          <action application="set" data="GDF_PROJECT_ID=your_project_id"/>
          <action application="python" data="freeswitch_gdfv1"/>

      </condition>
    </extension> 
```
## Dialogflow CX  instructions
Configure expected NLSML format of unimrcp server on umsgdf.xml for json
```xml

    <results
      format="json"
      indent="0"
      replace-dots="true"
      confidence-format="auto"
      tag-format="semantics/json"
   />
```
Configure expected NLSML format of unimrcp server on umsgdf.xml for xml
```xml

    <results
      format="standard"
      indent="0"
      replace-dots="true"
      confidence-format="auto"
      tag-format="semantics/xml"
   />
```

```xml
    <extension name="492">
      <condition field="destination_number" expression="^492$">

          <action application="answer"/>
          <action application="set" data="tts_engine=unimrcp:gdf_mrcp-v2"/>
          <action application="set" data="asr_engine=unimrcp:gdf_mrcp-v2"/>
          <action application="set" data="GDF_PROJECT_ID=rosy-crawler-288816"/>
          <action application="set" data="GDF_AGENT_ID=11f9f5bd-9754-407d-ac0a-3a7f6023589d"/>
          <action application="set" data="GDF_LOCATION=global"/>
          <action application="python" data="freeswitch_gdf_cx_xml"/>

      </condition>
    </extension> 
```
## Azure bot instructions
Configure expected NLSML format of unimrcp server on umsazurebot.xml for json
```xml

    <results
      format="json"
      indent="0"
      replace-dots="true"
      confidence-format="auto"
      tag-format="semantics/json"
   />
```

Configure expected NLSML format of unimrcp server on umsazurebot.xml for xml
```xml

    <results
      format="standart"
      indent="0"
      replace-dots="true"
      confidence-format="auto"
      tag-format="semantics/xml"
   />
```


```xml
    <extension name="487">
      <condition field="destination_number" expression="^487$">

          <action application="answer"/>
          <action application="python" data="freeswitch_azurebot"/>

      </condition>
    </extension> 
```
