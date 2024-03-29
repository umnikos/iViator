#!/usr/bin/env nix-shell
#!nix-shell --pure -i python3 -p "python37.withPackages (pkgs: with python37Packages; [ flask flask-httpauth pyjwt flask-cors ])"

import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
from secrets import jwt_secret

import database
import jwt
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
db = database.DB()

### LOGIN & REGISTER ###

@app.route('/api/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    username = data['username']
    password = data['password']
    try:
        token = request.headers['Authorization']
        uid = decode_jwt(token)
        if db.is_staff(uid):
            is_staff = data['is_staff']
    except:
        is_staff = False

    try:
        app.logger.debug("Registration attempt '%s'" % (username,))

        if (db.username_exists(username)):
            app.logger.debug("Registration for '%s' failed - username already taken" % username)
            return jsonify({"success":False, "error_message":"username already taken"}), 409

        if (len(password) < 8):
            app.logger.debug("Registration for '%s' failed - password too short" % username)
            return jsonify({"success":False, "error_message":"password too short"}), 422

        if (len(password) > 64):
            app.logger.debug("Registration for '%s' failed - password too long" % username)
            return jsonify({"success":False, "error_message":"password too long"}), 422

        db.add_new_user(is_staff, username, password)
        app.logger.info("Registered new user '%s'" % (username,))

        return jsonify({"success":True}), 201

    except Exception as e:
        app.logger.error("Error while processing registration '%s'\n%s" % (username, e))
        return jsonify({"success":False, "error_message":"internal server error"}), 500

@app.route('/api/user_exists', methods=['GET'])
def user_exists():
    data = json.loads(request.data)
    username = data['username']
    app.logger.debug("Check if username '%s' exists" % username)
    return jsonify({"success":True, "response":db.username_exists(username)}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    username = data['username']
    password = data['password']
    app.logger.debug("Attempt to login as '%s'" % username)
    if (not db.check_credentials(username, password)):
        app.logger.debug("Invalid credentials on login as '%s'" % username)
        return jsonify({"success":False, "error_message":"username or password not correct"}), 401
    app.logger.info("User '%s' logged in" % username)
    return encode_jwt(db.get_uid(username))

def encode_jwt(uid):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': uid
    }
    return jsonify({
        "success": True,
        "is_staff": db.is_staff(uid),
        "exp": '{}'.format(payload["exp"]),
        "token":jwt.encode(
            payload,
            jwt_secret,
            algorithm='HS256'
        ).decode('utf-8')
    }), 200

def jwt_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"success":False, "error_message":"expired token"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success":False, "error_message":"invalid token"}), 400
    return wrapper

def decode_jwt(token):
    payload = jwt.decode(token.encode('utf-8'), jwt_secret)
    return payload['sub']

### FLIGHT BOOKING ###

@jwt_handler
@app.route('/api/flights', methods=['GET'])
def list_flights():
    token = request.headers['Authorization']
    uid = decode_jwt(token)
    if db.is_staff(uid):
        flights = db.get_all_flights()
    else:
        flights = db.get_pending_flights()
    return jsonify({"success":True, "flights":flights}), 200

@jwt_handler
@app.route('/api/my_flights', methods=['GET'])
def my_flights():
    token = request.headers['Authorization']
    uid = decode_jwt(token)
    flights = db.get_user_flights(uid)
    return jsonify({"success":True, "flights":flights}), 200

@jwt_handler
@app.route('/api/buy_ticket', methods=['POST'])
def buy_ticket():
    data = json.loads(request.data)
    fid = data['fid']
    token = request.headers['Authorization']
    uid = decode_jwt(token)
    db.add_new_ticket(fid, uid)
    return jsonify({"success":True}), 200

@jwt_handler
@app.route('/api/create_flight', methods=['POST'])
def create_flight():
    data = json.loads(request.data)
    origin = data['origin']
    destination = data['destination']
    db.add_new_flight(origin, destination)
    return jsonify({"success":True}), 200

@jwt_handler
@app.route('/api/change_flight_status', methods=['POST'])
def change_flight_status():
    data = json.loads(request.data)
    fid = data['fid']
    status = data['status']
    db.change_flight_status(fid, status)
    return jsonify({"success":True}), 200

@jwt_handler
@app.route('/api/delete_flight', methods=['POST'])
def delete_flight():
    data = json.loads(request.data)
    fid = data['fid']
    db.delete_flight_id(fid)
    return jsonify({"success":True}), 200

### MAIN ###

if jwt_secret == "[temporary]":
    print("WARNING: Please replace the jwt secret in secrets.py to a real secret.")

if __name__ == '__main__':
    today = datetime.date.today().strftime("%d%m%y")
    handler = RotatingFileHandler(
        "%s.log" % today,
        maxBytes = 10000,
        backupCount = 1
    )
    formatter = logging.Formatter(
        "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')
