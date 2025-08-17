#!/usr/bin/python3

from flask import Flask, abort, request, jsonify
import logging
import mysql.connector

logging.basicConfig(
    format = '%(asctime)s %(levelname)s %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    filename = "/var/log/app/app.log",
    level = logging.INFO
)

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='your-rds-endpoint.amazonaws.com',
        user='your_rds_username',
        password='your_rds_password',
        database='your_database'
    )

@app.route('/v1/color', methods=['GET'])
def get_color():
    try:
        color_name = request.args['name']
        color_hash = request.args['hash']
        ret = {'code': '', 'name': ''}
        if color_name == 'red':
            ret['code'] = 'f34a07'
            ret['name'] = 'orange'
        elif color_name == 'blue':
            ret['code'] = '71f0f9'
            ret['name'] = 'sky'
        else:
            ret['code'] = 'ff00ff'
            ret['name'] = 'pink'
        return jsonify(ret), 200
    except Exception as e:
        logging.error(e)
        abort(500)

@app.route('/health', methods=['GET'])
def get_health():
    try:
        ret = {'status': 'ok'}
        return jsonify(ret), 200
    except Exception as e:
        logging.error(e)
        abort(500)

@app.route('/v1/user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        username = data['username']
        email = data['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'id': user_id, 'username': username, 'email': email}), 201
    except Exception as e:
        logging.error(e)
        abort(500)

@app.route('/v1/user', methods=['GET'])
def get_user():
    try:
        user_id = request.args.get('id')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return jsonify(user), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(e)
        abort(500)

@app.route('/v1/user', methods=['DELETE'])
def delete_user():
    try:
        user_id = request.args.get('id')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'result': 'User deleted'}), 200
    except Exception as e:
        logging.error(e)
        abort(500)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
