import os
import psycopg2
import bcrypt
from flask import Flask, render_template, session, request, redirect, url_for, g


app = Flask(__name__)
app.secret_key = 'col362project'

def get_db_connection():
    conn = psycopg2.connect(host = "localhost", database = "col362project", user = "postgres", password = "")
    conn.autocommit = True
    return conn

def reset_errors():
    session['error'] = 0
    session['saved'] = 0
    session['login_user_username_err'] = 0
    session['login_user_password_err'] = 0
    session['login_rest_username_err'] = 0
    session['login_rest_password_err'] = 0
    session['reg_user_username_err'] = 0
    session['reg_user_password_err'] = 0
    session['reg_rest_username_err'] = 0
    session['reg_rest_password_err'] = 0
    session['edit_phone_rest_err'] = 0
    session['edit_phone_rest_saved'] =0
    session['edit_URL_rest_saved'] =0
    session['edit_cost_rest_err']=0
    session['edit_cost_rest_saved']=0
    session['edit_password_rest_err']=0
    session['edit_password_rest_saved']=0
    session['cuisine_selected']=-1
    session['rating_selected']=-1
    session['cost_selected']=-1
    session['booking_confirmed']=0
    session['booking_err']=0

def get_restaurant_info(restid, short=0):
    conn = get_db_connection()
    cur = conn.cursor()
    q1 = """SELECT * FROM restaurants WHERE restaurantid = %s limit 1"""
    t1 = (restid,)
    cur.execute(q1,t1)
    y = cur.fetchall()
    if len(y) == 0:
        return -1
    info = y[0]
    context = {}
    context['id'] = info[0]
    context['name'] = info[7]
    context['url'] = info[8]
    context['address'] = info[9]
    context['rating'] = round(info[4], 1)
    context['onlineorder'] = info[3]
    if context['rating'] is None:
        context['rating'] = 'Not yet rated'
    else:
        context['rating'] = str(context['rating'])+'/5'
    context['votes'] = int(info[5])
    context['costfortwo'] = info[6]
    if context['costfortwo'] is None:
        context['costfortwo'] = 'Unknown'
    else:
        context['costfortwo'] = 'Rs. '+str(context['costfortwo'])+' for two people (approx.)'
    context['locationid'] = info[1]
    if context['locationid'] is None:
        context['location'] = 'Unknown'
    else:
        q2 = """SELECT * FROM locationref WHERE locationid = %s"""
        t2 = (context['locationid'],)
        cur.execute(q2,t2)
        context['location'] = cur.fetchall()[0][1]
    context['listedid'] = info[2]
    q2 = """SELECT * FROM listedref WHERE listedid = %s"""
    t2 = (context['listedid'],)
    cur.execute(q2,t2)
    context['listed'] = cur.fetchall()[0][1]
    q2 = """SELECT name FROM (SELECT * FROM types WHERE restaurantid = %s) as temp, typesref where temp.typeid=typesref.typeid"""
    t2 = (restid,)
    cur.execute(q2,t2)
    context['types'] = ''
    for x in cur.fetchall():
        context['types'] += x[0]+', '
    if len(context['types']) > 0:
        context['types'] = context['types'][:-2]
    else:
        context['types'] = 'Unknown'
    q2 = """SELECT name FROM (SELECT * FROM cuisines WHERE restaurantid = %s) as temp, cuisinesref where temp.cuisineid=cuisinesref.cuisineid"""
    t2 = (restid,)
    cur.execute(q2,t2)
    context['cuisines'] = ''
    for x in cur.fetchall():
        context['cuisines'] += x[0]+', '
    if len(context['cuisines']) > 0:
        context['cuisines'] = context['cuisines'][:-2]
    else:
        context['cuisines'] = 'Unknown'
    if short == 1:
        return context
    q2 = """SELECT name FROM (SELECT * FROM liked WHERE restaurantid = %s) as temp, likedref where temp.likedid=likedref.likedid"""
    t2 = (restid,)
    cur.execute(q2,t2)
    context['liked'] = ''
    for x in cur.fetchall():
        context['liked'] += x[0]+', '
    if len(context['liked']) > 0:
        context['liked'] = context['liked'][:-2]
    else:
        context['liked'] = 'Unknown'
    q2 = """SELECT phone FROM phones WHERE restaurantid = %s"""
    t2 = (restid,)
    cur.execute(q2,t2)
    context['phones'] = ''
    for x in cur.fetchall():
        context['phones'] += x[0]+', '
    if len(context['phones']) > 0:
        context['phones'] = context['phones'][:-2]
    else:
        context['phones'] = 'Unknown'
    q2 = """SELECT userid, rating, review FROM reviews WHERE restaurantid = %s order by rating desc"""
    t2 = (restid,)
    cur.execute(q2,t2)
    context['reviews'] = [[x[0], x[1], x[2]] for x in cur.fetchall()]
    for i in range(len(context['reviews'])):
        if context['reviews'][i][1] is not None:
            context['reviews'][i][1] = str(context['reviews'][i][1])+'/5'
        else:
            context['reviews'][i][1] = 'N.A.'
        user = context['reviews'][i][0]
        if user is None:
            user = 'Anonymous'
        else:
            user = int(user)
            q2 = """SELECT username FROM user_login WHERE userid = %s limit 1"""
            t2 = (user,)
            cur.execute(q2,t2)
            user = cur.fetchall()[0][0]
        context['reviews'][i][0] = user

    q3 = """SELECT username,person,date,time,bookingid FROM bookings,user_login where bookings.userid = user_login.userid and restaurantid =%s and status = 'PENDING' order by date asc, time asc"""
    # A join required
    t3 = (restid,)
    cur.execute(q3,t3)
    context['bookings'] = [[x[0],x[1],x[2],x[3],x[4]] for x in cur.fetchall()]
    q4 = """SELECT username,person,date,time,bookingid,status FROM bookings,user_login where bookings.userid = user_login.userid and restaurantid =%s and (status = 'COMPLETED' or status = 'ACCEPTED') order by status asc, date asc, time asc"""
    # Showing accepted bookings first
    t4 = (restid,)
    cur.execute(q4,t4)
    context['booking_history'] = [[x[0],x[1],x[2],x[3],x[4],x[5]] for x in cur.fetchall()]
    return context

