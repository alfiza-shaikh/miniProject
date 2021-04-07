from database.conn import execute
import psycopg2


def register(name,email,password):
    registered=execute("INSERT INTO users (uname,email,pass) values('"+name+"','"+email+"','"+password+"')")
    return registered

    
def login(email,password):
    data=execute("SELECT * FROM users WHERE email='"+email+"' AND pass='"+password+"'")
    if data:
        return data[0][2]
    return None

