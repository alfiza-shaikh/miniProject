from database.conn import executeIDU,executeSelect
import psycopg2


def register(name,email,password):
    registered=executeIDU("INSERT INTO users (uname,email,pass) values('"+name+"','"+email+"','"+password+"')")
    return registered

    
def login(email,password):
    data=executeSelect("SELECT * FROM users WHERE email='"+email+"' AND pass='"+password+"'")
    if data:
        return data[0][2]
    return None

