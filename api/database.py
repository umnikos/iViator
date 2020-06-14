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
