from flask_wtf import FlaskForm
from flask import Flask, render_template, request, session,redirect, url_for,flash
from wtforms import TextField, PasswordField, validators, StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
import database.authdb
import database.uploadsdb
import database.historydb
import hashlib
import os
from decorators import login_required


csrf = CSRFProtect()
UPLOAD_FOLDER = os.path.join(os.getcwd(), r'static/uploads')
ALLOWED_EXTENSIONS = set(['mp4'])

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
    if "email" not in session:
        if "login-submit" in request.form:
            form = Login(request.form)
            
            if request.method == 'POST':
                email=request.form['email']
                password=hashlib.md5(request.form['password'].encode()).hexdigest()
                print(email,password)
            if form.validate_on_submit():
                print(form.errors)
                email_id=database.authdb.login(email,password)
                if email_id:
                    session['email']=email_id  
                    print('Logged in ' + email)
                    return redirect(url_for('index'))
                else:
                    flash('Incorrect email or password!')
            
            return render_template('login.html', loginform=form)
        return render_template('login.html', loginform=None)
    return redirect(url_for('index'))

#Register
@app.route("/register", methods=['GET', 'POST'])
def register():
    if "email" not in session:
        if "register-submit" in request.form:
            form = Register(request.form)
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
                        return redirect(url_for('login'))
                    else:
                        flash('Email Address already registered.')
            
            return render_template('register.html',registerform=form)
        return render_template('register.html',registerform=None)
    return redirect(url_for('index'))
    
#Logut
@app.route('/logout')
@login_required
def logout():
   # remove the email from the session if it is there
   session.pop('email', None)
   return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# My Uploads
@app.route("/uploads", methods=['GET', 'POST'])
@csrf.exempt
@login_required
def uploads():
    openFolder=request.args.get('folder', default = None, type = str)
    openVideo=request.args.get('video', default = None, type = str)
    
    if request.method == 'POST':
        #Manage Folders

        #Create Folder
        if 'createFolder' in request.form:
            fname=request.form['newFolder']
            if fname!="":
                folderAdded=database.uploadsdb.createFolderDB(fname,session['email'])
                if folderAdded:
                    database.historydb.insertHistoryDB(session['email'],'Create','Folder '+fname+' created')
                    flash('Folder '+fname+' created.','success')
                else:
                    flash('Folder '+fname+' already exists.','warning')
            else:
                flash('Folder name cannot be blank','warning')
        
        #Delete Folder
        elif 'deleteFolder' in request.form:
            fname=request.form['deleteFolder']
            deleted=database.uploadsdb.deleteFolderDB(fname,session['email'])
            if deleted:
                database.historydb.insertHistoryDB(session['email'],'Delete','Folder '+fname+' deleted')
                flash('Folder '+fname+' deleted.','danger')
                user_folder=os.path.join(UPLOAD_FOLDER,session['email'])
                if os.path.exists(user_folder):
                    for filename in os.listdir(user_folder):
                        if filename.startswith(fname+"_"):
                            os.remove(os.path.join(user_folder, filename))
            else:
                flash('Folder '+fname+' cannot be deleted.','warning')
        
        # Edit Folder Name
        elif 'editFolder' in request.form:
            fname=request.form['editFolder']
            newfname=request.form['newFolderName']
            updated=database.uploadsdb.updateFolderDB(fname,session['email'],newfname)
            if updated:
                database.historydb.insertHistoryDB(session['email'],'Rename','Folder '+fname+' renamed to '+newfname)
                flash('Folder '+fname+' renamed to '+newfname+'.','success')
            else:
                flash('Folder '+fname+' cannot be renamed.','warning')
        
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
                print(os.path.exists(user_folder))
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                # filename foldername_videoname.extension
                filename = session['email']+'/'+openFolder+"_"+request.form['video-name']+"."+file.filename.split(".")[-1]
                
                # Add video with given details to db and folder
                video={ 'name':request.form['video-name'],
                        'comment':request.form['video-comment'],
                        'ref':filename}
                videoUploaded=database.uploadsdb.uploadVideoDB(video,openFolder,session['email'])
                if videoUploaded:
                    file.save(os.path.join(user_folder, filename.split("/")[1]))
                    msg='Video '+request.form['video-name']+' uploaded in folder '+openFolder+'.'
                    database.historydb.insertHistoryDB(session['email'],'Upload',msg)
                    flash(msg,'success')
                else:
                    flash('Video '+request.form['video-name']+' already exists.','warning')
        
        # Delete single Video
        elif 'deleteVideo' in request.form: 
            video=request.form['deleteVideo'].split("/")[1]
            fname=video.split("_")[0]
            vname=video.split("_")[1].split(".")[0]
            deleted=database.uploadsdb.deleteVideoDB(request.form['deleteVideo'])
            if deleted:
                database.historydb.insertHistoryDB(session['email'],'Delete','Video '+vname+' deleted from '+fname)
                flash('Video '+vname+' deleted from '+fname,'danger')
                if os.path.exists(os.path.join(UPLOAD_FOLDER,request.form['deleteVideo'])):
                    os.remove(os.path.join(UPLOAD_FOLDER,request.form['deleteVideo']))
            else:
                flash('Video '+vname+' cannot be deleted.','warning')

    # Displaying folders and videos content
    folders=database.uploadsdb.getAllFolders(session['email'])
    videos=None
    if openFolder: #if any foldername is found in query
        if folders and (openFolder in [f[0] for f in folders]): # and exists in folders list
            videos=database.uploadsdb.getVideosinFolder(openFolder,session['email']) #Display videos
            if openVideo and videos: #if any videoname is present inquery
                openVideo=[v for v in videos if v[0]==openVideo]
                if len(openVideo)==1: # and exists in video list of given folder
                    openVideo=openVideo[0] #Open Video
                else:
                    openVideo=None
        else:
            openFolder=None
            openVideo=None
    

    return render_template('uploads.html',folders=folders,openFolder=openFolder,videos=videos,openVideo=openVideo)





