# all the imports
import os
import sqlite3
from functools import wraps
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key'))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#registration
class RegistrationForm(Form):
	#basic validators for form fields
    username = TextField('Username', [validators.Length(min=1, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

@app.route('/register', methods=["GET","POST"])
def register():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))

            db = get_db()
            cur = db.execute('select * from users where username = ?', [username])
            count = cur.fetchall()

            #if username already exists in db, ask user to choose a different username.
            if len(count) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                db.execute("INSERT INTO users (username, password, email) VALUES (?,?,?)",[username,password,email])
                
                db.commit()
                flash("Thanks for registering!")

                #once user has registered, they are automtically logged in.
                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('show_entries'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))

#login required decorator to wrap routes that require login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login or register to view your Kanban!")
            return redirect(url_for('login'))

    return wrap

#login route
@app.route('/login', methods=["GET","POST"])
def login():
    error = ''
    try:
        db = get_db()
        if request.method == "POST":

            cur = db.execute("select * from users where username = ?",[request.form['username']])
            data = cur.fetchone()[2]

            #ensure that hashed password from login form matches password in db for same username.
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("show_entries"))

            else:
                error = " Invalid credentials, try again."

        return render_template("login.html", error=error)

    except Exception as e:
    	error = " Invalid credentials, try again."
    	return render_template("login.html", error = error)

#logout route
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for('login'))

#show entries
@app.route('/')
@login_required
def show_entries():
    db = get_db()

    #get specific user_id to present personal user kanban board by referencing current session's username.
    useridcur = db.execute('select id from users where username=?',[session['username']])
    userid = useridcur.fetchone()[0]

    cur = db.execute('select id, title, text from DO where status="DO" and user_id=? order by id desc',[userid])
    do = cur.fetchall()
    cur = db.execute('select id, title, text from DO where status="DOING" and user_id=? order by id desc',[userid])
    doing = cur.fetchall()
    cur = db.execute('select id, title, text from DO where status="DONE" and user_id=? order by id desc',[userid])
    done = cur.fetchall()
    return render_template('show_entries.html', do=do, doing=doing, done=done)


#create task
@app.route('/do', methods=['POST'])
def do():
    db = get_db()
    #insert task with user_id as foreign key so that personal board can be retrieved when user logs back in.
    useridcur = db.execute('select id from users where username=?',[session['username']])
    userid = useridcur.fetchone()[0]
    db.execute('insert into DO (title, text, status, user_id) values (?, ?, ?, ?)',
                 [request.form['title'], request.form['text'], "DO", userid])
    db.commit()
    return redirect(url_for('show_entries'))

#change status to doing
@app.route('/doing', methods=['POST'])
def doing():
    db = get_db()
    db.execute('update DO set status="DOING" where id=?',[request.form['id']])
    db.commit()
    return redirect(url_for('show_entries'))

#change status to done
@app.route('/done', methods=['POST'])
def done():
    db = get_db()
    db.execute('update DO set status="DONE" where id=?',[request.form['id']])
    db.commit()
    return redirect(url_for('show_entries'))

#delete entries
@app.route('/delete', methods=['POST'])
def delete():
   	db = get_db()
   	db.execute('delete from DO where id = ?', [request.form['id']])
   	db.commit()
   	return redirect(url_for('show_entries'))






