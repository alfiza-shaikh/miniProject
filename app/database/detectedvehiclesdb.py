from database.conn import execute

def insertDVDB(lpn,vtype,color,video_ref,time):
    inserted=execute("INSERT INTO vehicles values('"+lpn+"','"+vtype+"','"+color+"','"+video_ref+"','"+time+"')")
    return inserted

def getDV(email):
    data=execute("SELECT * FROM vehicles WHERE user_email='"+email+"' ORDER BY timestamp DESC")
    if data:
        return data 
    return None

def getDVFiltered(videos,filters):
    query="SELECT * FROM vehicles WHERE ("
    for v in videos:
        query+=" video_ref='"+v+"' OR" 
    query = query[:-2]+") "
    if filters['From Date']!="":
        query+=" AND timestamp::date>='"+ filters['From Date']+"'"
    if filters['To Date']!="":
        query+=" AND timestamp::date<='"+filters['To Date']+"'"
    if filters['From Time']!="":
        query+=" AND time::time>='"+filters['From Time']+"'"
    if filters['To Time']!="":
        query+=" AND time::time<='"+filters['To Time']+"'"
    if filters['Vehicle Number']!="":
        query+=" AND vehicle_lnp='"+filters['Vehicle Number']+"'"
    if filters['Vehicle Type']!="":
        query+=" AND vehicle_type='"+filters['Vehicle Type']+"'"
    if filters['Color']!="":
        query+=" AND vehicle_color='"+filters['Color']+"'"
    query+=" ORDER BY timestamp DESC"
    data=execute(query)
    if data:
        return data 
    return None