from watson_developer_cloud import AssistantV1
import settings
import re

assistant = AssistantV1(
    iam_apikey=settings.WATSON_API_KEY,
    url=settings.WATSON_URL,
    version='2018-07-10')

workspace_id = settings.WATSON_WORKSPACE_ID # replace with workspace ID


def ask_watson(query, context=None, debug=False):
    """
    Connect to the Watson service, and process the input. 
    Returns the result, containing the intent, resposne message and context.

    :param query: query string. What you ask Watson.
    :param context=None: Optional context from previous requests. Use to pass previous state.
    :param debug=False: Print the detecten intent and result to stdout 
    """

    # Watson cannot handle new lines or tabs
    query = re.sub(r'[\t\n]', '', query)

    response = assistant.message( workspace_id = workspace_id, input = { 'text': query }, context=context )
    result = response.result

    if debug:
        if result['intents']:
            print('detected intent: #' + result['intents'][0]['intent'])
        print(result)

    return result

if __name__ == '__main__':
    # Test connection
    result = ask_watson('What can you do?')

    if result['output']['text']:
        print(result['output']['text'][0])
    else:
        print('no response')
