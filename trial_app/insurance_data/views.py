import os
import pandas as pd
import numpy as np

from flask import (request, redirect, url_for, render_template, Blueprint,
                   flash, jsonify, send_from_directory)
from werkzeug.utils import secure_filename
from flask_restful import Resource, reqparse

from trial_app import app, engine, api
from trial_app.insurance_data.models import (db, Facts, facts_schema)
from trial_app.insurance_data.utils import (fill_dim_agency, fill_dim_date,
                                            fill_dim_product, fill_facts,
                                            fill_dim_risk_state)

ALLOWED_EXTENSIONS = set(['csv'])
dims_available = {'agency': 'agencyId', 'product': 'productId'}
analytics = Blueprint('analytics', __name__)


@analytics.route('/')
@analytics.route('/home')
def home():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@analytics.route('/file_upload/', methods=['GET', 'POST'])
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
            df = pd.read_csv(upload)
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
    df = pd.read_csv(upload)
    df = df.head()
    return render_template('data_frame.html', df=df.to_html())


@analytics.route('/api/choose_row_by_index/<int:row_number>/', methods=['GET'])
def row(row_number):
    df = pd.read_sql_table('facts', engine)
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


class FilterFactsBy(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('agency_id')
        parser.add_argument('product_id')
        parser.add_argument('date_id')
        parser.add_argument('risk_id')
        args = parser.parse_args()
        facts = db.session.query(Facts)
        for attr, value in args.items():
            if value is not None:
                facts = facts.filter(getattr(Facts, attr) == value)
        facts = facts.all()
        result = facts_schema.dump(facts)
        return jsonify({"facts": result.data})


api.add_resource(FilterFactsBy, '/filter_by/', endpoint='filter_facts')


class Reports(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('group_by', action='append')
        parser.add_argument('calculate')
        parser.add_argument('explore_dim')
        args = parser.parse_args()
        print (args)
        if args['explore_dim']:
            if dims_available.get(args['explore_dim']) not in args['group_by']:
                return {"message": args['explore_dim'] +
                        "must also be in the group_by list"}
        df_facts = pd.read_sql_table('facts', engine)
        df_facts = df_facts.groupby(args['group_by'])
        if args['calculate']:
            if args['calculate'] == 'sum':
                df_facts = df_facts.sum()
            elif args['calculate'] == 'mean':
                df_facts = df_facts.mean()
            elif args['calculate'] == 'size':
                df_facts = df_facts.size()
            elif args['calculate'] == 'describe':
                df_facts = df_facts.describe()
            else:
                return {"message": args['calculate'] +
                        "is not a valid operation"}
        if args['explore_dim']:
            df_facts = df_facts.reset_index()
            if args['explore_dim'] == 'agency':
                df_agency = pd.read_sql_table('dim_agency', engine)
                df_facts = pd.merge(df_facts, df_agency,
                                    left_on='agencyId', right_on='id')
                df_facts = df_facts.drop(['id_x', 'id_y'], axis=1)
            else:
                return {"message": args['explore_dim'] + "is not supported"}
        df_facts = df_facts.replace(99999, np.nan)
        df_facts = df_facts.to_csv(os.path.join(app.config['UPLOAD_FOLDER'],
                                   'yourCSV.csv'))
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   'yourCSV.csv', as_attachment=True)


api.add_resource(Reports, '/report/', endpoint='reports')
