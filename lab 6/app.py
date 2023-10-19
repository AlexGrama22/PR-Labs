from flask import Flask, request, jsonify, abort, render_template
from flasgger import Swagger
import requests

app = Flask(__name__)

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "Electric Scooter Management API",
    "uiversion": 3,
}

swagger = Swagger(app, template_file='static/swagger.json')

POSTGREST_URL = 'http://localhost:3000'

@app.route('/scooters/', methods=['GET'])
def get_all_scooters():
    """Retrieve all scooters"""
    response = requests.get(f'{POSTGREST_URL}/scooter')
    if response.status_code != 200:
        abort(500)
    return jsonify(response.json())

@app.route('/scooters/', methods=['POST'])
def add_scooter():
    """Add a new scooter"""
    data = request.json
    if not data or not all(key in data for key in ('name', 'battery_level')):
        abort(400)

    response = requests.post(f'{POSTGREST_URL}/scooter', json=data)
    if response.status_code != 201:
        abort(500)
    return jsonify(response.json()[0]), 201

@app.route('/scooters/<int:scooter_id>', methods=['GET'])
def get_specific_scooter(scooter_id):
    """Get scooter details"""
    response = requests.get(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}')
    if response.status_code != 200 or not response.json():
        abort(404)
    return jsonify(response.json()[0])

@app.route('/scooter', methods=['DELETE'])
def delete_scooter():
    scooter_id = request.args.get('id')
    delete_password = request.headers.get('X-Delete-Password')
    if not delete_password or delete_password != "admin":
        return jsonify({"error": "Incorrect password"}), 401

    if scooter_id == "1":
        return jsonify({"message": "Scooter deleted successfully"}), 200
    return jsonify({"error": "Scooter not found"}), 404

@app.route('/scooters/<int:scooter_id>', methods=['PUT'])
def update_scooter(scooter_id):
    """Update scooter details"""
    data = request.json
    if not data or not any(key in data for key in ('name', 'battery_level')):
        abort(400)

    response = requests.put(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}', json=data)
    if response.status_code != 200:
        abort(500)
    return jsonify(response.json()[0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
