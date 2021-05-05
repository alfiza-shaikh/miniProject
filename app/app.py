from flask_wtf import FlaskForm
from flask import Flask, render_template, request, session,redirect, url_for,flash
from flask import Markup
from wtforms import TextField, PasswordField, validators, StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
import database.authdb
import database.uploadsdb
import database.historydb
import database.detectedvehiclesdb
import hashlib
import os
import time
import datetime
import re
from decorators import login_required
import detection_model.detect_video as detection



csrf = CSRFProtect()
UPLOAD_FOLDER = os.path.join(os.getcwd(), r'static/uploads')
ALLOWED_EXTENSIONS = set(['mp4'])
FOLDER_VIDEO_NAME_REGEX="^[A-Za-z0-9_ -]*$"
app = Flask(__name__) 
app.secret_key = 'your secret key'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True


csrf.init_app(app)

#Home
@app.route('/') 
def index():
    return render_template('index.html')

#Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login(request.form)
    if "email" not in session:
        if "login-submit" in request.form:
            if request.method == 'POST':
                email=request.form['email']
                password=hashlib.md5(request.form['password'].encode()).hexdigest()
                next_url = request.form.get("next")
                print(email,password)
            if form.validate_on_submit():
                print(form.errors)
                user=database.authdb.login(email,password)
                if user:
                    session['email']=user[2]
                    session['name']=user[1]   
                    # print('Logged in ' + email)
                    if next_url:
                        return redirect(next_url)
                    return redirect(url_for('index'))
                else:
                    flash('Incorrect email or password!')
            
            return render_template('login.html', loginform=form)
        return render_template('login.html', loginform=form)
    return redirect(url_for('index'))

#Register
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = Register(request.form)
    if "email" not in session:
        if "register-submit" in request.form:
            
            if request.method == 'POST':
                name=request.form['name']
                email=request.form['email']
                password=hashlib.md5(request.form['password'].encode()).hexdigest()
                confirm_password=hashlib.md5(request.form['cpassword'].encode()).hexdigest()
                print(email,name)
                if form.validate_on_submit():
                    print("register form")
                    print(form.errors)
                    registered=database.authdb.register(name,email,password)
                    if registered:
                        flash('Registration Successful. Please Login to continue','registered')
                        return redirect(url_for('login'))
                    else:
                        flash('User already exists.')
            
            return render_template('register.html',registerform=form)
        return render_template('register.html',registerform=form)
    return redirect(url_for('index'))
    
#Logut
@app.route('/logout')
@login_required
def logout():
   # remove the email from the session if it is there
   session.pop('email', None)
   session.pop('name', None)
   return redirect(url_for('index'))



# Functions for uploads page
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def createFolder(fname):
    fname=fname.strip()
    if fname!=""  and len(fname)>=3 and len(fname)<=20:
        folderAdded=database.uploadsdb.createFolderDB(fname,session['email'])
        if folderAdded:
            database.historydb.insertHistoryDB(session['email'],'Create','Folder '+fname+' created')
            flash('Folder '+fname+' created.','success')
        else:
            flash('Folder '+fname+' already exists.','warning')
    else:
        flash('Length of folder name should be between 3 and 20 characters long.','warning')

def deleteFolder(fname):
    videosinFolder=database.uploadsdb.getVideosinFolder(fname,session['email'])
    deleted=database.uploadsdb.deleteFolderDB(fname,session['email'])
    if deleted:
        database.historydb.insertHistoryDB(session['email'],'Delete','Folder '+fname+' deleted')
        flash('Folder '+fname+' deleted.','danger')
        user_folder=os.path.join(UPLOAD_FOLDER,session['email'])
        if os.path.exists(user_folder) and videosinFolder:
            for video in videosinFolder:
                if os.path.exists(os.path.join(user_folder, video[2])):
                    os.remove(os.path.join(user_folder, video[2]))
    else:
        flash('Folder '+fname+' cannot be deleted.','warning')

def editFolder(fname,newfname):
    newfname=newfname.strip()
    matched= bool(re.match(FOLDER_VIDEO_NAME_REGEX, newfname))
    if newfname!="" and len(newfname)>=3 and len(newfname)<=20 and matched:
        updated=database.uploadsdb.updateFolderDB(fname,session['email'],newfname)
        if updated:
            database.historydb.insertHistoryDB(session['email'],'Rename','Folder '+fname+' renamed to '+newfname)
            flash('Folder '+fname+' renamed to '+newfname+'.','success')
        else:
            flash('Folder '+fname+' cannot be renamed.','warning')
    else:
        if matched:
            flash('Length of folder name should be between 3 and 20 characters long.','warning') 
        else:
            flash('Only alphabets, numbers, spaces, hiphens and underscores allowed.','warning')


