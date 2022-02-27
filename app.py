import os
import psycopg2
import bcrypt
from flask import Flask, render_template, session, request, redirect, url_for, g


app = Flask(__name__)
app.secret_key = 'col362project'

def get_db_connection():
    conn = psycopg2.connect(host = "localhost", database = "col362project", user = "postgres", password = "")
    return conn

def reset_errors():
    session['error'] = 0
    session['login_user_username_err'] = 0
    session['login_user_password_err'] = 0
    session['login_rest_username_err'] = 0
    session['login_rest_password_err'] = 0
    session['reg_user_username_err'] = 0
    session['reg_user_password_err'] = 0
    session['reg_rest_username_err'] = 0
    session['reg_rest_password_err'] = 0

@app.before_request
def before_request():
    if 'userid' not in session:
        session['userid'] = -1
        session['restid'] = -1
        reset_errors()
        

@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('userid') > 0 or session.get('restid') > 0:
        return redirect(url_for('profile'))

    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form['type_'] == '0':
        reset_errors()
        session['userid'] = -1
        session['restid'] = -1
        username=request.form['username1']
        password=request.form['password1']
        if len(username) == 0 or len(username.replace(' ', '')) == 0 or not username.replace(' ', '').isalnum():
            session['error'] = 1
            session['login_user_username_err'] = 1
            return redirect(url_for('login'))
        if len(password) == 0 or ' ' in password or not password.isalnum():
            session['error'] = 1
            session['login_user_password_err'] = 1
            return redirect(url_for('login'))
        # Check if username is already present in the table
        conn = get_db_connection()
        cur = conn.cursor()
        q1 = """SELECT * FROM user_login WHERE username = %s"""
        t1 = (username,)
        cur.execute(q1,t1)
        credentials = cur.fetchall()

        if (len(credentials) == 0):
            # User does not exist, currently redirecting to registration
            session['error'] = 1
            session['login_user_username_err'] = 1
            return redirect(url_for('login'))

        else:
            # Check if passwords match
            hash_ = credentials[0][2].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'),hash_):
                # passwords match, login and authenticate the user
                session['userid'] = int(credentials[0][0])
                return redirect(url_for('profile'))

            else:
                session['error'] = 1
                session['login_user_password_err'] = 1
                return redirect(url_for('login'))
    elif request.method == 'POST' and request.form['type_'] == '1':
        reset_errors()
        session['restid'] = -1
        session['userid'] = -1
        username=request.form['username2']
        password=request.form['password2']
        if len(username) == 0 or len(username.replace(' ', '')) == 0 or not username.replace(' ', '').isalnum():
            session['error'] = 1
            session['login_rest_username_err'] = 1
            return redirect(url_for('login'))
        if len(password) == 0 or ' ' in password or not password.isalnum():
            session['error'] = 1
            session['login_rest_password_err'] = 1
            return redirect(url_for('login'))
        # Check if username is already present in the table
        conn = get_db_connection()
        cur = conn.cursor()
        q1 = """SELECT * FROM restaurant_login WHERE username = %s"""
        t1 = (username,)
        cur.execute(q1,t1)
        credentials = cur.fetchall()

        if (len(credentials) == 0):
            # User does not exist, currently redirecting to registration
            session['error'] = 1
            session['login_rest_username_err'] = 1
            return redirect(url_for('login'))

        else:
            # Check if passwords match
            hash_ = credentials[0][2].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'),hash_):
                # passwords match, login and authenticate the user
                session['restid'] = int(credentials[0][0])
                return redirect(url_for('restprofile'))

            else:
                session['error'] = 1
                session['login_rest_password_err'] = 1
                return redirect(url_for('login'))
    return render_template('login.html', sess=session)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['userid'] = -1
    session['restid'] = -1
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', sess=session)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if session.get('userid') <= 0:
        return redirect(url_for('home'))
    if request.method=="POST":
        # how to know if user has actually selected it ?
        cost = int(request.form['cost'])
        if cost==0:
            costlow = 0
            costhigh = 5000
        elif cost==1:
            costlow = 5000
            costhigh = 10000
        else:
            costlow = 10000
            costhigh = 999999999
        rating = int(request.form['rating'])
        cuisine = request.form['cuisine']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT cuisineid FROM cuisinesref WHERE name = %s",(cuisine,))
        cuisineid = cur.fetchall()[0][0]
        print(type(cost),rating,cuisineid,cuisine)
        q1 = "SELECT name,url FROM restaurants,cuisines WHERE costfortwo<%s and costfortwo>=%s and rating < %s and rating>=%s and restaurants.restaurantid = cuisines.restaurantid and cuisines.cuisineid = %s  limit 10;"
        cur.execute(q1,(costhigh,costlow,rating+1,rating,cuisineid)) 
        restaurants = cur.fetchall()
        return render_template('profile.html', restaurants = restaurants)
    # return render_template('profile.html')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name,url FROM restaurants limit 10;")
    restaurants = cur.fetchall()
    cur.execute("SELECT name FROM cuisinesref")
    cuisines = cur.fetchall()
    return render_template('profile.html', restaurants = restaurants, cuisines = cuisines)

