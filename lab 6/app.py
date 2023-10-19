from flask import Flask, request, jsonify, abort
import requests

app = Flask(__name__)

POSTGREST_URL = 'http://localhost:3000'

@app.route('/scooters/', methods=['GET'])
def get_all_scooters():
    response = requests.get(f'{POSTGREST_URL}/scooter')
    if response.status_code != 200:
        abort(500)
    return jsonify(response.json())

@app.route('/scooters/', methods=['POST'])
def add_scooter():
    data = request.json
    if not data or not all(key in data for key in ('name', 'battery_level')):
        abort(400)

    response = requests.post(f'{POSTGREST_URL}/scooter', json=data)
    if response.status_code != 201:
        abort(500)
    return jsonify(response.json()[0]), 201

@app.route('/scooters/<int:scooter_id>', methods=['GET'])
def get_specific_scooter(scooter_id):
    response = requests.get(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}')
    if response.status_code != 200 or not response.json():
        abort(404)
    return jsonify(response.json()[0])

@app.route('/scooters/<int:scooter_id>', methods=['PUT'])
def modify_scooter(scooter_id):
    data = request.json
    if not data:
        abort(400)

    response = requests.patch(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}', json=data)
    if response.status_code != 204:
        abort(500)
    return jsonify({'id': scooter_id, **data})

@app.route('/scooters/<int:scooter_id>', methods=['DELETE'])
def remove_scooter(scooter_id):
    if request.headers.get('X-Delete-Password') != 'admin':
        return jsonify({"error": "Incorrect password"}), 401

    response = requests.delete(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}')
    if response.status_code != 204:
        return jsonify({"error": "Scooter not found"}), 404
    return jsonify({"message": "Scooter deleted successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
