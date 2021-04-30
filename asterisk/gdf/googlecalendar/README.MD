Asterisk python agi scripts for interacting with unimrcp server 

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

install python google packages
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
Enable Calendar api for service account

## NOTE 
For using calendar without G Suite domain wide delegation

create calendar for service account 
```python
    calendar = {
    'summary': 'calendarSummary',
    'timeZone': 'America/Los_Angeles'
}

created_calendar = service.calendars().insert(body=calendar).execute()

print created_calendar['id']
```

Giv calendar owner role to your gmail 
```python
rule = {
    'scope': {
        'type': 'user',
        'value': 'your gmail',
    },
    'role': 'owner'
}


created_rule = service.acl().insert(calendarId='created calendar id', body=rule).execute()

print created_rule['id']
```

Insert gcalendar.sql to mysql gcalendar database

Define mysql credentials in config.py

Insert  gclanedar.zip to dialogflow agent


Add  extention to your /etc/asterisk/extensions.conf
```bash

;dialogflow gcalendar
exten=> 747,1,Answer
exten=> 747,2,Set(GDF_PROJECT_ID="gcalendar-glrl")
exten=> 747,3,agi(googlecalendar/agi_dialogflow.py)
exten=> 747,4,Hangup()
```




Add nif=json  expected NLSML INSTANCE FORMAT  from unimrcp-server is json.Default format is xml

```bash
options = 'plt=1&b=1&sct=1000&sint=15000&nit=10000&nif=json'
```

Set full path of  element for geting xml/json object string value

json example

```bash
prompt = agi.get_variable('RECOG_INSTANCE(0/0/responseMessages/0/text/text/0)')
```
xml example
```bash
prompt = agi.get_variable('RECOG_INSTANCE(0/0/response_Messages/0/text/text/0)')
```

