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