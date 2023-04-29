# ETL-Project-with-Apache-Airflow-Docker-and-MongoDB  
This project is an example of an ETL (Extract, Transform, Load) pipeline that is used to extract data from multiple CSV files, transform the data through merging, cleaning and preprocessing, and finally load the transformed data into a final CSV file and a MongoDB database.

The project is built using Docker and Docker Compose to ensure consistency in the environment and easy deployment. Apache Airflow is used to manage the pipeline through DAGs (Directed Acyclic Graphs) which define the workflow and dependencies between the different tasks in the pipeline.

The pipeline starts by extracting data from CSV files containing information about clients, hotels, and bookings. The extracted data is then cleaned and transformed through merging and preprocessing before being loaded into a final CSV file and a MongoDB database.

The MongoDB database serves as the persistent storage for the transformed data, while the final CSV file can be used as a backup or for further analysis.

Overall, this project serves as an example of how to use ETL pipelines and popular technologies such as Docker, Docker Compose, Apache Airflow, and MongoDB to extract, transform, and load data from various sources.
