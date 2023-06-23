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

;nuance-sr
exten => 751,1,Answer()
exten => 751,2,agi(agi_nuance_sr.py)

;nuance-nlu
exten => 752,1,Answer()
exten => 753,2,agi(agi_nuance_sr_nlu.py)

;nuance-bot
exten => 753,1,Answer()
exten => 753,2,Set(MODEL="urn:nuance-mix:tag:model/A7315_C150290/mix.dialog")
exten => 753,3,Set(SSML=True)
exten => 753,4,agi(agi_nuance_bot.py)
```



Note that if your expected NLSML INSTANCE FORMAT  from unimrcp-server is json you must add nif=json to options or delete it if you want to use default xml format

```bash
options = 'plt=1&nif=json'
```


Uncomment this line if your python version is 2.7 

```python
        if isinstance(prompt, str):
        prompt = unicode(prompt, 'utf-8')
```
