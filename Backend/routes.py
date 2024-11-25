from flask import Blueprint, render_template
from .models import User, Product

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return render_template('index.html')

# Add more routes as needed
