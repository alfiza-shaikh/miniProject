# from database.conn import connection,cursor
import psycopg2

def register(name,email,password):
    
    print("registered")
    try:
        connection = psycopg2.connect(user="postgres",
                                        password="postgres",
                                        host="127.0.0.1",
                                        database="ALPR")

        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (uname,email,pass) values('"+name+"','"+email+"','"+password+"')")
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        connection.rollback()
        connection.rollback()
        print(error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    