def deleteVideo(videoref):
    video=database.uploadsdb.getVideoFromRef(videoref)
    if video:
        deleted=database.uploadsdb.deleteVideoDB(videoref)
        if deleted:
            database.historydb.insertHistoryDB(session['email'],'Delete','Video '+video[0]+' deleted from '+video[4])
            flash('Video '+video[0]+' deleted from '+video[4],'danger')
            user_folder=os.path.join(UPLOAD_FOLDER, session['email'])
            if os.path.exists(os.path.join(user_folder,videoref)):
                os.remove(os.path.join(user_folder,videoref))
        else:
            flash('Video '+video[0]+' cannot be deleted.','warning')


# My Uploads
@app.route("/uploads", methods=['GET', 'POST'])
@csrf.exempt
@login_required
def uploads():
    openFolder=request.args.get('folder', default = None, type = str)
    openVideo=request.args.get('video', default = None, type = str)
    folder_search=None
    video_search=None
    if request.method == 'POST':
        #Manage Folders
        #Create Folder            
        if 'createFolder' in request.form:
            createFolder(request.form['newFolder'])
        #Delete Folder
        elif 'deleteFolder' in request.form:
            deleteFolder(request.form['deleteFolder'])
        # Edit Folder Name
        elif 'editFolder' in request.form:
            fname=request.form['editFolder']
            newfname=request.form['newFolderName']
            editFolder(fname,newfname)
        
        # Manage Videos
        # Upload Video
        elif openFolder and 'uploadVideo' in request.form:    
            #Video Upload
            if 'video' not in request.files:
                flash('No file uploaded')
                return redirect(request.url)
            file = request.files['video']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            # If file is of valid type
            if file and allowed_file(file.filename):
                # create a folder in static/uploads/ named 'email of user'
                user_folder=os.path.join(UPLOAD_FOLDER, session['email'])
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                # filename foldername_videoname.extension
                # filename = session['email']+'/'+openFolder+"_"+request.form['video-name']+"."+file.filename.split(".")[-1]
                filename = str(time.time()).replace('.', '')+"."+file.filename.split(".")[-1]
                # Add video with given details to db and folder
                video={ 'name':request.form['video-name'],
                        'comment':request.form['video-comment'],
                        'ref':filename}
                videoUploaded=database.uploadsdb.uploadVideoDB(video,openFolder,session['email'])
                print("Video Uploaded")
                if videoUploaded:
                    video_path=os.path.join(user_folder, filename)
                    file.save(video_path)
                    msg='Video '+request.form['video-name']+' uploaded in folder '+openFolder+'.'
                    database.historydb.insertHistoryDB(session['email'],'Upload',msg)
                    flash(msg,'success')
                    detection.main(video_path)
                else:
                    flash('Video '+request.form['video-name']+' already exists.','warning')
            else:
                flash('Invalid file type! Allowed file type is .mp4','warning')
        
        # Delete single Video
        elif 'deleteVideo' in request.form: 
            videoref=request.form['deleteVideo']
            deleteVideo(videoref)
            
        # delete multiple videos
        elif 'deleteVideos' in request.form: 
            # print(request.form.getlist('selectedVideos'))
            for videoref in request.form.getlist('selectedVideos'):
                deleteVideo(videoref)
        
        elif 'editVideo' in request.form:
            videoref=request.form['editVideo']
            oldvideo=database.uploadsdb.getVideoFromRef(videoref)
            new_vn=request.form['new-video-name']
            new_vc=request.form['new-video-comment']
            videoUpdated=database.uploadsdb.updateVideoDB(videoref,new_vn,new_vc)
            if videoUpdated:
                if new_vn!=oldvideo[0]:
                    msg='Video '+oldvideo[0]+' renamed to '+new_vn+' in folder '+openFolder+'.'
                    database.historydb.insertHistoryDB(session['email'],'Rename',msg)
                else:
                    msg='Video details updated'
                flash(msg,'success')
            else:
                flash('Video details not updated.','warning')
        # Detect Vehicles
        elif 'detectVehicles' in request.form:
            for videoref in request.form.getlist('selectedVideos'):
                print(videoref)
            # Redirect to detected vehicles
            # Pass videos and use POST (code = 307 tells the browser to preserve the used HTTP method )
            return redirect(url_for('detected_vehicles',videos=request.form.getlist('selectedVideos')))
        
        if 'searchFolder' in request.form:
            folder_search=request.form['sfolder']
        # if 'searchVideos' in request.form:
        #     video_search=request.form['svideo']
        #     video_date=request.form['videodate']
            

    # Displaying folders and videos content
    if folder_search:
        folders=database.uploadsdb.searchFolderDB(folder_search,session['email'])
    else:
        folders=database.uploadsdb.getAllFolders(session['email'])

    videos=None
    if openFolder: #if any foldername is found in query
        if folders and (openFolder in [f[0] for f in folders]): # and exists in folders list
            #Display videos
            if request.method == 'POST' and 'searchVideos' in request.form:
                video_search=request.form['svideo']
                video_date=request.form['videodate']
                today=datetime.date.today().strftime("%Y-%m-%d")
                if video_date and video_date>today:
                    flash("Date exceeds today's date",'warning')
                videos=database.uploadsdb.searchVideoDB(openFolder,session['email'],video_search,video_date)
            else:
                videos=database.uploadsdb.getVideosinFolder(openFolder,session['email']) 
            if openVideo and videos: #if any videoname is present in query
                openVideo=[v for v in videos if v[0]==openVideo]
                if len(openVideo)==1: # and exists in video list of given folder
                    openVideo=openVideo[0] #Open Video
                else:
                    openVideo=None
            else:
                openVideo=None
        else:
            openFolder=None
            openVideo=None

    return render_template('uploads.html',folders=folders,openFolder=openFolder,videos=videos,openVideo=openVideo)