#History
@app.route("/history", methods=['GET', 'POST'])
@login_required
def history():
    history=database.historydb.getHistory(session['email'])
    historyData={}
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
    return render_template('history.html',history=historyData)

#Detected Vehicles
@app.route("/detected_vehicles", methods=['GET', 'POST'])
@login_required
def detected_vehicles():
    return render_template('detected_vehicles.html')



"""
@app.route("/authenticate", methods=['GET', 'POST'])
def authenticate():
    if "login-submit" in request.form:
        form = Login(request.form)
        print("Login form submitted")
        print(form.errors)
        if request.method == 'POST':
            email=request.form['email']
            password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            # bcrypt.check_password_hash(pw_hash, 'hunter2') 
            print(email,password)
        if form.validate():
            print('Logged in ' + email)
        else:
            flash('All the form fields are required. ')
    
        return render_template('auth.html', loginform=form,registerform=None)
    
    if "register-submit" in request.form:
        form = Register(request.form)
        print("Register form submitted")
        print(form.errors)
        if request.method == 'POST':
            name=request.form['name']
            email=request.form['email']
            password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            confirm_password=bcrypt.generate_password_hash(request.form['confirm-password']).decode('utf-8')
            # bcrypt.check_password_hash(pw_hash, 'hunter2') 
            
            # if form.validate() and password==confirm_password:
            database.authdb.register(name,email,password)
        
    
        return render_template('auth.html',loginform=None, registerform=form)
    return render_template('auth.html',loginform=None, registerform=None)
"""
class Login(FlaskForm):
    email = TextField('Email:', validators=[validators.required()])
    password = PasswordField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
   
class Register(FlaskForm):
    name = TextField('Full Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required()])
    password = PasswordField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
    cpassword = PasswordField('Confirm Password:', validators=[validators.required(), validators.Length(min=3, max=35),
                validators.EqualTo('password', message='Passwords must match')])


if __name__=="__main__":
    app.run(debug=True)