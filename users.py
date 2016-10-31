import psycopg2 as dbapi2

class User:
    def __init__(self, user_id, name, birthday, location, ocupation, interests):
        self.user_id = user_id
        self.name = name
        self.birthday = birthday
        self.location = location
        self.ocupation = ocupation
        self.interests = interests

class Players:
    def __init__(self, app):
        self.app = app

    def initialize_tables(self):
    	with dbapi2.connect(self.app.config['dsn'] as connection):
    		cursor = connection.cursor()
    		cursor.execute ("""
    			CREATE TABLE IF NOT EXISTS USERS
    			( 	USER_ID serial NOT NULL PRIMARY KEY,
    				NAME varchar(100) NOT NULL,
    				BIRTHDAY date NOT NULL,
    				LOCATION varchar(50) NOT NULL,
    				OCUPATION varchar(50) NOT NULL,
    				INTERESTS varchar(100) NOT NULL
    				)
    			""")
    		connection.commit()

    def add_user(self, name, birthday, location, ocupation, interests):
    	with dbapi2.connect(self.app.config['dsn'] as connection):
    		cursor = connection.cursor()
    		query = """ INSERT INTO USER (NAME, BIRTHDAY, LOCATION, OCUPATION, INTERESTS) VALUES (%s, %s, %s)"""
    		cursor.execute(query, (name, birthday, location, ocupation, interests))
    		connection.commit()