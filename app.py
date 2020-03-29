from flask import Flask, render_template, request, redirect, session, flash
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import yaml
app = Flask(__name__)
Bootstrap(app)
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24)



@app.route('/')
def index():
    return render_template('index.html')
@app.route('/about/')
def about():
    return render_template('about.html')
@app.route('/news/<int:id>/')
def news(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM news WHERE news_id = {}".format(id))
    if resultValue > 0:
        new = cur.fetchone()
        return render_template('news.html', new=new)
    return 'Blog not found'

@app.route('/my_news/')
def my_news():
    author = session['firstname'] + ' ' + session['lastname']
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM news WHERE author = %s",[author])
    if result_value > 0:
        my_news = cur.fetchall()
        return render_template('my_news.html',my_news=my_news)
    else:
        return render_template('my_news.html',my_news=None)
@app.route('/write_news/',methods=['GET', 'POST'])
def write_news():
    if request.method == 'POST':
        newspost = request.form
        title = newspost['title']
        body = newspost['body']
        author = session['firstname'] + ' ' + session['lastname']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO news(title, body, author) VALUES(%s, %s, %s)", (title, body, author))
        mysql.connection.commit()
        cur.close()
        flash("Successfully posted new blog", 'success')
        return redirect('/my_news')
    return render_template('write_news.html')
@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method =='POST':
        userDetails=request.form
        username=userDetails['username']
        cur=mysql.connection.cursor()
        resultValue=cur.execute("select * from user where username=%s",([username]))
        if resultValue>0:
            user=cur.fetchone()
            if check_password_hash(user['password'], userDetails['password']):
                session['login']=True
                session['firstname']=user['first_name']
                session['lastname']=user['last_name']
                flash('Welcome '+ session['firstname']+'! You are logged in','success')
            else:
                cur.close()
                flash('Password does not match','danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found','danger')
            return render_template('login.html')
        cur.close()
        return redirect('/my_news')
    return render_template('login.html')
@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method =='POST':
        userDetails=request.form
        if userDetails['password']!=userDetails['confirm_password']:
            flash("Passwords do not match! Try Again.","danger")
            return render_template("register.html")
        cur=mysql.connection.cursor()
        cur.execute("insert into user(first_name, last_name, username, email, password)"\
        "values(%s,%s,%s,%s,%s)",(userDetails['first_name'],userDetails['last_name'],\
        userDetails['username'],userDetails['email'],generate_password_hash(userDetails['password'])))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please login.','success')
        return redirect('/login')
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
