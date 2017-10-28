import argparse

from sqlalchemy import create_engine
import pandas as pd


def main(filename):
    df = pd.read_csv(filename)
    df = df[['STAT_PROFILE_DATE_YEAR']]
    df.columns = ['id']
    df['year'] = df['id']
    df = df.drop_duplicates()
    df.to_sql('dim_date', engine, if_exists='replace', index=False)
    print(df.head())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('--db_connection')
    args = parser.parse_args()
    engine = create_engine(args.db_connection)
    main(args.file)
