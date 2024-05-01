from flask_testing import TestCase
from app import app, db

class TestAddToCart(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_to_cart(self):
        with app.test_client() as client:
            response = client.post('/add_to_cart/1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
