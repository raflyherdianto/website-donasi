from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'rahasia123'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'users.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads', 'resi')
    instance_path = os.path.join(basedir, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import routes
    app.register_blueprint(routes.bp)

    from . import models

    return app