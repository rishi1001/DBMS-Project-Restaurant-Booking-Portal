import os
import psycopg2
from flask import Flask, render_template, session, request, redirect, url_for


app = Flask(__name__)
app.secret_key = 'col362project'

def get_db_connection():
    conn = psycopg2.connect(
    host = "localhost",
    database = "dbname",
    user = "read_only_user",
    password = "password"
    )
    return conn



@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('userid') > 0:
        return redirect(url_for('profile'))
    # conn = get_db_connection()
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM users limit 10;")
    # users = cur.fetchall()

    # for user in users:
    #     print(user)

    # cur.close()
    # conn.close()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['userid'] = -1
        username=request.form['username']
        password=request.form['password']
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
    return render_template('home.html', sess=session)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if session.get('userid') <= 0:
        return redirect(url_for('home'))
    return render_template('profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['userid'] = -1
        username=request.form['username2']
        password=request.form['password2']
        print(username, password)
        if 1 == 1: # authenticate user and register
            session['userid'] = 1
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('register'))
    return render_template('register.html')