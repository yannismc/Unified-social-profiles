# -*- coding: utf-8 -*-

from flask import Flask,jsonify,_app_ctx_stack,render_template, request
from json import load
import mysql.connector as MySQLdb
import ast

#------------------------------ FB FUNCTIONS ------------------------------
def SearchTableFBUsers(user_name):
    sql = """
    SELECT NAME,TITLE,SHARES,COMMENTS,LIKES
    FROM `fb_posts`
    INNER JOIN `fb_users` ON `fb_users`.UID=`fb_posts`.UID_POST
    WHERE `fb_users`.UID=%s
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
    sql = """
    SELECT NAME,FOLLOWERS_COUNT, FRIENDS_COUNT,FAVORITES_COUNT, TWEETS_COUNT,
    TITLE,CREATED_AT,HASHTAGS,SOURCE,LANGUAGE,FAVORITE_COUNT,RETWEET_COUNT
    FROM `twitter_tweets`
    INNER JOIN `twitter_users` ON `twitter_users`.UID=`twitter_tweets`.UID_TWEET
    WHERE `twitter_users`.UID=%s
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
    auth = OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    return API(auth)

#------------------------------ENUMERATE ALIAS---------------------------------
def enumerateAlias():
    try:
        # Execute the SQL command
        cursor.execute("SELECT `AID`,`UID_TWITTER`,`UID_FB` FROM `alias`")
        sql_results=cursor.fetchall()
    except:
        print('EnumerateAlias:DB error')
    return sql_results
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
            'Date-Time','Hashtags','Source','Language',
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

# @app.route('/twitter?user=<username>',methods=['POST'])
# def profile(username):
#     response = [tweet._json for tweet in public_tweets]
#     return jsonify(response)

@app.route('/alias', methods=['GET', 'POST'])
def alias():
    if request.method == 'POST':
        print(request.form)
        print(request.values)
        (_twitter_id, _fb_id)=ast.literal_eval(request.form.get('aid'))
        public_tweets=SearchTableTwitterUsers(_twitter_id)
        post_list=SearchTableFBUsers(_fb_id)
        return render_template('results.html',
            cols_user= ['Username',
            'Followers',
            'Friends','Favorites','Tweets'],cols_tweets=['Text',
            'Date-Time','Hashtags','Source','Language',
            'Favorites','Retweets'],
            public_tweets=public_tweets,
            cols_fb_user= ['Username'],cols_posts=['Text',
            'Likes','Comments','Shares'],
             public_posts=post_list)
    alias_list = enumerateAlias()
    return render_template('alias.html',items=alias_list)

# @app.route('/alias?aid=<alias>',methods=['POST'])
# def search(aid):
#         response = [tweet._json for tweet in public_tweets]
#         return jsonify(response)

if __name__ == '__main__':
    app.run()

@app.teardown_appcontext
def teardown_db(exception):
    db.close()
