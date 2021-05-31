from database.conn import execute

def insertDVDB(lpn,vtype,video_ref,time):
    if vtype=='Car':
        vtype='Car / Taxi'
    elif vtype=='Motorcycle':
        vtype='Motorcycle / Scooter'
    print(vtype)
    inserted=execute("INSERT INTO vehicles values('"+lpn+"','"+vtype+"','"+video_ref+"',"+str(time)+")")
    return inserted


def getDVFiltered(videos,filters):
    query="SELECT vehicle_lpn,vehicle_type,video_time,folder_name,video_name FROM vehicles INNER JOIN videos\
            ON vehicles.video_ref = videos.video_ref\
            WHERE ("
    for v in videos:
        query+=" vehicles.video_ref='"+v+"' OR" 
    query = query[:-2]+") "
    # if filters['From Date']!="":
    #     query+=" AND timestamp::date>='"+ filters['From Date']+"'"
    # if filters['To Date']!="":
    #     query+=" AND timestamp::date<='"+filters['To Date']+"'"
    # if filters['From Time']!="":
    #     fromtime=filters['From Time']
    #     query+=" AND video_time>="+str(fromtime)+""
    # if filters['To Time']!="":
    #     totime=filters['To Time']
    #     query+=" AND video_time<="+str(totime)+""
    if filters['Vehicle Number']!="":
        query+=" AND vehicle_lpn  iLIKE '%"+filters['Vehicle Number']+"%'"
    if filters['Vehicle Type']!="":
        query+=" AND vehicle_type='"+filters['Vehicle Type']+"'"
    # if filters['Color']!="":
    #     query+=" AND vehicle_color='"+filters['Color']+"'"
    query+=" ORDER BY folder_name,video_name, video_time "
    data=execute(query)
    if data:
        return data 
    return None