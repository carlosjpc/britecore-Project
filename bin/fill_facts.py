import argparse

from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://postgres:andrea1990@localhost/britcore1')


def main(filename):
    df = pd.read_csv(filename)
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
             'STAT_PROFILE_DATE_YEAR', 'PROD_LINE', 'STATE_ABBR']]
    df['boundQuotes'] = df_bound_q.sum(axis=1)
    df['totalQuotes'] = df_total_q.sum(axis=1)
    df['agencyId'] = df['AGENCY_ID']
    df['dateId'] = df['STAT_PROFILE_DATE_YEAR']
    df['lineId'] = df['PROD_LINE']
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
             'dateId', 'lineId', 'riskStateId']]
    summary = df.pivot_table(
        index=['agencyId', 'dateId', 'lineId', 'riskStateId'],
        values=[
            'boundQuotes',
            'earnedPremium',
            'growthRate3Years',
            'incurredLosses',
            'lossRatio',
            'lossRatio3Year',
            'newBusinessInWrittenPremium',
            'policyInforceQuantity',
            'prevPolicyInforceQuantity',
            'prevWrtittenPremium',
            'retentionPolicyQuantity',
            'retentionRatio',
            'totalQuotes',
            'totalWrittenPremium'
        ],
        aggfunc={
            'boundQuotes': 'sum',
            'earnedPremium': 'sum',
            'growthRate3Years': 'sum',
            'incurredLosses': 'sum',
            'lossRatio': 'mean',
            'lossRatio3Year': 'mean',
            'newBusinessInWrittenPremium': 'sum',
            'policyInforceQuantity': 'sum',
            'prevPolicyInforceQuantity': 'sum',
            'prevWrtittenPremium': 'sum',
            'retentionPolicyQuantity': 'sum',
            'retentionRatio': 'mean',
            'totalQuotes': 'sum',
            'totalWrittenPremium': 'sum'
        }
    )
    summary.to_sql('facts', engine, if_exists='replace')
    print(summary.head())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    args = parser.parse_args()
    main(args.file)
