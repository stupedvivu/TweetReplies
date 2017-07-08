#########################################################################################################################################
  ##                          PROGRAME TO GET THE REPLIES CONVERSATION OF A TWEET ID                                                 ##
  ##                          CODE IS WRITTEN IN PYTHON 3.X..                                                                        ##
  ##                          USES TWEEPY LIBRARY TO USE TWITTER API...                                                              ## 
  ##                          WRITTEN BY VIVEK SHARMA...                                                                             ##
#########################################################################################################################################

import tweepy
import json
import os
import sys
from bs4 import BeautifulSoup
import requests



##variables...
key_count = 0
reply_count = 0
request_count = 0
keys = []
id_list = []
id_name_list = []

##path variables...
##save your access token credentials in a dictionary format as a json file...

access_token_path = "E:\\projects\\internship\\modelling\\key.json" ##add your path for your access token...
reply_database_path = "E:\\projects\\internship\\modelling\\database\\tweet" ##add your path where you want to save your replies and tweets....



##function to get the access tokens...
def GetKeys():
    global keys
    f = open(access_token_path, "r")
    data = json.load(f)
    f.close()
    for k in data:
        keys.append(k)



##function to create a request...
def CreateRequest():
    global key_count
    global keys

    ##set the access tokens..
    auth = tweepy.OAuthHandler(keys[key_count]['consumer_key'], keys[key_count]['consumer_secret'])
    auth.set_access_token(keys[key_count]['access_token'], keys[key_count]['access_secret'])
    key_count += 1

    return tweepy.API(auth)



##function to check rate limit error...
def IsRateLimit():
    try:
        return False
    except tweepy.TweepError:
        return True



##get replies...
def SaveReplies(tweet_id, screen_name, api, tweet_count):
    
    global reply_count
    global request_count
    global id_name_list
    global id_list
    os.makedirs(reply_database_path + str(tweet_count) + "\\replies")

    ##iterate through all the cursored response..
    for item in tweepy.Cursor(api.search, q = screen_name, since_id = tweet_id).items():
        request_count += 1

        try:
            ##if the current tweet is a reply of the given tweet_id...
            if( item.in_reply_to_status_id == tweet_id ):
                reply_count += 1
                d = {}
                f = open(reply_database_path + str(tweet_count) + "\\replies\\reply" + str(reply_count) + ".json", "w")
                obj = json.dumps(item._json)
                data = json.loads(obj)
                json.dump(data, f, indent = 2)
                f.close()
                print("got reply!")
                
                d['id'] = data['id']
                d['name'] = data['user']['screen_name']
                id_name_list.append(d)
                id_list.append(d['id'])
                

        except tweepy.TweepError:
            api = CreateRequest()



##function to find the threaded conversation id against a tweet id...
##USES WEB SCROLLING TO FIND THE ID..
def findThread(screen_name, id, previous_id):
    
    html = requests.get("https://twitter.com/" + screen_name + "/status/" + str(id) )
    html_data = html.text
    soup = BeautifulSoup(html_data, "html5lib")
    
    lists = []
    for item in soup.find_all(attrs = {"data-tweet-id" : True }): ##search for the data 'data-tweet-id'.. 
        tweet_id = item['data-tweet-id']
        if tweet_id not in previous_id:
            lists.append(tweet_id)

    return lists




GetKeys()
api = CreateRequest()

tweet_id = int(input("Enter the id of the tweet: "))
tweet_count = int(input("Enter the tweet count: "))

##save the original tweet...
id_list.append(tweet_id)
request_count += 1
response = api.get_status(tweet_id)
obj = json.dumps(response._json)
data = json.loads(obj)
author = data["user"]["screen_name"]
d = {}
d['id'] = tweet_id
d['name'] = author
id_name_list.append(d)
os.makedirs(reply_database_path + str(tweet_count))
f = open(reply_database_path + str(tweet_count) + "\\tweet.json", "w")
json.dump(data, f, indent = 2)
f.close()
print("got the tweet!")


##saving replies..
print("saving replies...")
search_name = "to:@" + author
SaveReplies(tweet_id, search_name, api, tweet_count)

##finding threaded conversation...
print("finding threaded conversation...")

for i in id_name_list:
    t = findThread(i['name'], i['id'], id_list)
    print("got thread!")
    
    for u in t:
        if( IsRateLimit() ):
            api = CreateRequest()
            
        ##save the id....    
        request_count += 1
        response = api.get_status(u)
        obj = json.dumps(response._json)
        data = json.loads(obj)
        reply_count += 1
        
        f = open(reply_database_path + str(tweet_count) + "\\replies\\reply" + str(reply_count) + ".json", "w")
        json.dump(data, f, indent = 2)
        f.close()
        print("got the tweet!")
        
        id_list.append(u)  
    
