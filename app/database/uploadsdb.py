from database.conn import executeIDU,executeSelect

def getAllFolders(email):
    data=executeSelect("SELECT folder_name FROM folders WHERE user_email='"+email+"'")
    if data:
        return data 
    return None

def createFolderDB(folderName,email):
    created=executeIDU("INSERT INTO folders (folder_name,user_email) values('"+folderName+"','"+email+"')")
    return created

def deleteFolderDB(folderName,email):
    deleted=executeIDU("DELETE FROM folders WHERE folder_name='"+folderName+"' AND user_email='"+email+"'")
    return deleted

def updateFolderDB(folderName,email,newFolderName):
    updated=executeIDU("UPDATE folders SET folder_name='"+newFolderName+"' WHERE folder_name='"+folderName+"' AND user_email='"+email+"'")
    return updated

def getVideosinFolder(folderName,email):
    data=executeSelect("SELECT * FROM videos WHERE user_email='"+email+"' AND folder_name='"+folderName+"'")
    if data:
        return data 
    return None

def uploadVideoDB(video,folderName,email):
    uploaded=executeIDU("INSERT INTO videos (video_name,video_comment,video_ref,folder_name,user_email) \
    values('"+video['name']+"','"+video['comment']+"','"+video['ref']+"','"+folderName+"','"+email+"')")
    return uploaded

def deleteVideoDB(video_ref):
    deleted=executeIDU("DELETE FROM videos WHERE video_ref='"+video_ref+"'")
    return deleted

def updateVideoDB(folderName,email,newFolderName):
    updated=executeIDU("UPDATE folders SET folder_name='"+newFolderName+"' WHERE folder_name='"+folderName+"' AND user_email='"+email+"'")
    return updated