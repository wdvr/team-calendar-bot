#!/usr/bin/python

from flask import Flask, request, Response
import settings
import json
import bot
import responses

app = Flask(__name__)

@app.route('/', methods=['GET'])
def api_welcome():
    return responses.API_WELCOME

@app.route('/', methods=['POST'])
def receive_mattermost():
    try:
        body = request.json
        token = body['token']
        fromChannel = body['channel_name']
        user_name = body['user_name']
        requestText = body['text']
    except:
        return send_message_back( get_error_payload( fromChannel, responses.WRONG_SETUP ) )

    if settings.MATTERMOST_TOKEN:
        if not token == settings.MATTERMOST_TOKEN:
            return send_message_back( get_error_payload( fromChannel, responses.INVALID_TOKEN ) )

    payload = get_response( fromChannel, user_name, requestText )

    return send_message_back( payload )

def send_message_back( payload ):
    resp = Response(
		json.dumps( payload ),
        status=200,
        mimetype='application/json')
    return resp

def get_error_payload( channel, errorMessage ):
    '''
    Return the payload of the return message in case of an error
    '''
    return { 'response_type': 'ephemeral', 'channel': channel, 'text': responses.GENERIC_ERROR, 'username': settings.BOT_NAME, 
	          'attachments': [{
                    'fallback': responses.GENERIC_PROBLEM,
                    'color': '#FF141A',
		            'text': '',
					'fields': [
					    {
						  'short': False,
						  'title': responses.REASON,
						  'value': errorMessage
						}
				     ]
                  }]
				}

def get_response( fromChannel, user_name, requestText ):
    response_text, attachment = bot.get_response_and_attachments(user_name, requestText)
    
    return { 'response_type': 'in_channel', 
                'channel': fromChannel, 
                'text': response_text, 
                'username': settings.BOT_NAME,
                'icon_url': settings.BOT_ICON,
                'attachments': attachment
	          }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=settings.WEBSERVER_PORT, debug=True)
