from flask import Flask, request, jsonify, abort
import psycopg2
from flask_swagger_ui import get_swaggerui_blueprint
from psycopg2 import sql

app = Flask(__name__)

class Database:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="scooters",
            user="admin",
            password="admin",
            host="localhost",
            port="5432"
        )

    def __enter__(self):
        return self.connection.cursor()

    def __exit__(self, type, value, traceback):
        self.connection.commit()
        self.connection.close()

def get_scooter_data(scooter):
    return {'id': scooter[0], 'name': scooter[1], 'battery_level': scooter[2]}

@app.route('/scooters/', methods=['GET'])
def get_all_scooters():
    with Database() as cursor:
        cursor.execute("SELECT id, name, battery_level FROM scooter")
        return jsonify([get_scooter_data(scooter) for scooter in cursor.fetchall()])

@app.route('/scooters/', methods=['POST'])
def add_scooter():
    data = request.json
    if not data or not all(key in data for key in ('name', 'battery_level')):
        abort(400)

    with Database() as cursor:
        insert = sql.SQL("INSERT INTO scooter (name, battery_level) VALUES (%s, %s) RETURNING id")
        cursor.execute(insert, (data['name'], data['battery_level']))
        new_scooter_id = cursor.fetchone()[0]

    return jsonify({'id': new_scooter_id, **data}), 201

@app.route('/scooters/<int:scooter_id>', methods=['GET'])
def get_specific_scooter(scooter_id):
    with Database() as cursor:
        cursor.execute("SELECT id, name, battery_level FROM scooter WHERE id = %s", (scooter_id,))
        scooter = cursor.fetchone()

    if scooter is None:
        abort(404)

    return jsonify(get_scooter_data(scooter))

@app.route('/scooters/<int:scooter_id>', methods=['PUT'])
def modify_scooter(scooter_id):
    data = request.json
    if not data:
        abort(400)

    with Database() as cursor:
        update = sql.SQL("UPDATE scooter SET name = %s, battery_level = %s WHERE id = %s")
        cursor.execute(update, (data['name'], data['battery_level'], scooter_id))

    return jsonify({'id': scooter_id, **data})

@app.route('/scooters/<int:scooter_id>', methods=['DELETE'])
def remove_scooter(scooter_id):
    if request.headers.get('X-Delete-Password') != 'admin':
        return jsonify({"error": "Incorrect password"}), 401

    with Database() as cursor:
        cursor.execute("DELETE FROM scooter WHERE id = %s", (scooter_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Scooter not found"}), 404

    return jsonify({"message": "Scooter deleted successfully"}), 200

# Swagger documentation
swagger_config = get_swaggerui_blueprint(
    '/api/docs',
    '/static/swagger.json',
    config={'app_name': "Scooter API"}
)

app.register_blueprint(swagger_config, url_prefix='/api/docs')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
