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

@app.route('/places')
def places_page():
    return render_template('places.html')


@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ INSERT INTO USER (USER_NAME, BIRTHDAY, LOCATION, OCUPATION, INTERESTS) VALUES (%s, %s, %s)"""
            cursor.execute(query, (user_name, birthday, location, ocupation, interests))
    return render_template('mypage.html')


@app.route('/deleteEvent',  methods=['POST', 'GET'])
def delete_event():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            if request.form['EVENT_ID'] is not "":
                cursor = connection.cursor()
                query = ("DELETE FROM EVENT WHERE EVENT_ID = %s")
                cursor.execute(query, [request.form['EVENT_ID']])
                connection.commit()
    return redirect(url_for('events_page'))

@app.route('/updateEvent',  methods=['POST', 'GET'])
def update_event():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            #:)
            if request.form['EVENT_ID'] is "":
                return redirect(url_for('events_page'))
            cursor = connection.cursor()
            query = ("UPDATE EVENT SET ")
            if request.form['Name'] is not "":
                query = query + " NAME =" + request.form['Name']
            if request.form['Short_Description'] is not "":
                if request.form['Name'] is not "":
                    if request.form['Short_Description'] is not "":
                        query = query + ","
                query = query + " SHORT_DESCRIPTION =" + request.form['Short_Description']
            if request.form['Description'] is not "":
                if request.form['Short_Description'] is not "":
                    if request.form['Name'] is not "":
                        query = query + ","
                query = query + " Description =" + request.form['Description']
            if request.form['startingDate'] is not "":
                if request.form['Description'] is not "":
                    if request.form['Short_Description'] is not "":
                        if request.form['Name'] is not "":
                            query = query + ","
                query = query + " STARTING_DATE =" + request.form['startingDate']
            if request.form['endingDate'] is not "":
                if request.form['startingDate'] is not "":
                    if request.form['Description'] is not "":
                        if request.form['Short_Description'] is not "":
                            if request.form['Name'] is not "":
                                query = query + ","
                query = query + " ENDING_DATE =" + request.form['endingDate']
            if request.form['place'] is not "":
                if request.form['endingDate'] is not "":
                    if request.form['startingDate'] is not "":
                        if request.form['Description'] is not "":
                            if request.form['Short_Description'] is not "":
                                if request.form['Name'] is not "":
                                    print("DEBUG")
                                    #crashes
                                    #query = query + ","
                #query = query + " PLACE = none"+ request.form['place']
            if request.form['place'] is not "":
                if request.form['endingDate'] is not "":
                    if request.form['startingDate'] is not "":
                        if request.form['Description'] is not "":
                            if request.form['Short_Description'] is not "":
                                if request.form['Name'] is not "":
                                    return redirect(url_for('events_page'))
            query = query + " WHERE EVENT_ID = " + request.form['EVENT_ID']
            cursor.execute(query)
            connection.commit()
    return redirect(url_for('events_page'))

@app.route('/events', methods=['POST', 'GET'])
def events_page():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = ("INSERT INTO EVENT (NAME,SHORT_DESCRIPTION,DESCRIPTION,STARTING_DATE,ENDING_DATE,PLACE)"
            + " VALUES (%s, %s, %s, %s, %s, %s)")
            cursor.execute(query, [request.form['Name'],
                                  request.form['Short_Description'],
                                  request.form['Description'],
                                  request.form['startingDate'],
                                  request.form['endingDate'],
                                  request.form['place']])

            connection.commit()
    if request == 'PUT':
        print("DEBUG PT")
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = ("SELECT * FROM EVENT ")
        cursor.execute(query)
        eventTable = cursor.fetchall()
        connection.commit()
        return render_template('events.html', event = eventTable)


@app.route('/initdb')
def initDataBase():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """DROP TABLE IF EXISTS EVENT"""
        cursor.execute(query)
        query = """CREATE TABLE EVENT (
                EVENT_ID SERIAL  PRIMARY KEY,
                NAME VARCHAR(50) NOT NULL,
                SHORT_DESCRIPTION VARCHAR(200) NOT NULL,
                DESCRIPTION VARCHAR(2000) NOT NULL,
                STARTING_DATE VARCHAR(50),
                ENDING_DATE VARCHAR(50),
                PLACE VARCHAR(100)
                )"""
        cursor.execute(query)
        ###################################################################
        # Creating Places Table In Database, and filling it with a sample #
        ###################################################################
        query = """DROP TABLE IF EXISTS PLACES"""
        cursor.execute(query)
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
        query = """ DROP TABLE IF EXISTS FRIENDS"""
        cursor.execute(query)
        query = """
                CREATE TABLE FRIENDS (
                PERSON_ID INT NOT NULL,
                FRIEND_ID INT NOT NULL,
                FRIEND_STATUS INT,
                primary key (PERSON_ID, FRIEND_ID)
                )"""
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
        return redirect(url_for('home_page'))


@app.route('/friends', methods=['POST', 'GET'])
def friends_page():
    last_query = "SELECT * FROM FRIENDS"
    if request.method == 'POST':
        personID = request.form['personID']
        friendID = request.form['friendID']
        actionType = request.form['actionType']
        actionData = request.form['actionData']
        friendStatus = request.form['friendStatus']
        if friendStatus == '':
            friendStatus = '0'
        if actionType == 'delete':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                pid, fid = actionData.split(',')
                query = """DELETE FROM FRIENDS WHERE PERSON_ID = %s AND FRIEND_ID=%s"""
                cursor.execute(query, (pid, fid))
                connection.commit()
        elif personID == '' or friendID == '':
            return """<script> alert('Fill the necessary inputs');
                   window.location = '/friends';</script>"""
        elif actionType == 'add':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO FRIENDS
                           (PERSON_ID, FRIEND_ID, FRIEND_STATUS) VALUES (%s, %s, %s)"""
                data = (personID, friendID, friendStatus)
                cursor.execute(query, data)
                connection.commit()
        else:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                pid, fid = actionData.split(',')
                query = """UPDATE FRIENDS SET PERSON_ID = %s, FRIEND_ID = %s, FRIEND_STATUS = %s
                           WHERE PERSON_ID = %s AND FRIEND_ID=%s"""
                cursor.execute(query, (personID, friendID, friendStatus, pid, fid))
                connection.commit()
    if request.method == 'GET':
        personID = request.args.get('personID')
        friendID = request.args.get('friendID')
        friendStatus = request.args.get('friendStatus')
        query = """SELECT * FROM FRIENDS"""
        if personID != '' or friendID != '' or friendStatus != '':
            query += """ WHERE """
            addquery = []
            if personID != '' and personID is not None:
                addquery.append('PERSON_ID = ' + format(personID))
            if friendID != '' and friendID is not None:
                addquery.append("""FRIEND_ID = """ + format(friendID))
            if friendStatus != '' and friendStatus is not None:
                addquery.append(""" FRIEND_STATUS = """ + format(friendStatus))
            for s in addquery:
                query += s
                query += """ AND """
            query = query[:-5]
            last_query = query
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        cursor.execute(last_query)
        rows = cursor.fetchall()
        connection.commit()
    return render_template('friends.html', rows=rows)


