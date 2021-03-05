import psycopg2

try:
    connection = psycopg2.connect(user="postgres",
                                    password="postgres",
                                    host="127.0.0.1",
                                    database="ALPR")

    cursor = connection.cursor()
except (Exception, psycopg2.DatabaseError) as error:
    connection.rollback()
    connection.rollback()
    print(error)
finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
    