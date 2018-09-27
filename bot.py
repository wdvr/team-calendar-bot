#!/usr/bin/python

from flask import Flask, request, Response, json
import settings
import re
import requests
import json
import watson

app = Flask(__name__)

contexts = {}

@app.route('/', methods=['GET'])
def api_welcome():
    return 'Welcome to the CalendarBot API. It seems that the server is running correctly. Use a POST to this URL to get '

@app.route('/', methods=['POST'])
def receive_mattermost():
    """We only have 1 incoming hook"""
    try:
        body = request.json
        token = body['token']
        fromChannel = body['channel_name']
        userName = body['user_name']
        requestText = body['text']
        requestUserid = body['user_id']
    except:
        app.logger.error('Something went wrong when initializing the parameters.')
        return send_message_back( get_error_payload( fromChannel, "The integration is not correctly set up. Could not fetch all necessary request parameters." ) )

    if settings.MATTERMOST_TOKEN:
        if not token == settings.MATTERMOST_TOKEN:
            app.logger.error('Received wrong token, received [%s]', token)
            return send_message_back( get_error_payload( fromChannel, "The integration is not correctly set up. Token not valid." ) )

    
    payload = get_response( fromChannel, userName, requestText )

    if payload is None:
        return send_message_back( get_error_payload( fromChannel, "There was an exception when searching for the issue in Jira." ) )

    return send_message_back( payload )

def send_message_back( payload ):
    resp = Response(
		json.dumps( payload ),
        status=200,
        mimetype='application/json')
    return resp

def get_error_payload( channel, errorMessage ):
    """Return the payload of the return message in case of an error"""
    return { 'response_type': 'ephemeral', 'channel': channel, 'text': 'Oops, something went wrong.', 'username': settings.BOT_NAME, 
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

def get_response( fromChannel, userName, requestText ):
    context = None
    if userName in contexts:
        context = contexts[userName]
    response = watson.ask_watson(requestText, context=context)
    contexts[userName] = response['context']
    payload = { 'response_type': 'in_channel', 
                'channel': fromChannel, 
                'text': userName + ', I got your message: ' + requestText, 
                'username': settings.BOT_NAME,
                'icon_url': settings.BOT_ICON
	          }

    return payload


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
