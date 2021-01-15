# -*- coding: utf-8 -*-

from tweepy import OAuthHandler, API
from flask import Flask,jsonify,_app_ctx_stack,render_template, request
from json import load
import facebook_scraper
# import sqlite3
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy import create_engine,Column,ForeignKey,Integer,String,BigInteger,Unicode, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/users', methods=['GET', 'POST'])
def render_search():
    # POST: Search string
    if request.method == 'POST':
        print(request.form)
        print(request.values)
        _twitter_name = request.form.get('inputNameTwitter')
        _fb_name = request.form.get('inputNameFacebook')
        # read the posted values from the UI
        if _twitter_name:
            api = twitter_api()
            public_tweets = api.user_timeline(_twitter_name)
            print(render_template('results.html',
            cols_user= ['User id','Username','Location','Description','Followers',
            'Friends','Favorites','Tweets'],cols_tweets=['Tweet id','Text',
            'Date-Time','Source','Language','Location','Latitude','Longitude',
            'Favorites','Retweets'],
            rows=public_tweets))
            return render_template('results.html',
            cols_user= ['User id','Username','Location','Description','Followers',
            'Friends','Favorites','Tweets'],cols_tweets=['Tweet id','Text',
            'Date-Time','Source','Language','Location','Latitude','Longitude',
            'Favorites','Retweets'],
            public_tweets=public_tweets)
        if _fb_name:
            get_p = facebook_scraper.get_posts(_fb_name, pages=2)
            post_list = []
            for post in get_p:
                post_list.append(post)
            return render_template('results.html', user= _fb_name, public_posts=post_list)
    # GET: Serve search page
    return render_template('user_search.html')

@app.route('/twitter/home')
def home():
    api = twitter_api()
    public_tweets = api.home_timeline()
    response = [tweet._json for tweet in public_tweets]
    return jsonify(response)

@app.route('/twitter?user=<username>',methods=['POST'])
def profile(username):
    api = twitter_api()
    public_tweets = api.user_timeline(username)
    # for tweet in public_tweets:
    #     user_id = tweet.user.id
    #     name = tweet.user.name
    #     screen_name = tweet.user.name
    #     location = tweet.user.location
    #     description = tweet.user.description
    #     followers = tweet.user.followers_count
    #     friends = tweet.user.friends_count
    #     favorites = tweet.user.favourites_count
    #     tweets_count = tweet.user.statuses_count
    #     check_user(user_id,name,screen_name,location,description,friends,followers,favorites,tweets_count)
    #     tweetid = tweet.id
    #     text = tweet.text
    #     created_time = tweet.created_at
    #     source = tweet.source
    #     quoted_id = tweet.quoted_status_id
    #     retweeted_id = tweet.retweeted_status
    #     language = tweet.lang
    #     location = tweet.place.full_name +" "+ tweet.place.country
    #     latitude = tweet.coordinates.coordinates[2]
    #     longitude = tweet.coordinates.coordinates[1]
    #     retweets = tweet.retweetcount
    #     favorites = tweet.favorite_count
    #     check_tweet(tweet_id,text,created_time,source,quoted_id,retweeted_id,language,location,latitude,longitude,retweets,favorites)
    #
    #     if  hasattr('tweet', 'quoted_status'):
    #         tweet_= tweet.quoted_status
    #         user_id = tweet_.user.id
    #         name = tweet_.user.name
    #         screen_name = tweet_.user.name
    #         location = tweet_.user.location
    #         description = tweet_.user.description
    #         followers = tweet_.user.followers_count
    #         friends = tweet_.user.friends_count
    #         favorites = tweet_.user.favourites_count
    #         tweet_s_count = tweet_.user.statuses_count
    #         check_user(user_id,name,screen_name,location,description,friends,followers,favorites,tweets_count)
    #         tweetid = tweet_.id
    #         text = tweet_.text
    #         created_time = tweet_.created_at
    #         source = tweet_.source
    #         quoted_id = tweet_.quoted_status_id
    #         retweeted_id = tweet_.retweeted_status
    #         language = tweet_.lang
    #         location = tweet_.place.full_name +" "+ tweet_.place.country
    #         latitude = tweet_.coordinates.coordinates[2]
    #         longitude = tweet_.coordinates.coordinates[1]
    #         retweets = tweet_.retweetcount
    #         favorites = tweet_.favorite_count
    #         check_tweet(tweet_id,text,created_time,source,quoted_id,retweeted_id,language,location,latitude,longitude,retweets,favorites)
    #     if hasattr('tweet', 'retweeted_status'):
    #         tweet_= tweet.retweeted_status
    #         user_id = tweet_.user.id
    #         name = tweet_.user.name
    #         screen_name = tweet_.user.name
    #         location = tweet_.user.location
    #         description = tweet_.user.description
    #         followers = tweet_.user.followers_count
    #         friends = tweet_.user.friends_count
    #         favorites = tweet_.user.favourites_count
    #         tweet_s_count = tweet_.user.statuses_count
    #         check_user(user_id,name,screen_name,location,description,friends,followers,favorites,tweets_count)
    #         tweetid = tweet_.id
    #         text = tweet_.text
    #         created_time = tweet_.created_at
    #         source = tweet_.source
    #         quoted_id = tweet_.quoted_status_id
    #         retweeted_id = tweet_.retweeted_status
    #         language = tweet_.lang
    #         location = tweet_.place.full_name +" "+ tweet_.place.country
    #         latitude = tweet_.coordinates.coordinates[2]
    #         longitude = tweet_.coordinates.coordinates[1]
    #         retweets = tweet_.retweetcount
    #         favorites = tweet_.favorite_count
    #         check_tweet(tweet_id,text,created_time,source,quoted_id,retweeted_id,language,location,latitude,longitude,retweets,favorites)
    response = [tweet._json for tweet in public_tweets]
    return jsonify(response)