@app.before_request
def before_request():
    if 'userid' not in session:
        session['userid'] = -1
        session['restid'] = -1
        reset_errors()
        

@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('userid') > 0:
        return redirect(url_for('profile'))
    elif session.get('restid') > 0:
        return redirect(url_for('restprofile'))

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
    if request.method == 'POST' and request.form['type_'] == '0':
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

        session['cuisine_selected'] = cuisine
        print(cuisine)
        session['rating_selected'] = rating
        session['cost_selected'] = cost
        # also sort and do stuff
        q1 = "SELECT name,url,restaurants.restaurantid FROM restaurants,cuisines WHERE costfortwo<%s and costfortwo>=%s and rating < %s and rating>=%s and restaurants.restaurantid = cuisines.restaurantid and cuisines.cuisineid = %s  limit 10;"
        cur.execute(q1,(costhigh,costlow,rating+1,rating,cuisineid)) 
        restaurants = cur.fetchall()
        cur.execute("SELECT name FROM cuisinesref")
        cuisines = cur.fetchall()
        return render_template('profile.html', restaurants = restaurants, cuisines = cuisines, sess=session)
    # return render_template('profile.html')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name,url,restaurantid FROM restaurants limit 10;")
    restaurants = cur.fetchall()
    cur.execute("SELECT name FROM cuisinesref")
    cuisines = cur.fetchall()
    return render_template('profile.html', restaurants = restaurants, cuisines = cuisines, sess=session)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if session.get('userid') <= 0:
        return redirect(url_for('home'))
    # print(request.form)
    bid = {}
    bid['bid'] = -1
    session['booking_confirmed']=0
    session['booking_err'] = 0
    if request.method == 'POST':

        if request.form['type_'] == 'bth':

            session['booking_confirmed']=0
            return redirect(url_for('profile'))

        else:
            # For a fixed day, restaurantid, atmost one PENDING/APPROVED booking
            # Add option to cancel a booking as well
            # Add option to check booking status as well (will be done through tabs)
            persons = request.form['tot_person']
            date = request.form['date']                
            time = request.form['time']
            restid = request.form['type_']
            if restid.isnumeric():
                restid=int(restid)
            if restid < 0:
                return redirect(url_for('profile'))

            conn = get_db_connection()
            cur = conn.cursor()

            q1 = """SELECT bookingid FROM bookings WHERE userid = %s and restaurantid = %s and date = %s and (status = 'PENDING' or status = 'APPROVED')"""
            t1 = (session.get('userid'),restid,date)
            cur.execute(q1,t1)
            res = cur.fetchall()
            if (len(res) == 0):
                cur.execute("""SELECT bookingid FROM bookings ORDER BY bookingid DESC LIMIT 1""")
                last_id = cur.fetchall()

                if (len(last_id) == 0): # This is the first booking so far
                    bookingid = 1
                else:
                    bookingid = int(last_id[0][0])+1

                t1 = (bookingid,session.get('userid'),restid,persons,date,time)      # how to generate booking id? (currently set as 1)
                q1 = """INSERT INTO bookings VALUES (%s,%s,%s,%s,%s,%s,'PENDING')""" # Pending status
                cur.execute(q1,t1)
                conn.commit()
                # Now print booking confirmed, set a flag of session
                bid['bid'] = bookingid
                session['booking_confirmed'] = 1
            else:
                bid['bid'] = int(res[0][0])
                session['booking_err'] = 1

    if 'restid' not in request.args:
        return redirect(url_for('profile'))
    restid = request.args['restid']
    if restid.isnumeric():
        restid=int(restid)
    if restid < 0:
        return redirect(url_for('profile'))
    context=get_restaurant_info(int(request.args['restid']), 1)
    if context == -1:
        return redirect(url_for('profile'))
    return render_template('booking.html', context=context, sess = session, bid = bid )

