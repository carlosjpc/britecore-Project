import argparse

from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://postgres:andrea1990@localhost/britcore1')


def main(filename):
    df = pd.read_csv(filename)
    df = df[['AGENCY_ID', 'AGENCY_APPOINTMENT_YEAR', 'ACTIVE_PRODUCERS',
             'MAX_AGE', 'MIN_AGE', 'VENDOR', 'COMMISIONS_START_YEAR',
             'COMMISIONS_END_YEAR']]
    df.columns = ['id', 'agencyAppointmentYear', 'activeProducers', 'maxAge',
                  'minAge', 'vendor', 'comissionsStartYear',
                  'comissionsEndYear']
    df = df.drop_duplicates()
    df.to_sql('dim_agency', engine, if_exists='replace', index=False)
    print(df.head())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    args = parser.parse_args()
    main(args.file)
