from flask import Flask, render_template, request, redirect, url_for,flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
import database.authdb


csrf = CSRFProtect()

app = Flask(__name__) 
app.secret_key = 'your secret key'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True


csrf.init_app(app)
bcrypt = Bcrypt(app)

@app.route('/') 
def index():
    return render_template('index.html')

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
        #     print(name,email,password)
            database.authdb.register(name,email,password)
        
    
        return render_template('auth.html',loginform=None, registerform=form)
    return render_template('auth.html',loginform=None, registerform=None)

class Login(Form):
    email = TextField('Email:', validators=[validators.required(), validators.Length(min=6, max=35)])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
   
class Register(Form):
    name = TextField('Full Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required(), validators.Length(min=6, max=35)])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
    cpassword = TextField('Confirm Password:', validators=[validators.required(), validators.Length(min=3, max=35)])


if __name__=="__main__":
    app.run(debug=True)