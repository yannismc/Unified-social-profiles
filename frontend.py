# -*- coding: utf-8 -*-

from flask import Flask,jsonify,render_template, request
from json import load
import mysql.connector as MySQLdb
import ast
import tweepy
import plotly.express as px
from pandas import DataFrame, merge
import dash
import dash_core_components as dcc
import dash_html_components as html


#------------------------------ FB FUNCTIONS ------------------------------
def SearchTableFBUsers(user_name):
    if type(user_name) is int:
        sql = """
        SELECT NAME,TITLE,TIME,SHARES,COMMENTS,LIKES
        FROM `fb_posts`
        INNER JOIN `fb_users` ON `fb_users`.UID=`fb_posts`.UID_POST
        WHERE `fb_users`.UID=%s
        """
    if type(user_name) is str:
        sql = """SELECT NAME,TITLE,TIME,SHARES,COMMENTS,LIKES
            FROM `fb_posts`
            INNER JOIN `fb_users` ON `fb_users`.UID=`fb_posts`.UID_POST
            WHERE `fb_users`.NAME=%s
            """
    user_search=(str(user_name),)
    try:
        # Execute the SQL command
        cursor.execute(sql,user_search)
        sql_results=cursor.fetchall()
    except:
        print('SearchTableFBUsers:DB error')
        sql_results=[]
    return sql_results
#------------------------------ TWITTER FUNCTIONS ------------------------------
def SearchTableTwitterUsers(user_name):
    if type(user_name) is int:
        sql = """
        SELECT NAME,FOLLOWERS_COUNT, FRIENDS_COUNT,FAVORITES_COUNT, TWEETS_COUNT,
        TITLE,CREATED_AT,HASHTAGS,SOURCE,LANGUAGE,FAVORITE_COUNT,RETWEET_COUNT
        FROM `twitter_tweets`
        INNER JOIN `twitter_users` ON `twitter_users`.UID=`twitter_tweets`.UID_TWEET
        WHERE `twitter_users`.UID=%s
        """
    if type(user_name) is str:
        sql = """
        SELECT NAME,FOLLOWERS_COUNT, FRIENDS_COUNT,FAVORITES_COUNT, TWEETS_COUNT,
        TITLE,CREATED_AT,HASHTAGS,SOURCE,LANGUAGE,FAVORITE_COUNT,RETWEET_COUNT
        FROM `twitter_tweets`
        INNER JOIN `twitter_users` ON `twitter_users`.UID=`twitter_tweets`.UID_TWEET
        WHERE `twitter_users`.NAME=%s
        """
    user_search=(str(user_name),)
    try:
        # Execute the SQL command
        cursor.execute(sql,user_search)
        sql_results=cursor.fetchall()
    except:
        print('SearchTableTwitterUsers:DB error')
        sql_results=[]
    return sql_results
#------------------------------ TWITTER API FUNCTIONS --------------------------

def twitter_api():
    # Load credentials from json file
    with open("twitter_credentials.json", "r") as file:
        creds = load(file)
    auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    return tweepy.API(auth)

#------------------------------ENUMERATE ALIAS---------------------------------
def enumerateAlias():
    try:
        # Execute the SQL command
        cursor.execute("SELECT `AID`,`UID_TWITTER`,`UID_FB` FROM `alias`")
        sql_results=cursor.fetchall()
    except:
        print('EnumerateAlias:DB error')
    return sql_results

#------------------------------CLEAN DATAFRAME---------------------------------

def clean_data(list_of_tuples,type):
    if type == 'tweets':
        df = DataFrame(list_of_tuples, columns=['NAME',
        'FOLLOWERS_COUNT', 'FRIENDS_COUNT','FAVORITES_COUNT',
        'TWEETS_COUNT','TITLE',
        'created_at',
        'HASHTAGS','SOURCE','LANGUAGE',
        'favorite_count','retweet_count'])
        clean_df=df[['created_at','retweet_count','favorite_count']]

    if type == 'posts':
        df= DataFrame(list_of_tuples, columns=['NAME','TITLE',
        'time','shares','comments','likes'])
        clean_df=df[['time','shares','comments','likes']]

    return clean_df

#------------------------------ MAIN PROGRAMM ------------------------------
db = 0
# Open database connection
try:
    db = MySQLdb.connect(host="localhost", use_unicode = True, charset = "utf8", user="root", passwd="", db="socialmedia_db")
except:
    print ("DB connection error!\n")
# prepare a cursor object using cursor() method
cursor = db.cursor()

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
            public_tweets=SearchTableTwitterUsers(_twitter_name)
            return render_template('results.html',
            cols_user= ['Username',
            'Followers',
            'Friends','Favorites','Tweets'],cols_tweets=['Text',
            'Date-Time','Hashtags','Language',
            'Favorites','Retweets'],
            public_tweets=public_tweets)
        if _fb_name:
            post_list=SearchTableFBUsers(_fb_name)
            return render_template('results.html',
            cols_fb_user= ['Username'],cols_posts=['Text',
            'Likes','Comments','Shares'],
             public_posts=post_list)
    # GET: Serve search page
    return render_template('user_search.html')

@app.route('/twitter/home')
def home():
    api = twitter_api()
    public_tweets = api.home_timeline()
    response = [tweet._json for tweet in public_tweets]
    return jsonify(response)

@app.route('/alias', methods=['GET', 'POST'])
def alias():
    if request.method == 'POST':
        print(request.form)
        print(request.values)
        (_twitter_id, _fb_id)=ast.literal_eval(request.form.get('aid'))
        public_tweets=SearchTableTwitterUsers(int(_twitter_id))
        post_list=SearchTableFBUsers(int(_fb_id))
        return render_template('results.html',
            cols_user= ['Username',
            'Followers',
            'Friends','Favorites','Tweets'],cols_tweets=['Text',
            'Date-Time','Hashtags','Language',
            'Favorites','Retweets'],
            public_tweets=public_tweets,
            cols_fb_user= ['Username'],cols_posts=['Text',
            'Likes','Comments','Shares'],
             public_posts=post_list)
    alias_list = enumerateAlias()
    return render_template('alias.html',items=alias_list)

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if request.method == 'POST':
        print(request.form)
        print(request.values)
        (_twitter_id, _fb_id)=ast.literal_eval(request.form.get('aid'))
        public_tweets=SearchTableTwitterUsers(int(_twitter_id))
        # post_list=SearchTableFBUsers(int(_fb_id))
        # df_post_list=clean_data(post_list,'posts')
        df_tweets_list = clean_data(public_tweets,'tweets')


        # dfs = merge(df_tweets_list.rename(columns={'created_at':'time'}),
        #            df_post_list,
        #            on='time',
        #            how = 'outer')
        # fig_metrics=px.line(dfs,x='time',y=['shares',
        #                                   'comments',
        #                                   'likes',
        #                                   'retweet_count',
        #                                   'favorite_count'
        #                                   ])
        fig_metrics=px.line(df_tweets_list,x='created_at',y=[
                                          'retweet_count',
                                          'favorite_count'
                                          ])
        fig_metrics.write_html("templates/fig.html")
        return render_template('fig.html')
    alias_list = enumerateAlias()
    return render_template('analytics.html',items=alias_list)

if __name__ == '__main__':
    app.run()

@app.teardown_appcontext
def teardown_db(exception):
    db.close()
