
"""
    Google Calendar Connector Routine

    This script provides helper routine for retrieving data from
    the Google Calendar.

    * Revision: 1
    * Date: Apr 29, 2020
    * Vendor: Universal Speech Solutions LLC
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient
import dateutil.parser
from datetime import datetime, timedelta
import pytz
import json
import os.path
from config import *
from google.api_core.exceptions import AlreadyExists, NotFound


class GoogleCalendarConnector:

    """A Google Calendar connector class"""

    def get_calendar_service(self):
        """Builds calendar service"""
        SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/calendar.events']
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE_PATH, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        # print(str(service))
        return service

    def get_event_by_mail(self,email):
        """Retrieves event from Google Calendar by email"""
        result=dict()
        result['status'] = False
        try:
            service = self.get_calendar_service() 
            now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                result['status'] = True
                result['message'] = 'No events found'
            for event in events:
                result['status'] = True
                if 'attendees' in event:
                    for i in event['attendees']:
                        if i['email'] == email:
                            result['status'] = True
                            self.eventId = event['id']
                            result['id'] = event['id']
                            result['appointment_date'] = self.get_date_from_event(event['start'])
                            break

        except googleapiclient.errors.HttpError:
            result['error_cause']= 'Failed to get event'
        except:
            result['error_cause'] = 'Unknown error occurred'

        return result

    def get_event_by_id(self,eventid):
        """Retrieves event from Google Calendar by event id"""
        result=dict()
        result['status'] = False
        try:
            service = self.get_calendar_service()
            self.eventId = eventid
            event= service.events().get(
                calendarId=CALENDAR_ID,
                eventId=eventid
            ).execute()

            if event:
                result['status'] = True
                result['appointment_date'] = self.get_date_from_event(event['start'])

        except googleapiclient.errors.HttpError:
            result['error_cause']= 'Failed to get event'
        except:
            result['error_cause'] = 'Unknown error occurred'

        return result

    

    def create_event(self,dates,callerid,callid,email):
        """Creates event in Google Calendar"""
        result=dict()
        result['status'] = False
        try:
            service = self.get_calendar_service()
            # print(service)
            start = dates['startDateTime']
            end = dates['endDateTime']
            event_result = service.events().insert(
                calendarId=CALENDAR_ID,
                body={
                    "summary": 'GDF Event for %s' % (callerid),
                    "description": 'Created by GDF script for callerid %s, callid %s, email %s' % (callerid,callid,email),
                    "start": {"dateTime": start },
                    "end": {"dateTime": end },
                   
                    
                }
            ).execute()

            if event_result:
                
                result['status'] = True
                result['id'] = event_result['id']

        except googleapiclient.errors.HttpError:
            result['error_cause']= 'Failed to update event'
        except:
            result['error_cause'] = 'Unknown error occurred'
        return result

    def get_date_from_event(self,date):
        date_time_str = date.get('dateTime')
        time_zone_str = date.get('timeZone')

        date_time = dateutil.parser.parse(date_time_str)
        if time_zone_str:
            time_zone = pytz.timezone(time_zone_str)
            date_time = date_time.astimezone(time_zone)

        if TIME_ZONE:
            time_zone = pytz.timezone(TIME_ZONE)
            date_time = date_time.astimezone(time_zone)

        return date_time.strftime("%Y/%m/%d %H:%M:%S")

