from database.conn import executeIDU,executeSelect

def getHistory(email):
    data=executeSelect("SELECT * FROM history WHERE user_email='"+email+"' ORDER BY timestamp DESC")
    if data:
        return data 
    return None

def insertHistoryDB(email,action_name,action_on):
    inserted=executeIDU("INSERT INTO history (action_name,action_on,user_email) values('"+action_name+"','"+action_on+"','"+email+"')")
    return inserted
