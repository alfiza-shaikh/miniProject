from flask_wtf import FlaskForm
from flask import Flask, render_template, request, session,redirect, url_for,flash
from wtforms import TextField, PasswordField, validators, StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
import database.authdb
import hashlib


csrf = CSRFProtect()

app = Flask(__name__) 
app.secret_key = 'your secret key'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True


csrf.init_app(app)


@app.route('/') 
def index():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if "name" not in session:
        if "login-submit" in request.form:
            form = Login(request.form)
            
            if request.method == 'POST':
                email=request.form['email']
                password=hashlib.md5(request.form['password'].encode()).hexdigest()
                print(email,password)
            if form.validate_on_submit():
                print(form.errors)
                name=database.authdb.login(email,password)
                if name:
                    session['name']=name   
                    print('Logged in ' + email)
                    return redirect(url_for('index'))
                else:
                    flash('Incorrect email or password!')
            
            return render_template('login.html', loginform=form)
        return render_template('login.html', loginform=None)
    return redirect(url_for('index'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if "name" not in session:
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
    

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('name', None)
   return redirect(url_for('index'))

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