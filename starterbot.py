import os
import time
import re
from slackclient import SlackClient
import google.oauth2.credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def result_list(key_word):
  # The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
  # the OAuth 2.0 information for this application, including its client_id and
  # client_secret.
  service_account_file = "client_secret.json"

  # This OAuth 2.0 access scope allows for full read/write access to the
  # authenticated user's account and requires requests to use an SSL connection.
  SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
  API_SERVICE_NAME = 'youtube'
  API_VERSION = 'v3'

  def get_authenticated_service():
      credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
      #flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
      #credentials = flow.run_console()
      return build(API_SERVICE_NAME, API_VERSION, credentials = credentials, cache_discovery=False)

  def remove_empty_kwargs(**kwargs):
      good_kwargs = {}
      if kwargs is not None:
        for key, value in kwargs.items():
          if value:
            good_kwargs[key] = value
      return good_kwargs

  def search_list_by_keyword(client, **kwargs):
      # See full sample for function
      kwargs = remove_empty_kwargs(**kwargs)
      response = client.search().list(**kwargs).execute()
      details = {}
      for items in response['items']:
            details[items['snippet']['title']] = items['id']['videoId']
      return details

  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()

  title = search_list_by_keyword(client,part='snippet',maxResults=5,q=key_word,type='video')
  return title

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """

    # Sends the response back to the channel
    response = result_list(command)
    #attachments = [{"title": "python",
    #                         "image_url": image_url}]
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        attachments=[
        {
            "color": "033E96",
            "author_name": "Search result for " + command,
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "fields": [
                {
                    "value": r'<https://www.youtube.com/watch?v='+video_id+'|'+title+'>',
                    "short": 'true'
                }
            ],
            "actions": [
                {
                    "name": title +' '+'https://www.youtube.com/watch?v='+video_id,
                    "text": "Download",
                    "type": "button",
                    "value": "recommend"
                }
            ]       
        }for title,video_id in response.items()
    ]
    )

# instantiate Slack client
SLACK_BOT_TOKEN = 'Slack_secret_token'
slack_client = SlackClient(SLACK_BOT_TOKEN)
print (SLACK_BOT_TOKEN)
print (slack_client)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

if __name__ == "__main__":
    print (slack_client)
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
