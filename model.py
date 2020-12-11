c
def insertValue(fb_user, title, likes, comments, link, shares,cursor,db):
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



def CreateFBTable(fb_user,cursor):
    # Drop table if it already exist using execute() method.
    cursor.execute("DROP TABLE IF EXISTS fb_posts_" + str(fb_user))

    # Create table as per requirement
    sql = """CREATE TABLE fb_posts_%s (ID INT AUTO_INCREMENT PRIMARY KEY, TITLE VARCHAR(1024), LIKES INT, COMMENTS INT, LINK VARCHAR(1024), SHARES INT)""" % \
    		(str(fb_user))

    cursor.execute(sql)
