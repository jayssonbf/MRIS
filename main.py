#import all necessary libraries
from sqlalchemy import create_engine
import pyodbc
import psycopg2
import os
import pandas as pd

# Retrieves and verifies data from SQL server (CMS database)
def extract():

    driver = 'SQL+Server+Native+Client+11.0'
    server_name = 'DESKTOP-K9B044T\SQLEXPRESS'
    db_name = 'CMS'
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')

    # Establish a connection to the SQL server (CMS database)
    engine = create_engine(f'mssql+pyodbc://{db_user}:{db_pass}@{server_name}:1433/{db_name}?driver={driver}')

    # Query to obtain all recipients data from CMS database
    query = """Select * from CMS_DB"""

    # Convert the resulting data into a pandas DataFrame
    cms_data = pd.read_sql(query, engine)

    # Close the connection
    engine.dispose()

    transform(cms_data)


# Processes and organizes extracted data
def transform(cms_data):

    pg_host = '192.168.0.14'
    pg_name = 'NAIC_db'
    pg_user = os.getenv("PGUID")
    pg_pass = os.getenv("PGPASS")

    # Establish a connection to the PostgreSQL server (NAIC database)
    engine = create_engine(f'postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_name}')

    # Constructs the SQL query to get recipients data from NAIC
    query = "SELECT * FROM insured WHERE policy_holder_id IN (%s)" % ','.join(['%s']*len(cms_data['recipient_id']))

    # Contains the tuple of values that we want to match against
    params = tuple(cms_data['recipient_id'])

    # Execute the query and retrieve the data into a pandas dataframe
    naic_data = pd.read_sql_query(query, engine, params=params)


    load(naic_data)

# Load into MRIS the data extracted from PostgreSQL Server (NAIC database)
def load(naic_data):

    # Stores the data extracted from NAIC system to MRIS
    naic_data.to_csv('MRI_data.csv', mode='w', index=False)
    print('NAIC data has been succesfully stored in MRIS!!!')


if __name__ == '__main__':

    extract();


