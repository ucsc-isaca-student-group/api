import pymysql
from app import app
from db_conf import mysql
from flask import jsonify
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import generate_password_hash, check_password_hash
import json
from collections import OrderedDict

class User(object):	
	def __init__(self, id, username):
		self.id = id
		self.username = username

	def __str__(self):
		return "User(id='%s')" % self.id

@app.route('/players')
def get_players():
	conn = mysql.connect()
	cursor = conn.cursor(pymysql.cursors.DictCursor)
	cursor.execute("SELECT id,username,name,photo FROM info WHERE extra != 0")
	data = cursor.fetchall()
	response = list()

	for row in data:
		print(row)
		response.append(row)
	
	return json.dumps({"players": response}), 200

@app.route('/player/<username>')
def get_player(username):
	conn = mysql.connect()
	cursor = conn.cursor(pymysql.cursors.DictCursor)
	cursor.execute("SELECT id FROM user WHERE username=%s", username)
	data = cursor.fetchone()
	print(data)
	cursor.execute("SELECT id,name,description,moreinfo,photo FROM info WHERE extra != 0 and id = %s", data['id'])
	data = cursor.fetchone()
	if data:
		return json.dumps({"information": data}), 200
	else:
		cursor.execute("SELECT count(*) AS count FROM info WHERE id = %s",id)
		data = cursor.fetchone()
		print(data)
		if data["count"]>0:
			return json.dumps({"information": "You dont have Permission"}), 401
		else:
			return json.dumps({"information": "No User Found"}), 404

@app.route('/generateHash/<psd>')
def get_password(psd):
	password = generate_password_hash(psd)	
	return json.dumps({"hash": password}), 200 

@app.route('/profile')
@jwt_required()
def get_response():
	conn = mysql.connect()
	print(current_identity[2])
	cursor = conn.cursor(pymysql.cursors.DictCursor)
	cursor.execute("SELECT type,flag FROM user where id = %s",str(current_identity[0]))
	data = cursor.fetchone()
	if data:
		return json.dumps({"information": data}), 200
	else:
		return json.dumps({"information": "No information"}), 200
	# return jsonify('You are an authenticate person to see this message')

def authenticate(username, password):	
	if username and password:
		conn = None;
		cursor = None;
		try:
			conn = mysql.connect()
			cursor = conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute("SELECT id, username, password, type FROM user WHERE username=%s", username)
			row = cursor.fetchone()
			
			if row:
				if check_password_hash(row['password'], password):
					return User(row['id'], row['username'])
			else:
				return None
		except Exception as e:
			print(e)
		finally:
			cursor.close() 
			conn.close()
	return None

def identity(payload):
	if payload['identity']:
		conn = None;
		cursor = None;
		try:
			conn = mysql.connect()
			cursor = conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute("SELECT id,username,type FROM user WHERE id=%s", payload['identity'])
			row = cursor.fetchone()
			
			if row:
				return (row['id'], row['username'], row['type'])
			else:
				return None
		except Exception as e:
			print(e)
		finally:
			cursor.close() 
			conn.close()
	else:
		return None
	
jwt = JWT(app, authenticate, identity)

if __name__ == "__main__":
    app.run(debug=true,host='0.0.0.0')