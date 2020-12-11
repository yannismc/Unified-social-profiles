
import mysql.connector as MySQLdb
import facebook_scraper
from model import CreateFBTable, insertValue

#------------------------------ MAIN PROGRAMM ------------------------------
fb_user = 'DonaldTrump'

get_p = facebook_scraper.get_posts(fb_user, pages=2)

post_list = []

for post in get_p:
    post_list.append(post)


db = 0
# Συνδέω db με localhost
try:
    db = MySQLdb.connect(host="localhost", use_unicode = True, charset = "utf8", user="root", passwd="", db="socialmedia_db")
except Exception as e:
    print ("DB connection error!\n")
# prepare a cursor object using cursor() method
cursor = db.cursor()

CreateFBTable(fb_user,cursor)

for i in range (0, len(post_list)):
    post = post_list[i]
    print(str(post['text']), int(post['likes']), int(post['comments']), str(post['link']), int(post['shares']))
    insertValue(fb_user, str(post['text']), int(post['likes']), int(post['comments']), str(post['link']), int(post['shares']),cursor,db)


 # disconnect from server
db.close()


#------------------------------ END MAIN PROGRAMM ------------------------------
