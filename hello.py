import os
import psycopg2
from flask import Flask, render_template


app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
    host = "localhost",
    database = "dbname",
    user = "read_only_user",
    password = "password"
    )
    return conn



@app.route('/')
def index():

    # conn = get_db_connection()
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM users limit 10;")
    # users = cur.fetchall()

    # for user in users:
    #     print(user)

    # cur.close()
    # conn.close()
    return render_template('index.html',x=5)