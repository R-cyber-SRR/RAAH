import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)

# Configure application secret key
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure the database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create the uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Import models here to avoid circular imports
with app.app_context():
    # Import models after db is initialized
    from models import User, Student, Teacher, Module, Attendance, Grade, Notification
    db.create_all()
    
    # Check if there are any users, if not create admin
    if not User.query.first():
        admin = User(
            username="admin",
            email="admin@example.com",
            role="admin",
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Admin user created")

# Register blueprints
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# Add user loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import and register routes
from routes import *
