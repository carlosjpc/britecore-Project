import sqlalchemy
import pandas as pd

from pandas import DataFrame

from trial_app import engine


def fill_dim_agency(df):
    df = df[['AGENCY_ID', 'AGENCY_APPOINTMENT_YEAR', 'ACTIVE_PRODUCERS',
             'MAX_AGE', 'MIN_AGE', 'VENDOR', 'COMMISIONS_START_YEAR',
             'COMMISIONS_END_YEAR']]
    df.columns = ['id', 'agencyAppointmentYear', 'activeProducers',
                  'maxAge', 'minAge', 'vendor', 'comissionsStartYear',
                  'comissionsEndYear']
    save_table_to_db(df, 'dim_agency')


def fill_dim_date(df):
    df = df[['STAT_PROFILE_DATE_YEAR']]
    df.columns = ['id']
    df['id'] = df['id'].astype(str)
    save_table_to_db(df, 'dim_date')


def fill_dim_product(df):
    df = df[['PROD_ABBR', 'PROD_LINE']]
    df.columns = ['id', 'line']
    save_table_to_db(df, 'dim_product')


def fill_dim_risk_state(df):
    df = df[['STATE_ABBR']]
    df.columns = ['id']
    save_table_to_db(df, 'dim_risk_state')


def fill_facts(df):
    df_bound_q = df[['CL_BOUND_CT_MDS', 'CL_BOUND_CT_SBZ', 'CL_BOUND_CT_eQT',
                     'PL_BOUND_CT_ELINKS', 'PL_BOUND_CT_PLRANK',
                     'PL_BOUND_CT_eQTte', 'PL_BOUND_CT_APPLIED',
                     'PL_BOUND_CT_TRANSACTNOW']]
    df_bound_q = df_bound_q.replace('99999', 0)
    df_total_q = df[['CL_QUO_CT_MDS', 'CL_QUO_CT_SBZ', 'CL_QUO_CT_eQT',
                     'PL_QUO_CT_ELINKS', 'PL_QUO_CT_PLRANK', 'PL_QUO_CT_eQTte',
                     'PL_QUO_CT_APPLIED', 'PL_QUO_CT_TRANSACTNOW']]
    df_total_q = df_total_q.replace('99999', 0)
    df = df[['RETENTION_POLY_QTY', 'POLY_INFORCE_QTY', 'PREV_POLY_INFORCE_QTY',
             'NB_WRTN_PREM_AMT', 'WRTN_PREM_AMT', 'PREV_WRTN_PREM_AMT',
             'PRD_ERND_PREM_AMT', 'PRD_INCRD_LOSSES_AMT', 'RETENTION_RATIO',
             'LOSS_RATIO', 'LOSS_RATIO_3YR', 'GROWTH_RATE_3YR',
             'CL_BOUND_CT_MDS', 'CL_QUO_CT_MDS', 'CL_BOUND_CT_SBZ',
             'CL_QUO_CT_SBZ', 'CL_BOUND_CT_eQT', 'CL_QUO_CT_eQT',
             'PL_BOUND_CT_ELINKS', 'PL_QUO_CT_ELINKS', 'PL_BOUND_CT_PLRANK',
             'PL_QUO_CT_PLRANK', 'PL_BOUND_CT_eQTte', 'PL_QUO_CT_eQTte',
             'PL_BOUND_CT_APPLIED', 'PL_QUO_CT_APPLIED',
             'PL_BOUND_CT_TRANSACTNOW', 'PL_QUO_CT_TRANSACTNOW', 'AGENCY_ID',
             'STAT_PROFILE_DATE_YEAR', 'PROD_ABBR', 'STATE_ABBR']]
    df['boundQuotes'] = df_bound_q.sum(axis=1)
    df['totalQuotes'] = df_total_q.sum(axis=1)
    df['agencyId'] = df['AGENCY_ID']
    df['dateId'] = df['STAT_PROFILE_DATE_YEAR']
    df['productId'] = df['PROD_ABBR']
    df['riskStateId'] = df['STATE_ABBR']
    df = df.rename(columns={
        'RETENTION_POLY_QTY': 'retentionPolicyQuantity',
        'POLY_INFORCE_QTY': 'policyInforceQuantity',
        'PREV_POLY_INFORCE_QTY': 'prevPolicyInforceQuantity',
        'NB_WRTN_PREM_AMT': 'newBusinessInWrittenPremium',
        'WRTN_PREM_AMT': 'totalWrittenPremium',
        'PREV_WRTN_PREM_AMT': 'prevWrtittenPremium',
        'PRD_ERND_PREM_AMT': 'earnedPremium',
        'PRD_INCRD_LOSSES_AMT': 'incurredLosses',
        'RETENTION_RATIO': 'retentionRatio',
        'LOSS_RATIO': 'lossRatio',
        'LOSS_RATIO_3YR': 'lossRatio3Year',
        'GROWTH_RATE_3YR': 'growthRate3Years',
    })
    df = df[['retentionPolicyQuantity', 'policyInforceQuantity',
             'prevPolicyInforceQuantity', 'newBusinessInWrittenPremium',
             'totalWrittenPremium', 'prevWrtittenPremium', 'earnedPremium',
             'incurredLosses', 'retentionRatio', 'lossRatio', 'lossRatio3Year',
             'growthRate3Years', 'boundQuotes', 'totalQuotes', 'agencyId',
             'dateId', 'productId', 'riskStateId']]
    save_table_to_db(df, 'facts')


def save_table_to_db(df, table_to_write_to):
    df = df.drop_duplicates()
    list_to_write = df.to_dict(orient='records')
    metadata = sqlalchemy.schema.MetaData(bind=engine, reflect=True)
    table = sqlalchemy.Table(table_to_write_to, metadata, autoload=True)
    conn = engine.connect()
    conn.execute(table.insert(), list_to_write)
