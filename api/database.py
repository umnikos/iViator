import sqlite3
import hashlib
import threading

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class DB:
    def __init__(self, db_name='database.sqlite3'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS `users` (
            `uid` INTEGER PRIMARY KEY AUTOINCREMENT,
            `email` TEXT NOT NULL UNIQUE,
            `username` TEXT NOT NULL UNIQUE,
            `password` TEXT NOT NULL
        )''')
        self.conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS flights (
            fid INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            status TEXT NOT NULL UNIQUE
        )''')
        self.conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            fid INTEGER,
            uid INTEGER,
            FOREIGN KEY(fid) REFERENCES flights(fid),
            FOREIGN KEY(uid) REFERENCES users(uid)
        )''')
        self.conn.commit()
        self.conn_lock = threading.Lock()

    def sql_select1(self, query, params):
        self.conn_lock.acquire()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        self.conn_lock.release()
        return result

    def sql_select(self, query, params):
        self.conn_lock.acquire()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        self.conn_lock.release()
        return result

    def sql_execute(self, query, params):
        self.conn_lock.acquire()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = cursor.rowcount
        self.conn.commit()
        self.conn_lock.release()
        return result

    def email_exists(self, email):
        query = """SELECT email FROM users WHERE email = ?"""
        result = self.sql_select1(query, (email,))
        return bool(result)

    def username_exists(self, username):
        query = """SELECT username FROM users WHERE username = ?"""
        result = self.sql_select1(query, (username,))
        return bool(result)

    def add_new_user(self, email, username, password):
        query = """INSERT INTO users (email, username, password) VALUES (?,?,?)"""
        self.sql_execute(query, (email, username,hash_password(password)))

    def check_credentials(self, email, password):
        query = """SELECT email FROM users WHERE email = ? AND password = ?"""
        result = self.sql_select1(query, (email,hash_password(password)))
        return bool(result)

    def get_uid(self, email):
        query = """SELECT uid FROM users WHERE email = ?"""
        result = self.sql_select1(query, (email,))
        return result[0]

    def add_new_flight(self, origin, destination):
        query = """INSERT INTO flights (origin, destination, status) VALUES (?,?,?)"""
        self.sql_execute(query, (origin, destination, "pending"))

    def get_flight_information(self, fid):
        query = """SELECT origin, destination, status FROM flights WHERE fid = ?"""
        result = self.sql_select1(query, (fid,))
        return result

    def change_flight_status(self, fid, status):
        query = """UPDATE flights SET status = ? WHERE fid = ?"""
        self.sql_execute(query, (status, fid))

    def delete_flight_id(self, fid):
        query = """DELETE FROM flights WHERE fid = ?"""
        self.sql_execute(query, (fid,))

    def delete_flight_destination(self, destination):
        query = """DELETE FROM flights WHERE destination = ?"""
        self.sql_execute(query, (destination,))

    def delete_flight_origin(self, origin):
        query = """DELETE FROM flights WHERE origin = ?"""
        self.sql_execute(query, (origin,))

    def add_new_ticket(self, fid, uid):
        query = """INSERT INTO tickets (fid, uid) VALUES (?,?)"""
        self.sql_execute(query, (fid, uid))

    def get_user_flight_id(self, uid)
        query = """ SELECT fid FROM tickets WHERE uid = ?"""
        result = self.sql_select1(query, (uid,))
        return result[0]

    def get_user_flight_destination(self, uid):
        query = """ SELECT f.destination
        FROM Tickets t
        INNER JOIN Flights f ON f.fid = t.fid
        WHERE t.uid = ?"""
        result = self.sql_select1(query, (uid,))
        return result[0]

    def get_user_flight_origin(self, uid):
        query = """ SELECT f.origin
        FROM Tickets t
        INNER JOIN Flights f ON f.fid = t.fid
        WHERE t.uid = ?"""
        result = self.sql_select1(query, (uid,))
        return result[0]

    def get_user_flight_count(self, uid):
        query = """ SELECT COUNT(t.fid)
        FROM users u
        INNER JOIN tickets t ON t.uid = u.uid
        WHERE u.uid = ?"""
        result = self.sql_select1(query, (uid,))
        return result[0]
