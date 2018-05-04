from flask import Flask
from flask import jsonify
from flask import request
from flask import make_response
from slackclient import SlackClient
import json
from s3_uplod import download_and_upload

app = Flask(__name__)

SLACK_BOT_TOKEN = 'YOUR SLACKBOT TOKEN'
slack_client = SlackClient(SLACK_BOT_TOKEN)


@app.route('/slack', methods=['POST'])
def hello_world():
    '''
    Return: response 200 
    Usage: Getting the payload from the slack and extracting the
    title and link from that it download and upload the video in
    AWS s3 and return url for the link
    '''
    form_json = json.loads(request.form["payload"])
    with open("search_result.json",'w') as f:
        f.write(json.dumps(form_json,indent = 2))
    #print (form_json)
    print(request)
    #print(request.get_json())
    with open("search_result.json",'r') as file:
         file = json.loads(file.read())
    title = " ".join((file['actions'][0]['name']).split(" ")[0:-1])
    link = file['actions'][0]['name'].split(" ")[-1]
    # link = details[1]
    # title = details[0]
    print(link)
    print(title)    
    url = download_and_upload(link, title)
    print(url)
    postmessage(url)
    print("Message posted")
    return make_response("", 200)
def postmessage(link):

    slack_client.api_call(
        "chat.postMessage",
        channel = "YOUR CHANNEL NAME",
        text = link,
        #attachments = attachments_json
        )

if __name__ == "__main__":
    app.run()
