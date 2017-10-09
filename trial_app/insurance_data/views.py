import os
import sqlalchemy
import numpy as np

from flask import (request, redirect, url_for, render_template, Blueprint,
                   flash, jsonify, request)
from pandas import read_csv, DataFrame, read_sql_table, read_sql
from werkzeug.utils import secure_filename
from flask_restful import Resource, reqparse

from trial_app import app, engine, api
from trial_app.insurance_data.models import (db, User, Facts, fact_schema,
                                             facts_schema)
from trial_app.insurance_data.utils import (fill_dim_agency, fill_dim_date,
                                            fill_dim_product, fill_facts,
                                            fill_dim_risk_state)

ALLOWED_EXTENSIONS = set(['csv'])

analytics = Blueprint('analytics', __name__)


@analytics.route('/')
@analytics.route('/home')
def home():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@analytics.route('/file_upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('.preview_file',
                                    filename=filename))
        else:
            flash('that file extension is not allowed, please upload CVS file')
    return render_template('upload.html')


@analytics.route('/save_file_to_db/<filename>/<dim>/', methods=['GET', 'POST'])
def save_file_to_db(filename, dim):
    if request.method == 'POST':
        if request.form['submit'] == 'yes':
            upload = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            df = read_csv(upload)
            if dim == 'agency':
                fill_dim_agency(df)
            elif dim == 'date':
                fill_dim_date(df)
            elif dim == 'product':
                fill_dim_product(df)
            elif dim == 'risk_state':
                fill_dim_risk_state(df)
            elif dim == 'facts':
                fill_facts(df)
            elif dim == 'all':
                fill_dim_agency(df)
                fill_dim_date(df)
                fill_dim_product(df)
                fill_dim_risk_state(df)
                fill_facts(df)
            else:
                message = {"message": "Dimension NOT found in this DataFrame"}
                return jsonify(message)
            return redirect(url_for('.home'))
        elif request.form['submit'] == 'no':
            return redirect(url_for('.upload_file'))
    upload = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = read_csv(upload)
    df = df.head()
    return render_template('data_frame.html', df=df.to_html())


@analytics.route('/api/choose_row_by_index/<int:row_number>/', methods=['GET'])
def row(row_number):
    df = read_sql_table('complete_table', engine)
    if not row_number > 0 and row_number < len(df.index):
        return {"message": row_number + "Not found in this DataFrame"}
    else:
        row = df.loc[[row_number]]
        json = row.to_json()
        return json


@analytics.route('/<int:agency_id>/', methods=['GET'])
def my_query(agency_id):
    facts = Facts.query.filter_by(agency_id=None).all()
    return render_template('list.html', facts=facts)


class HelloWorld(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('agency_id', type=int)
        parser.add_argument('product_id')
        parser.add_argument('date_id', type=int)
        parser.add_argument('risk_id')
        args = parser.parse_args()
        print (args)
        facts = db.session.query(Facts)
        for attr, value in args.items():
            if value is not None:
                print (attr + ' ' + str(value))
                facts = facts.filter(getattr(Facts, attr) == value)
        facts = facts.all()
        result = facts_schema.dump(facts)
        return jsonify({"facts": result.data})


api.add_resource(HelloWorld, '/hello/', endpoint='home')
