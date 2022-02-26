import os
import psycopg2
import bcrypt
from flask import Flask, render_template, session, request, redirect, url_for, g


app = Flask(__name__)
app.secret_key = 'col362project'

def get_db_connection():
    conn = psycopg2.connect(
    host = "localhost",
    database = "col362project",
    user = "postgres",
    password = "your_password"
    )
    return conn



@app.route('/', methods=['GET', 'POST'])
def index():
    if 'userid' not in session:
        session['userid'] = -1
    if session.get('userid') > 0:
        return redirect(url_for('profile'))

    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'userid' not in session:
        session['userid'] = -1
    if request.method == 'POST':
        session['userid'] = -1
        username=request.form['username']
        password=request.form['password']
        hash_ = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) # To generate hash
        if bcrypt.checkpw(password.encode('utf-8'), hash_): # To compare hash with unhashed if same
            print(hash_)
        print(username, password)
        if 1 == 1: # authenticate user
            session['userid'] = 1
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['userid'] = -1
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'userid' not in session:
        session['userid'] = -1
    return render_template('home.html', sess=session)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'userid' not in session:
        session['userid'] = -1
    if session.get('userid') <= 0:
        return redirect(url_for('home'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name,url FROM restaurants limit 10;")
    restaurants = cur.fetchall()
    return render_template('profile.html', restaurants = restaurants)

@app.route('/register', methods=['GET', 'POST'])
def register():

    if 'userid' not in session:
        session['userid'] = -1
    if request.method == 'POST':
        session['userid'] = -1
        username=request.form['username2']
        password=request.form['password2']
        hash_ = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Now, establish a connection to the database and put the username and password in login_info
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT userid FROM login_info ORDER BY userid DESC limit 1;")
        last_id = cur.fetchall()
        if (len(last_id) == 0): # This is the first user
            tuple1 = (username,hash_)
            query1 = """INSERT INTO login_info VALUES (1,%s,%s)"""
            cur.execute(query1,tuple1)
            conn.commit()

        else:
            tuple1 = (str(int(last_id[0][0])+1),username,hash_)
            query1 = """INSERT INTO login_info VALUES (%s,%s,%s)"""
            cur.execute(query1,tuple1)
            conn.commit()

        # Check if insertion has actually happened in the database

        cur.close()
        conn.close()

        if 1 == 1: # authenticate user and register
            session['userid'] = 1
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('register'))
    return render_template('register.html')