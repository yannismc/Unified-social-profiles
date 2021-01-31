# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 00:09:30 2020


"""

import MySQLdb
#import mysql.connector as MySQLdb
import facebook_scraper
import tweepy
import csv
from pandas import read_csv
import datetime
#------------------------------ FB FUNCTIONS ------------------------------


def CreateTableFBUsers():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS fb_users")

    # Create table as per requirement
    sql = """CREATE TABLE fb_users (
    UID BIGINT NOT NULL,
    NAME VARCHAR(255) NOT NULL,
    PRIMARY KEY (UID))"""

    cursor.execute(sql)

def CreateTableFBPosts():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS fb_posts")

    # Create table as per requirement
    sql = """CREATE TABLE fb_posts (
    PID BIGINT NOT NULL,
    UID_POST BIGINT NOT NULL,
    TITLE VARCHAR(1024),
    LIKES INT,
    COMMENTS INT,
    SHARES INT,
    TIME DATETIME,
PRIMARY KEY (PID),
FOREIGN KEY (UID_POST)
 REFERENCES fb_users(UID))"""

    cursor.execute(sql)


def insertValueFBUsers(user_id, fb_user):
  sql = """INSERT INTO fb_users (UID, NAME) \
	VALUES ('%d', '%s')""" % \
	(int(user_id), str(fb_user))

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
    # Rollback in case there is any error
    db.rollback()


def insertValueFBPosts(post_id, user_id, title, likes, comments, shares, time):
  if((post_id == 'None') or (user_id == 'None')):
      return
  sql = """INSERT INTO fb_posts (PID, UID_POST, TITLE, LIKES, COMMENTS, SHARES, ΤΙΜΕ) \
	VALUES ('%d', '%d', '%s', '%d', '%d', '%d', '%m-%d-%y')""" % \
	(int(post_id), int(user_id), title, likes, comments, shares, time)
    
  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
    # Rollback in case there is any error
    db.rollback()


def RecordFBValuesToDB(fb_user, post_list):
    user_id = post_list[0]['user_id']
    insertValueFBUsers(user_id, fb_user)

# key from dictionaries
    for i in range (0, len(post_list)):
        post = post_list[i]
        insertValueFBPosts(str(post['post_id']), user_id, str(post['text']), int(post['likes']), int(post['comments']), int(post['shares']), str(post['time']))


def fb_scraper(fb_user):
    get_p = facebook_scraper.get_posts(fb_user, pages=2)
    post_list = []

    for post in get_p:
        post_list.append(post)

    return post_list


#------------------------------ TWITTER FUNCTIONS ------------------------------

def CreateTableTwitterUsers():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS twitter_users")

    # Create table as per requirement
    sql = """CREATE TABLE twitter_users (
    UID BIGINT NOT NULL,
    NAME VARCHAR(255) NOT NULL,
    FAVORITES_COUNT BIGINT NOT NULL,
    FOLLOWERS_COUNT BIGINT NOT NULL,
    FRIENDS_COUNT BIGINT NOT NULL,
    TWEETS_COUNT BIGINT NOT NULL,
    PRIMARY KEY (UID))"""

    cursor.execute(sql)


def CreateTableTwitterPosts():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS twitter_tweets")

    # Create table as per requirement
    sql = """CREATE TABLE twitter_tweets (
    TID BIGINT NOT NULL,
    UID_TWEET BIGINT NOT NULL,
    TITLE VARCHAR(1024),
    RETWEET_COUNT INT,
    FAVORITE_COUNT INT,
    CREATED_AT VARCHAR(1024),
    LANGUAGE VARCHAR(1024),
    SOURCE VARCHAR(1024),
    HASHTAGS VARCHAR(1024),
    PRIMARY KEY (TID),
    FOREIGN KEY (UID_TWEET)
    REFERENCES twitter_users(UID))"""

    cursor.execute(sql)

def insertValueTwitterUsers(user_id, twitter_user, favourites_count, followers_count, friends_count, statuses_count):
  sql = """INSERT INTO twitter_users (UID, NAME, FAVORITES_COUNT, FOLLOWERS_COUNT, FRIENDS_COUNT, TWEETS_COUNT) \
	VALUES ('%d', '%s', '%d', '%d', '%d', '%d')""" % \
	(int(user_id), str(twitter_user), int(favourites_count), int(followers_count), int(friends_count), int(statuses_count))

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
    # Rollback in case there is any error
    db.rollback()

def insertValueTwitterPosts(tweet_id, user_id, title, retweet_count, favorite_count, created_at, lang, source_url, hashtags):
  sql = """INSERT INTO twitter_tweets (TID, UID_TWEET, TITLE, RETWEET_COUNT, FAVORITE_COUNT, CREATED_AT, LANGUAGE, SOURCE, HASHTAGS) \
	VALUES ('%d', '%d', '%s', '%d', '%d', '%s', '%s', '%s', '%s')""" % \
	(int(tweet_id), int(user_id), title, retweet_count, favorite_count, created_at, lang, source_url, hashtags)
    
  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
    # Rollback in case there is any error
    db.rollback()



def RecordTwitterValuesToDB(twitter_user, user_id, tweets_list):
    tweet_model = tweets_list[0]
    tweet = tweet_model._json
    tweet_usr = tweet['user']
    
    insertValueTwitterUsers(user_id, twitter_user, tweet_usr['favourites_count'], tweet_usr['followers_count'], tweet_usr['friends_count'], tweet_usr['statuses_count'])
    
    
    for i in range (0, len(tweets_list)):
        tweet_model = tweets_list[i]
        tweet = tweet_model._json
        #Get the source url
        source_url = 'https://twitter.com/' + str(twitter_user) + '/status/' + str(tweet['id'])
        
        #Get the hashtags
        hashtags = ''
        for j in range (0, len(tweet['entities']['hashtags'])):
            if(j == len(tweet['entities']['hashtags'])-1):
                hashtags += tweet['entities']['hashtags'][j]['text']
            else:
                hashtags += tweet['entities']['hashtags'][j]['text'] + ', '
        
        insertValueTwitterPosts(str(tweet['id']), user_id, str(tweet['full_text']), int(tweet['retweet_count']), int(tweet['favorite_count']), str(tweet['created_at']), str(tweet['lang']), str(source_url), str(hashtags))


def twitter_api(twitter_user):
    auth = tweepy.OAuthHandler("ftQlu6bo1bNANdyldduBhzVaH", "aU9St3CFR2m6IlSLKEcSzdOghojQCV7K2HOniLG8BjA05EjHds")
    auth.set_access_token("606314285-0aWgonCbBFS10Bv0BEMSi94gY14tjNxB6Rrb21jc", "l6GTdpPfe5LooPgdzluDwSHbnEyJRf4EzilTpMSxXI51y")

    api = tweepy.API(auth)

    # fetching the user
    user = api.get_user(twitter_user)

    # fetching the ID
    user_id = user.id_str

    tweets_list = []

    for status in tweepy.Cursor(api.user_timeline, twitter_user, tweet_mode="extended").items(5):
        tweets_list.append(status)

    return user_id, tweets_list



#------------------------------ MAIN PROGRAMM ------------------------------
db = 0
# Open database connection
try:
    db = MySQLdb.connect(host="localhost", use_unicode = True, charset = "utf8", user="root", passwd="", db="socialmedia_db")
except Exception as e:
    print ("DB connection error!\n")
# prepare a cursor object using cursor() method
cursor = db.cursor()

CreateTableFBUsers()
CreateTableFBPosts()
CreateTableTwitterUsers()
CreateTableTwitterPosts()


try:
    df = read_csv("usernames_.csv",encoding = "ISO-8859-7",delimiter=";")
except:
    print ("Usernames file error!\n")
    df=[]

for fb_user in df["Facebook"]:
    post_list = fb_scraper(fb_user)
    RecordFBValuesToDB(fb_user, post_list)


#for twitter_user in df["Twitter"]:
   # user_id, tweets_list = twitter_api(twitter_user)
   # RecordTwitterValuesToDB(twitter_user, user_id, tweets_list)







 # disconnect from server
db.close()


#------------------------------ END MAIN PROGRAMM ------------------------------
