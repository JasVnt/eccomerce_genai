from flask_testing import TestCase
from app import app, db

class TestUserLogin(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()
        # Create a test user for login testing
        from app import User
        user = User(username='test_user', password='test_password', phone_number='')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_login(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                username='test_user',
                password='test_password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_invalid_user_login(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                username='invalid_user',
                password='invalid_password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid username or password', response.data)
