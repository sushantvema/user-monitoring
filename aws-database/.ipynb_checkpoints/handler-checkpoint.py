import pymysql

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
connection = pymysql.connect(host=endpoint, user=username, passwd=password, db=database_name)

def lambda_handler(event, context):
    cursor = connection.cursor()
    cursor.execute('SELECT * from UCS')

    rows = cursor.fetchall()
    for row in rows:
        print('{0} {1}'.format(row[0], row[1]))
lambda_handler(None, None)