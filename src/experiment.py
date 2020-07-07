from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client()

query = """
SELECT * FROM (
    SELECT * FROM `kernel-mlops.IMU.MbientlabSensor` ORDER BY time DESC LIMIT 10
) AS desc_table
ORDER BY time;"""
query_job = client.query(query)  # Make an API request.
query = query_job.result()  # Waits for query to finish

# field_names = [f.name for f in query.shcema.]
print(query.to_dataframe().to_json())
