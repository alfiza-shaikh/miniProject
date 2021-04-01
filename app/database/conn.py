import psycopg2

def executeIDU(query):
    result=None
    try:
        connection = psycopg2.connect(user="postgres",
                                        password="postgres",
                                        host="127.0.0.1",
                                        database="ALPR")

        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        result=True
    except (Exception, psycopg2.DatabaseError) as error:
        connection.rollback()
        connection.rollback()
        print(error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    return result

def executeSelect(query):
    data=None
    try:
        connection = psycopg2.connect(user="postgres",
                                        password="postgres",
                                        host="127.0.0.1",
                                        database="ALPR")

        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        connection.rollback()
        connection.rollback()
        print(error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    return data
        

