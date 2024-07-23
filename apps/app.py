from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from apps.config import config
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.signup'
login_manager.login_message = ''
gv_socketio = SocketIO(logger=True, engineio_logger=True)

def create_app(config_key):
    app = Flask(__name__)
    app.config.from_object(config[config_key])
    gv_socketio.init_app(app)
    CORS(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{Path(__file__).parent.parent / "local.sqlite"}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True,
        WTF_CSRF_SECRET_KEY='dev'
    )

    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from apps.bertapp import views as bert_views
    app.register_blueprint(bert_views.bertapp, url_prefix='/bertapp')

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.crud, url_prefix='/crud')

    from apps.auth import views as auth_views
    app.register_blueprint(auth_views.auth, url_prefix='/auth')

    return app