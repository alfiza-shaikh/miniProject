from database.conn import execute

def insertDVDB(lpn,vtype,video_ref,time):
    inserted=execute("INSERT INTO vehicles values('"+lpn+"','"+vtype+"','"+video_ref+"','"+time+"')")
    return inserted


def getDVFiltered(videos,filters):
    query="SELECT vehicle_lpn,vehicle_type,time,folder_name,video_name FROM vehicles INNER JOIN videos\
            ON vehicles.video_ref = videos.video_ref\
            WHERE ("
    for v in videos:
        query+=" vehicles.video_ref='"+v+"' OR" 
    query = query[:-2]+") "
    # if filters['From Date']!="":
    #     query+=" AND timestamp::date>='"+ filters['From Date']+"'"
    # if filters['To Date']!="":
    #     query+=" AND timestamp::date<='"+filters['To Date']+"'"
    if filters['From Time']!="":
        query+=" AND time>='"+filters['From Time']+"'"
    if filters['To Time']!="":
        query+=" AND time::time<='"+filters['To Time']+"'"
    if filters['Vehicle Number']!="":
        query+=" AND vehicle_lpn  iLIKE '%"+filters['Vehicle Number']+"%'"
    if filters['Vehicle Type']!="":
        query+=" AND vehicle_type='"+filters['Vehicle Type']+"'"
    # if filters['Color']!="":
    #     query+=" AND vehicle_color='"+filters['Color']+"'"
    query+=" ORDER BY folder_name,video_name, time "
    data=execute(query)
    if data:
        return data 
    return None