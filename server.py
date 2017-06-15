from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
mysql = MySQLConnector(app, 'wall_db')
app.secret_key = "KSJDgn;jsnd;gJNSD:gjnKSJDNGISDni1u23kajsng"

@app.route('/')
def index():
	if 'user' not in session:
		session['user'] = ''
	return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
	email_check = request.form['email']
	print email_check
	pw_check = md5.new(request.form['password']).hexdigest()
	print pw_check

	query = "SELECT email, password FROM users WHERE email = :email"
	data = {
		'email': request.form['email']
	}
	verify = mysql.query_db(query, data)
	print verify
	if verify[0]['password'] == pw_check:
		print 'Good password!'
		session['user'] = request.form['email']
		return redirect('/success')
	else:
		flash('Invalid email or password. Please try again.')

@app.route('/register', methods=['POST'])
def register():
	errors = 0

	print "Registered!"
	name_check = re.compile(r'^[0-9]+$')
	print "name_check!"
	email_check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
	print "email_check!"

	first_name = request.form['f_name']
	print first_name
	last_name = request.form['l_name']
	print last_name
	email = request.form['email']
	print email
	password = request.form['password']
	confirm_pw = request.form['confirm_pw']
	if len(first_name) < 1:
		flash('First Name is a required field')
		errors += 1
	elif name_check.match(first_name):
		flash('First Name cannot contain numbers')
		errors += 1
	else:
		pass
	if len(last_name) < 1:
		flash('Last Name is a required field')
		errors += 1
	elif name_check.match(last_name):
		errors += 1
		flash('Last Name cannot contain numbers')
	else:
		pass
	if len(email) < 1:
		flash('Email is a required field')
		errors += 1
	elif not email_check.match(email):
		flash("Please enter a valid email address")
		errors += 1
	if len(password) < 1:
		flash('Password is a required field')
		errors += 1
	elif password != confirm_pw:
		flash('Password not confirmed, please try again. ')
		errors += 1
	else:
		hash_pw = md5.new(password).hexdigest()
	if errors == 0:
		query = "INSERT INTO users(first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
		data = {
			'first_name': first_name,
			'last_name': last_name,
			'email': email,
			'password': hash_pw
		}
		mysql.query_db(query, data)
		session['user'] = email
		return redirect('/success')

	else:
		return redirect('/')


@app.route('/success')
def success():
	query = "SELECT first_name FROM users WHERE email =  :email"
	data = {
		'email': session['user']
	}
	get_user = mysql.query_db(query, data)
	name = get_user[0]['first_name']
	print get_user
	return render_template('success.html', name=name)

@app.route('/logout', methods=['POST'])
def logout():
	session.clear()
	return redirect('/')


app.run(debug=True)
