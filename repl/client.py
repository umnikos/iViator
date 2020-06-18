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
    password = input("Password: ")
    r = requests.post(api_url+"login", json={'username':username, 'password':password, })
    j = r.json()
    if j['success']:
        global un
        un = username
        print("Login successful")
        login_token = j['token']
        login_token_expire = datetime.strptime(j['exp'], '%Y-%m-%d %H:%M:%S.%f')
    else:
        print("Login failed: %s" % (j['error_message'],))
    print()
    return main_screen()

def register():
    username = input("Username: ")
    password = input("Password: ")
    is_staff = input("Are you staff: ")
    if(is_staff == "yes"):
        r = requests.post(api_url+"register", json={'username':username, 'password':password, 'is_staff':True})
    else:
        r = requests.post(api_url+"register", json={'username':username, 'password':password, 'is_staff':False})
    j = r.json()
    if j['success']:
        print("Registration successful")
    else:
        print("Registration failed: %s" % (j['error_message'],))
    print()
    return main_screen()

def main_screen_logged_in():
    r = requests.get(api_url+"is_staff", json={'username':un})
    j = r.json()
    if(j['response']):
        yield '1', 'Create a flight', create_flight
        yield '2', 'Change flight status', change_flight_status
        yield '3', 'Delete flight', delete_flight
    else:
        yield '1', 'Book a flight', choose_flight
    yield 'q', 'Quit', quit

def choose_flight():
    yield '0', 'Go back', main_screen
    r = requests.get(api_url+"flights", headers = {'Authorization':login_token})
    j = r.json()
    for flight in j['flights']:
        yield str(flight[0]), f"{flight[1]} - {flight[2]}", buy_ticket(flight)

def buy_ticket(flight):
    def wrapper():
        r = requests.post(api_url+"buy_ticket", json={'fid':flight[0]}, headers = {'Authorization':login_token})
        j = r.json()
        if j['success']:
            print("Purchase successful")
        else:
            print("Purchase failed: %s" % (j['error_message'],))
        print()
        return main_screen()
    return wrapper

def create_flight():
    origin = input("Origin: ")
    destination = input("Destination: ")
    r = requests.post(api_url+"create_flight", json={'origin':origin, 'destination':destination})
    j = r.json()
    if j['success']:
        print("Flight succesfully created")
    else:
        print("Flight creation failed: %s" % (j['error_message'],))
    print()
    return main_screen()

def change_flight_status():
    status = input("Status: ")
    yield '0', 'Go back', main_screen
    r = requests.get(api_url+"flights", headers = {'Authorization':login_token})
    j = r.json()
    for flight in j['flights']:
        yield str(flight[0]), f"{flight[1]} - {flight[2]}", edit_flight_status(flight, status)

def edit_flight_status(flight, status):
    def wrapper():
        r = requests.post(api_url+"change_flight_status", json={'fid':flight.fid, 'status':status})
        j = r.json()
        if j['success']:
            print("Edit successful")
        else:
            print("Edit failed: %s" % (j['error_message'],))
        print()
    return wrapper

def delete_flight():
    status = input("Status: ")
    yield '0', 'Go back', main_screen
    r = requests.get(api_url+"flights", headers = {'Authorization':login_token})
    j = r.json()
    for flight in j['flights']:
        yield str(flight[0]), f"{flight[1]} - {flight[2]}", remove_flight(flight)

def remove_flight(flight):
    def wrapper():
        r = requests.post(api_url+"delete_flight", json={'fid':flight.fid})
        j = r.json()
        if j['success']:
            print("Deletion successful")
        else:
            print("Deletion failed: %s" % (j['error_message'],))
        print()
    return wrapper

repl(main_screen)
