from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth
    from app.routes.user import user_bp
    from app.routes.pelanggan import pelanggan_bp
    from app.routes.tapping import tapping_bp
    from app.routes.transaksi import transaksi_bp

    app.register_blueprint(auth)
    app.register_blueprint(user_bp)
    app.register_blueprint(pelanggan_bp)
    app.register_blueprint(tapping_bp)
    app.register_blueprint(transaksi_bp)

    return app
