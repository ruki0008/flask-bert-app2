from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
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

    from apps.bertapp import views as bert_views
    app.register_blueprint(bert_views.bertapp, url_prefix='/bertapp')

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.crud, url_prefix='/crud')

    return app