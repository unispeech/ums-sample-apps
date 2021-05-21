Freeswitch javascript v8 script for interacting with unimrcp server google dialogflow and jira 

## NOTE

For using this script you must  have a working instance of unimrcp server.

Use the web page  [unimrcp](http://www.unimrcp.org/) to explore documentations and guids.




Set up your umsgdf.xml on Unimrcp server
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
Applicable FreeSWITCH version is 1.6

## freeswitch deployment on centos with rpms
```bash
    yum install -y git alsa-lib-devel autoconf automake bison broadvoice-devel bzip2 curl-devel db-devel e2fsprogs-devel flite-devel g722_1-devel gcc-c++ gdbm-devel gnutls-devel ilbc2-devel ldns-devel libcodec2-devel libcurl-devel libedit-devel libidn-devel libjpeg-devel libmemcached-devel libogg-devel libsilk-devel libsndfile-devel libtheora-devel libtiff-devel libtool libuuid-devel libvorbis-devel libxml2-devel lua-devel lzo-devel mongo-c-driver-devel ncurses-devel net-snmp-devel openssl-devel opus-devel pcre-devel perl perl-ExtUtils-Embed pkgconfig portaudio-devel postgresql-devel python26-devel python-devel soundtouch-devel speex-devel sqlite-devel unbound-devel unixODBC-devel wget which yasm zlib-devel patch

    git clone -b v1.10 https://github.com/signalwire/freeswitch.git freeswitch

    ./bootstrap.sh -j

```
Enable compilation of unimrcp and v8 modules in modules.conf before building FreeSWITCH.
```
mod_unimrcp
mod_curl
mod_v8

```
Build and install FreeSWITCH in /usr/local/freeswitch directory or any other directory of your choice.
```bash
    ./configure --prefix=/usr/local/freeswitch
    make
    make install
    make cd-sounds-install

```
Enable loading of unimrcp,v8 and curl modules in modules.conf.xml located in /usr/local/freeswitch/etc/freeswitch/autoload_configs directory.
```
mod_unimrcp
mod_curl
mod_v8

```

Start FreeSWITCH
```bash
    cd /usr/local/freeswitch/bin
    freeswitch -ncwait

    fs_cli
```
## Configuring UniMRCP profile

Create a new UniMRCP profile ums-v2.xml, located in /usr/local/freeswitch/etc/freeswitch/mrcp_profiles, and pointing to the UniMRCP server configured in the previous step. In the example below, the IP address of UniMRCP Server is 10.128.0.4, and the IP address of FreeSWITCH is 10.128.0.5.
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
## Put following extentions to your dialplan xml

```xml
    <extension name="494">
      <condition field="destination_number" expression="^494$">

      <action application="javascript" data="/usr/local/freeswitch/scripts/dialogflow-jira-ivr/serviceDeskJira.js"/>

      </condition>
    </extension> 
```

Create dialogflow agent and import Support.zip
