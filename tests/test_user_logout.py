from flask_testing import TestCase
from app import app, db

class TestUserLogout(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_logout(self):
        with app.test_client() as client:
            response = client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
