from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random
from twilio.rest import Client
import phonenumbers



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Twilio configuration
TWILIO_ACCOUNT_SID = 'AC3501435a8c7adfce14581521aa0d5c99'
TWILIO_AUTH_TOKEN = '20e9bd75c24bbb57b0559e79db2b812e'
TWILIO_PHONE_NUMBER = '+16623732352'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

footbal_image = "https://cdn.pixabay.com/photo/2016/05/20/21/57/football-1406106_640.jpg"
basketball_image = "https://cdn.pixabay.com/photo/2020/03/10/16/47/moon-4919501_640.jpg"
volleyball_image = "https://cdn.pixabay.com/photo/2017/01/13/14/07/volleyball-1977364_1280.jpg"
rugbyball_image = "https://cdn.pixabay.com/photo/2015/01/11/21/23/rugby-596747_640.jpg"
cricketball_image = "https://cdn.pixabay.com/photo/2013/07/12/15/55/cricket-150561_1280.png"
tennisball_image = "https://cdn.pixabay.com/photo/2016/03/05/19/42/alone-1238482_640.jpg"

products = [
    {"id": 1, "name": "Basketball", "price": 10, "description": "Beautiful Basketball", "image_url": basketball_image},
    {"id": 2, "name": "Football", "price": 19, "description": "Sturdy Football", "image_url": footbal_image},
    {"id": 3, "name": "Volleyball", "price": 29, "description": "Flexible vollyball", "image_url": volleyball_image},
    {"id": 4, "name": "Cricketball", "price": 9, "description": "Cricket's leather ball", "image_url": cricketball_image},
    {"id": 5, "name": "RugbyBall", "price": 22, "description": "Rugby ball", "image_url": rugbyball_image},
    {"id": 6, "name": "Tennisball", "price": 20, "description": "Tennis ball", "image_url": tennisball_image},
    # Add more products as needed
]


@app.teardown_appcontext
def teardown_session(exception=None):
    try:
        session.clear()
    except RuntimeError:
        pass


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)


@app.route('/')
def index():
    # Dummy product data for demonstration
    return render_template('newindex.html', products=products)
    # return render_template('index.html')


@app.route('/order', methods=['POST'])
def place_order():
    address = request.form.get('address')
    payment_method = request.form.get('payment_method')
    # Extract cart items data
    product_names = request.form.getlist('product_name[]')
    product_descriptions = request.form.getlist('product_description[]')
    product_prices = request.form.getlist('product_price[]')
    cart_items = [{'name': name, 'description': desc, 'price': float(price)} for name, desc, price in zip(product_names, product_descriptions, product_prices)]
    total_price = sum(item['price'] for item in cart_items)
    # Render order page with data
    return render_template('order.html', cart_items=cart_items, total_price=total_price, delivery_address=address, payment_method=payment_method)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    print("total cart is - ",str(session['cart']))
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    cart_items = []
    total_price = 0
    if 'cart' in session:
        for product_id in session['cart']:
            for product in products:
                if product['id'] == product_id:
                    cart_items.append(product)
                    total_price += product['price']
                    break
    print("Cartitems- ",str(cart_items))
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


def format_phone_number(phone_number, default_region='IN'):
    try:
        parsed_number = phonenumbers.parse(phone_number, default_region)
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.phonenumberutil.NumberParseException as e:
        print("Error parsing phone number:", e)
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone_number']
        otp = random.randint(1000, 9999)  # Generate random OTP
        # Save user details to the database
        new_user = User(username=username, password=password, phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()
        # Format phone number to E.164 format
        formatted_phone_number = format_phone_number(phone_number)
        # Send OTP to the user's phone number
        print("hpne is  - ",format_phone_number, " , orginal was - ",phone_number)
        message = client.messages.create(
            body=f'Your OTP for registration is: {otp}',
            from_=TWILIO_PHONE_NUMBER,
            to=formatted_phone_number  # Use the formatted phone number
        )
        session['otp'] = otp  # Store OTP in session
        session['username'] = username  # Store username in session
        return redirect(url_for('verify_login_otp'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Clear existing session data
            session.clear()
            # Generate a new OTP
            otp = random.randint(1000, 9999)
            # Retrieve user's phone number
            phone_number = user.phone_number
            # Format phone number to E.164 format
            formatted_phone_number = format_phone_number(phone_number)
            if not formatted_phone_number:
                return "Invalid phone number format"
            # Send OTP to the user's phone number
            message = client.messages.create(
                body=f'Your new OTP for login is: {otp}',
                from_=TWILIO_PHONE_NUMBER,
                to=formatted_phone_number
            )
            session['otp'] = otp  # Store OTP in session
            session['username'] = username  # Set username in session upon successful login
            return redirect(url_for('verify_login_otp'))
        else:
            return "Invalid username or password"
    return render_template('login.html')

@app.route('/verify_login_otp', methods=['GET', 'POST'])
def verify_login_otp():
    if request.method == 'POST':
        otp_entered = request.form['otp']
        stored_otp = session.get('otp')
        print("Stored OTP is - ",stored_otp)
        if not stored_otp:
            return redirect(url_for('login'))  # Redirect to login if OTP is not in session
        if otp_entered == str(stored_otp):
            # OTP verification successful, proceed to index page
            return redirect(url_for('index'))
        else:
            return "Invalid OTP. Please try again."
    return render_template('verify_login_otp.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
