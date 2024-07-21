from pathlib import Path

basedir = Path(__file__).parent.parent

class BaseConfig:
    SECRET_KEY = 'dev'
    WTF_CSRF_SECRET_KEY = 'dev'

class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI=f'sqlite:///{Path(__file__).parent.parent / "local.sqlite"}',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=True

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI=f'sqlite:///{Path(__file__).parent.parent / "local.sqlite"}',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED = False

config = {
    'testing': TestingConfig,
    'local': LocalConfig
}