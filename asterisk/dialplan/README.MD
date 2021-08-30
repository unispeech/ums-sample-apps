Asterisk sample dialplan applications for interaction  with unimrcp servers 

## NOTE

For using this script you must  have a working instance of unimrcp server and asterisk unimrcp module installed

Use the web page  [unimrcp](http://www.unimrcp.org/) to explore documentations.




## Usage


Download extension to  /etc/asterisk/,
Include extensions to /etc/asterisk/extensions.conf for example 
```
#include filename.conf
```

Change input parametr "p" mrcp profile p=your_mrcp_profile
```

exten => s,3,SynthAndRecog(${PROMPT},builtin:speech/transcribe?,plt-1&b=1&sct=1000&sint=15000&nit=10000,spl=en-US&p=your_mrcp_profile)

```
## query parameters to dialogflow cx agent
```
builtin:intent/00000000-0000-0000-0000-000000000000?parameters={'name':'Mike'}
```
get parameter from cx agent 
```
$session.params.name
```

