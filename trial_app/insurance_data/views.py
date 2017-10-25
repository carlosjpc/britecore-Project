import os
import pandas as pd
import numpy as np
import pdfkit

from flask import (request, redirect, url_for, render_template, Blueprint,
                   flash, jsonify, send_from_directory, make_response)
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
config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')


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
            return redirect(url_for('.save_file_to_db',
                                    filename=filename, dim='all'))
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
                message = {'message': 'Dimension NOT found in this DataFrame'}
                return jsonify(message)
            return redirect(url_for('.home'))
        elif request.form['submit'] == 'no':
            return redirect(url_for('.upload_file'))
    upload = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(upload)
    df = df.head()
    return render_template('data_frame.html', df=df.to_html())


class AgencyPerformance(Resource):

    def append_df_to_dic(self, df_industry, df_agency_i):
        facts = ['retentionPolicyQuantity', 'policyInforceQuantity',
                 'prevPolicyInforceQuantity', 'newBusinessInWrittenPremium',
                 'totalWrittenPremium', 'earnedPremium', 'incurredLosses',
                 'retentionRatio', 'lossRatio', 'lossRatio3Year',
                 'growthRate3Years', 'boundQuotes', 'totalQuotes']
        df_to_insert = pd.concat([df_industry, df_agency_i], axis=1)
        df_to_insert.columns = ['Industy Avg.', 'Agency Avg.']
        df_to_insert = df_to_insert.loc[facts]
        return df_to_insert.to_html(classes='my_table')

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('agency_id', required=True)
        parser.add_argument('product_id')
        parser.add_argument('date_id')
        parser.add_argument('risk_id')
        parser.add_argument('line_type')
        args = parser.parse_args()
        dfs_to_make = []
        df = pd.read_sql_table('facts', engine)
        # make a sub data frame with the parameters passed
        if args['product_id']:
            df = df[df.productId == args['product_id']]
        else:
            dfs_to_make.append('dim_product')
        if args['date_id']:
            df = df[df.dateId == args['date_id']]
        else:
            dfs_to_make.append('dim_date')
        if args['risk_id']:
            df = df[df.riskStateId == args['risk_id']]
        else:
            dfs_to_make.append('dim_risk_state')
        if args['line_type']:
            df_product = pd.read_sql_table('dim_product', engine)
            df = pd.merge(df, df_product,
                          left_on='productId', right_on='id')
            df = df.drop(['id_x', 'id_y'], axis=1)
            df = df[df.line == args['line_type']]
        df = df.replace([99999, '99999', 99999.0, '99999.00000'], 0)
        # from the trimmed DF select the rows of the selected agency
        df_agency = df[df.agencyId == args['agency_id']]
        dataframe_collection = {}
        list_of_dim_keys = []
        if not dfs_to_make:
            message = {'message': 'Please leave at least one dimension open'}
            return jsonify(message)
        # create the DF for each id in ea Dimension not provieded
        df_dim_id = []
        for index1, dim in enumerate(dfs_to_make):
            df_dim = pd.read_sql_table(dim, engine)
            df_dim_id = df_dim['id'].tolist()
            dataframe_collection['Dimension'] = dim
            if dim == 'dim_date':
                for index2, id in enumerate(df_dim_id):
                    df_industry = df[df.dateId == df_dim_id[index2]].mean()
                    df_agency_i = df_agency[df_agency.dateId ==
                                            df_dim_id[index2]].mean()
                    dataframe_collection[id] = self.append_df_to_dic(
                                                    df_industry, df_agency_i)
                    list_of_dim_keys.append(id)
            elif dim == 'dim_risk_state':
                for index2, id in enumerate(df_dim_id):
                    df_industry = df[df.riskStateId == df_dim_id[
                                                                index2]].mean()
                    df_agency_i = df_agency[df_agency.riskStateId == df_dim_id[
                                                                index2]].mean()
                    dataframe_collection[id] = self.append_df_to_dic(
                                                    df_industry, df_agency_i)
                    list_of_dim_keys.append(id)
            elif dim == 'dim_product':
                for index2, id in enumerate(df_dim_id):
                    df_industry = df[df.productId == df_dim_id[index2]].mean()
                    df_agency_i = df_agency[df_agency.productId ==
                                            df_dim_id[index2]].mean()
                    dataframe_collection[id] = self.append_df_to_dic(
                                                    df_industry, df_agency_i)
                    list_of_dim_keys.append(id)
            return self.make_response_pdf(dataframe_collection,
                                          list_of_dim_keys)

    def make_response_pdf(self, dataframe_collection, list_of_dim_keys):
        rendered = render_template('htmlreport.html',
                                   df_collection=dataframe_collection,
                                   list_keys=list_of_dim_keys)
        pdf = pdfkit.from_string(rendered, False, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = (
                                                'inline; filename=report.pdf')
        return response


api.add_resource(AgencyPerformance, '/pdf_report/',
                 endpoint='agency_performance')


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
        return jsonify({'facts': result.data})


api.add_resource(FilterFactsBy, '/facts/', endpoint='filter_facts')


class Reports(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('group_by', action='append')
        parser.add_argument('aggregation', required=True)
        parser.add_argument('add_dim_attributes')
        args = parser.parse_args()
        if args['add_dim_attributes']:
            if (dims_available.get(args['add_dim_attributes'])
               not in args['group_by']):
                return {'message': args['add_dim_attributes'] +
                        'must also be in the group_by list or its not' +
                        'supported'}
        df_facts = pd.read_sql_table('facts', engine)
        df_facts = df_facts.groupby(args['group_by'])
        if args['aggregation'] == 'sum':
            df_facts = df_facts.sum()
        elif args['aggregation'] == 'mean':
            df_facts = df_facts.mean()
        elif args['aggregation'] == 'size':
            df_facts = df_facts.size()
        elif args['aggregation'] == 'describe':
            df_facts = df_facts.describe()
        else:
            return {'message': args['aggregation'] +
                    ' is not a valid operation'}
        if args['add_dim_attributes']:
            df_facts = df_facts.reset_index()
            if args['add_dim_attributes'] == 'agency':
                df_agency = pd.read_sql_table('dim_agency', engine)
                df_facts = pd.merge(df_facts, df_agency,
                                    left_on='agencyId', right_on='id')
                df_facts = df_facts.drop(['id_x', 'id_y'], axis=1)
            else:
                return {'message': args['add_dim_attributes']
                        + 'is not supported'}
        df_facts = df_facts.replace(99999, np.nan)
        df_facts = df_facts.to_csv(os.path.join(app.config['UPLOAD_FOLDER'],
                                   'yourCSV.csv'))
        return redirect(url_for('analytics.download_csv',
                                filename='yourCSV.csv'))


api.add_resource(Reports, '/report/', endpoint='reports')


@analytics.route('/download_csv/<filename>/', methods=['GET'])
def download_csv(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               'yourCSV.csv', as_attachment=True)
