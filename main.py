from tweepy import OAuthHandler, API
from flask import Flask,jsonify,g
from flask_sqlalchemy import SQLAlchemy
from json import load
import sqlite3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)

# Load credentials from json file
with open("twitter_credentials.json", "r") as file:
    creds = load(file)

@app.route('/')
def welcome():
    return 'Welcome to Unified social profiles!'

@app.route('/twitter/user/<int:username>')
def profile(username):
    api = tweepy()

    public_tweets = api.user_timeline(username)
    for tweet in public_tweets:
        for tweet_ in [tweet,tweet.quoted_status,tweet.retweeted_status]:
            user_id = tweet_.user.id
            name = tweet_.user.name
            screen_name = tweet_.user.name
            location = tweet_.user.location
            description = tweet_.user.description
            followers = tweet_.user.followers_count
            friends = tweet_.user.friends_count
            favourites = tweet_.user.favourites_count
            tweets_count = tweet_.user.statuses_count
            check_user(user_id,name,screen_name,location,description,friends,followers,favourites,tweets_count)
            tweet_id = tweet_.id
            text = tweet_.text
            created_time = tweet_.created_at
            source = tweet_.source
            quoted_id = tweet_.quoted_status_id
            retweeted_id = tweet_.retweeted_status
            language = tweet_.lang
            location = tweet_.place.full_name +" "+ tweet_.place.country
            latitude = tweet_.coordinates.coordinates[2]
            longitude = tweet_.coordinates.coordinates[1]
            retweets = tweet_.retweet_count
            favorites = tweet_.favorite_count
            check_tweet(tweet_id,text,created_time,source,quoted_id,retweeted_id,language,location,latitude,longitude,retweets,favorites)
    response = [tweet._json for tweet in public_tweets]
    return jsonify(response)

def tweepy():
    auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    return API(auth)

db = SQLAlchemy(app)

class Tweet(db.Model):
    __tablename__='tweets'
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.Unicode(320),nullable=False)
    created_time = db.Column(db.DateTime,nullable=False)
    source = db.Column(db.String(50))
    # entities_id = db.Column(db.Integer, db.ForeignKey('entities.id'))
    # entities = db.relationship('Entity', back_populates='entities')
    # to change to three objects : mentions, hashtags and urls
    # and to corresponding intermediate tables
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'),nullable=False)
    user = db.relationship('User', back_populates='tweets')
    quoted_id = db.Column(db.BigInteger, db.ForeignKey('tweets.id'))
    quoted = db.relationship('Tweet', back_populates='tweets')
    retweeted_id = db.Column(db.BigInteger, db.ForeignKey('tweets.id'))
    retweeted = db.relationship('Tweet', back_populates='tweets')
    language = db.Column(db.String(36))
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    retweets = db.Column(db.Integer)
    favorites = db.Column(db.Integer)

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.BigInteger, primary_key=True)
    screen_name = db.Column(db.String(15),unique=True,nullable=False)
    name = db.Column(db.String(50))
    description = db.Column(db.Unicode(200))
    tweets = db.relationship('Tweet', back_populates='users')
    language = db.Column(db.String(36))
    location = db.Column(db.String(200))
    followers = db.Column(db.Integer)
    friends = db.Column(db.Integer)
    favorites = db.Column(db.Integer)
    tweets_count = db.Column(db.Integer)

db.create_all()

engine = create_engine('sqlite:///twitter.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

def add_item(item):
    db.session.add(item)
    db.session.commmit()

def check_user(userid,name,screen_name,location,description,friends,followers,favourites,tweets_count):
    if userid not in [user.id for user in User.query.all()]:
        user = User(id=userid,name=name,screen_name=screen_name,location=location,description=description,friends=friends,followers=followers,favourites=favourites,tweets_count=tweets_count)
        add_item(user)

def check_tweet(tweet_id,text,created_time,source,quoted_id,retweeted_id,language,location,latitude,longitude,retweets,favorites):
    if tweet_id not in [tweet.id for tweet in Tweet.query.all()]:
        tweet = Twwet(id=tweet_id,text=text,created_time=created_time,source=source,quoted_id=quoted_id,retweeted_id=retweeted_id,language=language,location=location,latitude=latitude,longitude=longitude,retweets=retweets,favorites=favorites)
        add_item(tweet)

if __name__ == '__main__':
    app.run()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db.session is not None:
        db.session.close()
