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
from json import load
from urllib.error import HTTPError
import urllib3.exceptions
import socket
import requests



#------------------------------ TABLE FUNCTION ----------------------------
def checkTableExists(tablename):
    sql = """SHOW TABLES LIKE '%s'""" % \
	(tablename)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False

#---------------------------------------------------------------------------
def checkEntryExists(tablename,key_name,value):
    try:
        value = int(value)
        sql = """SELECT * FROM %s WHERE %s = '%d' """ % \
        	       (tablename,key_name,value)
    except ValueError:
        pass
        sql = """SELECT * FROM %s WHERE %s = '%s' """ % \
	       (tablename,key_name,value)

    cursor.execute(sql)
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False

#------------------------------ ALIAS FUNCTION ----------------------------
def CreateTableAlias():
    if checkTableExists('alias'):
        return

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
        # print ("CreateTableAlias:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()
#--------------------------------------------------------------------------

def insertValueAlias(alias,twitter_id,fb_id):
    if checkEntryExists('alias','AID',alias):
        return

    sql = """INSERT INTO alias (AID,UID_TWITTER,UID_FB) \
	VALUES ('%s', '%d', '%d')""" % \
	(str(alias),int(twitter_id), int(fb_id))

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        print("Successfuly added alias: ",alias)
    except:
      print ("insertValueAlias:DB error!\n",sql,"\n")
      # Rollback in case there is any error
      db.rollback()

#------------------------------ FB FUNCTIONS ------------------------------


def CreateTableFBUsers():
    if checkTableExists('fb_users'):
        return

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
        # print ("CreateTableFBUsers:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

