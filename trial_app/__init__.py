from flask import Flask
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api

app = Flask(__name__)
app.config['SECRET_KEY'] = '8216219686188755103'
api = Api(app)
from trial_app.insurance_data.models import db  # noqa
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

from trial_app.insurance_data.views import analytics # noqa
app.register_blueprint(analytics)
