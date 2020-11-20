
import MySQLdb
import facebook_scraper



def insertValue(fb_user, title, likes, comments, link, shares):
  sql = """INSERT INTO fb_posts_%s (TITLE, LIKES, COMMENTS, LINK, SHARES) \
	VALUES ('%s', '%d', '%d', '%s', '%d')""" % \
	(str(fb_user), title, likes, comments, link, shares)

  try:
    # Execute the SQL command
    cursor.execute(sql)
    # Commit your changes in the database
    db.commit()
  except:
    # Rollback in case there is any error
    db.rollback()



def CreateFBTable(fb_user):
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS fb_posts_" + str(fb_user))
      
    # Create table as per requirement
    sql = """CREATE TABLE fb_posts_%s (ID INT AUTO_INCREMENT PRIMARY KEY, TITLE VARCHAR(1024), LIKES INT, COMMENTS INT, LINK VARCHAR(1024), SHARES INT)""" % \
    		(str(fb_user))
    	    
    cursor.execute(sql)








 
#------------------------------ MAIN PROGRAMM ------------------------------
fb_user = 'DonaldTrump'

get_p = facebook_scraper.get_posts(fb_user, pages=2, credentials=('bilospap.2020@gmail.com', 'bil.1994!!$$'))

post_list = []

for post in get_p:
    post_list.append(post)


db = 0
# Συνδέω db με localhost
try:
    db = MySQLdb.connect(host="localhost", use_unicode = True, charset = "utf8", user="root", passwd="", db="bilos_db")
except Exception as e:
    print ("DB connection error!\n")
# prepare a cursor object using cursor() method
cursor = db.cursor()

CreateFBTable(fb_user)

for i in range (0, len(post_list)):
    post = post_list[i]
    print(str(post['text']), int(post['likes']), int(post['comments']), str(post['link']), int(post['shares']))
    insertValue(fb_user, str(post['text']), int(post['likes']), int(post['comments']), str(post['link']), int(post['shares']))



 # disconnect from server
db.close()


#------------------------------ END MAIN PROGRAMM ------------------------------
    
   


