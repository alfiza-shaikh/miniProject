from flask_wtf import FlaskForm
from flask import Flask, render_template, request, session,redirect, url_for,flash
from wtforms import TextField, PasswordField, validators, StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
import database.authdb
import database.uploadsdb
import database.historydb
import hashlib
from decorators import login_required


csrf = CSRFProtect()

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

# My Uploads
@app.route("/uploads", methods=['GET', 'POST'])
@csrf.exempt
@login_required
def uploads():
    if request.method == 'POST':
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
        if 'deleteFolder' in request.form:
            fname=request.form['deleteFolder']
            deleted=database.uploadsdb.deleteFolderDB(fname,session['email'])
            if deleted:
                database.historydb.insertHistoryDB(session['email'],'Delete','Folder '+fname+' deleted')
                flash('Folder '+fname+' deleted.','danger')
            else:
                flash('Folder '+fname+' cannot be deleted.','warning')
        if 'editFolder' in request.form:
            fname=request.form['editFolder']
            newfname=request.form['newFolderName']
            updated=database.uploadsdb.updateFolderDB(fname,session['email'],newfname)
            if updated:
                database.historydb.insertHistoryDB(session['email'],'Rename','Folder '+fname+' renamed to '+newfname)
                flash('Folder '+fname+' renamed to '+newfname+'.','success')
            else:
                flash('Folder '+fname+' cannot be renamed.','warning')
    folders=database.uploadsdb.getAllFolders(session['email'])
    return render_template('uploads.html',folders=folders)





#History
@app.route("/history", methods=['GET', 'POST'])
@login_required
def history():
    history=database.historydb.getHistory(session['email'])
    historyData={}
    print(history)
    for h in history:
        listH=list(h)
        listH[1]=h[1]
        listH[2]=h[3].strftime("%I:%M %p")
        date=h[3].strftime("%d %B, %Y")
        print(date)
        if date in historyData:
            historyData[date].append(listH[:3])
        else:
            historyData[date]=[listH[:3]]
    print(historyData)
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