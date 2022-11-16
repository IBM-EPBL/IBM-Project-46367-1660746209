import sqlite3 as sql

from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for,flash)
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import ibm_db

app= Flask(__name__)
app.config['DEBUG']=True
app.secret_key="mgyftuiu"
connection=ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zpj04244;PWD=xB9fQaRJsweFh5pv","","")

@app.route('/home')
def hello():
     if 'loggedin' in session and 'name' in session:
        return render_template('home.html',msg="TRUE")
     return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/blog")
def blog():
    return "<h1>Hello World from blog page</h1>"

@app.route("/blog/<int:id>")
def blogId(id):
    return "<h1>Hello World from blog page" +str(id)+"</h1>"

@app.route('/about')
def about():
    if 'loggedin' in session and 'name' in session:
        return render_template('about.html')
    return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/adduser',methods= ['POST','GET'])
def adduser():
    message=""
    if request.method=='POST':
        try:
            name= request.form['username']
            mail= request.form['mail']
            mobile= request.form['mobile']
            password= request.form['password']

           
            sql = "SELECT * FROM ACCOUNT WHERE USERNAME =?"
            stmt = ibm_db.prepare(connection, sql)
            ibm_db.bind_param(stmt,1,name)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)

            if account:
                return render_template('list.html', msg="Account Already Exists")
            else:
                command="INSERT INTO ACCOUNT (USERNAME,EMAIL,PHONENO,PASSWORD) VALUES (?,?,?,?)"
                prep_stmt = ibm_db.prepare(connection, command)
                ibm_db.bind_param(prep_stmt, 1, name)
                ibm_db.bind_param(prep_stmt, 2, mail)
                ibm_db.bind_param(prep_stmt, 3, mobile)
                ibm_db.bind_param(prep_stmt, 4, password)
                ibm_db.execute(prep_stmt)
                return render_template('login.html', msg="TRUE")

        except:
            con.rollback()
            message="error"
            return render_template("signup.html",error="TRUE")
   

@app.route("/check", methods=['POST','GET'])
def check():
    msg=""
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']

        account=""
        try:

            command= "SELECT * FROM ACCOUNT WHERE USERNAME =? AND PASSWORD =?"
            stmt=ibm_db.prepare(connection,command)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, password)
            ibm_db.execute(stmt)
            result = ibm_db.fetch_assoc(stmt)
            while result !=False:
                account=result['USERNAME']
                result = ibm_db.fetch_assoc(stmt)
            if account:
                session['loggedin'] = True
                session['name'] = account
                return redirect(url_for('hello'))
            else:
                msg = "Incorrect username/password!"
                return render_template('login.html', msg=msg)
        except:
            return render_template('login.html', msg="Account not found")


        #return render_template("list.html",rows=rows)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('name', None)
   return redirect(url_for('login'))

if __name__=='__main__':
    app.run()