@app.route('/restprofile', methods=['GET', 'POST'])
def restprofile():
    if session.get('restid') <= 0:
        return redirect(url_for('home'))
    return render_template('restprofile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and request.form['type_'] == '0':
        reset_errors()
        session['userid'] = -1
        session['restid'] = -1
        username=request.form['username3']
        password=request.form['password3']
        if len(username) == 0 or len(username.replace(' ', '')) == 0 or not username.replace(' ', '').isalnum():
            session['error'] = 1
            session['reg_user_username_err'] = 1
            return redirect(url_for('register'))
        if len(password) == 0 or ' ' in password or not password.isalnum():
            session['error'] = 1
            session['reg_user_password_err'] = 1
            return redirect(url_for('register'))
        hash_ = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hash_ = hash_.decode('utf8')
        # Now, establish a connection to the database and put the username and password in login_info
        conn = get_db_connection()
        cur = conn.cursor()
        q1 = """SELECT * FROM user_login WHERE username = %s"""
        t1 = (username,)
        cur.execute(q1,t1)
        if len(cur.fetchall()) > 0:
            session['error'] = 1
            session['reg_user_username_err'] = 1
            return redirect(url_for('register'))
        cur.execute("SELECT userid FROM user_login ORDER BY userid DESC limit 1;")
        last_id = cur.fetchall()

        if (len(last_id) == 0): # This is the first user
            tuple1 = (username,hash_)
            query1 = """INSERT INTO user_login VALUES (1,%s,%s)"""
            cur.execute(query1,tuple1)
            conn.commit()
            session['userid'] = 1

        else:
            session['userid'] = int(last_id[0][0])+1
            tuple1 = (str(int(last_id[0][0])+1),username,hash_)
            query1 = """INSERT INTO user_login VALUES (%s,%s,%s)"""
            cur.execute(query1,tuple1)
            conn.commit()
        return redirect(url_for('profile'))
    elif request.method == 'POST' and request.form['type_'] == '1':
        reset_errors()
        session['userid'] = -1
        session['restid'] = -1
        username=request.form['username4']
        password=request.form['password4']
        location = request.form['location']
        category = request.form.get('category')
        onlineorder = request.form['onlineorder']
        costfortwo = request.form['costfortwo']
        url = request.form['urll']
        address = request.form['address']
        phonenum = request.form['phonenum']
        typerest = request.form.get('type')
        if len(username) == 0 or len(username.replace(' ', '')) == 0 or not username.replace(' ', '').isalnum():
            session['error'] = 1
            session['reg_rest_username_err'] = 1
            return redirect(url_for('register'))
        if len(password) == 0 or ' ' in password or not password.isalnum():
            session['error'] = 1
            session['reg_rest_password_err'] = 1
            return redirect(url_for('register'))
        hash_ = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hash_ = hash_.decode('utf8')
        # Now, establish a connection to the database and put the username and password in login_info
        conn = get_db_connection()
        cur = conn.cursor()
        q1 = """SELECT * FROM restaurant_login WHERE username = %s"""
        t1 = (username,)
        cur.execute(q1,t1)
        if len(cur.fetchall()) > 0:
            session['error'] = 1
            session['reg_rest_username_err'] = 1
            return redirect(url_for('register'))
        cur.execute("SELECT restaurantid FROM restaurant_login ORDER BY restaurantid DESC limit 1;")
        last_id = cur.fetchall()
        restaurantid = 1
        if (len(last_id) == 0): # This is the first user
            tuple1 = (username,hash_)
            query1 = """INSERT INTO restaurant_login VALUES (1,%s,%s)"""
            cur.execute(query1,tuple1)
            conn.commit()
            session['restid'] = 1

        else:
            restaurantid = int(last_id[0][0])+1
            session['restid'] = int(last_id[0][0])+1
            tuple1 = (str(int(last_id[0][0])+1),username,hash_)
            query1 = """INSERT INTO restaurant_login VALUES (%s,%s,%s)"""
            cur.execute(query1,tuple1)
            conn.commit()
        # In locationref, check if location is present, and if not, add a new location to locationref.
        # Insert rid,locationid,listedid,onlineorder,0,0,costfortwo,username,url,address to restaurants (commit)
        # insert rid,phone in phones
        # Insert restaurantid, typeid (select from dropdown)
        q1 = """SELECT locationid FROM locationref WHERE name = %s"""
        t1 = (location,)
        cur.execute(q1,t1)
        locid = cur.fetchall()
        locationid = 0 # To be inserted to table 
        if (len(locid) == 0):
            # This is a new location
            cur.execute("SELECT locationid FROM locationref ORDER BY locationid DESC limit 1;")
            last_id = cur.fetchall()
            if (len(last_id) == 0):
                locationid = 1
            else:
                locationid = int(last_id[0][0])+1
            q1 = """INSERT INTO locationref VALUES (%s,%s)"""
            t1 = (locationid,location)
            cur.execute(q1,t1)
            conn.commit() # as inserted a new location
        else:
            # location already exists
            locationid = int(locid[0][0])
        # presently, not added any checks for the added new fields
        # obtain listedid also
        q1 = """SELECT listedid FROM listedref WHERE name = %s"""
        t1 = (category,)
        cur.execute(q1,t1)
        print(category)
        listedid = (cur.fetchall())[0][0]
        # obtain restaurantid
        q1 ="""INSERT INTO restaurants VALUES(%s,%s,%s,%s,0,0,%s,%s,%s,%s)"""
        t1 = (restaurantid,locationid,listedid,onlineorder,costfortwo,username,url,address)
        cur.execute(q1,t1)
        conn.commit()
        q1 = """INSERT INTO phones VALUES(%s,%s)"""
        t1 = (restaurantid,phonenum)
        cur.execute(q1,t1)
        conn.commit()
        # obtain typeid
        q1 = """SELECT typeid FROM typesref WHERE name = %s"""
        t1 = (typerest,)
        cur.execute(q1,t1)
        typeid = (cur.fetchall())[0][0]

        q1 = """INSERT INTO types VALUES(%s,%s)"""
        t1 = (restaurantid,typeid)
        cur.execute(q1,t1)
        conn.commit()

        # Need to check if results have actually been commited
        cur.execute("""SELECT * from restaurants ORDER BY restaurantid DESC limit 1""")
        print(cur.fetchall())
        cur.execute("""SELECT * from types ORDER BY restaurantid DESC limit 1""")
        print(cur.fetchall())
        cur.execute("""SELECT * from phones ORDER BY restaurantid DESC limit 1""")
        print(cur.fetchall())
        cur.execute("""SELECT * from locationref ORDER BY locationid DESC limit 1""")
        print(cur.fetchall())
        return redirect(url_for('restprofile'))
    # Implement drop down list
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT name FROM listedref""")
    categorylist = cur.fetchall()
    cur.execute("""SELECT name from typesref""")
    typelist = cur.fetchall()
    return render_template('register.html', sess=session, categorylist= categorylist, typelist = typelist)