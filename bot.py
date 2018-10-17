import requests
import events
import re
import settings
import json
import watson
import responses as r

UNKNOWN_USER = {'name': 'Unknown user', 'color': '#FF141A'}

contexts = {}

def hasTrigger(requestText):
    '''
    Returns true if the input text starts with the triggerword, or greets the bot (e.g. "hi BOT_NAME [...]", or "@BOTNAME, [...]", etc.)
    '''
    match = re.match(r'^(hi|hey|hello|yo)?\s*@?'+settings.BOT_NAME, requestText, re.IGNORECASE)
    return True if match else False

def did_conversation_end(response):
    '''
    Returns true if the response is a 'final message', i.e. no more information is requested from the user.
    '''
    return 'branch_exited' in response['context']['system'] and response['context']['system']['branch_exited']

def get_response_from_intent(user_name, watson_response):
    '''
    This method creates a response based on what Watson returned (intent found? If yes, which one?).
    The method makes a call to the API to either POST or GET events, so it can take a while.
    '''
    intent = watson_response['intents'][0]['intent']
        
    if intent == 'createvacation':
        response_text, attachment = handle_create_vacation(user_name, watson_response['context'])
    elif intent == 'thisweeksholidays':
        response_text, attachment = handle_this_week_holidays()
    elif intent == 'todaysholidays':
        response_text, attachment = handle_today_holidays()
    else:
        attachment = None
        # As a default, do not alter the repsonse and delegate back to Watson.
        try:
            response_text = watson_response['output']['text'][0]
        except:
            response_text = r.WATSON_CONFUSED

    return response_text, attachment

def handle_create_vacation(user_name, context):
    '''
    Handles the creation of a new vacation request. Returns a result string, no attachment.
    '''
    try:
        vacation_type = context['vacationtype']
        start_date = context['date']
    except: 
        # Intent must have been interrupted, because we don't have what we need.
        return r.CALENDAR_UNCHANGED, None
    end_date = context['date_2'] if 'date_2' in context else context['date']

    users = requests.get(settings.TEAM_CALENDAR_API_URL+'/users').json()
    user = findUser(user_name, users)
    vacation = events.VacationEvent(user=user_name, type=vacation_type, start_date=start_date, end_date=end_date)
    response = requests.post(settings.TEAM_CALENDAR_API_URL+'/events', json=json.loads(vacation.toJSON()))
    if response.status_code > 199 and response.status_code < 300:
        user_info = r.USER_UNKNOWN if user == UNKNOWN_USER else ""

        date_string = r.FROM_UNTIL.format(start_date, end_date) if start_date != end_date else r.ON_DAY.format(start_date)
        response_text = r.AVAILABILITY_ADDED.format(vacation_type, date_string) + user_info + ' ' + r.CHECK_WEBSITE.format(settings.TEAM_CALENDAR_URL)
    else:
        response_text = r.CALENDAR_API_ERROR.format(response.status_code, response.reason, response.content)

    return response_text, None

def handle_this_week_holidays():
    '''
    Handles the request for this weeks holidays. Returns a result string, and attachment cards for every holiday found.
    '''
    start = events.getStartOfThisWeekString()
    end = events.getEndOfThisWeekString()

    result = requests.get(settings.TEAM_CALENDAR_API_URL+'/events', params = {"start" : start, "end": end})
    results = result.json()
    count = len(results)

    if count:
        return r.THIS_WEEKS_HOLIDAYS, getVacationTable(results)
    else:
        return r.NOBODY_OFF_THIS_WEEK, None

def handle_today_holidays():
    '''
    Handles the request for todays holidays. Returns a result string, and attachment cards for every person that is off today.
    '''
    start = events.getStartOfTodayString()
    end = events.getEndOfTodayString()

    response = requests.get(settings.TEAM_CALENDAR_API_URL+'/events', params = {"start" : start, "end": end})
    results = response.json()
    count = len(results)

    if count:
        return r.OFF_TODAY.format(count, r.PERSON_SINGULAR if count == 1 else r.PERSON_PLURAL), getVacationTable(results)
    else:
        return r.NOBODY_OFF_TODAY, None

def findUser(username, users):
    for user in users:
        if user['username'] == username:
            return user
    return UNKNOWN_USER

def getVacationTable(vacation_json):
    users = requests.get(settings.TEAM_CALENDAR_API_URL+'/users').json()

    vacations_attachment = []
    for vacation in vacation_json:
        type = events.get_watson_type_string(vacation['type'])
        user = findUser(vacation['user'], users)
        attachment = {
                    'fallback': '',
                    'color': user['color'],
                    'text': user['name'],
                    'fields': [
                        {
                            'short': True,
                            'title': 'Type',
                            'value': type
                        },
                        {
                            'short': True,
                            'title': r.WHEN,
                            'value': vacation['start'] + ' - ' + vacation['end']
                        }
                    ],
                }
        vacations_attachment.append( attachment )

    return vacations_attachment

def get_response_and_attachments(user_name, requestText, direct_message=False):
    context = None

    # First check if we have an ongoing session, in which case a context should exist for this user
    if user_name in contexts and contexts[user_name]:
        context = contexts[user_name]
    # If there is no context, and no trigger word, we will not react to the message
    elif not direct_message and not hasTrigger(requestText):
        return "", None
    
    response = watson.ask_watson(requestText, context=context)
    conversation_ended = did_conversation_end(response)
    contexts[user_name] = response['context']

    attachment = None

    # If we don't have all information yet, delegate back to Watson and keep the context
    if not conversation_ended:
        response_text = response['output']['text'][0]

    elif response['intents']:
        print('processing intent #'+response['intents'][0]['intent'])
        response_text, attachment = get_response_from_intent(user_name, response)    
        
        # We fully handled the user's request, so we clear the context.
        if response['intents'][0]['intent'] in ['help', 'General_About_You', 'General_Negative_Feedback', 'General_Positive_Feedback', 'General_Ending', 'todaysholidays', 'createvacation', 'thisweeksholidays' ]:
            contexts[user_name] = None
    else:
        response_text = r.DID_NOT_UNDERSTAND

    return response_text, attachment
