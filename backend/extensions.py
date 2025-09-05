"""Extension initialization separated from app creation"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate

# Create extension instances
db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
cors = CORS()
mail = Mail()
migrate = Migrate()