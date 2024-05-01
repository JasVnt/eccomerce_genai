from flask_testing import TestCase
from app import app, db

class TestPlaceOrder(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_place_order(self):
        with app.test_client() as client:
            # Assuming the user is logged in and has items in the cart
            client.post('/login', data=dict(
                username='test_user',
                password='test_password'
            ), follow_redirects=True)
            client.post('/add_to_cart/1', follow_redirects=True)  # Add item to cart
            response = client.post('/order', data=dict(
                address='Test Address',
                payment_method='Credit Card'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            print("response.data: ", response.data)
            self.assertIn(b'Order Details', response.data)
