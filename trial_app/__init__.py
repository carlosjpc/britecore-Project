from flask import Flask
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api

UPLOAD_FOLDER = '/Users/carlospceballos/proyectoBritcore/trial_app/uploads'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
                        'postgresql://andrea1990:williamsburg@agencyperformance.cdjhfndhsudv.us-west-2.rds.amazonaws.com:5432/kaggleagencydata')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '8216219686188755103'
app.config['DEBUG'] = True
api = Api(app)
from trial_app.insurance_data.models import db  # noqa
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

engine = create_engine('postgresql://andrea1990:williamsburg@agencyperformance.cdjhfndhsudv.us-west-2.rds.amazonaws.com:5432/kaggleagencydata') # noqa

from trial_app.insurance_data.views import analytics # noqa
app.register_blueprint(analytics)