@app.route('/edit_profile_rest',methods =['GET','POST'])
def edit_profile_rest():
    if session.get('restid') <= 0:
        return redirect(url_for('home'))
    if request.method == 'POST':
        print(request.form['type__'])
        if request.form['type__'] == '5':
            session['saved']=0
            return redirect(url_for('restprofile'))
        elif request.form['type__'] == '1':
            session['edit_phone_rest_saved'] =0
            # Currently not handling error case here
            # Save the phone number for this restid
            q1 = """UPDATE phones  SET phone = %s WHERE restaurantid = %s"""
            t1 = (request.form['phonenum1'],session['restid'])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(q1,t1)
            conn.commit()
            session['saved'] = 1
            session['edit_phone_rest_saved'] =1

        elif request.form['type__'] == '2':
            session['edit_URL_rest_saved'] =0
            q1 = """UPDATE restaurants SET url = %s WHERE restaurantid =%s"""
            t1 = (request.form['url1'],session['restid'])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(q1,t1)
            conn.commit()
            session['saved'] = 1
            session['edit_URL_rest_saved'] =1

        elif request.form['type__'] == '3':
            session['edit_cost_rest_saved'] =0
            q1 = """UPDATE restaurants SET costfortwo = %s WHERE restaurantid =%s"""
            t1 = (request.form['cost1'],session['restid'])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(q1,t1)
            conn.commit()
            session['saved'] = 1
            session['edit_cost_rest_saved'] =1

        else:
            session['edit_password_rest_err']=0
            session['edit_password_rest_saved']=0
            password = request.form['pass1']
            if len(password) == 0 or ' ' in password or not password.isalnum():
                session['error'] = 1
                session['edit_password_rest_err'] = 1
            else:
                q1 = """UPDATE restaurant_login SET password = %s WHERE restaurantid=%s"""
                hash_ = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                hash_ = hash_.decode('utf8')
                t1 = (hash_,session['restid'])
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(q1,t1)
                conn.commit()
                session['saved']=1
                session['edit_password_rest_saved']=1

    return render_template('edit_profile_rest.html',sess = session)

@app.route('/restprofile', methods=['GET', 'POST'])
def restprofile():
    if session.get('restid') <= 0:
        return redirect(url_for('home'))
    context=get_restaurant_info(session['restid'])
    tab_state = ['active','','','']
    disp_state = ['show active','','','']
    if request.method == 'POST':
        val = request.form['type_']
        bookingid = int(val[1:])
        if (val[0] == 'a'):
            # accept the booking and change the status to accepted
            q1 = """UPDATE bookings SET status = 'ACCEPTED' WHERE bookingid = %s"""
            t1 = (bookingid,)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(q1,t1)
            conn.commit()
            context=get_restaurant_info(session['restid']) # New context
            tab_state = ['','active','','']
            disp_state = ['','show active','','']
        else:
            # reject the booking and change the status to rejected
            q1 = """UPDATE bookings SET status = 'REJECTED' WHERE bookingid = %s"""
            t1 = (bookingid,)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(q1,t1)
            conn.commit()
            context=get_restaurant_info(session['restid']) # New context
            tab_state = ['','active','','']
            disp_state = ['','show active','','']

    return render_template('restprofile.html', context=context, tab_state = tab_state, disp_state = disp_state)

