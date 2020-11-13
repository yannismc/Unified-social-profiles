import tweepy
from flask import Flask,jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/user/<int:username>')
def profile(username):
    auth = tweepy.OAuthHandler("ftQlu6bo1bNANdyldduBhzVaH", "aU9St3CFR2m6IlSLKEcSzdOghojQCV7K2HOniLG8BjA05EjHds")
    auth.set_access_token("606314285-8reNCexye4Ils8UXIKJQfnsJbRDYJA8hpQdd5p2h", "tRcv25I65iNMoZM0TY9TdkgCacEMcfbEb4C8CJf4IVsDG")

    api = tweepy.API(auth)

    public_tweets = api.user_timeline(username)
    response = [tweet._json for tweet in public_tweets]
    return jsonify(response)

if __name__ == '__main__':
    app.run()
