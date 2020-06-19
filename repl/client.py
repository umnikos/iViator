from repl import *
import getpass
import requests
from datetime import datetime

login_token_expire = None
login_token = None
is_staff = False
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
    yield '2', 'Register', register(False)
    yield 'q', 'Quit', quit

def log_in():
    global login_token
    global login_token_expire
    global username
    global is_staff
    username = input("Username: ")
    password = input("Password: ")
    r = requests.post(api_url+"login", json={'username':username, 'password':password, })
    j = r.json()
    if j['success']:
        print("Login successful")
        login_token = j['token']
        login_token_expire = datetime.strptime(j['exp'], '%Y-%m-%d %H:%M:%S.%f')
        is_staff = j['is_staff']
    else:
        print("Login failed: %s" % (j['error_message'],))
    print()
    return main_screen()

def register(is_staff):
    def wrapper():
        username = input("Username: ")
        password = input("Password: ")
        r = requests.post(api_url+"register", json={'username':username, 'password':password, 'is_staff':is_staff})
        j = r.json()
        if j['success']:
            print("Registration successful")
        else:
            print("Registration failed: %s" % (j['error_message'],))
        print()
        return main_screen()
    return wrapper

def main_screen_logged_in():
    if(is_staff):
        yield '1', 'Create a flight', create_flight
        yield '2', 'Change flight status', change_flight_status
        yield '3', 'Delete flight', delete_flight
        yield '4', 'Register staff', register(True)
    else:
        yield '1', 'Book a flight', choose_flight
        yield '2', 'View booked flights', view_booked
    yield 'q', 'Quit', quit

def choose_flight():
    yield '0', 'Go back', main_screen
    r = requests.get(api_url+"flights", headers = {'Authorization':login_token})
    j = r.json()
    i = 1
    for flight in j['flights']:
        yield str(i), f"{flight[1]} -> {flight[2]}", buy_ticket(flight)
        i += 1

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

def view_booked():
    r = requests.get(api_url+"my_flights", headers = {'Authorization':login_token})
    j = r.json()
    print("Your booked flights:")
    i = 1
    for flight in j['flights']:
        print(f"{str(i)} - {flight[1]} -> {flight[2]}")
        i += 1
    input("Press enter to continue.")
    print()
    return main_screen()

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
    yield '0', 'Go back', main_screen
    r = requests.get(api_url+"flights", headers = {'Authorization':login_token})
    j = r.json()
    i = 1
    for flight in j['flights']:
        yield str(i), f"{flight[1]} -> {flight[2]} ({flight[3]})", edit_flight_status(flight)
        i += 1

def edit_flight_status(flight):
    def wrapper():
        status = input("New status: ")
        r = requests.post(api_url+"change_flight_status", json={'fid':flight[0], 'status':status})
        j = r.json()
        if j['success']:
            print("Edit successful")
        else:
            print("Edit failed: %s" % (j['error_message'],))
        print()
        return main_screen()
    return wrapper

def delete_flight():
    yield '0', 'Go back', main_screen
    r = requests.get(api_url+"flights", headers = {'Authorization':login_token})
    j = r.json()
    i = 1
    for flight in j['flights']:
        yield str(i), f"{flight[1]} -> {flight[2]} ({flight[3]})", remove_flight(flight)
        i += 1

def remove_flight(flight):
    def wrapper():
        r = requests.post(api_url+"delete_flight", json={'fid':flight[0]})
        j = r.json()
        if j['success']:
            print("Deletion successful")
        else:
            print("Deletion failed: %s" % (j['error_message'],))
        print()
        return main_screen()
    return wrapper

def handler():
    print("An error occured!")
    print("It could be caused by a connectivity issue or a server error.")
    print()
    return main_screen()

repl(main_screen, handler)