@app.route('/restdisplay', methods=['GET', 'POST'])
def restdisplay():
    if session.get('userid') <= 0:
        return redirect(url_for('home'))
    if request.method == 'POST':
        rating = float(request.form['rating'])
        review = request.form['review']
        restid = int(request.form['restid'])
        conn = get_db_connection()
        cur = conn.cursor()
        q = """SELECT reviewid, rating FROM reviews WHERE restaurantid = %s and userid = %s limit 1"""
        t = (restid, session['userid'])
        cur.execute(q, t)
        x = cur.fetchall()
        if len(x) == 0:
            cur.execute("SELECT reviewid FROM reviews ORDER BY reviewid DESC limit 1")
            x = cur.fetchall()[0][0]
            q = """INSERT INTO reviews VALUES(%s, %s, %s, %s, %s);"""
            t = (restid, x+1, session['userid'], rating, review)
            cur.execute(q, t)
            q = """SELECT * from restaurants where restaurantid=%s limit 1"""
            t = (restid,)
            cur.execute(q, t)
            x = cur.fetchall()[0]
            rating_ = x[4]
            votes = x[5]
            if rating_ is None:
                rating_ = 0
            rating_ = (rating_*votes+rating)/(votes+1)
            q = """UPDATE restaurants set rating=%s, votes=%s where restaurantid=%s"""
            t = (rating_, votes+1, restid)
            cur.execute(q, t)
        else:
            reviewid = x[0][0]
            old_rating = x[0][1]
            print(old_rating)
            q = """UPDATE reviews SET rating=%s, review=%s WHERE reviewid=%s;"""
            t = (rating, review, reviewid)
            cur.execute(q, t)
            q = """SELECT * from restaurants where restaurantid=%s limit 1"""
            t = (restid,)
            cur.execute(q, t)
            x = cur.fetchall()[0]
            rating_ = x[4]
            votes = x[5]
            if rating_ is None:
                rating_ = 0
            if old_rating is None:
                old_rating = 0
            rating_ = (rating_*votes-old_rating+rating)/votes
            q = """UPDATE restaurants set rating=%s, votes=%s where restaurantid=%s"""
            t = (rating_, votes, restid)
            cur.execute(q, t)
        return redirect(url_for('restdisplay')+'?restid='+str(restid))
    if 'restid' not in request.args:
        return redirect(url_for('profile'))
    restid = request.args['restid']
    if restid.isnumeric():
        restid=int(restid)
    if restid < 0:
        return redirect(url_for('profile'))
    context=get_restaurant_info(int(request.args['restid']))
    if context == -1:
        return redirect(url_for('profile'))
    conn = get_db_connection()
    cur = conn.cursor()
    q = """SELECT * FROM reviews WHERE restaurantid = %s and userid = %s limit 1"""
    t = (restid, session['userid'])
    cur.execute(q, t)
    x = cur.fetchall()
    if len(x) == 0:
        context['userrating'] = -1
        context['review'] = ''
        context['reviewid'] = -1
    else:
        context['userrating'] = int(x[0][3])
        context['review'] = x[0][4]
        context['reviewid'] = x[0][1]
    # add Previous bookings (show all states)
    q4 = """SELECT person,date,time,status FROM bookings where restaurantid =%s order by date asc, time asc"""
    # Showing accepted bookings first
    t4 = (restid,)
    cur.execute(q4,t4)
    context['previous_bookings'] = [[x[0],x[1],x[2],x[3]] for x in cur.fetchall()]
    return render_template('restdisplay.html', context=context)

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
        cur.execute("""SELECT * from types ORDER BY restaurantid DESC limit 1""")
        cur.execute("""SELECT * from phones ORDER BY restaurantid DESC limit 1""")
        cur.execute("""SELECT * from locationref ORDER BY locationid DESC limit 1""")
        return redirect(url_for('restprofile'))
    # Implement drop down list
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT name FROM listedref""")
    categorylist = cur.fetchall()
    cur.execute("""SELECT name from typesref""")
    typelist = cur.fetchall()
    return render_template('register.html', sess=session, categorylist= categorylist, typelist = typelist)