import os
import json
import urllib
from selenium import webdriver
from datetime import date
from datetime import datetime

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

today = date.today()

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

base_video_url = "https://www.youtube.com/watch?v="

channelsJson = ""
videoTitles = []
videoIDs = []

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "YOUR_CLIENT_SECRETS_FILE.json"

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

def getChannels():
    request = youtube.subscriptions().list(
        part="snippet",
        mine=True,
        maxResults=500
    )
    response = request.execute()

    #print(response)

    return response

def get_video_info(video_id):
    request = youtube.videos().list(
        part="snippet",
        id = video_id
    )

    request = request.execute()
    title = request["items"][0]["snippet"]["title"]
    date = request["items"][0]["snippet"]["publishedAt"]
    date = date[0:10]
    return [title, date]
    

def look_for_new_videos(channel_id):
    api_key = "YOUR_API_KEY"

    base_search_url = "https://www.googleapis.com/youtube/v3/search?"

    url = base_search_url + ('key={}&channelId={}&part=snippet,id&order=date&maxResults=1'.format(api_key, channel_id))
    inp = urllib.request.urlopen(url)
    resp = json.load(inp)

    vidID = resp['items'][0]['id']['videoId']

    video_exists = True

    with open('videoid.json', 'r') as json_file:
        data = json.load(json_file)
        if data['videoId'] != vidID:
            videoInfo = get_video_info(vidID)
            if videoInfo[1] == today.strftime('%Y-%m-%d'):
                videoTitles.append(videoInfo[1])
                videoIDs.append(vidID)
                video_exists = True
    if video_exists:
        with open('videoid.json', 'w') as json_file:
            data = {'videoId': vidID}
            json.dump(data, json_file)

channels = getChannels()
channelIDs = []
channelTitles = []

#print(channelsJson)

if datetime.now().hour >= 6 and datetime.now().hour <= 21:
    if datetime.now().minute == 0 or datetime.now().minute == 30:
        for channel in channels["items"]:
            channelIDs.append(channel['snippet']['resourceId']['channelId'])
            channelTitles.append(channel['snippet']['title'])
        for channel in channelIDs:
            look_for_new_videos(channel)
        print(videoTitles)
        print(videoIDs)
