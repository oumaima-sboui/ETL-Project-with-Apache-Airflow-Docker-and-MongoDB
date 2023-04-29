# We'll start by importing the DAG object
from datetime import datetime, timedelta

from airflow import DAG
# We need to import the operators used in our tasks
from airflow.operators.python_operator import PythonOperator
# We then import the days_ago function
from airflow.utils.dates import days_ago

import pandas as pd
import psycopg2
import os
#from pymongo import MongoClient

# get dag directory path
dag_path = os.getcwd()


def extract_data(**context):
    booking = pd.read_csv(f"{dag_path}/raw_data/booking.csv", low_memory=False)
     # Convert the DataFrame to a JSON string
    booking = booking.to_json()
    context['ti'].xcom_push(key='my_data_1', value=booking)
    
    client = pd.read_csv(f"{dag_path}/raw_data/client.csv", low_memory=False)

     # Convert the DataFrame to a JSON string
    client = client.to_json()
    context['ti'].xcom_push(key='my_data_2', value=client)
    
    hotel = pd.read_csv(f"{dag_path}/raw_data/hotel.csv", low_memory=False)
 
         # Convert the DataFrame to a JSON string
    hotel = hotel.to_json()
    context['ti'].xcom_push(key='my_data_3', value=hotel)
    return("data extarted from different CSV file")

    

def transform_data(**context):
    print("ready for transform")
    booking = context['ti'].xcom_pull(key='my_data_1')
    #booking = booking.data
    # Convert the JSON string to a DataFrame
    booking = pd.read_json(booking)
    
    client = context['ti'].xcom_pull(key='my_data_2')
    #client = client.data
    client = pd.read_json(client)
    
    hotel = context['ti'].xcom_pull(key='my_data_3')
    #hotel = hotel.data
    hotel = pd.read_json(hotel)
    
    # merge booking with client
    data = pd.merge(booking, client, on='client_id')
    data.rename(columns={'name': 'client_name', 'type': 'client_type'}, inplace=True)

    # merge booking, client & hotel
    data = pd.merge(data, hotel, on='hotel_id')
    data.rename(columns={'name': 'hotel_name'}, inplace=True)
    
   
     # make date format consistent
    data.booking_date = pd.to_datetime(data.booking_date, infer_datetime_format=True)

    # make all cost in GBP currency
    data.loc[data.currency == 'EUR', ['booking_cost']] = data.booking_cost * 0.8
    data.currency.replace("EUR", "GBP", inplace=True)

    # remove unnecessary columns
    data = data.drop('address', 1)
    data = data.to_json()
    context['ti'].xcom_push(key='my_data_4', value=data)
    return("data cleaning and merging")

   
def load_data(**context):
    data = context['ti'].xcom_pull(key='my_data_4')
   
    # Convert the JSON string to a DataFrame
    data = pd.read_json(data)
         # load processed data
    data.to_csv(f"{dag_path}/processed_data/processed_data.csv", index=False)

     ################################### add to mongodb database ###############################
    # Connect to the MongoDB server
##    client = MongoClient(host='localhost', port=27017)
##
##    # Select the database and collection to store the data
##    db = client['my_database']
##    collection = db['my_collection']
##
##    # Insert the data into the collection
##    collection.insert_many(data.to_dict('records'))

    
    return (data.to_json())
    


# initializing the default arguments that we'll pass to our DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(2)
}

ingestion_dag = DAG(
    'booking_ingestion_DAG',
    default_args=default_args,
    description='Aggregates booking records for data analysis',
    schedule_interval=timedelta(days=1),
    catchup=False
)
task_1 = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=ingestion_dag,
    provide_context=True
)


task_2 = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=ingestion_dag,
   
)

task_3 = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=ingestion_dag,
)




task_1 >> task_2 >> task_3