#History
@app.route("/history", methods=['GET', 'POST'])
@csrf.exempt
@login_required
def history():
    history=database.historydb.getHistory(session['email'])
    historyData={}
    dates={'fromdate':'','todate':''}
    if request.method == 'POST':
        today=datetime.date.today().strftime("%Y-%m-%d")
        if request.form['fromdate'] and request.form['todate'] and request.form['fromdate']>request.form['todate']:
            flash("From Date should be before or same as To Date")
        elif (request.form['fromdate'] and request.form['fromdate']>today) or\
        (request.form['todate'] and request.form['todate']>today):
            flash("Date should not exceed today's date")
        else:
            dates['fromdate']=request.form['fromdate']
            dates['todate']=request.form['todate']
            history=database.historydb.getHistoryFiltered(session['email'],request.form['fromdate'],request.form['todate'])
    if history:
        for h in history:
            listH=list(h)
            listH[1]=h[1]
            listH[2]=h[3].strftime("%I:%M %p")
            date=h[3].strftime("%d %B, %Y")
            if date in historyData:
                historyData[date].append(listH[:3])
            else:
                historyData[date]=[listH[:3]]
    return render_template('history.html',history=historyData,dates=dates)

@app.template_filter('convert_time')
def convert_time(seconds): 
    hours=seconds//(60*60)
    seconds%=(60*60)
    minutes=seconds//60
    seconds%=60
    time=""
    if hours!=0:
        time=str(hours)+"hr "
    if minutes!=0:
        time=str(minutes)+"min "
    time=str(seconds)+"s "

    return time

#Detected Vehicles
@app.route("/detected_vehicles", methods=['GET', 'POST'])
@csrf.exempt
@login_required
def detected_vehicles():
    videos=request.args.getlist('videos')  
    if not videos:
        flash(Markup('Select video(s) first. Go to <a href="uploads">Uploads page</a>.'))
    filters={'From Date':'',"To Date":'',"From Time":'',"To Time":'',
    "Vehicle Number":'',"Vehicle Type":'',"Color":''}
    if request.method == 'POST':
        # prevfilters=request.form['filters']
        # print(prevfilters)
        # today=datetime.date.today().strftime("%Y-%m-%d")
        # if request.form['fromtime'] and request.form['totime'] and request.form['fromtime']>request.form['totime']:
        #     flash("From Time should be before or same as To Time")
        # elif (request.form['fromdate'] and request.form['fromdate']>today) or\
        # (request.form['todate'] and request.form['todate']>today):
        #     flash("Date should not exceed today's date")
        # else:
        #     filters['From Time']=request.form['fromtime']
        #     filters['To Time']=request.form['totime']
        # if request.form['fromtime']:
        #     filters['From Time']=request.form['fromtime']
        # if request.form['totime']:
        #     filters['To Time']=request.form['totime']
        if request.form['vehiclenumber']:
            filters['Vehicle Number']=request.form['vehiclenumber']
        if request.form['vehicles']:
            filters['Vehicle Type']=request.form['vehicles']
        # if request.form['color']:
        #     filters['Color']=request.form['color']
        if request.form.get("deleteFilter"):
            filters[request.form['deleteFilter']]=""

    d_vehicles=database.detectedvehiclesdb.getDVFiltered(videos,filters)

    return render_template('detected_vehicles.html',vehiclesList=['Ambulance','Bus','Car','Motorcycle','Truck'],filters=filters,detected_vehicles=d_vehicles)


class Login(FlaskForm):
    email = StringField(label=('Email:'), validators=[validators.DataRequired(),validators.Email(),
     validators.Length(max=120)])
    password = PasswordField(label=('Password:'), validators=[validators.DataRequired(),
     validators.Length(min=3, max=35,message="Password should be between %(min)d and %(max)d characters long")])
   
class Register(FlaskForm):
    name = TextField('Full Name:', validators=[validators.required(), validators.Length(min=3, max=120),
    validators.Regexp("^[a-zA-Z\\s]*$", message="Name can contain only alphabets and spaces")])
    email = TextField('Email:', validators=[validators.DataRequired(), validators.Email(),
     validators.Length(max=120)])
    password = PasswordField('Password:', validators=[validators.required(),
     validators.Length(min=3, max=35,message="Password should be between %(min)d and %(max)d characters long")])
    cpassword = PasswordField('Confirm Password:', validators=[validators.required(), 
        validators.Length(min=3, max=35,message="Password should be between %(min)d and %(max)d characters long"),
                validators.EqualTo('password', message='Passwords must match')])


if __name__=="__main__":
    app.run(debug=True)