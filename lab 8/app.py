from flask import Flask, request, jsonify, abort, render_template
from flasgger import Swagger
import requests
from flask_cors import CORS
from raft_election import elect_leader

app = Flask(__name__, static_folder='static')
CORS(app)
is_leader = elect_leader()
LEADER_ADDRESS = "http://leader-ip:leader-port"

followers_addresses = [
    '127.0.0.1:5002',
    '127.0.0.1:5003'
]

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "Electric Scooter Management API",
    "uiversion": 3,
}

swagger = Swagger(app, template_file='static/swagger.json')

POSTGREST_URL = 'http://localhost:3000'

def forward_to_leader(method, endpoint, data=None, params=None):
    url = f"{LEADER_ADDRESS}{endpoint}"
    headers = {'Content-Type': 'application/json'}

    try:
        if method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, json=data, headers=headers, params=params)
        return response
    except requests.RequestException as e:
        print(e)
        abort(500)

def notify_followers(data):
    for follower_address in followers_addresses:
        url = f"http://{follower_address}/sync_state"
        try:
            requests.post(url, json=data)
        except requests.RequestException as e:
            print(f"Failed to synchronize with follower {follower_address}: {e}")




@app.route('/scooters/', methods=['GET'])
def get_all_scooters():
    """Retrieve all scooters"""
    response = requests.get(f'{POSTGREST_URL}/scooter')
    if response.status_code != 200:
        abort(500)
    return jsonify(response.json())

@app.route('/scooters/', methods=['POST'])
def add_scooter():
    data = request.json

    if not is_leader:
        response = forward_to_leader('POST', '/scooters/', data)
        return jsonify(response.json()), response.status_code

    if not data or not all(key in data for key in ('name', 'battery_level')):
        abort(400)

    response = requests.post(f'{POSTGREST_URL}/scooter', json=data)
    if response.status_code != 201:
        abort(500)

    new_scooter = response.json()[0]
    notify_followers({'action': 'create', 'data': new_scooter})

    return jsonify(new_scooter), 201



@app.route('/scooters/<int:scooter_id>', methods=['GET'])
def get_specific_scooter(scooter_id):
    """Get scooter details"""
    response = requests.get(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}')
    if response.status_code != 200 or not response.json():
        abort(404)
    return jsonify(response.json()[0])

@app.route('/scooters/<int:scooter_id>', methods=['DELETE'])
def delete_scooter(scooter_id):
    if not is_leader:
        params = {'id': scooter_id}
        response = forward_to_leader('DELETE', f'/scooters/{scooter_id}', params=params)
        return jsonify(response.json()), response.status_code

    delete_password = request.headers.get('X-Delete-Password')
    if not delete_password or delete_password != "admin":
        return jsonify({"error": "Incorrect password"}), 401

    response = requests.delete(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}')
    if response.status_code != 200:
        return jsonify({"error": "Scooter not found"}), 404

    notify_followers({'action': 'delete', 'scooter_id': scooter_id})

    return jsonify({"message": "Scooter deleted successfully"}), 200


@app.route('/scooters/<int:scooter_id>', methods=['PUT'])
def update_scooter(scooter_id):
    data = request.json

    if not is_leader:
        response = forward_to_leader('PUT', f'/scooters/{scooter_id}', data)
        return jsonify(response.json()), response.status_code

    if not data:
        abort(400)

    response = requests.put(f'{POSTGREST_URL}/scooter?id=eq.{scooter_id}', json=data)
    if response.status_code != 200:
        abort(500)

    updated_scooter = response.json()[0]
    notify_followers({'action': 'update', 'scooter_id': scooter_id, 'data': updated_scooter})

    return jsonify(updated_scooter)



if __name__ == '__main__':
    app.run(debug=True)