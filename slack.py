#!/usr/bin/python

from flask import Flask, request, Response, abort
import settings
import json
import requests
import bot
import responses

app = Flask(__name__)

@app.route('/', methods=['GET'])
def api_welcome():
    return responses.API_WELCOME

@app.route('/', methods=['POST'])
def receive_slack():
    body = request.json
    if 'challenge' in body:
        return Response(json.dumps({'challenge': body['challenge']}),
                        status=200,
                        mimetype='application/json')
    event_type = body['event']['type']

    # not reacting to the bot's own messages
    if 'username' in body['event'] and body['event']['username'] == 'Calendar Bot':
        return ""

    if event_type != "app_mention" and event_type != "message":
        return ""

    try:
        fromChannel = body['event']['channel']
        user_name = body['event']['user']
        requestText = body['event']['text']
        eventType = body['event']['type']
    except:
        abort(500)

    payload = get_response( fromChannel, user_name, requestText, eventType )
    send_message_back( payload )
    return ""

def send_message_back( payload ):
    headers = {"Authorization":"Bearer "+ settings.SLACK_BOT_USER_OAUTH_TOKEN}
    requests.post(settings.SLACK_URL, headers=headers, json=payload)

def get_response( fromChannel, user_name, requestText, eventType ):
    is_mention = eventType == 'app_mention'
    response_text, attachment = bot.get_response_and_attachments(user_name, requestText, direct_message=is_mention)

    return {    'channel': fromChannel,
                'text': response_text,
                'attachments': attachment
	          }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=settings.WEBSERVER_PORT, debug=True)
