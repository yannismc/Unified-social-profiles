import tweepy

auth = tweepy.OAuthHandler("ftQlu6bo1bNANdyldduBhzVaH", "aU9St3CFR2m6IlSLKEcSzdOghojQCV7K2HOniLG8BjA05EjHds")
auth.set_access_token("606314285-8reNCexye4Ils8UXIKJQfnsJbRDYJA8hpQdd5p2h", "tRcv25I65iNMoZM0TY9TdkgCacEMcfbEb4C8CJf4IVsDG")

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)