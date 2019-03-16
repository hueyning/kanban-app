import os
from flaskr import flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):
    #Setting up temp database and initializing it to get simple interface to app.
    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    #root of app should have login as part of output since unlogged in users are redirected to login page.
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'login' in rv.data

    #Testing registration by following the redirect after a new user registers.
    def register(self,username,email,password,confirm):
        return self.app.post('/register', data=dict(
                username=username,
                email=email,
                password=password,
                confirm=confirm
        ),follow_redirects=True)

    #validated user registrations should be greeted with thanks for registering!
    def test_register(self):
        rv = self.register('admins', 'admin@email.com', 'default', 'default')
        assert b'Thanks for registering' in rv.data
        rv = self.register('Jack', 'sparrow@blackpearl.com', 'rum', 'rum')
        assert b'Thanks for registering' in rv.data

    #Duplicate username results in error message: username is already taken.
    def test_register_duplicate_user(self):
        rv = self.register('Jack', 'sparrow@blackpearl.com', 'default', 'default')
        rv = self.register('Jack', 'sparrow@blackpearl.com', 'rum', 'rum')
        assert b'username is already taken' in rv.data

    #unmatching passwords will alert error to user
    def test_register_nonmatching_pass(self):
        rv = self.register('Josh', 'sparrow@blackpearl.com', 'rum', 'beer')
        assert b'Passwords must match' in rv.data

    #Testing login and logout page by following the redirect.
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    #Test login and logout by registering a user, Jack, logging him out, then logging him back in with the right credentials. 
    #The appropriate messages of "logged in" and "logged out" should be shown.
    def test_login_logout_valid(self):
        rv = self.register('Jack', 'sparrow@blackpearl.com', 'rum', 'rum')
        rv = self.logout()
        assert b'You have been logged out' in rv.data
        rv = self.login('Jack', 'rum')
        assert b'You are now logged in' in rv.data
        rv = self.logout()
        assert b'You have been logged out' in rv.data

    #test invalid credential login by logging in an unregistered user
    def test_login_unregistered_user(self):
        rv = self.login('blablablabla', 'default')
        assert b'Invalid' in rv.data
        rv = self.login('Jackkk', 'defaultx')
        assert b'Invalid' in rv.data    

    #test invalid credential login by logging in registered user with wrong password
    def test_login_logout_valid(self):
        rv = self.register('Jack', 'sparrow@blackpearl.com', 'rum', 'rum')
        rv = self.logout()
        assert b'You have been logged out' in rv.data
        rv = self.login('Jack', 'rom')
        assert b'Invalid' in rv.data

    #test that tasks can be added to todo table
    def test_add_todo(self):
        self.register('Jack', 'sparrow@blackpearl.com', 'rum', 'rum')
        rv = self.app.post('/do', data=dict(
            title='Buy some rum',
            text='We are all outta rum'
            ),follow_redirects=True)
        assert b'Buy some rum' in rv.data
        assert b'We are all outta rum' in rv.data

    #test that todo tasks can be migrated to the 'doing' table
    def test_change_doing(self):
        self.register('Jack', 'sparrow@blackpearl.com', 'rum', 'rum')
        self.app.post('/do', data=dict(
            title='Buy some rum',
            text='We are all outta rum'
            ),follow_redirects=True)
        rv = self.app.post('/doing', data=dict(
            id=id),follow_redirects=True)
        assert b'Buy some rum' in rv.data
        assert b'We are all outta rum' in rv.data

    #test that doing tasks can be moved to the "done" table
    def test_change_done(self):
        self.register('Jack', 'sparrow@blackpearl.com', 'rum', 'rum')
        self.app.post('/do', data=dict(
            title='Buy some rum',
            text='We are all outta rum'
            ),follow_redirects=True)
        self.app.post('/doing', data=dict(
            id=id),follow_redirects=True)
        rv = self.app.post('/done', data=dict(
            id=id),follow_redirects=True)
        assert b'Buy some rum' in rv.data
        assert b'We are all outta rum' in rv.data


if __name__ == '__main__':
    unittest.main()


