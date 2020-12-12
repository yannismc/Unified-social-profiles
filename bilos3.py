# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 00:09:30 2020

@author: tampn
"""


import MySQLdb
import facebook_scraper
import tweepy

#------------------------------ FB FUNCTIONS ------------------------------


def CreateTableFBUsers():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS fb_users")
      
    # Create table as per requirement
    sql = """CREATE TABLE fb_users (UID BIGINT PRIMARY KEY NOT NULL, NAME VARCHAR(255) NOT NULL)"""
    	    
    cursor.execute(sql)
    
def CreateTableFBPosts():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS fb_posts")
      
    # Create table as per requirement
    sql = """CREATE TABLE fb_posts (PID BIGINT PRIMARY KEY NOT NULL, UID BIGINT NOT NULL, TITLE VARCHAR(1024), LIKES INT, COMMENTS INT, FOREIGN KEY (UID) REFERENCES fb_users)"""
    	    
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
    

def insertValueFBPosts(post_id, user_id, title, likes, comments):
  sql = """INSERT INTO fb_posts (PID, UID, TITLE, LIKES, COMMENTS) \
	VALUES ('%d', '%d', '%s', '%d', '%d')""" % \
	(int(post_id), int(user_id), title, likes, comments)

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


    for i in range (0, len(post_list)):
        post = post_list[i]
        insertValueFBPosts(str(post['post_id']), user_id, str(post['text']), int(post['likes']), int(post['comments']))
        
        
def fb_scraper(fb_user):
    get_p = facebook_scraper.get_posts(fb_user, pages=2, credentials=('bilospap.2020@gmail.com', 'bil.1994!!$$'))
    post_list = []

    for post in get_p:
        post_list.append(post)
    
    return post_list


#------------------------------ TWITTER FUNCTIONS ------------------------------

def CreateTableTwitterUsers():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS twitter_users")
      
    # Create table as per requirement
    sql = """CREATE TABLE twitter_users (UID BIGINT PRIMARY KEY NOT NULL, NAME VARCHAR(255) NOT NULL)"""
    	    
    cursor.execute(sql)    
    
    
def CreateTableTwitterPosts():
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS twitter_tweets")
      
    # Create table as per requirement
    sql = """CREATE TABLE twitter_tweets (TID BIGINT PRIMARY KEY NOT NULL, UID BIGINT NOT NULL, TITLE VARCHAR(1024), RETWEET_COUNT INT, FAVORITE_COUNT INT, FOREIGN KEY (UID) REFERENCES twitter_users)"""
    	    
    cursor.execute(sql)  

def insertValueTwitterUsers(user_id, twitter_user):
  sql = """INSERT INTO twitter_users (UID, NAME) \
	VALUES ('%d', '%s')""" % \
	(int(user_id), str(twitter_user))

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
    # Rollback in case there is any error
    db.rollback()   

def insertValueTwitterPosts(tweet_id, user_id, title, retweet_count, favorite_count):
  sql = """INSERT INTO twitter_tweets (TID, UID, TITLE, RETWEET_COUNT, FAVORITE_COUNT) \
	VALUES ('%d', '%d', '%s', '%d', '%d')""" % \
	(int(tweet_id), int(user_id), title, retweet_count, favorite_count)

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
    # Rollback in case there is any error
    db.rollback()    



def RecordTwitterValuesToDB(twitter_user, user_id, tweets_list):
    insertValueTwitterUsers(user_id, twitter_user)

    for i in range (0, len(tweets_list)):
        tweet_model = tweets_list[i]
        tweet = tweet_model._json
        insertValueTwitterPosts(str(tweet['id']), user_id, str(tweet['full_text']), int(tweet['retweet_count']), int(tweet['favorite_count']))


def twitter_api(twitter_user):
    auth = tweepy.OAuthHandler("ftQlu6bo1bNANdyldduBhzVaH", "aU9St3CFR2m6IlSLKEcSzdOghojQCV7K2HOniLG8BjA05EjHds")
    auth.set_access_token("606314285-0aWgonCbBFS10Bv0BEMSi94gY14tjNxB6Rrb21jc", "l6GTdpPfe5LooPgdzluDwSHbnEyJRf4EzilTpMSxXI51y")
    
    api = tweepy.API(auth)
    
    # fetching the user 
    user = api.get_user(twitter_user) 
      
    # fetching the ID 
    user_id = user.id_str 
    
    tweets_list = []

    for status in tweepy.Cursor(api.user_timeline, twitter_user, tweet_mode="extended").items():
        tweets_list.append(status)
    
    return user_id, tweets_list  



#------------------------------ MAIN PROGRAMM ------------------------------
db = 0
# Open database connection
try:
    db = MySQLdb.connect(host="localhost", use_unicode = True, charset = "utf8", user="root", passwd="", db="bilos_db")
except Exception as e:
    print ("DB connection error!\n")
# prepare a cursor object using cursor() method
cursor = db.cursor()

CreateTableFBUsers()
CreateTableFBPosts()
CreateTableTwitterUsers()
CreateTableTwitterPosts()


fb_user         = ['ERTformula1', 'DonaldTrump']
twitter_user    = ['VasilisPapadak2']

for i in range(0, len(fb_user)):
    post_list = fb_scraper(fb_user[i])
    RecordFBValuesToDB(fb_user[i], post_list)


for i in range(0, len(twitter_user)):
    user_id, tweets_list = twitter_api(twitter_user[i])
    RecordTwitterValuesToDB(twitter_user[i], user_id, tweets_list)


 # disconnect from server
db.close()


#------------------------------ END MAIN PROGRAMM ------------------------------
    
   


