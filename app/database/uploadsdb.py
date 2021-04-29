from database.conn import execute

def getAllFolders(email):
    data=execute("SELECT folder_name FROM folders WHERE user_email='"+email+"'")
    if data:
        return data 
    return None

def createFolderDB(folderName,email):
    created=execute("INSERT INTO folders (folder_name,user_email) values('"+folderName+"','"+email+"')")
    return created

def deleteFolderDB(folderName,email):
    deleted=execute("DELETE FROM folders WHERE folder_name='"+folderName+"' AND user_email='"+email+"'")
    return deleted

def updateFolderDB(folderName,email,newFolderName):
    updated=execute("UPDATE folders SET folder_name='"+newFolderName+"' WHERE folder_name='"+folderName+"' AND user_email='"+email+"'")
    return updated

def searchFolderDB(folderLike,email):
    data=execute("SELECT folder_name FROM folders WHERE user_email='"+email+"' AND folder_name iLIKE '%"+folderLike+"%'")
    if data:
        return data 
    return None

def getVideoFromRef(ref):
    data=execute("SELECT * FROM videos WHERE video_ref='"+ref+"'")
    if data:
        return data[0] 
    return None

def getVideosinFolder(folderName,email):
    data=execute("SELECT * FROM videos WHERE user_email='"+email+"' AND folder_name='"+folderName+"'")
    if data:
        return data 
    return None

def uploadVideoDB(video,folderName,email):
    uploaded=execute("INSERT INTO videos (video_name,video_comment,video_ref,folder_name,user_email) \
    values('"+video['name']+"','"+video['comment']+"','"+video['ref']+"','"+folderName+"','"+email+"')")
    return uploaded

def deleteVideoDB(video_ref):
    deleted=execute("DELETE FROM videos WHERE video_ref='"+video_ref+"'")
    return deleted

def updateVideoDB(video_ref,video_name,video_comment):
    updated=execute("UPDATE videos SET video_name='"+video_name+"',video_comment='"+video_comment+"' WHERE video_ref='"+video_ref+"'")
    return updated

def searchVideoDB(folderName,email,vname,vdate):
    query="SELECT * FROM videos WHERE user_email='"+email+"'AND folder_name='"+folderName+"'"
    print(vdate)
    if vname:
        query+=" AND video_name iLIKE '%"+vname+"%'"
    if vdate:
        query+=" AND timestamp::date='"+vdate+"'"
        
    data=execute(query)
    if data:
        return data 
    return None