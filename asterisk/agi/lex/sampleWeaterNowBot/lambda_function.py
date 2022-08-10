from botocore.vendored import requests

import time
import os
import logging

# from datetime import datetime
"""
    AWS lexV2 lambda script

    * This script demonstrates interaction with OpenWeatherMap api
    * Before begin please create account on OpenWeatherMap and get api key.
    * Use python 3.7 to deploy this script in aws lambda functions
    * Use cloudWatch to check logs 


    
"""

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

OWM_API_KEY = "*********************************"


def build_response(message):
    return {
        "dialogAction":{
            "type":"Close",
            "fulfillmentState":"Fulfilled",
            "message":{
                "contentType":"PlainText",
                "content": message
            }
        }
    }




def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }




def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    

    if 'sessionAttributes' in sessionState:
        sessionAttributes=sessionState['sessionAttributes']
        logger.debug('got  sessionAttributes={}'.format(sessionAttributes))
        return sessionAttributes
    return {}

def get_weather_now(intent_request):
    source = intent_request['invocationSource']
    session_attributes = get_session_attributes(intent_request) if get_session_attributes(intent_request) is not None else {}
    lattitude = None
    longitude = None
    if 'Latitude' in session_attributes and 'Longitude' in session_attributes:
        lattitude = session_attributes['Latitude']
        longitude = session_attributes['Longitude']
    logger.debug('got  Lattitude={},Longitude={}'.format(lattitude,longitude))
    logger.debug('got  source={}'.format(source))
    response = ""
    if lattitude is None or longitude is None:
        response+='Please enter lattitude and longitude respectively'
        
        return close(
                    intent_request,
                    session_attributes,
                    'Fulfilled',
                    {
                        'contentType': 'PlainText',
                        'content': response
                    }
                ) 
            
    elif ('-90' > lattitude > '90') or ('-180' > longitude > '180'):
        
        response+='Lattitude or Longitude value invalid. lat(-90 to 90), lon(-180 to 180)'
        
    else:
        current_weather = requests.get("http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=hourly,alerts,minutely,current&appid={}".format(lattitude, longitude, OWM_API_KEY)).json()
        logger.debug('got  current_weather={}'.format(current_weather))
        # current_date = ""
    
        # date_list = []
        # for i in range(len(current_weather['daily'])):
        #     date_list = datetime.fromtimestamp(current_weather['daily'][i]['dt'])
            
        
        # for item in current_weather['daily']:
        #     date = datetime.fromtimestamp(dt[item])
            
    
        response += "Weather forecast for tomorrow in location coordinates %s and %s: " % (lattitude,longitude)  + " Temperature: {:.2f} degree celsius,Winds: {} mph,Pressure level: {} millibars, Humidity: {}% ".format(
            # current_weather['daily'][0]['weather'][0]['main'],
            current_weather['daily'][1]['temp']['day'] - 273.15,
            current_weather['daily'][1]['wind_speed'],
            current_weather['daily'][1]['pressure'],
            current_weather['daily'][1]['humidity']
        )
        
    if response!="":
        logger.debug('got  response={}'.format(response))
        return close(
                    intent_request,
                    session_attributes,
                    'Fulfilled',
                    {
                        'contentType': 'PlainText',
                        'content': response
                    }
                ) 
           
        



def dispatch(intent_request):
    logger.debug('dispatch sessionId={}, intentName={}'.format(intent_request['sessionId'], intent_request['sessionState']['intent']['name']))

    intent_name = intent_request['sessionState']['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'WeatherForecast':
        return get_weather_forecast(intent_request)
        
    elif intent_name == 'WeatherNow':
        return get_weather_now(intent_request)
    
    raise Exception('Intent with name ' + intent_name + ' not supported')




def lambda_handler(event, context):
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
