from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
mysql = MySQLConnector(app, 'wall_db')
app.secret_key = "KSJDgn;jsnd;gJN:gjnKSJDNGISDni1u23kajsng"

@app.route('/')
def index():
	#check to see if user is logged in or not.
	if  'user_id' not in session or session['user_id'] < 1:
		session['user'] = ''
		session['user_id'] = 0
		return render_template('index.html')
	elif session['user_id'] > 0:
		return redirect('/wall')

@app.route('/login', methods=['POST'])
def login():
	#Prep email and pw for login verification
	email_check = request.form['email']
	pw_check = md5.new(request.form['password']).hexdigest()

	query = "SELECT email, password, id FROM users WHERE email = :email"
	data = {
		'email': request.form['email']
	}
	verify = mysql.query_db(query, data)
	if len(verify) == 0:
		print "No email!"
		flash ("Invalid email or password. Please try again.")
		return redirect('/')
	elif verify[0]['password'] == pw_check:
		print 'Good password!'
		session['user'] = request.form['email']
		session['user_id'] = verify[0]['id']
		return redirect('/wall')
	else:
		flash('Invalid email or password. Please try again.')
		return redirect('/')

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
		user_id = mysql.query_db(query, data)
		session['user'] = email
		session['user_id'] = user_id
		return redirect('/wall')

	else:
		return redirect('/')

@app.route('/wall')
def wall():
	if session['user_id'] < 1:
		return redirect('/')

	msg_query = "SELECT messages.id, messages.message, messages.user_id, concat(users.first_name, ' ', users.last_name) as user_name, concat(MONTHNAME(messages.created_at), ' ', DAY(messages.created_at), ' ', YEAR(messages.created_at)) as submit_date FROM messages JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC"

	com_query = "SELECT comments.id, comments.comment, comments.message_id, concat(users.first_name, ' ', users.last_name) as user_name, concat(MONTHNAME(messages.created_at), ' ', DAY(messages.created_at), ' ', YEAR(messages.created_at)) as submit_date FROM comments JOIN users ON comments.user_id = users.id JOIN messages ON comments.message_id = messages.id ORDER BY comments.created_at ASC"
	wall_msgs = mysql.query_db(msg_query)
	wall_coms = mysql.query_db(com_query)
	return render_template('wall.html', messages=wall_msgs, comments=wall_coms)


@app.route('/new_message', methods=['POST'])
def new_message():
	query = "INSERT INTO messages(message, user_id, created_at, updated_at) VALUES(:message, :user_id, NOW(), NOW())"
	data ={
		'message': request.form['message'],
		'user_id': session['user_id']
	}
	message_id = mysql.query_db(query, data)
	return redirect('/wall')

@app.route('/new_comment', methods=['POST'])
def new_comment():
	query = "INSERT INTO comments(comment, user_id, message_id, created_at, updated_at) VALUES(:comment, :user_id, :message_id, NOW(), NOW())"
	data ={
		'comment': request.form['comment'],
		'user_id': session['user_id'],
		'message_id': request.form['message_id']
	}
	print data
	comment_id = mysql.query_db(query, data)
	return redirect('/wall')

@app.route('/logout', methods=['POST'])
def logout():
	session.clear()
	return redirect('/')


app.run(debug=True)
