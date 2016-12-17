import os
import psycopg2 as dbapi2
import json
import re

from flask import Flask
from flask import redirect
from flask import request
from flask.helpers import url_for
from flask import render_template
from flask import session
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
    if 'logged_in' in session:
        return render_template('home.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return render_template('home.html')
    if request.method == 'POST':
        attempted_name = request.form['name']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ SELECT * FROM USERS WHERE USER_NAME=%s"""
            cursor.execute(query, [attempted_name])
            fetched_user = cursor.fetchone()
            if fetched_user is not None:
                session['logged_in'] = True
                session['username'] = attempted_name
                session['USER_ID'] = fetched_user[0]
                return redirect(url_for('home_page'))
            else:
                return render_template('login.html', invalid_login=True)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('USER_ID', None)
    return redirect(url_for('login'))


@app.route('/EventCreation')
def eventcreation_page():
    try:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = ("SELECT * FROM PLACES")
            cursor.execute(query)
            Places = cursor.fetchall()
            cursor.close()
        return render_template('EventCreation.html', Places = Places)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/create_meeting')
def createmeeting_page():
    try:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = ("SELECT * FROM PLACES")
            cursor.execute(query)
            Places = cursor.fetchall()
            cursor.close()
        return render_template('create_meeting.html',Places = Places)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/mypage')
def my_page():
    return render_template('mypage.html')

@app.route('/places')
def places_page():
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()
        statement = """SELECT PLACES_ID, PLACES.NAME, PLACES.INFORMATION, ADDRESS, PHONENUMBER, PHOTOURL
                    FROM PLACES, PHOTOS
                    WHERE (PROFILEPHOTO = ID)"""
        cursor.execute(statement)
        connection.commit()
        test = cursor.fetchall()
        cursor.close()
        return render_template('places.html', test = test)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
        connection.close()

@app.route('/places', methods=['POST'])
def my_form_post():
    if 'add_button' in request.form:
       return add_place_page()
    elif 'update_button' in request.form:
       id = request.form['place_to_delete'];
       return update_place_page(id)
    elif 'delete_button' in request.form:
        id = request.form['place_to_delete'];
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()
        statement = """ DELETE FROM PLACES
                    WHERE PLACES_ID = %s """
        cursor.execute(statement, [id])
        connection.commit()
        cursor.close()
        return places_page()
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
        connection.close()

@app.route('/addplace')
def add_place_page():
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()
        statement = """SELECT ID, NAME
                    FROM PHOTOS"""
        cursor.execute(statement)
        connection.commit()
        test = cursor.fetchall()
        cursor.close()
        return render_template('add_place.html', test = test)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
        connection.close()

@app.route('/addplace', methods=['POST'])
def add_place():
    if  'add_button' in request.form:
        PlaceName = request.form['PlaceName']
        description = request.form['description']
        address = request.form['address']
        phone = request.form['phone']
        profilephoto = request.form['getphotoid']
        try:
            connection = dbapi2.connect(app.config['dsn'])
            cursor = connection.cursor()
            statement = """
            INSERT INTO PLACES (NAME, INFORMATION, ADDRESS, PHONENUMBER, PROFILEPHOTO)
            VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(statement, [PlaceName, description, address, phone, profilephoto])
            connection.commit()
            cursor.close()
            return places_page()
        except dbapi2.DatabaseError:
            connection.rollback()
            return render_template('error_page.html')
        finally:
            connection.close()

@app.route('/updateplace')
def update_place_page(id):
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()
        statement = """SELECT ID, NAME
                    FROM PHOTOS"""
        cursor.execute(statement)
        connection.commit()
        test = cursor.fetchall()
        cursor.close()
        return render_template('update_place.html', test = test, id = id)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/updateplace', methods=['POST'])
def update_place():
    if 'add_button' in request.form:
        id = request.form['place_to_delete']
        PlaceName = request.form['PlaceName']
        description = request.form['description']
        address = request.form['address']
        phone = request.form['phone']
        profilephoto = request.form['getphotoid']

        try:
            connection = dbapi2.connect(app.config['dsn'])
            cursor = connection.cursor()
            statement = """
                        UPDATE PLACES
                        SET NAME=%s, INFORMATION=%s, ADDRESS=%s, PHONENUMBER=%s, PROFILEPHOTO=%s
                        WHERE (%s = PLACES_ID)"""
            cursor.execute(statement, [PlaceName, description, address, phone, profilephoto, id])
            connection.commit()
            cursor.close()
            return places_page()
        except dbapi2.DatabaseError:
            connection.rollback()
            return render_template('error_page.html')
        finally:
            connection.close()

@app.route('/photos')
def photos_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            statement = """SELECT ID, INFORMATION, URL, USERNAME
                        FROM PHOTOS"""
            cursor.execute(statement)
            photo_db = cursor.fetchall()
            cursor.close()
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
                cursor.close()
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
                cursor.close()
    elif 'delete_button' in request.form:
        id = request.form['id']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """ DELETE FROM PHOTOS
                                    WHERE ID = %s """
                cursor.execute(statement,[id])
    return photos_page()
@app.route('/init_phdb')
def initilize_photos_db():
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()
        statement = "DROP TABLE IF EXISTS PHOTOS CASCADE"
        cursor.execute(statement)
        statement = """CREATE TABLE PHOTOS (
                    ID SERIAL PRIMARY KEY,
                    INFORMATION VARCHAR(300) NOT NULL,
                    PHOTOURL VARCHAR(1000) NOT NULL,
                    USERNAME VARCHAR(20)
                    )"""
        cursor.execute(statement)
        cursor.close()
        return home_page()
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
        connection.close()

''' USERS '''


@app.route('/users')
def user_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            statement = """SELECT * FROM USERS"""
            cursor.execute(statement)
            user_all = cursor.fetchall()
            cursor.close()
    return render_template('home.html', user_all = user_all)

@app.route('/users/<pk>/favourites')
def favourite_places(pk):
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            statement = """SELECT * FROM USER_FAVS WHERE USER_ID = %(user_id)s"""
            cursor.execute(statement)
            fav_places = cursor.fetchall()
            cursor.close()
    return render_template('favourites.html', favourite_places=fav_places, user_pk=pk)

@app.route('/users', methods=['POST'])
def operation():
    if 'add_button' in request.form:
        return user_add_page()
    elif 'update_button' in request.form:
        name = request.form['name']
        birthday = request.form['birthday']
        location = request.form['location']
        ocupation = request.form['ocupation']
        interests = request.form['interests']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """ UPDATE USERS
                        SET NAME = %s,
                        BIRTHDAY = %s,
                        LOCATION = %s,
                        OCUPATION = %s,
                        INTERESTS = %s
                        WHERE
                        USER_ID = %s """
                cursor.execute(statement, [name, birthday, location, ocupation, interests])
    elif 'delete_button' in request.form:
        user_id = request.form['user_id']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """ DELETE FROM USERS
                                    WHERE USER_ID = %s"""
            cursor.execute(statement, [user_id])
            cursor.close()
    return users()

@app.route('/user_add')
def user_add_page():
    return render_template('user_add.html')
@app.route('/user_add', methods = ['POST'])
def useradd():
    if 'add_button' in request.form:
        name = request.form['name']
        birthday = request.form['birthday']
        location = request.form['location']
        ocupation = request.form['ocupation']
        interests = request.form['interests']
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """
                INSERT INTO USERS (USER_NAME, BIRTHDAY, LOCATION, OCUPATION, INTERESTS) VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, [name, birthday, location, ocupation, interests])
                cursor.close()
    return render_template('home.html')

''' end of USERs part'''
@app.route('/deleteEvent',  methods=['GET', 'POST'])
def delete_event():
    try:
        if request.method == 'POST':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM EVENT_PARTICIPANTS
                WHERE EVENT_ID = %s AND USER_ID = %s"""
                id = request.form['button']
                event_id = session['USER_ID']
                cursor.execute(query, [str(id), str(event_id)])
                query = """SELECT * FROM EVENT_PARTICIPANTS
                WHERE EVENT_ID = %s"""
                cursor.execute(query, str(id))
                isExist = cursor.fetchall()
                flag = True
                for isexist in isExist:
                    flag = False
                if flag:
                    query = """DELETE FROM EVENT
                    WHERE EVENT_ID = %s"""
                    cursor.execute(query, str(id))
                cursor.close()
        return redirect(url_for('events_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/meeting_delete',  methods=['GET', 'POST'])
def meeting_delete():
    try:
        if request.method == 'POST':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM MEETING_PARTICIPANTS
                WHERE MEETING_ID = %s AND USER_ID = %s"""
                id = request.form['button']
                event_id = session['USER_ID']
                cursor.execute(query, [str(id), str(event_id)])
                query = """SELECT * FROM MEETING_PARTICIPANTS
                WHERE MEETING_ID = %s"""
                cursor.execute(query, str(id))
                isExist = cursor.fetchall()
                flag = True
                for isexist in isExist:
                    flag = False
                if flag:
                    query = """DELETE FROM MEETING
                    WHERE MEETING_ID = %s"""
                    cursor.execute(query, str(id))
                cursor.close()
        return redirect(url_for('events_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/eventPage',  methods=['GET', 'POST'])
def eventPage():
    try:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = ("SELECT * FROM EVENT WHERE EVENT_ID = %s")
            id = request.form['button']
            cursor.execute(query, str(id))
            Event = cursor.fetchone()
            query = """SELECT * FROM EVENT_PARTICIPANTS JOIN USERS
            ON EVENT_PARTICIPANTS.USER_ID = USERS.USER_ID
            WHERE EVENT_PARTICIPANTS.EVENT_ID = %s"""
            cursor.execute(query, str(id))
            Participants = cursor.fetchall()
            query = ("SELECT * FROM PLACES WHERE PLACES_ID = %s")
            id = Event[6]
            cursor.execute(query, (str(id)))
            Place = cursor.fetchone()
            personID = session['USER_ID']
            query = """
            SELECT * FROM FRIENDS JOIN USERS
            ON FRIENDS.FRIEND_ID = USERS.USER_ID
            WHERE PERSON_ID = %s"""
            cursor.execute(query, [str(personID)])
            Friends = cursor.fetchall()
            cursor.close()
        return render_template('eventPage.html', Event = Event,  Place = Place, Participants = Participants, Friends = Friends)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()
@app.route('/meeting_page',  methods=['GET', 'POST'])
def meeting_page():
    try:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = ("SELECT * FROM MEETING WHERE MEETING_ID = %s")
            id = request.form['button']
            cursor.execute(query, (id))
            Meeting = cursor.fetchone()
            query = """SELECT * FROM MEETING_PARTICIPANTS JOIN USERS
            ON MEETING_PARTICIPANTS.USER_ID = USERS.USER_ID
            WHERE MEETING_PARTICIPANTS.MEETING_ID = %s"""
            cursor.execute(query, str(id))
            Participants = cursor.fetchall()
            personID = session['USER_ID']
            query = """
            SELECT * FROM FRIENDS JOIN USERS
            ON FRIENDS.FRIEND_ID = USERS.USER_ID
            WHERE PERSON_ID = %s"""
            cursor.execute(query, [str(personID)])
            Friends = cursor.fetchall()
            query = ("SELECT * FROM PLACES WHERE PLACES_ID = %s")
            id = Meeting[4]
            cursor.execute(query, (str(id)))
            Place = cursor.fetchone()
            cursor.close()
        return render_template('meeting_page.html', Meeting = Meeting,  Place = Place,Participants = Participants, Friends = Friends)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()
@app.route('/update_event_page',  methods=['GET', 'POST'])
def update_event_page():
    try:
        if request.method == 'POST':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = ("SELECT * FROM EVENT WHERE EVENT_ID = %s")
                id = request.form['button']
                cursor.execute(query,(str(id)))
                Event = cursor.fetchone()
                query = ("SELECT * FROM PLACES WHERE PLACES_ID = %s")
                id = Event[6]
                cursor.execute(query, (str(id)))
                Place = cursor.fetchone()
                cursor.close()
                return render_template('event_update.html', Event = Event, Place = Place)
        return redirect(url_for('events_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()


@app.route('/updateEvent',  methods=['GET', 'POST'])
def update_event():
    try:
        if request.method == 'POST':
            with dbapi2.connect(app.config['dsn']) as connection:
                id = request.form['button']
                cursor = connection.cursor()
                query = "SELECT EVENT_ID FROM EVENT WHERE EVENT_ID = %s"
                cursor.execute(query, (str(id)))
                if cursor.fetchall is "":
                    connection.commit()
                    return redirect(url_for('events_page'))
                if request.form['NAME'] is not "":
                    query = "UPDATE EVENT SET NAME = %s WHERE EVENT_ID = %s"
                    cursor.execute(query, [request.form['NAME'], str(id)])
                if request.form['SHORT_DESCRIPTION'] is not "":
                    query = "UPDATE EVENT SET SHORT_DESCRIPTION = %s WHERE EVENT_ID = %s"
                    cursor.execute(query, [request.form['SHORT_DESCRIPTION'], str(id)])
                if request.form['DESCRIPTION'] is not "":
                    query = "UPDATE EVENT SET DESCRIPTION = %s WHERE EVENT_ID = %s"
                    cursor.execute(query, [request.form['DESCRIPTION'], str(id)])
                if request.form['STARTING_DATE'] is not "":
                    query = "UPDATE EVENT SET STARTING_DATE = %s WHERE EVENT_ID = %s"
                    cursor.execute(query, [request.form['STARTING_DATE'], str(id)])
                if request.form['ENDING_DATE'] is not "":
                    query = "UPDATE EVENT SET ENDING_DATE = %s WHERE EVENT_ID = %s"
                    cursor.execute(query, [request.form['ENDING_DATE'], str(id)])
                cursor.close()
                return redirect(url_for('events_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/meeting_update_page',  methods=['GET', 'POST'])
def meeting_update_page():
    try:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = ("SELECT * FROM MEETING WHERE MEETING_ID = %s")
            id = request.form['button']
            cursor.execute(query, (str(id)))
            Meeting = cursor.fetchone()
            query = ("SELECT * FROM PLACES WHERE PLACES_ID = %s")
            id = Meeting[4]
            cursor.execute(query, (str(id)))
            Place = cursor.fetchone()
            cursor.close()
            return render_template('meeting_update.html', Meeting = Meeting, Place = Place)
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/meeting_update',  methods=['GET', 'POST'])
def meeting_update():
    try:
        if request.method == 'POST':
            with dbapi2.connect(app.config['dsn']) as connection:
                id = request.form['button']
                cursor = connection.cursor()
                query = "SELECT MEETING_ID FROM MEETING WHERE MEETING_ID = %s"
                cursor.execute(query, (str(id)))
                if cursor.fetchall is "":
                    connection.commit()
                    return redirect(url_for('events_page'))
                if request.form['NAME'] is not "":
                    query = "UPDATE MEETING SET NAME = %s WHERE MEETING_ID = %s"
                    token = request.form['NAME']
                    cursor.execute(query, (token, str(id)))
                if request.form['DESCRIPTION'] is not "":
                    query = "UPDATE MEETING SET DESCRIPTION = %s WHERE MEETING_ID = %s"
                    token = request.form['DESCRIPTION']
                    cursor.execute(query, (token, str(id)))
                if request.form['DATE'] is not "":
                    query = "UPDATE MEETING SET DATE = %s WHERE MEETING_ID = %s"
                    token = request.form['DATE']
                    cursor.execute(query, (token, str(id)))
                cursor.close()
                return redirect(url_for('events_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/events', methods=['POST', 'GET'])
def events_page():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            if request.form['button'] == "event":
                cursor = connection.cursor()
                query = "SELECT * FROM PLACES WHERE (NAME = %s)"
                cursor.execute(query, [request.form['PLACE_NAME']])
                placeRow = cursor.fetchone()
                placeId = placeRow[0]
                query = """INSERT INTO EVENT(NAME, SHORT_DESCRIPTION,DESCRIPTION ,STARTING_DATE,ENDING_DATE,PLACE)
                                VALUES (%s,%s,%s,%s,%s,%s)"""
                cursor.execute(query, [request.form['NAME'], request.form['SHORT_DESCRIPTION'],
                                       request.form['DESCRIPTION'],request.form['STARTING_DATE'],request.form['ENDING_DATE'],placeId])

                query = "SELECT *FROM EVENT WHERE NAME = %s AND STARTING_DATE = %s"
                cursor.execute(query,[request.form['NAME'],request.form['STARTING_DATE']])
                EVENT_ID = cursor.fetchone()
                query = "INSERT INTO EVENT_PARTICIPANTS (EVENT_ID, USER_ID) VALUES (%s, %s)"
                cursor.execute(query,[str(EVENT_ID[0]) ,str(session['USER_ID'])])
                #
                cursor.close()
            if request.form['button'] == "meeting":
                cursor = connection.cursor()
                query = "SELECT * FROM PLACES WHERE (NAME = %s)"
                cursor.execute(query, [request.form['PLACE_NAME']])
                placeRow = cursor.fetchone()
                placeId = placeRow[0]
                query = """INSERT INTO MEETING (NAME, DESCRIPTION , DATE, PLACE)
                                VALUES (%s,%s,%s,%s)"""
                cursor.execute(query, [request.form['NAME'],
                                       request.form['DESCRIPTION'],request.form['DATE'],placeId])
                #
                query = "SELECT *FROM MEETING WHERE NAME = %s AND DATE = %s"
                cursor.execute(query,[request.form['NAME'],request.form['DATE']])
                MEETING_ID = cursor.fetchone()
                query = "INSERT INTO MEETING_PARTICIPANTS (MEETING_ID, USER_ID) VALUES (%s, %s)"
                cursor.execute(query,[str(MEETING_ID[0]) ,str(session['USER_ID'])])
                #
                cursor.close()
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM EVENT JOIN EVENT_PARTICIPANTS
        ON EVENT_PARTICIPANTS.EVENT_ID = EVENT.EVENT_ID
        WHERE EVENT_PARTICIPANTS.USER_ID = %s
        """
        cursor.execute(query,[str(session['USER_ID'])])
        eventTable = cursor.fetchall()
        query = ("SELECT * FROM PLACES ")
        cursor.execute(query)
        Place = cursor.fetchall()
        query = """SELECT * FROM MEETING JOIN MEETING_PARTICIPANTS
        ON MEETING_PARTICIPANTS.MEETING_ID = MEETING.MEETING_ID
        WHERE MEETING_PARTICIPANTS.USER_ID = %s
        """
        cursor.execute(query,[str(session['USER_ID'])])
        meetingTable = cursor.fetchall()
        cursor.close()
        return render_template('events.html', Event = eventTable, Meeting = meetingTable, Place = Place)

@app.route('/add_participant_event',  methods=['GET', 'POST'])
def add_participant_event():
    try:
        if request.method == 'POST':
            with dbapi2.connect(app.config['dsn']) as connection:
                id = request.form['button']
                USER_ID = request.form['participant']
                cursor = connection.cursor()
                query = "INSERT INTO EVENT_PARTICIPANTS (USER_ID, EVENT_ID) VALUES (%s, %s)"
                cursor.execute(query, [str(USER_ID), str(id)])
                cursor.close()
        return redirect(url_for('events_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()

@app.route('/add_participant_meeting',  methods=['GET', 'POST'])
def add_participant_meeting():
    try:
        if request.method == 'POST':
            with dbapi2.connect(app.config['dsn']) as connection:
                id = request.form['button']
                USER_ID = request.form['participant']
                cursor = connection.cursor()
                query = "INSERT INTO MEETING_PARTICIPANTS (USER_ID, MEETING_ID) VALUES (%s, %s)"
                cursor.execute(query, [str(USER_ID), str(id)])
                cursor.close()
        return redirect(url_for('events_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
            connection.close()


@app.route('/initdb')
def initDataBase():
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()
        cursor = connection.cursor()
        statement = "DROP TABLE IF EXISTS PHOTOS CASCADE"
        cursor.execute(statement)
        statement = """CREATE TABLE PHOTOS (
                    ID SERIAL PRIMARY KEY,
                    INFORMATION VARCHAR(300) NOT NULL,
                    PHOTOURL VARCHAR(1000) NOT NULL,
                    USERNAME VARCHAR(20)
                    )"""
        cursor.execute(statement)
        query = """DROP TABLE IF EXISTS PLACES CASCADE """
        cursor.execute(query)
        ###################################################################
        # Creating Places Table In Database, and filling it with a sample #
        ###################################################################
        # !! ADDED PLACES_ID AS PRIMARY KEY, REMOVED PRIMARY_KEY ATTR. FROM NAME
        query = """CREATE TABLE PLACES (
                PLACES_ID SERIAL PRIMARY KEY,
                NAME VARCHAR(50) NOT NULL,
                INFORMATION VARCHAR(300) NOT NULL,
                ADDRESS VARCHAR(1000) NOT NULL,
                PHONENUMBER VARCHAR(20),
                PROFILEPHOTO INTEGER REFERENCES PHOTOS(ID)
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

        ############################
        # Event and Meeting Tabels #
        ############################
        query = """DROP TABLE IF EXISTS EVENT CASCADE """
        cursor.execute(query)
        query = """CREATE TABLE EVENT (
                EVENT_ID SERIAL  PRIMARY KEY,
                NAME VARCHAR(50) NOT NULL,
                SHORT_DESCRIPTION VARCHAR(200) NOT NULL,
                DESCRIPTION VARCHAR(2000) NOT NULL,
                STARTING_DATE VARCHAR(50),
                ENDING_DATE VARCHAR(50),
                PLACE INT REFERENCES PLACES (PLACES_ID)
                )"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS MEETING CASCADE """
        cursor.execute(query)
        query = """CREATE TABLE MEETING (
                MEETING_ID SERIAL  PRIMARY KEY,
                NAME VARCHAR(50) NOT NULL,
                DESCRIPTION VARCHAR(200) NOT NULL,
                DATE VARCHAR(50),
                PLACE INT REFERENCES PLACES (PLACES_ID)
                )"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)
        # Added unique constraint, to be able to use username as login name
        query = """ CREATE TABLE USERS
            (
            USER_ID serial NOT NULL PRIMARY KEY,
            USER_NAME varchar(100) NOT NULL UNIQUE,
            BIRTHDAY date NOT NULL,
            LOCATION varchar(50) NOT NULL,
            OCUPATION varchar(50) NOT NULL,
            INTERESTS varchar(100) NOT NULL
            )"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS USER_FAVS CASCADE;"""
        cursor.execute(query)
        query = """CREATE TABLE USER_FAVS
            (
            ID SERIAL NOT NULL PRIMARY KEY,
            USER_ID INT NOT NULL,
            PLACE_ID INT NOT NULL
            );"""
        cursor.execute(query)
        query = """ALTER TABLE ONLY USER_FAVS ADD CONSTRAINT user_favs_fk_user_id FOREIGN KEY (USER_ID)
                REFERENCES USERS(USER_ID) DEFERRABLE INITIALLY DEFERRED"""
        cursor.execute(query)
        query = """ALTER TABLE ONLY USER_FAVS ADD CONSTRAINT user_favs_fk_place_id FOREIGN KEY (PLACE_ID)
                REFERENCES PLACES(PLACES_ID) DEFERRABLE INITIALLY DEFERRED"""
        cursor.execute(query)
        #
        # Creating friends table and filling it with sample data
        #
        query = """ DROP TABLE IF EXISTS FRIENDS"""
        cursor.execute(query)
        query = """
                CREATE TABLE FRIENDS (
                PERSON_ID INT NOT NULL REFERENCES USERS (USER_ID),
                FRIEND_ID INT NOT NULL REFERENCES USERS (USER_ID),
                FRIEND_STATUS INT,
                primary key (PERSON_ID, FRIEND_ID)
                )"""
        cursor.execute(query)

		################################$$
        # Event and Meeting participants #
        ##################################
        query = """DROP TABLE IF EXISTS EVENT_PARTICIPANTS"""
        cursor.execute(query)
        query = """CREATE TABLE EVENT_PARTICIPANTS(
            EVENT_ID INT REFERENCES EVENT (EVENT_ID),
            USER_ID INT REFERENCES USERS (USER_ID)
        )
        """
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS MEETING_PARTICIPANTS"""
        cursor.execute(query)
        query = """CREATE TABLE MEETING_PARTICIPANTS(
            MEETING_ID INT REFERENCES MEETING (MEETING_ID),
            USER_ID INT REFERENCES USERS (USER_ID)
        )
        """
        cursor.execute(query)
        cursor.close()
        connection.commit()
        return redirect(url_for('home_page'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return render_template('error_page.html')
    finally:
        connection.close()


@app.route('/friends', methods=['POST', 'GET'])
def friends_page():
    last_query = ""
    personID = None
    if request.method == 'POST' and request.args.get('user') is not None:
        personID = request.args.get('user')
        friendID = request.form['friendID']
        actionType = request.form['actionType']
        actionData = request.form['actionData']
        friendStatus = request.form['friendStatus']
        friendName = request.form['newfriend']
        if friendStatus == '':
            friendStatus = '0'
        if actionType == 'delete':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                pid, fid = actionData.split(',')
                query = """DELETE FROM FRIENDS WHERE PERSON_ID = %s AND FRIEND_ID=%s"""
                cursor.execute(query, (pid, fid))
                cursor.close()
        elif personID == '' or friendID == '':
            return """<script> alert('Fill the necessary inputs');
                   window.location = '/friends';</script>"""
        elif actionType == 'add':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT USER_ID FROM USERS WHERE USER_NAME = """ + friendName
                cursor.execute(query)
                newfriend = cursor.fetchall()
                if newfriend is None:
                    return """<script> alert('Fill the necessary inputs');
                                       window.location = '/friends';</script>"""
                query = """INSERT INTO FRIENDS
                           (PERSON_ID, FRIEND_ID, FRIEND_STATUS) VALUES (%s, %s, %s)"""
                data = (personID, newfriend[0], 1)
                cursor.execute(query, data)
                cursor.close()
        else:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                pid, fid = actionData.split(',')
                query = """UPDATE FRIENDS SET PERSON_ID = %s, FRIEND_ID = %s, FRIEND_STATUS = %s
                           WHERE PERSON_ID = %s AND FRIEND_ID=%s"""
                cursor.execute(query, (personID, friendID, friendStatus, pid, fid))
                cursor.close()
    if request.method == 'GET' and request.args.get('user') is not None:
        personID = request.args.get('user')
        query = """SELECT * FROM FRIENDS"""
        if personID != '' or friendID != '' or friendStatus != '':
            query += """ WHERE """
            addquery = []
            if personID != '' and personID is not None:
                addquery.append('PERSON_ID = ' + format(personID))
            for s in addquery:
                query += s
                query += """ AND """
            query = query[:-5]
            last_query = query
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if last_query != "":
            cursor.execute(last_query)
            rows = cursor.fetchall()
        else:
            rows = []
        cursor.execute("""SELECT USER_NAME, USER_ID FROM USERS""")
        users = cursor.fetchall()
        if personID is not None:
            query = """SELECT USER_NAME FROM USERS WHERE USER_ID = """ + format(personID)
            cursor.execute(query)
            user = cursor.fetchall()
        else:
            user = [['User']]
        cursor.close()
    return render_template('friends.html', rows=rows, users=users, user=user)


@app.route('/friends_init', methods=['POST', 'GET'])
def friends_init():
    if request.args.get('action') == 'drop':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ DROP TABLE IF EXISTS FRIENDS"""
            cursor.execute(query)
            cursor.close()
        return render_template('friends.html')
    elif request.args.get('action') == 'create':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ DROP TABLE IF EXISTS FRIENDS"""
            cursor.execute(query)
            query = """CREATE TABLE FRIENDS (
                       PERSON_ID INT NOT NULL REFERENCES USERS (USER_ID),
                       FRIEND_ID INT NOT NULL REFERENCES USERS (USER_ID),
                       FRIEND_STATUS INT,
                       primary key (PERSON_ID, FRIEND_ID)
                       )"""
            cursor.execute(query)
            cursor.close()
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
            cursor.close()
            return redirect('/friends')


if __name__ == '__main__':
    app.secret_key = 'itucsdb1619'
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