def CreateTableFBPosts():
    if checkTableExists('fb_posts'):
        return

    # Create table as per requirement
    sql = """CREATE TABLE fb_posts (
    PID BIGINT NOT NULL,
    UID_POST BIGINT NOT NULL,
    TITLE VARCHAR(1024),
    CREATED_AT DATETIME,
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
        # print ("CreateTableFBPosts:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

def insertValueFBUsers(user_id, fb_user):
    if checkEntryExists('fb_users','UID',user_id):
        return
    else:
        sql = """INSERT INTO fb_users (UID, NAME) \
            VALUES ('%d', '%s')""" % \
            (int(user_id), str(fb_user))
        try:
            # Execute the SQL commandv
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except:
            print ("insertValueFBUsers:DB error!\n",sql,"\n")
            # Rollback in case there is any error
            db.rollback()

#--------------------------------------------------------------------------

def insertValueFBPosts(post_id, user_id, title, time, likes, comments, shares):
    if((post_id == None) or (user_id == None)):
        return 0
    if checkEntryExists('fb_posts','PID',post_id):
        sql = """UPDATE fb_posts SET LIKES = '%d', COMMENTS = '%d', SHARES = '%d'
        WHERE PID = '%d'""" % \
      	(int(likes), int(comments), int(shares),int(post_id))
        try:
          # Execute the SQL command
          cursor.execute(sql)
          # Commit your changes in the database
          db.commit()
          return 1
        except:
          print ("updateValueFBPosts:DB error!\n",sql,"\n")
          # Rollback in case there is any error
          db.rollback()
          return 0
    else:
        if (time != None):
            try:
                time = time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time = ''
        sql = """INSERT INTO fb_posts (PID, UID_POST, TITLE, CREATED_AT, LIKES, COMMENTS, SHARES) \
	           VALUES ('%d', '%d', '%s', '%s' ,'%d', '%d', '%d')""" % \
                   (int(post_id),
                    int(user_id),
                    title.replace("'", " ").replace('"', ' '),
                    time,
                    int(likes),
                    int(comments),
                    int(shares))
        try:
          # Execute the SQL command
          cursor.execute(sql)
          # Commit your changes in the database
          db.commit()
          return 1
        except:
          print ("insertValueFBPosts:DB error!\n",sql,"\n")
          # Rollback in case there is any error
          db.rollback()
          return 0

#--------------------------------------------------------------------------

def RecordFBValuesToDB(fb_user, post_list):
    if post_list:
        user_id = post_list[0]['user_id']
        insertValueFBUsers(user_id, fb_user)
        # key from dictionaries
        count = 0
        for i in range (0, len(post_list)):
            post = post_list[i]
            count = count + insertValueFBPosts(post['post_id'],
            user_id,
            post['text'],
            post['time'],
            post['likes'],
            post['comments'],
            post['shares'])

        pritn('Stored successfully in DB '+str(count)+' posts')


#--------------------------------------------------------------------------

def fb_scraper(fb_user):
    try:
        get_p = facebook_scraper.get_posts(fb_user, pages=150)
    except (HTTPError, requests.exceptions.RequestException, ValueError,
            socket.timeout,ConnectionError,urllib3.exceptions ) as ex:
        print('Failed with exception [%s]' % ex)
        get_p = []

    post_list = []

    for post in get_p:
        post_list.append(post)

    return post_list


#------------------------------ TWITTER FUNCTIONS ----------------------------

def CreateTableTwitterUsers():
    if checkTableExists('twitter_users'):
        return

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
        # print ("CreateTableTwitterUsers:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

def CreateTableTwitterPosts():
    if checkTableExists('twitter_tweets'):
        return

    # Create table as per requirement
    sql = """CREATE TABLE twitter_tweets (
    TID BIGINT NOT NULL,
    UID_TWEET BIGINT NOT NULL,
    TITLE VARCHAR(1024),
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
        # print ("CreateTableTwitterPosts:DB connection error!\n")
        # Rollback in case there is any error
        db.rollback()

#--------------------------------------------------------------------------

def insertValueTwitterUsers(user_id, twitter_user, favourites_count, followers_count, friends_count, statuses_count):
    if checkEntryExists('twitter_users','UID',user_id):
        sql = """UPDATE twitter_users SET FAVORITES_COUNT = '%d', FOLLOWERS_COUNT = '%d'
            WHERE UID = '%d'""" % \
            (favourites_count, followers_count,int(user_id))
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
            return 1
        except:
            print ("updateValueTwitterPosts:DB error!\n",sql,"\n")
            # Rollback in case there is any error
            db.rollback()
            return 0
    else:
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
            return 1
        except:
            print ("insertValueTwitterUsers:DB error!\n",sql,"\n")
            # Rollback in case there is any error
            db.rollback()
            return 0

#--------------------------------------------------------------------------
def insertValueTwitterPosts(tweet_id, user_id, title, retweet_count, favorite_count, created_at, lang, source_url, hashtags):
    if checkEntryExists('twitter_tweets','TID',tweet_id):
        sql = """UPDATE twitter_tweets SET RETWEET_COUNT = '%d', FAVORITE_COUNT = '%d'
        WHERE TID = '%d'""" % \
        (retweet_count, favorite_count,int(tweet_id))
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
            return 1
        except:
            print ("upadteValueTwitterPosts:DB connection error!\n",sql,"\n")
            # Rollback in case there is any error
            db.rollback()
            return 0
    else:
        sql = """INSERT INTO twitter_tweets (TID, UID_TWEET, TITLE, RETWEET_COUNT, FAVORITE_COUNT, CREATED_AT, LANGUAGE, SOURCE, HASHTAGS) \
        VALUES ('%d', '%d', '%s', '%d', '%d', '%s', '%s', '%s', '%s')""" % \
        (int(tweet_id), int(user_id), title, retweet_count, favorite_count, created_at, lang, source_url, hashtags)
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
            return 1
        except:
            print ("insertValueTwitterPosts:DB error!\n",sql,"\n")
            # Rollback in case there is any error
            db.rollback()
            return 0

#--------------------------------------------------------------------------

def RecordTwitterValuesToDB(tweets_list):
    tweet_usr = tweets_list[0].user
    insertValueTwitterUsers(tweet_usr.id,
    tweet_usr.name.replace("'", " ").replace('"', ' '),
    tweet_usr.favourites_count,
    tweet_usr.followers_count,
    tweet_usr.friends_count,
    tweet_usr.statuses_count)
    count=0

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

        count = count + insertValueTwitterPosts(tweet.id,
        tweet.user.id,
        tweet.full_text.replace("'", " ").replace('"', ' '),
        tweet.retweet_count,
        tweet.favorite_count,
        tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        tweet.lang,
        source_url,
        str(hashtags))

    print('Stored successfully in DB '+str(count)+' tweets')

#--------------------------------------------------------------------------

def twitter_api():
    # Load credentials from json file
    with open("twitter_credentials.json", "r") as file:
        creds = load(file)
    auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    return tweepy.API(auth)

#--------------------------------------------------------------------------

def twitter_scrapper(twitter_user):

    api = twitter_api()

    # fetching the user
    try:
        tweets_list = []
        for status in tweepy.Cursor(api.user_timeline, id = twitter_user, tweet_mode="extended").items(600):
            tweets_list.append(status)
    except:
        tweets_list=[]

    return tweets_list

#-------------------------------CONTAINER FUNCTIONS--------------------------
def collectTwitter(twitter_user):
    print("Start twitter crawl "+ datetime.now().strftime("%H:%M:%S"))
    tweets_list = twitter_scrapper(twitter_user)
    print("Crawled "+str(len(tweets_list))+" tweets")

    # Save tweets to DB

    try:
        user_id=tweets_list[0].user.id
        print("Start Store tweets to DB "+datetime.now().strftime("%H:%M:%S"))
        RecordTwitterValuesToDB(tweets_list)
    except:
        user_id = 0
    return user_id

#-----------------------------------------------------------------------------
def collectFacebook(fb_user):
    # Retrieve FB posts
    msg = "Start FB crawl "+datetime.now().strftime("%H:%M:%S")
    print(msg)
    post_list = fb_scraper(fb_user)
    print("Crawled "+str(len(post_list))+" posts")


    # Save FB posts to DB

    try:
        fb_id=int(post_list[0]['user_id'])
        print("Start Store Posts to DB "+datetime.now().strftime("%H:%M:%S"))
        RecordFBValuesToDB(fb_user, post_list)
    except:
        fb_id=0
    return fb_id


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

# Read list of usernames from csv
try:
    df = read_csv("usernames.csv",encoding = "ISO-8859-7",delimiter=";")
except:
    print ("Usernames file error!\n")
    df=[]

# Retrieve tweets
for i in range (0, len(df)):
    twitter_user=df["Twitter"][i]
    user_id = collectTwitter(twitter_user)

    fb_user=df["Facebook"][i]
    fb_id = collectFacebook(fb_user)
# Save relation between FB and twitter users

    if (user_id & fb_id):
        alias=twitter_user+" - "+fb_user
        print("Start Aliases ",datetime.now().strftime("%H:%M:%S"))
        insertValueAlias(alias,user_id, fb_id)

 # disconnect from server
db.close()


#------------------------------ END MAIN PROGRAMM ------------------------------
