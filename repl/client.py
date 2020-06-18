from repl import *
import getpass
import requests
from datetime import datetime

login_token_expire = None
login_token = None
api_url = "http://localhost:5000/api/"

def quit():
    pass # no options given

def main_screen():
    check_token_expired()
    print("Main menu:")
    if login_token:
        return main_screen_logged_in()
    else:
        return main_screen_not_logged_in()

def check_token_expired():
    global login_token
    global login_token_expire
    if login_token_expire:
        if login_token_expire < datetime.now():
            login_token = None
            login_token_expire = None

def main_screen_not_logged_in():
    yield '1', 'Log in', log_in
    yield '2', 'Register', register
    yield 'q', 'Quit', quit

def log_in():
    global login_token
    global login_token_expire
    username = input("Username: ")
    password = getpass.getpass()
    r = requests.post(api_url+"login", json={'username':username, 'password':password})
    j = r.json()
    if j['success']:
        print("Login successful")
        login_token = j['token']
        login_token_expire = datetime.strptime(j['exp'], '%Y-%m-%d %H:%M:%S.%f')
    else:
        print("Login failed: %s" % (j['error_message'],))
    print()
    return main_screen()

def register():
    username = input("Username: ")
    password = getpass.getpass()
    r = requests.post(api_url+"register", json={'username':username, 'password':password})
    j = r.json()
    if j['success']:
        print("Registration successful")
    else:
        print("Registration failed: %s" % (j['error_message'],))
    print()
    return main_screen()

def main_screen_logged_in():
    yield '0', 'Not implemented', main_screen

repl(main_screen)
