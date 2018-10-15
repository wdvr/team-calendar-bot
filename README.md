# team-calendar-bot

Chatbot to interact with [team calendar](https://github.com/wdvr/team-calendar). You can add new vacation days via the bot, or ask who's off today or this week.

Works with Mattermost and Slack (soon). Uses IBM Watson for Text-to-Intent.

## Sample utterances
You can add availabilities:
> @calendarbot, I will be off tomorrow.

> @calendarbot, I am in holiday from next Tuesday till Friday.

> @calendarbot, I am sick today.

Then to fetch availabilities:
> calendarbot, who's in today?

> calendarbot, who is in the office this week?


## Requirements

### Python
You will need Python 3 with pip, or use docker (see below).

run `pip install -r requirements.txt` to install all python dependencies

### Settings

Adapt the first section settings.py to your needs. Make sure the calendar URL is updated, as well as your timezone.

### IBM Watson
Create an IBM Watson project (see [here](https://www.ibm.com/watson/how-to-build-a-chatbot/)), and import watson-workspace.json
Copy the workspace ID and api-key to settings.py. Your URL will probably be the default one.

### Slack / Mattermost

#### Mattermost
If using Mattermost, create an outgoing hook, without triggerword. The triggerword is parsed in the Python code, this allows for interactive conversations, without having to repeat the triggerword.

Content Type should be JSON, Callback URL should be wherever this python app is running.

#### Slack
Start `python slack.py`
Create a Slack app (follow steps (here)[https://api.slack.com/bot-users]). Copy the OAuth token to settings.py.

## Run
For testing, simply run `python slack.py` (for the slack integration) or `python bot.py` (for the mattermost integration).
To put in production, use any way of deploying Flask applications (Heroku, pythonanywhere, ...)

## Docker
Instead of using a local installation of python and dependencies, use the included Dockerfile. You still need to adapt the settings.

```
docker build --tag team-calendar-bot:latest .
docker run --rm -p 5000:5000 team-calendar-bot:latest
```
