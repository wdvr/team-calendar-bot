#!/usr/bin/python

from flask import Flask, request, Response, abort
import settings
import json
import requests
import bot
import responses
import threading

headers = {"Authorization":"Bearer "+ settings.SLACK_BOT_USER_OAUTH_TOKEN}

STATUS_200 = json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

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
        return STATUS_200

    if event_type != "app_mention" and event_type != "message":
        return STATUS_200

    try:
        fromChannel = body['event']['channel']
        user_name = get_slack_username(body['event']['user'])
        requestText = body['event']['text']
        eventType = body['event']['type'] + '.' + body['event']['channel_type']
    except:
        abort(500)

    thr = threading.Thread(target=send_response, args=(fromChannel, user_name, requestText, eventType), kwargs={})
    thr.start()
    return STATUS_200

def send_response( fromChannel, user_name, requestText, eventType ):
    is_direct = eventType == 'app_mention' or eventType == 'message.im'
    response_text, attachment = bot.get_response_and_attachments(user_name, requestText, direct_message=is_direct)

    payload = { 'channel': fromChannel, 'text': response_text, 'attachments': attachment }
    requests.post(settings.SLACK_URL+'/chat.postMessage', headers=headers, json=payload)

def get_slack_username(user_id):
    params = {'user': user_id}
    r = requests.get(settings.SLACK_URL + '/users.info', headers=headers, params=params)
    res = r.json()
    return res['user']['name']

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=settings.WEBSERVER_PORT, debug=True)
