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
            `username` TEXT NOT NULL UNIQUE,
            `password` TEXT NOT NULL,
            `staff` BOOLEAN NOT NULL
        )''')
        self.conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS flights (
            fid INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            status TEXT NOT NULL
        )''')
        self.conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            fid INTEGER,
            uid INTEGER,
            FOREIGN KEY(fid) REFERENCES flights(fid) ON DELETE CASCADE,
            FOREIGN KEY(uid) REFERENCES users(uid) ON DELETE CASCADE
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

    def username_exists(self, username):
        query = """SELECT username FROM users WHERE username = ?"""
        result = self.sql_select1(query, (username,))
        return bool(result)

    def add_new_user(self, staff, username, password):
        query = """INSERT INTO users (staff, username, password) VALUES (?,?,?)"""
        self.sql_execute(query, (staff, username,hash_password(password)))

    def check_credentials(self, username, password):
        query = """SELECT username FROM users WHERE username = ? AND password = ?"""
        result = self.sql_select1(query, (username,hash_password(password)))
        return bool(result)

    def get_uid(self, username):
        query = """SELECT uid FROM users WHERE username = ?"""
        result = self.sql_select1(query, (username,))
        return result[0]

    def is_staff(self, uid):
        query = """SELECT staff FROM users WHERE uid = ?"""
        result = self.sql_select1(query, (uid,))
        return bool(result[0])

    def add_new_flight(self, origin, destination):
        query = """INSERT INTO flights (origin, destination, status) VALUES (?,?,?)"""
        self.sql_execute(query, (origin, destination, "pending"))

    def get_pending_flights(self):
        query = """SELECT fid, origin, destination FROM flights WHERE status = 'pending'"""
        result = self.sql_select(query, ())
        return result

    def get_all_flights(self):
        query = """SELECT fid, origin, destination, status FROM flights"""
        result = self.sql_select(query, ())
        return result

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

    def add_new_ticket(self, fid, uid):
        query = """INSERT INTO tickets (fid, uid) VALUES (?,?)"""
        self.sql_execute(query, (fid, uid))

    def get_user_flights(self, uid):
        query = """SELECT f.fid, origin, destination
        FROM tickets t
        INNER JOIN flights f ON t.uid = ? AND f.fid = t.fid
        """
        result = self.sql_select(query, (uid,))
        return result
