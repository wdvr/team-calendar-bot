import json
from datetime import datetime, timedelta

import pytz
import settings

local_tz = pytz.timezone(settings.TIME_ZONE)
fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

# Map Watson strings to TeamCalendar strings
VACATION_TYPES = {
    'working from home': 'WORK_FROM_HOME',
    'sickness': 'SICK_DAY',
    'site visit' : 'ON_SITE',
    'vacation': 'VACATION'
    }


class VacationEvent():
    def __init__(self, user, type, start_date, end_date):
        self.user = user
        self.type = VACATION_TYPES[type]
        # add time to the events (full day always)
        self.start = convertToUTC(start_date + 'T00:00:00.000Z')
        self.end = convertToUTC(end_date + 'T23:59:59.999Z')

        self.resizable = { 'beforeStart': True, 'afterEnd': True }
        self.draggable = True
        self.title = ''
        self.color = {'primary': '', 'secondary': ''}

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

def get_watson_type_string(search_key):
    for watson_string, enum_key in VACATION_TYPES.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
        if search_key == enum_key:
            return watson_string.capitalize()
    return "Unknown type"


def convertToUTC(dt_string):
    dt = datetime.strptime(dt_string, fmt)

    local_dt = local_tz.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)    

    return date_to_string(utc_dt)

def date_to_string(date):
    '''
    Converts to our specific string format.
    '''
    return date.strftime(format=fmt)

def getStartOfTodayString():
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    start_local = local_tz.localize(start, is_dst=None)
    return date_to_string(start_local.astimezone(pytz.utc) )

def getEndOfTodayString():
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day, 23, 59)
    start_local = local_tz.localize(start, is_dst=None)
    return date_to_string(start_local.astimezone(pytz.utc) )

def getStartOfThisWeekString():
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day) - timedelta(days=today.weekday())
    start_local = local_tz.localize(start, is_dst=None)
    return date_to_string(start_local.astimezone(pytz.utc))

def getEndOfThisWeekString():
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day) + timedelta(days=(7 - today.weekday()))
    start_local = local_tz.localize(start, is_dst=None)
    return date_to_string(start_local.astimezone(pytz.utc) )

if __name__ == "__main__":
    event = VacationEvent('john', 'working from home', '2019-01-05', '2019-01-06')
    print(event.toJSON())
