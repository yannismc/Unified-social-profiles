# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 00:09:30 2020


"""

#import MySQLdb
import mysql.connector as MySQLdb
import facebook_scraper
import tweepy
from pandas import read_csv
from datetime import datetime
from urllib.error import HTTPError


#------------------------------ ALIAS FUNCTION ----------------------------
def CreateTableAlias():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS alias")

    # Create table as per requirement
    sql = """CREATE TABLE alias (
    AID VARCHAR(68) NOT NULL,
    UID_TWITTER BIGINT NOT NULL,
    UID_FB BIGINT NOT NULL,
    FOREIGN KEY (UID_FB)
     REFERENCES fb_users(UID),
    FOREIGN KEY (UID_TWITTER)
 REFERENCES twitter_users(UID),
  PRIMARY KEY (AID))"""

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        print ("CreateTableAlias:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()
#--------------------------------------------------------------------------

def insertValueAlias(alias,twitter_id,fb_id):
  sql = """INSERT INTO alias (AID,UID_TWITTER,UID_FB) \
	VALUES ('%s', '%d', '%d')""" % \
	(str(alias),int(twitter_id), int(fb_id))

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
      print ("insertValueAlias:DB connection error!\n")
    # Rollback in case there is any error
      db.rollback()

#------------------------------ FB FUNCTIONS ------------------------------


def CreateTableFBUsers():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS fb_users")

    # Create table as per requirement
    sql = """CREATE TABLE fb_users (
    UID BIGINT NOT NULL,
    NAME VARCHAR(50) NOT NULL,
    PRIMARY KEY (UID))"""

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        print ("CreateTableFBUsers:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

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
PRIMARY KEY (PID),
FOREIGN KEY (UID_POST)
 REFERENCES fb_users(UID))"""

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        print ("CreateTableFBPosts:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

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
      print ("insertValueFBUsers:DB connection error!\n")
    # Rollback in case there is any error
      db.rollback()

#--------------------------------------------------------------------------

def insertValueFBPosts(post_id, user_id, title, likes, comments, shares):
  if((post_id == 'None') or (user_id == 'None')):
      return
  sql = """INSERT INTO fb_posts (PID, UID_POST, TITLE, LIKES, COMMENTS, SHARES) \
	VALUES ('%d', '%d', '%s', '%d', '%d', '%d')""" % \
	(int(post_id), int(user_id), title, likes, comments, shares)

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
      print ("insertValueFBPosts:DB connection error!\n")
    # Rollback in case there is any error
      db.rollback()

#--------------------------------------------------------------------------

def RecordFBValuesToDB(fb_user, post_list):
    if post_list:
        user_id = post_list[0]['user_id']
        insertValueFBUsers(user_id, fb_user)
        # key from dictionaries
        for i in range (0, len(post_list)):
            post = post_list[i]
            insertValueFBPosts(str(post['post_id']),
            user_id,
            str(post['text']),
            int(post['likes']),
            int(post['comments']),
            int(post['shares']))

#--------------------------------------------------------------------------

def fb_scraper(fb_user):
    try:
        get_p = facebook_scraper.get_posts(fb_user, pages=15)
    except convertapi.exceptions.ApiError as ex:
        logger.error('Failed with exception [%s]' % ex)
        get_p = []

    post_list = []

    for post in get_p:
        post_list.append(post)

    return post_list


#------------------------------ TWITTER FUNCTIONS ----------------------------

def CreateTableTwitterUsers():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS twitter_users")

    # Create table as per requirement
    sql = """CREATE TABLE twitter_users (
    UID BIGINT NOT NULL,
    NAME VARCHAR(15) NOT NULL,
    FAVORITES_COUNT BIGINT NOT NULL,
    FOLLOWERS_COUNT BIGINT NOT NULL,
    FRIENDS_COUNT BIGINT NOT NULL,
    TWEETS_COUNT BIGINT NOT NULL,
    PRIMARY KEY (UID))"""

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        print ("CreateTableTwitterUsers:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

def CreateTableTwitterPosts():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS twitter_tweets")

    # Create table as per requirement
    sql = """CREATE TABLE twitter_tweets (
    TID BIGINT NOT NULL,
    UID_TWEET BIGINT NOT NULL,
    TITLE VARCHAR(320),
    RETWEET_COUNT INT,
    FAVORITE_COUNT INT,
    CREATED_AT DATETIME,
    LANGUAGE VARCHAR(36),
    SOURCE VARCHAR(1024),
    HASHTAGS VARCHAR(1024),
    PRIMARY KEY (TID),
    FOREIGN KEY (UID_TWEET)
    REFERENCES twitter_users(UID))"""

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        print ("CreateTableTwitterPosts:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

def insertValueTwitterUsers(user_id, twitter_user, favourites_count, followers_count, friends_count, statuses_count):
  sql = """INSERT INTO twitter_users (UID, NAME, FAVORITES_COUNT, FOLLOWERS_COUNT, FRIENDS_COUNT, TWEETS_COUNT) \
	VALUES ('%d', '%s', '%d', '%d', '%d', '%d')""" % \
	(int(user_id),
    str(twitter_user),
    int(favourites_count),
    int(followers_count),
    int(friends_count),
    int(statuses_count))

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
      print ("insertValueTwitterUsers:DB connection error!\n")
    # Rollback in case there is any error
      db.rollback()

#--------------------------------------------------------------------------
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
    print ("insertValueTwitterPosts:DB connection error!\n")
    # Rollback in case there is any error
    db.rollback()

#--------------------------------------------------------------------------

def RecordTwitterValuesToDB(tweets_list):
    tweet_usr = tweets_list[0].user
    print("Start insertValueTwitterUsers ",datetime.now().strftime("%H:%M:%S"))
    insertValueTwitterUsers(tweet_usr.id,
    tweet_usr.name,
    tweet_usr.favourites_count,
    tweet_usr.followers_count,
    tweet_usr.friends_count,
    tweet_usr.statuses_count)


    for i in range (0, len(tweets_list)):
        tweet = tweets_list[i]
        #Get the source url
        source_url = 'https://twitter.com/' + tweet.user.id_str + '/status/' + tweet.id_str

        #Get the hashtags
        hashtags = ''
        for j in range (0, len(tweet.entities['hashtags'])):
            if(j == len(tweet.entities['hashtags'])-1):
                hashtags += tweet.entities['hashtags'][j]['text']
            else:
                hashtags += tweet.entities['hashtags'][j]['text'] + ', '
            print("Start insertValueTwitterPosts ",datetime.now().strftime("%H:%M:%S"))
            insertValueTwitterPosts(tweet.id,
        tweet.user.id,
        tweet.full_text,
        tweet.retweet_count,
        tweet.favorite_count,
        tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        tweet.lang,
        source_url,
        str(hashtags))

#--------------------------------------------------------------------------

def twitter_api():
    # Load credentials from json file
    with open("twitter_credentials.json", "r") as file:
        creds = load(file)
    auth = OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    return API(auth)

#--------------------------------------------------------------------------

def twitter_scrapper(twitter_user):

    api = twitter_api()

    # fetching the user
    try:
        tweets_list = []
        for status in tweepy.Cursor(api.user_timeline, id = twitter_user, tweet_mode="extended").items(200):
            tweets_list.append(status)
        user_id=tweets_list[0].user.id
    except:
        user_id=[]
        tweets_list=[]

    return tweets_list

#------------------------------ MAIN PROGRAMM ------------------------------
db = 0
# Open database connection
try:
    db = MySQLdb.connect(host="localhost", use_unicode = True, charset = "utf8", user="root", passwd="", db="socialmedia_db")
except:
    print ("DB connection error!\n")
# prepare a cursor object using cursor() method
cursor = db.cursor()

CreateTableFBUsers()
CreateTableFBPosts()
CreateTableTwitterUsers()
CreateTableTwitterPosts()
CreateTableAlias()

try:
    df = read_csv("usernames_.csv",encoding = "ISO-8859-7",delimiter=";")
except:
    print ("Usernames file error!\n")
    df=[]

for i in range (40, len(df)):
    twitter_user=df["Twitter"][i]
    print("Start twitter crawl ",datetime.now().strftime("%H:%M:%S"))
    tweets_list = twitter_scrapper(twitter_user)

    try:
        user_id=tweets_list[0].user.id
        print("Start Store tweets to DB ",datetime.now().strftime("%H:%M:%S"))
        RecordTwitterValuesToDB(tweets_list)
    except:
        user_id = 0

    fb_user=df["Facebook"][i]
    print("Start FB crawl ",datetime.now().strftime("%H:%M:%S"))
    post_list = fb_scraper(fb_user)

    try:
        fb_id=int(post_list[0]['user_id'])
        print("Start Store Posts to DB ",datetime.now().strftime("%H:%M:%S"))
        RecordFBValuesToDB(fb_user, post_list)
    except:
        fb_id=0

    if (user_id & fb_id):
        alias=twitter_user+" - "+fb_user
        print("Start Aliases ",datetime.now().strftime("%H:%M:%S"))
        insertValueAlias(alias,user_id, fb_id)

 # disconnect from server
db.close()


#------------------------------ END MAIN PROGRAMM ------------------------------
