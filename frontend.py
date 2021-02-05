# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 00:09:30 2020


"""

import mysql.connector as MySQLdb
#import MySQLdb
from flask import Flask,render_template, request
from ast import literal_eval
import plotly.express as px
from pandas import DataFrame, merge
from plotly.subplots import make_subplots
from datetime import datetime,timedelta
from math import ceil
import plotly.graph_objects as go
from collections import Counter

#------------------------------ FB FUNCTIONS ------------------------------
def SearchTableFBUsers(user_name):
    if type(user_name) is int:
        sql = """
        SELECT NAME,TITLE,CREATED_AT,SHARES,COMMENTS,LIKES
        FROM `fb_posts`
        INNER JOIN `fb_users` ON `fb_users`.UID=`fb_posts`.UID_POST
        WHERE `fb_users`.UID = %s
        """
    if type(user_name) is str:
        sql = """SELECT NAME,TITLE,CREATED_AT,SHARES,COMMENTS,LIKES
            FROM `fb_posts`
            INNER JOIN `fb_users` ON `fb_users`.UID=`fb_posts`.UID_POST
            WHERE `fb_users`.NAME=%s
            """
    user_search=(str(user_name),)
    try:
        # Execute the SQL command
        cursor.execute(sql,user_search)
        sql_results=cursor.fetchall()
    except ValueError as e :
        print('SearchTableFBUsers:DB error',sql,'\n',e,"\n")
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
        df=df.assign(tweets=lambda x:1)
        clean_df=df[['tweets','created_at','retweet_count','favorite_count',
                     'HASHTAGS']]

    if type == 'posts':
        df= DataFrame(list_of_tuples, columns=['NAME','TITLE',
        'created_at','shares','comments','likes'])
        df=df.assign(posts=lambda x:1)
        clean_df=df[['posts','created_at','shares','comments','likes','TITLE']]

    return clean_df

#----------------------------HASHATAGS FUNCTIONS----------------------------
def extarct_hashtags(tweets_list,df_post_list):
    df = tweets_list[tweets_list.HASHTAGS != '']
    df=df[['HASHTAGS']]
    df.dropna(inplace=True)
    hashtag_list = []
    for j in range (0, len(df.index)):
        hashtag=str(df.values[j]).replace("['",'').replace("']",'').split(", ")
        for h in hashtag:
            hashtag_list.append(h)
    for text in df_post_list['TITLE']:
        for word in text.split():

        # checking the first charcter of every word
            if word[0] == '#':

            # adding the word to the hashtag_list
                hashtag_list.append(word[1:])

    return hashtag_list


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

@app.route('/alias', methods=['GET', 'POST'])
def alias():
    if request.method == 'POST':
        print(request.form)
        print(request.values)
        (twitter_id, fb_id)=ast.literal_eval(request.form.get('aid'))
        public_tweets=SearchTableTwitterUsers(int(twitter_id))
        post_list=SearchTableFBUsers(int(fb_id))
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
        (twitter_id, fb_id)=literal_eval(request.form.get('aid'))
        public_tweets=SearchTableTwitterUsers(int(twitter_id))
        post_list=SearchTableFBUsers(int(fb_id))
        df_post_list=clean_data(post_list,'posts')
        df_tweets_list = clean_data(public_tweets,'tweets')


        dfs = merge(df_tweets_list,
                   df_post_list,
                   on='created_at',
                   how = 'outer')
        subfig  = make_subplots(specs=[[{"secondary_y": True}]])

        nbins = ceil((datetime.now() - datetime(2020,1,1)) / timedelta(hours=3))

        fig_metrics = px.histogram(dfs,x='created_at',y=['shares',
                                          'comments',
                                          'likes',
                                          'retweet_count',
                                          'favorite_count'
                                          ],nbins=nbins)
        fig2=px.histogram(dfs,x='created_at',y=['tweets','posts'],nbins=nbins)
        fig2.update_traces(yaxis="y2")
        subfig.add_traces(fig_metrics.data + fig2.data)
        subfig.layout.barmode='overlay'
        subfig.layout.xaxis.title="Time"
        subfig.layout.yaxis.title="Reactions"
        subfig.layout.yaxis2.title="Posts/Tweets"
        subfig.update_layout(xaxis_range=['2021-01-01','2021-02-04'])
        subfig.update_xaxes(rangeslider_visible=True)


        subfig.write_html("templates/fig1.html")


        return render_template('fig1.html')
    alias_list = enumerateAlias()
    return render_template('analytics.html',items=alias_list)

@app.route('/hashtags', methods=['GET', 'POST'])
def hashtags():
    if request.method == 'POST':
        print(request.form)
        print(request.values)
        (twitter_id, fb_id)=literal_eval(request.form.get('aid'))
        public_tweets=SearchTableTwitterUsers(int(twitter_id))
        post_list=SearchTableFBUsers(int(fb_id))
        df_post_list=clean_data(post_list,'posts')
        df_tweets_list = clean_data(public_tweets,'tweets')
        z=extarct_hashtags(df_tweets_list,df_post_list)
        data = Counter(z)
        data= dict(sorted(data.items(), key=lambda item: item[1],reverse=True))
        fig = go.Figure(data=[go.Table(header=dict(
            values=["Hashtag","Occurences"]),
        cells=dict(values=[list(data.keys())[:10],list(data.values())[:10]]))])

        fig.write_html("templates/fig2.html")

        return render_template('fig2.html')
    alias_list = enumerateAlias()
    return render_template('hashtags.html',items=alias_list)

if __name__ == '__main__':
    app.run()

@app.teardown_appcontext
def teardown_db(exception):
    db.close()