@app.route('/friends_init', methods=['POST', 'GET'])
def friends_init():
    if request.args.get('action') == 'drop':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ DROP TABLE IF EXISTS FRIENDS"""
            cursor.execute(query)
            connection.commit()
        return render_template('friends.html')
    elif request.args.get('action') == 'create':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ DROP TABLE IF EXISTS FRIENDS"""
            cursor.execute(query)
            query = """CREATE TABLE FRIENDS (
                       PERSON_ID INT NOT NULL,
                       FRIEND_ID INT NOT NULL,
                       FRIEND_STATUS INT,
                       primary key (PERSON_ID, FRIEND_ID)
                       )"""
            cursor.execute(query)
            connection.commit()
            return redirect('/friends')
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO FRIENDS VALUES (0, 1, 1)"""
            cursor.execute(query)
            query = """INSERT INTO FRIENDS VALUES (0, 2, 1)"""
            cursor.execute(query)
            query = """INSERT INTO FRIENDS VALUES (0, 3, 2)"""
            cursor.execute(query)
            query = """INSERT INTO FRIENDS VALUES (1, 3, 2)"""
            cursor.execute(query)
            query = """INSERT INTO FRIENDS VALUES (1, 5, 3)"""
            cursor.execute(query)
            connection.commit()
            return redirect('/friends')


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
