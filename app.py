from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing
from datetime import datetime as dt
import datetime
from datetime import timedelta


#configuration
DATABASE = '/tmp/app.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


#creates application
app = Flask(__name__)
app.config.from_object(__name__)
#app.config.from_envvar('APP SETTINGS', silent=True)


def connect_db():
	return sqlite3.connect(app.config['DATABASE'])


#initializes database
def init_db():
	#closing() helper function helps to keep connection open
	with closing(connect_db()) as db:
		#open_resource() method opens file from resource location
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()


@app.before_request
def before_request():
	g.db = connect_db()


#checks if an exception has been raised or not
@app.teardown_request
def teardown_request(exception):
	g.db.close()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def show():
	cur = g.db.execute('select company, position, date, status, contact \
						from applications order by id desc')
	applications = [dict(company=row[0], position=row[1], date=row[2],
					status=row[3], contact=row[4]) for row in cur.fetchall()]
	return render_template('show.html', applications=applications)


# must enter in date like this
@app.route('/add', methods=['POST'])
def add_application():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into applications (company, position, date, status, \
    			 contact, notes, interview) values (?, ?, ?, ?, ?, ?, ?)',
                 [request.form['company'], request.form['position'], 
                  request.form['date'], request.form['Status'],
                  request.form['contact'], request.form['notes'],
                  request.form['interview']])
    g.db.commit()
    flash('New application was successfully added')
    return redirect(url_for('show'))


@app.route('/update/<status>/<company>', methods=['POST'])
def update(status=None, company=None):
	g.db.execute('update applications set status = ? where company = ?',
							[status, company])
	g.db.commit()
	return redirect(url_for('see_company', company))


# did this
@app.route('/<comp>')
def see_company(comp=None):
	if not session.get('logged_in'):
			abort(401)
	c = g.db.execute('select company, position, date, status, contact, \
										notes, interview from applications where company = ?', 
										[comp]).fetchone()
	if c is None:
		return redirect(url_for('show'))
	return render_template('company.html', company=c)


# did this
@app.route('/status/<s>')
def show_status(s=None):
	cur = g.db.execute('select company, position, date, status, contact \
						from applications where status = ? order by id desc', [s])
	applications = [dict(company=row[0], position=row[1], date=row[2],
					status=row[3], contact=row[4]) for row in cur.fetchall()]
	return render_template('show.html', applications=applications)


@app.route('/reminder')
def reminder():
	today = dt.today()
	diff = datetime.timedelta(weeks=2)
	past = today - diff
	cur = g.db.execute('select company, contact, date from applications where \
						status = ?', ['Waiting'])
	applications = [dict(company=row[0], contact=row[1], date=row[2])
									for row in cur.fetchall()]
	print applications
	reminder = []
	for app in applications:
		if dt.strptime(app['date'], "%m/%d/%Y") < past:
			reminder.append(app)
	return render_template('reminder.html', applications = reminder)


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	#pop() will delete key from dictionary if present or do nothing
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show'))

if __name__ == '__main__':
	app.run()