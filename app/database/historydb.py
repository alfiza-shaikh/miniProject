from database.conn import execute

def getHistory(email):
    data=execute("SELECT * FROM history WHERE user_email='"+email+"' ORDER BY timestamp DESC")
    if data:
        return data 
    return None

def insertHistoryDB(email,action_name,action_on):
    inserted=execute("INSERT INTO history (action_name,action_on,user_email) values('"+action_name+"','"+action_on+"','"+email+"')")
    return inserted

def getHistoryFiltered(email,fromdate,todate):
    query="SELECT * FROM history WHERE user_email='"+email+"'" 
    if fromdate:
        query+=" AND timestamp::date>='"+fromdate+"'"
    if todate:
        query+=" AND timestamp::date<='"+todate+"'"
    query+=" ORDER BY timestamp DESC"
    data=execute(query)
    if data:
        return data 
    return None