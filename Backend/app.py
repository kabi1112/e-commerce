from flask import Flask, render_template, redirect, request, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import re

# Setup logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Update as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'key'
db = SQLAlchemy(app)

customers=[]

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('products', lazy=True))


# Admin credentials
admin_username = "admin"
admin_password_hash = generate_password_hash("adminpass")

@app.before_first_request
def create_tables():
    db.create_all()

# Admin login route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == admin_username and check_password_hash(admin_password_hash, password):
            session['admin_logged_in'] = True
            session['username'] = username  # Store the username in session
            flash("Welcome, Admin!", "success")
            print("Admin logged in successfully")  # Debug message
            
            # Redirect to the show_customers route after login
            return redirect(url_for('show_customers'))
        else:
            flash("Invalid credentials, please try again.", "danger")
            print("Invalid login attempt")  # Debug message
    return render_template('admin_login.html')


# Admin dashboard route
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for('admin_login'))

    try:
        users = User.query.all()
        products = Product.query.all()

        if not users:
            print("No users found in the database.")
        if not products:
            print("No products found in the database.")
    except Exception as e:
        print("Error fetching data:", e)
        flash("An error occurred while fetching data. Please try again later.", "danger")
        return redirect(url_for('admin_login'))

    return render_template('admin_dashboard.html', users=users, products=products)

# Route to logout from admin
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('admin_login'))

# Initialize the database
'''@app.before_first_request
def create_tables():
    db.create_all()  # Create tables if they don't exist'''

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/beauty')
def beauty():
    return render_template('beauty.html')

@app.route('/home-decor')
def home_decor():
    return render_template('home-decor.html')

@app.route('/electronics')
def electronics():
    return render_template('electronics.html')

@app.route('/fashion')
def fashion():
    return render_template('fashion.html')

@app.route('/toys')
def toys():
    return render_template('toys.html')

@app.route('/footwear')
def footwear():
    return render_template('footwear.html')

@app.route('/cart')
def cart():
    # Assume session['cart'] holds cart data as a list of items
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    total = sum(item['price'] * item.get('quantity', 1) for item in cart)
    
    if request.method == 'POST':
        # Logic to handle the order
        session['cart'] = []  # Clear cart after order
        return redirect(url_for('thankyou'))
    
    return render_template('checkout.html', cart=cart, total=total)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/support')
def support():
    return render_template('contact.html')

@app.route('/feedback')
def feedback():
    return render_template('faq.html')

@app.route('/join')
def join():
    return render_template('join.html')

@app.route('/submit_join', methods=['POST'])
def submit_join():
    # Capture form data
    customer_data = {
        'business_name': request.form.get('businessName'),
        'owner_name': request.form.get('ownerName'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'address': request.form.get('address'),
        'products': request.form.get('products')
    }
    # Store the customer data in memory
    customers.append(customer_data)
    # Redirect to a thank you page after submission
    return redirect(url_for('thank_join'))

@app.route('/thank_join')
def thank_join():
    return render_template('thank_join.html')

# Route to display all customer details (backend admin view)
@app.route('/admin/customers')
def show_customers():
    return render_template('customers.html', customers=customers)

@app.route('/contact', methods=['GET', 'POST'])  # Combined the two contact routes
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Here you would typically process the data (e.g., send an email)
        # For this example, let's just flash a success message.
        flash('Your message has been sent successfully!', 'success')
        
        # Redirect to the thank you page
        return redirect(url_for('thankyou'))  # Ensure this matches the thank you route

    return render_template('contact.html')

@app.route('/thankyou')  # Ensure the route name matches the redirect in contact
def thankyou():
    return render_template('thankyou.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # You can choose to ignore the password field

        # Simple email validation
        if is_valid_email(email):
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            flash('Invalid email format. Please try again.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        # Add your logic to save the user to your database here
        # For example, check if passwords match and save to DB

        return redirect(url_for('login'))  # Redirect to the login page

    return render_template('register.html')

@app.route('/product/<int:product_id>')
def product(product_id):
    # logic to retrieve product by product_id
    return render_template('product.html', product_id=product_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
