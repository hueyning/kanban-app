flaskr is a minimalist Kanban app used to organize tasks into do, doing and done depending on the progress of the task.

New users have to register before they can start setting up their own Kanban boards. After registration, the user can choose to use their kanban board or log out. If the user logs out, he/she will have to log back in with the same credentials to get access to their kanban board again.

The app supports multiple users, with each user having their personal board. Users cannot have the same username.

Project structure:
flaskr (root folder):
	- MANIFEST.in
	- setup.py
	- requirements.txt
	- test.py
	- flaskr (subfolder)
		- flaskr.db
		- flaskr.py
		- schema.sql
		- static
		- templates
flaskr/flaskr/static:
	- style.css
flaskr/flaskr/templates:
	- layout.html
	- register.html
	- login.html
	- show_entries.html
	- _formhelpers.html


Steps to setting up flaskr:

1) Create a virtual environment:
	$python3 -m venv .venv
	$source .venv/bin/activate

2) Unzip the flaskr.zip file in the virtual environment.

3) Install the requirements:
	$pip3 install -r requirements.txt

4) Install the application - in the root folder of flaskr, run: 
	$pip3 install --editable .

5) Start up the application:
	$export FLASK_APP=flaskr
	$flask run

6) Access the application at http://localhost:5000/.

7) If the db needs to be reset, type into the terminal:
    $flask initdb

Unit tests:
- In the root flaskr folder, run:
	$python3 -m unittest discover test -v
- Details on the various unit tests are commented in the test.py file.

