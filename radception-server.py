import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
import json
import flask
from flask_cors import CORS, cross_origin

app = flask.Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

cred = credentials.Certificate('./radception-database-credentials.json')
firebase_admin.initialize_app(cred, options={
    'databaseURL': 'https://radception-database.firebaseio.com'
})
USERS = db.reference('users')
DEVICES = db.reference('devices')

@app.route("/")
@cross_origin()
def hello():
    return "Hello World!"

@app.route('/users', methods=['POST'])
@cross_origin()
def create_user():
    req = flask.request.json
    user = USERS.child(req["username"]).set(req)
    return flask.jsonify({'id': user.key}), 201

@app.route('/users/<id>')
@cross_origin()
def read_user(id):
    return flask.jsonify(_ensure_user(id))

@app.route('/users/<id>', methods=['PUT'])
@cross_origin()
def update_user(id):
    _ensure_user(id)
    req = flask.request.json
    USERS.child(id).update(req)
    return flask.jsonify({'success': True})

@app.route('/users/<id>', methods=['DELETE'])
@cross_origin()
def delete_user(id):
    _ensure_user(id)
    USERS.child(id).delete()
    return flask.jsonify({'success': True})

def _ensure_user(id):
    user = USERS.child(id).get()
    if not user:
        flask.abort(404)
    return user

current_readings = [[], 0, 0]

@app.route('/devices', methods=['POST'])
@cross_origin()
def create_device():
    req = flask.request.json
    device = DEVICES.child(req["device_id"]).set(req)
    return flask.jsonify({'id': device.key}), 201

@app.route('/devices/<id>')
@cross_origin()
def read_device(id):
    return flask.jsonify(_ensure_device(id))

@app.route('/devices/<id>', methods=['PUT'])
@cross_origin()
def update_device(id):
    _ensure_device(id)
    req = flask.request.json
    device_id = req["device_id"]
    timestamp = int(req["timestamp"])
    reading = float(req["reading"])
    longitude = float(req["longitude"])
    latitude = float(req["latitude"])
    current_readings[0].append([timestamp, reading])
    current_readings[1] = longitude
    current_readings[2] = latitude
    if len(current_readings[0]) > 60:
        del current_readings[0][0]
    read = {"currentreadings": current_readings}
    DEVICES.child(id).update(read)
    return flask.jsonify({'success': True})

@app.route('/devices/<id>', methods=['DELETE'])
@cross_origin()
def delete_device(id):
    _ensure_device(id)
    DEVICES.child(id).delete()
    return flask.jsonify({'success': True})

def _ensure_device(id):
    device = DEVICES.child(id).get()
    if not device:
        flask.abort(404)
    return device