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

@app.route('/api/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    email = data['email']
    username = data['name']
    password = data['password']

    try:
        app.logger.debug("Registration attempt ('%s', '%s')" % (username, email))

        if (db.email_exists(email)):
            app.logger.debug("Registration for '%s' failed - email already taken" % email)
            return jsonify({"success":False, "error_message":"email already registered"}), 409

        if (db.username_exists(username)):
            app.logger.debug("Registration for '%s' failed - username already taken" % username)
            return jsonify({"success":False, "error_message":"username already taken"}), 409

        if (len(password) < 8):
            app.logger.debug("Registration for '%s' failed - password too short" % username)
            return jsonify({"success":False, "error_message":"password too short"}), 422

        if (len(password) > 64):
            app.logger.debug("Registration for '%s' failed - password too long" % username)
            return jsonify({"success":False, "error_message":"password too long"}), 422

        db.add_new_user(email, username, password)
        app.logger.info("Registered new user ('%s', '%s')" % (username, email))

        return jsonify({"success":True}), 201

    except Exception as e:
        app.logger.error("Error while processing registration ('%s', '%s')\n%s" % (username, email, e))
        return jsonify({"success":False, "error_message":"internal server error"}), 500

@app.route('/api/user_exists', methods=['GET'])
def user_exists():
    data = json.loads(request.data)
    email = data['email']
    app.logger.debug("Check if email '%s' exists" % email)
    return jsonify({"success":True, "response":db.email_exists(email)}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    email = data['email']
    password = data['password']
    app.logger.debug("Attempt to login as '%s'" % email)
    if (not db.check_credentials(email, password)):
        app.logger.debug("Invalid credentials on login as '%s'" % email)
        return jsonify({"success":False, "error_message":"email or password not correct"}), 401
    app.logger.info("User '%s' logged in" % email)
    return encode_jwt(db.get_uid(email))

def encode_jwt(uid):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': uid
    }
    return jsonify({
        "success": True,
        "exp":payload["exp"],
        "token":jwt.encode(
            payload,
            jwt_secret,
            algorithm='HS256'
        ).decode('utf-8')
    }), 200

def decode_jwt(token):
    payload = jwt.decode(token.encode('utf-8'), jwt_secret)
    return payload['sub']

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
