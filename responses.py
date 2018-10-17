'''
This class contains all translatable strings.
'''

# This one is technically not a bot response, but rather the welcome message when 
API_WELCOME = "Welcome to the CalendarBot API. It seems that the server is running correctly. Use a POST to this URL in the slack or mattermost format to use."

# Some error texts
WRONG_SETUP = "The integration is not correctly set up. Could not fetch all necessary request parameters."
INVALID_TOKEN = "The integration is not correctly set up. Token not valid."
GENERIC_ERROR = "Oops, something went wrong."
GENERIC_PROBLEM = "There was a problem with Calendar Bot."
REASON = "Reason"

CALENDAR_API_ERROR = "I couldn't save that. " \
                     "I understood you wanted to create a new vacation, " \
                     "but something went wrong when posting the request." \
                     "\nResponse from the calendar webservice: \n\n{} - {} - {}"

WATSON_CONFUSED = "Watson is confused. Try asking it another way."

# Some (partial) responses
CALENDAR_UNCHANGED = "I didn't change the calendar."
USER_UNKNOWN = "Your user is not in the DB though. Please add it manually."
THIS_WEEKS_HOLIDAYS = "This weeks holiday schedule:"
NOBODY_OFF_THIS_WEEK = "Nobody is off this week, looks like it's going to be full house this week!"
NOBODY_OFF_TODAY = "Nobody is off today, perfect day for a team lunch?"
DID_NOT_UNDERSTAND = "I didn't get that. Please try rephrasing. Ask 'What can I ask you?' for help"
AVAILABILITY_ADDED = "I added your availability ({} {}). "
CHECK_WEBSITE = "Check it out on {}."
WHEN = "When"
FROM_UNTIL = "from {} until {}"
ON_DAY = "for {}"

PERSON_SINGULAR = "person is"
PERSON_PLURAL = "people are"
OFF_TODAY = "{0} {1} off today: "