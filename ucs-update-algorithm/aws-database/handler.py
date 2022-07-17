import pymysql
import time
# 1. Install pymysql to local directory
# pip install -t $PWD pymysql

# 2. Write code, then zip it up

# Lambda Permissions:
# AWSLambdaVPCAccessExecutionRole

# Confiugration Files
endpoint = 'user-monitoring-database.crnwwfmibeif.us-west-1.rds.amazonaws.com'
username = 'admin'
password = 'user_monitoring'
database_name = 'User_Monitoring'

# Conncection
connection = pymysql.connect(
    host=endpoint, user=username, passwd=password, db=database_name)


def lambda_handler(event=None, context=None):
    insert_into_table(event['table'])


def insert_into_table(table):
    cursor = connection.cursor()
    if table == "ucs":
        insert_ucs = "INSERT INTO ucs (uuid, score) VALUES (%s, %s)"
        uuid = 1234
        score = 0.50000
        data_ucs = (uuid, score)
        cursor.execute(insert_ucs, data_ucs)
        # cursor.execute('SELECT * from ucs')
    elif table == "task_scores":
        insert_task_scores = "INSERT INTO task_scores (ts, quiz_task_uuid, user_uuid, task_score) VALUES (%s, %s, %s, %s)"
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        quiz_task_uuid = 1
        user_uuid = 1234
        task_score = 0.75000
        data_task_scores = (ts, quiz_task_uuid, user_uuid, task_score)
        cursor.execute(insert_task_scores, data_task_scores)
        # cursor.execute('SELECT * from task_scores')
    elif table == "datahunt_tracker":
        insert_datahunt_tracker = "INSERT INTO datahunt_tracker (datahunt_id, num_rows_processed) VALUES (%s, %s)"
        datahunt_id = 1
        num_rows_processed = 10
        data_datahunt_tracker = (datahunt_id, num_rows_processed)
        cursor.execute(insert_datahunt_tracker, data_datahunt_tracker)
        # cursor.execute('SELECT * from datahunt_tracker')

    cursor.execute('SELECT * from {}'.format(table))
    rows = cursor.fetchall()
    for row in rows:
        s = ''
        for item in row:
            s += '{} '.format(item)
        print(s)

# event = {
#   'table': 'ucs'
# }
# lambda_handler(event)
