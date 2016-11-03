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
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            statement = """SELECT NAME, INFORMATION, ADDRESS, PHONENUMBER
                        FROM PLACES"""
            cursor.execute(statement)
            test = cursor.fetchall()
    return render_template('places.html', test = test)
@app.route('/places', methods=['POST'])
def my_form_post():
    if 'add_button' in request.form:
        PlaceName = request.form['PlaceName']
        description = request.form['description']
        address = request.form['address']
        phone = request.form['phone']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """
                   INSERT INTO PLACES (NAME, INFORMATION, ADDRESS, PHONENUMBER)
                      VALUES (%s, %s, %s, %s)
                """
                cursor.execute(statement, [PlaceName, description, address, phone])
                connection.commit()
    elif 'update_button' in request.form:
        PlaceName = request.form['PlaceName']
        description = request.form['description']
        address = request.form['address']
        phone = request.form['phone']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """
                    UPDATE PLACES
                        SET INFORMATION = %s, ADDRESS = %s, PHONENUMBER = %s
                            WHERE NAME = %s"""
                cursor.execute(statement, [description, address, phone, PlaceName])
                connection.commit()
    elif 'delete_button' in request.form:
        PlaceName = request.form['PlaceName']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """ DELETE FROM PLACES
                                    WHERE NAME = %s """
                cursor.execute(statement, [PlaceName])
                connection.commit()
    return places_page()

@app.route('/photos')
def photos_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            statement = """SELECT ID, INFORMATION, URL, USERNAME
                        FROM PHOTOS"""
            cursor.execute(statement)
            photo_db = cursor.fetchall()
    return render_template ('meetings.html', photo_db = photo_db)
@app.route('/photos', methods=['POST'])
def photos_post():
    if 'create_button' in request.form:
        info = request.form['info']
        url = request.form['url']
        username = request.form['username']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """INSERT INTO PHOTOS (INFORMATION, URL, USERNAME)
                      VALUES (%s, %s, %s)"""
                cursor.execute(statement, [info, url, username])
    elif 'update_button' in request.form:
        id = request.form['id']
        info = request.form['info']
        url = request.form['url']
        username = request.form['username']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """UPDATE PHOTOS
                        SET INFORMATION = %s, URL = %s, USERNAME = %s
                            WHERE ID = %s"""
                cursor.execute(statement, [info, url, username, id])
    elif 'delete_button' in request.form:
        id = request.form['id']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """ DELETE FROM PHOTOS
                                    WHERE ID = %s """
                cursor.execute(statement,[id])
        connection.commit()
    return photos_page()
@app.route('/init_phdb')
def initilize_photos_db():
    with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """CREATE TABLE PHOTOS (
                ID SERIAL PRIMARY KEY,
                INFORMATION VARCHAR(300) NOT NULL,
                URL VARCHAR(1000) NOT NULL,
                USERNAME VARCHAR(20)
                )"""
                cursor.execute(statement)
                connection.commit()
    return photos_page()

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
            if request.form['EVENT_ID'] is "":
                return redirect(url_for('events_page'))
            cursor = connection.cursor()
            query = "SELECT EVENT_ID FROM EVENT WHERE EVENT_ID = %s"
            cursor.execute(query, [request.form['EVENT_ID']])
            if cursor.fetchall is "":
                connection.commit()
                return redirect(url_for('events_page'))
            if request.form['Name'] is not "":
                query = "UPDATE EVENT SET NAME = %s WHERE EVENT_ID = %s"
                cursor.execute(query, [request.form['Name'], request.form['EVENT_ID']])
            if request.form['Short_Description'] is not "":
                query = "UPDATE EVENT SET SHORT_DESCRIPTION = %s WHERE EVENT_ID = %s"
                cursor.execute(query, [request.form['Short_Description'], request.form['EVENT_ID']])
            if request.form['Description'] is not "":
                query = "UPDATE EVENT SET DESCRIPTION = %s WHERE EVENT_ID = %s"
                cursor.execute(query, [request.form['Description'], request.form['EVENT_ID']])
            if request.form['startingDate'] is not "":
                query = "UPDATE EVENT SET STARTING_DATE = %s WHERE EVENT_ID = %s"
                cursor.execute(query, [request.form['startingDate'], request.form['EVENT_ID']])
            if request.form['endingDate'] is not "":
                query = "UPDATE EVENT SET ENDING_DATE = %s WHERE EVENT_ID = %s"
                cursor.execute(query, [request.form['endingDate'], request.form['EVENT_ID']])
            if request.form['place'] is not "":
                query = "UPDATE EVENT SET PLACE = %s WHERE EVENT_ID = %s"
                cursor.execute(query, [request.form['place'], request.form['EVENT_ID']])
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
