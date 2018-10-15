#!/usr/bin/python

from flask import Flask, request, Response, json, abort
import settings
import re
import requests
import json
import watson
import events

app = Flask(__name__)

contexts = {}

UNKNOWN_USER = {'name': 'Unknown user', 'color': '#FF141A'}

@app.route('/', methods=['GET'])
def api_welcome():
    return 'Welcome to the CalendarBot API. It seems that the server is running correctly. Use a POST to this URL to get stuff.'

@app.route('/', methods=['POST'])
def receive_slack():
    body = request.json
    if 'challenge' in body:
        return Response(json.dumps({'challenge': body['challenge']}),
                        status=200,
                        mimetype='application/json')
    event_type = body['event']['type']

    if 'username' in body['event'] and body['event']['username'] == 'Calendar Bot':
        print("not reacting to my own message")
        return ""

    if event_type != "app_mention" and event_type != "message":
        print("I am not reacting to {}".format(event_type))
        return ""
    try:
        fromChannel = body['event']['channel']
        user_name = body['event']['user']
        requestText = body['event']['text']
    except:
        print('Something went wrong when initializing the parameters.')
        abort(500)

    payload = get_response( fromChannel, user_name, requestText )
    send_message_back( payload )
    return ""

def send_message_back( payload ):
    headers = {"Authorization":"Bearer "+ settings.SLACK_BOT_USER_OAUTH_TOKEN}
    requests.post(settings.SLACK_URL, headers=headers, json=payload)

def get_error_payload( channel, errorMessage ):
    '''
    Return the payload of the return message in case of an error
    '''
    return { 'channel': channel, 'text': 'Oops, something went wrong.',
	          'attachments': [{
                    'fallback': 'There was a problem with Calendar Bot.',
                    'color': '#FF141A',
		            'text': '',
					'fields': [
					    {
						  'short': False,
						  'title': 'Reason:',
						  'value': errorMessage
						}
				     ]
                  }]
				}

def hasTrigger(requestText):
    '''
    Returns true if the input text starts with the triggerword, or greets the bot (e.g. "hi BOT_NAME [...]", or "@BOTNAME, [...]", etc.)
    '''
    match = re.match(r'^(hi|hey|hello)?\s*@?'+settings.BOT_NAME, requestText, re.IGNORECASE)
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
            response_text = "Watson is confused. Try asking it another way."

    return response_text, attachment

def handle_create_vacation(user_name, context):
    '''
    Handles the creation of a new vacation request. Returns a result string, no attachment.
    '''
    vacation_type = context['vacationtype']
    start_date = context['date']
    end_date = context['date_2'] if 'date_2' in context else context['date']

    user_response = requests.get(settings.TEAM_CALENDAR_API_URL+'/users')
    users = user_response.json()
    user = findUser(user_name, users)
    vacation = events.VacationEvent(user=user_name, type=vacation_type, start_date=start_date, end_date=end_date)
    r = requests.post(settings.TEAM_CALENDAR_API_URL+'/events', json=json.loads(vacation.toJSON()))
    if r.status_code > 199 and r.status_code < 300:
        user_info = "Your user is not in the DB though. Please add it manually. " if user == UNKNOWN_USER else ""

        date_string = 'from ' + start_date + ' until ' + end_date if start_date != end_date else 'for ' + start_date
        response_text = "I added your availability ({} {}). ".format(vacation_type, date_string) \
                        + user_info + \
                        "Check it out on {}.".format(settings.TEAM_CALENDAR_URL)
    else:
        response_text = "I couldn't save that. " \
                        "I understood you wanted to create a new vacation, " \
                        "but something went wrong when posting the request." \
                        "\nResponse from the calendar webservice: \n\n{} - {} - {}".format(r.status_code, r.reason, r.content)
    return response_text, None

def handle_this_week_holidays():
    '''
    Handles the request for this weeks holidays. Returns a result string, and attachment cards for every holiday found.
    '''
    start = events.getStartOfThisWeekString()
    end = events.getEndOfThisWeekString()

    r = requests.get(settings.TEAM_CALENDAR_API_URL+'/events', params = {"start" : start, "end": end})
    results = r.json()
    count = len(results)

    if count:
        return "This weeks holiday schedule: ", getVacationTable(results)
    else:
        return "Nobody is off this week, looks like it's going to be full house this week!", None

def handle_today_holidays():
    '''
    Handles the request for todays holidays. Returns a result string, and attachment cards for every person that is off today.
    '''
    start = events.getStartOfTodayString()
    end = events.getEndOfTodayString()

    r = requests.get(settings.TEAM_CALENDAR_API_URL+'/events', params = {"start" : start, "end": end})
    results = r.json()
    count = len(results)

    if count:
        return "{0} {1} off today: ".format(count, "person is" if count == 1 else "people are"), getVacationTable(results)
    else:
        return "Nobody is off today, perfect day for a team lunch?", None

def findUser(username, users):
    for user in users:
        if user['username'] == username:
            return user
    return UNKNOWN_USER

def getVacationTable(vacation_json):
    user_response = requests.get(settings.TEAM_CALENDAR_API_URL+'/users')
    users = user_response.json()
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
                            "short": True,
                            "title": "Type",
                            "value": type
                        },
                        {
                            "short": True,
                            "title": "When",
                            "value": vacation['start'] + " - " + vacation['end']
                        }
                    ],
                }
        vacations_attachment.append( attachment )

    return vacations_attachment

def get_response( fromChannel, user_name, requestText ):
    context = None

    # First check if we have an ongoing session, in which case a context should exist for this user
    if user_name in contexts and contexts[user_name]:
        context = contexts[user_name]
    # If there is no context, and no trigger word, we will not react to the message
    elif not hasTrigger(requestText):
        return

    response = watson.ask_watson(requestText, context=context)
    conversation_ended = did_conversation_end(response)
    contexts[user_name] = response['context']

    attachment = None

    # If we don't have all information yet, delegate back to Watson and keep the context
    if not conversation_ended:
        response_text = response['output']['text'][0]
    elif response['intents']:
        response_text, attachment = get_response_from_intent(user_name, response)
        # We fully handled the user's request, so we clear the context.
        contexts[user_name] = None
    else:
        response_text = "I didn't get that. Please try rephrasing. Ask 'What can I ask you?' for help"

    return {    'channel': fromChannel,
                'text': response_text,
                'attachments': attachment
	          }

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
