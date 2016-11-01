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

@app.route('/EventCreation')
def eventcreation_page():
    return render_template('EventCreation.html')
@app.route('/mypage')
def my_page():
    return render_template('mypage.html')


@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ INSERT INTO USER (USER_NAME, BIRTHDAY, LOCATION, OCUPATION, INTERESTS) VALUES (%s, %s, %s)"""
            cursor.execute(query, (user_name, birthday, location, ocupation, interests))
    return render_template('mypage.html')

@app.route('/events', methods=['POST', 'GET'])
def events_page():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = "SELECT N FROM EVENT_COUNTER"
            eventId = cursor.execute(query)
            ##values for startingDate and endingDate not set
            query = ("INSERT INTO EVENT VALUES ("+ str(eventId) + "," + request.form['Name']
            + "," + request.form['Description']
            + "," + request.form['Description']
            + ",NULL"+ ",NULL,"
            + request.form['place']+ ")")
            cursor.execute(query)
            query = "UPDATE EVENT_COUNTER N = N + 1"
            cursor.execute(query)
            retVal = cursor.execute("SELECT * FROM EVENT")
            connection.commit()
    return retVal


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
        query = """INSERT INTO EVENT_COUNTER VALUES (0)"""
        cursor.execute(query)
        query = """CREATE TABLE EVENT (
                EVENT_ID INT NOT NULL PRIMARY KEY,
                NAME VARCHAR(50) NOT NULL DEFAULT 'EMPTY',
                SHORT_DESCRIPTION VARCHAR(200) NOT NULL DEFAULT 'EMPTY',
                DESCRIPTION VARCHAR(2000) NOT NULL DEFAULT 'EMPTY',
                STARTING_DATE VARCHAR(50),
                ENDING_DATE VARCHAR(50),
                PLACE VARCHAR(100)
                )"""
        cursor.execute(query)
        ###################################################################
        # Creating Places Table In Database, and filling it with a sample #
        ###################################################################
        query = """CREATE TABLE PLACES (
                NAME VARCHAR(50) NOT NULL PRIMARY KEY,
                INFORMATION VARCHAR(300) NOT NULL,
                ADDRESS VARCHAR(1000) NOT NULL,
                PHONENUMBER VARCHAR(20)
                )"""
        cursor.execute(query)
        place_data = [
        {'name': "Starbucks",
         'info': "Great place to drink coffe",
         'address': "Istanbul",
         'phonenum':"05458965896"}
        ]

        for item in place_data:
            statement = """
               INSERT INTO PLACES (NAME, INFORMATION, ADDRESS, PHONENUMBER)
                  VALUES (%(name)s, %(info)s, %(address)s, %(phonenum)s)
            """
            cursor.execute(statement, item)
            connection.commit()
        #
        # Creating friends table and filling it with sample data
        #
        query = """ DROP TABLE IF EXITS FRIENDS"""
        cursor.execute(query)
        query = """
                CREATE TABLE FRIENDS (
                PERSON_ID INT NOT NULL,
                FRIEND_ID INT NOT NULL,
                FRIEND_STATUS INT,
                primary key (PERSON_ID, FRIEND_ID)
                )"""
        cursor.execute(query)
        friends_data = {
                'person_id': 1,
                'friend_id': 3,
                'friend_status': 0 }
        query = """INSERT INTO FRIENDS VALUES (1, 3, 0)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS USERS"""
        cursor.execute(query)
        query = """ CREATE TABLE USERS
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
        return redirect(url_for('home_page'))


if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), True
    else:
        port, debug = 5000, True
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""
    app.run(host='0.0.0.0', port=port, debug=debug)
