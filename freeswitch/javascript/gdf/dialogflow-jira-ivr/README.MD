Freeswitch python scripts for interacting with unimrcp servers 

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

    git clone -b v1.6 https://github.com/signalwire/freeswitch.git freeswitch

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
Enable loading of unimrcp and v8 modules in modules.conf.xml located in /usr/local/freeswitch/etc/freeswitch/autoload_configs directory.
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



## Put following extentions to your dialplan xml

for gdf
```
    <extension name="494">
      <condition field="destination_number" expression="^494$">

      <action application="javascript" data="/usr/local/freeswitch/scripts/dialogflow-jira-ivr/serviceDeskJira.js"/>

      </condition>
    </extension> 
```