def twitter_api():
    # Load credentials from json file
    with open("twitter_credentials.json", "r") as file:
        creds = load(file)
    auth = OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    return API(auth)

SQLALCHEMY_DATABASE_URL= "sqlite:///./twitter.sqlite3"

engine = create_engine(
SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread":False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)
Base = declarative_base()

db = SessionLocal()
db_session = scoped_session(SessionLocal,scopefunc=_app_ctx_stack.__ident_func__)

class Tweet(Base):
    __tablename__='tweets'
    id = Column(BigInteger, primary_key=True)
    text = Column(Unicode(320),nullable=False)
    created_time = Column(DateTime,nullable=False)
    source = Column(String(50))
    # entities_id = Column(Integer, ForeignKey('entities.id'))
    # entities = relationship('Entity', back_populates='entities')
    # to change to three objects : mentions, hashtags and urls
    # and to corresponding intermediate tables
    user_id = Column(BigInteger, ForeignKey('users.id'),nullable=False)
    user = relationship('User', back_populates='tweets')
    quoted_id = Column(BigInteger, ForeignKey('tweets.id'))
    # quoted = relationship('Tweet', back_populates='quoted_id')
    retweeted_id = Column(BigInteger, ForeignKey('tweets.id'))
    # retweeted = relationship('Tweet', back_populates='retweeted_id')
    language = Column(String(36))
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    retweets = Column(Integer)
    favorites = Column(Integer)

class User(Base):
    __tablename__='users'
    id = Column(BigInteger, primary_key=True)
    screen_name = Column(String(15),unique=True,nullable=False)
    name = Column(String(50))
    description = Column(Unicode(200))
    tweets = relationship('Tweet', back_populates='user')
    language = Column(String(36))
    location = Column(String(200))
    followers = Column(Integer)
    friends = Column(Integer)
    favorites = Column(Integer)
    tweets_count = Column(Integer)


Base.metadata.create_all(bind=engine)
Base.query = db_session.query_property()

def add_item(item):
    db_session.add(item)
    db_session.commmit()

def check_user(userid,name,screen_name,location,description,friends,followers,favorites,tweets_count):
    if userid not in User.query.all():
        user = User(id=userid,name=name,screen_name=screen_name,location=location,description=description,friends=friends,followers=followers,favorites=favorites,tweets_count=tweets_count)
        add_item(user)

def check_tweet(tweet_id,text,created_time,source,quoted_id,retweeted_id,language,location,latitude,longitude,retweets,favorites):
    if tweet_id not in Tweet.query.all():
        tweet = Tweet(id=tweet_id,text=text,created_time=created_time,source=source,quoted_id=quoted_id,retweeted_id=retweeted_id,language=language,location=location,latitude=latitude,longitude=longitude,retweets=retweets,favorites=favorites)
        add_item(tweet)

if __name__ == '__main__':
    app.run()


@app.teardown_appcontext
def teardown_db(exception):
    db.close()
