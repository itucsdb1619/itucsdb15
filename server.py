import os
import psycopg2 as dbapi2
import json
import re

from flask import Flask
from flask import redirect
from flask import request
from flask.helpers import url_for
from flask import render_template
from users import User, Users


app = Flask(__name__)
def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@app.route('/')
def home_page():
    return render_template('home.html')

 @app.route('/users', methods=['GET', 'POST'])
 def users():
    return render_template('mypage.html')

@app.route('/events', methods=['POST', 'GET'])
def events_page():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            ##values for startingDate and endingDate not set
            query = "INSERT INTO EVENT VALUES ("+ request.form['Name'] + "," + request.form['Description'] + "," + request.form['Description']+ "," + request.form['place']
            cursor.execute(query)
            connection.commit()
    return render_template('events.html')

@app.route('/places')
def places_page():
    return render_template('places.html')

@app.route('/photos')
def photos_page():
    return render_template('photos.html')

@app.route('/EventCreation')
def eventcreation_page():
    return render_template('EventCreation.html')

@app.route('/initdb')
def initDataBase():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        ###
        query = """DROP TABLE IF EXISTS EVENT_COUNTER"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS EVENT"""
        cursor.execute(query)
        query = """CREATE TABLE EVENT_COUNTER (N INTEGER)"""
        cursor.execute(query)
        query = """CREATE TABLE EVENT_COUNTER (N INTEGER)"""
        cursor.execute(query)
        query = """INSERT INTO EVENT_COUNTER VALUES (0)"""
        cursor.execute(query)
        query = """CREATE TABLE EVENT (
                NAME VARCHAR(50) NOT NULL,
                DESCRIPTION VARCHAR(200) NOT NULL,
                STARTING_DATE DATETIME,
                ENDING_DATE DATETIME,
                PLACE VARCHAR(100),
                )"""
        cursor.execute(query)
         ##########################################################
        Creating Places Table In Database
        ##########################################################
        query = """CREATE TABLE PLACES (
                NAME VARCHAR(50) NOT NULL PRIMARY KEY,
                INFORMATION VARCHAR(300) NOT NULL,
                ADDRESS VARCHAR(1000) NOT NULL,
                PHONENUMBER VARCHAR(20)
                )"""
        cursor.execute(query)
        connection.commit()
        return render_template('events.html')

 def create_tables():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
    
        query = """ CREATE TABLE IF NOT EXISTS USERS
        (   
        USER_ID serial NOT NULL PRIMARY KEY,
        USER_NAME varchar(100) NOT NULL,
        BIRTHDAY date NOT NULL,
        LOCATION varchar(50) NOT NULL,
        OCUPATION varchar(50) NOT NULL,
        INTERESTS varchar(100) NOT NULL
        )"""    
        cursor.execute(query)
        connection.commit()
        app.user.initialize_tables()

if __name__ == '__main__':
    app.user = Users(app)
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""
    app.run(host='0.0.0.0', port=port, debug=debug)
