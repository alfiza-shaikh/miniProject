# from database.conn import connection,cursor
import psycopg2



def register(name,email,password):
    registered=None
    try:
        connection = psycopg2.connect(user="postgres",
                                        password="postgres",
                                        host="127.0.0.1",
                                        database="ALPR")

        cursor = connection.cursor()
        registered=cursor.execute("INSERT INTO users (uname,email,pass) values('"+name+"','"+email+"','"+password+"')")
        connection.commit()
        registered=True
    except (Exception, psycopg2.DatabaseError) as error:
        connection.rollback()
        connection.rollback()
        print(error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    print("registered",registered)
    return registered

    
def login(email,password):
    try:
        connection = psycopg2.connect(user="postgres",
                                        password="postgres",
                                        host="127.0.0.1",
                                        database="ALPR")

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email='"+email+"' AND pass='"+password+"'")
        data = cursor.fetchone()
        if data:
            return data[1]
        print(data)
    except (Exception, psycopg2.DatabaseError) as error:
        connection.rollback()
        connection.rollback()
        print(error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    return None
