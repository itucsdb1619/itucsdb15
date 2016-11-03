import psycopg2 as dbapi2

class User:
    def __init__(self, user_id, name, birthday, location, ocupation, interests):
        self.user_id = user_id
        self.name = name
        self.birthday = birthday
        self.location = location
        self.ocupation = ocupation
        self.interests = interests

class Users:
    def __init__(self, app):
        self.app = app

    def initialize_tables(self):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute ("""
                CREATE TABLE IF NOT EXISTS USERS
                (   USER_ID serial NOT NULL PRIMARY KEY,
                    NAME varchar(100) NOT NULL,
                    BIRTHDAY date NOT NULL,
                    LOCATION varchar(50) NOT NULL,
                    OCUPATION varchar(50) NOT NULL,
                    INTERESTS varchar(100) NOT NULL
                    )
                """)
            connection.commit()

    def select_user(self):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ SELECT * FROM USERS ORDER BY USER_ID"""
            cursor.execute(query)
            users = cursor.fetchall()
            return user

    def get_user(self, user_id):
        with dbapi2.connect(self.app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ SELECT * FROM USERS WHERE USER_ID = %s """
            cursor.execute(query, [user_id])
            user = cursor.fetchall()
            return user

    def add_user(self, name, birthday, location, ocupation, interests):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ INSERT INTO USER (NAME, BIRTHDAY, LOCATION, OCUPATION, INTERESTS) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (name, birthday, location, ocupation, interests))
            connection.commit()

    
    def update_user(self, user_id, name, birthday, location, ocupation, interests):
        with dbapi2.connect(self.app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """ UPDATE PLAYERS
                        SET NAME = %s,
                        BIRTHDAY = %s,
                        LOCATION = %s,
                        OCUPATION = %s,
                        INTERESTS = %s
                        WHERE
                        PLAYER_ID = %s """
                cursor.execute(query, (name, birthday, location, ocupation, interests, user_id))
                connection.commit()
    def delete_user(self, name):
        with dbapi2.connect(self.app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM USERS WHERE NAME LIKE %s ORDER BY USER_ID"""
            cursor.execute(query, ['%'+name+'%'])
            users = cursor.fetchall()
            return user