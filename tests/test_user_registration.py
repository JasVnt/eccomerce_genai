from flask_testing import TestCase
from app import app, db

class TestUserRegistration(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_registration(self):
        with app.test_client() as client:
            response = client.post('/register', data=dict(
                username='test_user',
                password='test_password',
                phone_number=''
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Check if the user is registered in the database
            from app import User
            user = User.query.filter_by(username='test_user').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'test_user')
            self.assertEqual(user.phone_number, '')