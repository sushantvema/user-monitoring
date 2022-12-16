import pymysql
import pandas as pd
import time
from dbInterface import DbInterface
from datetime import datetime


class LambdaHandler(DbInterface):
    def __init__(self, host, user, passwd, db):
        # Database Connection
        self.connection = pymysql.connect(host=host, user=user, passwd=passwd, db=db)

    def lambda_handler(self, event=None, context=None):
        self.insert_into_table(event["table"])

    def table_to_df(self, table):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * from {}".format(table))
        rows = cursor.fetchall()
        field_names = [i[0] for i in cursor.description]
        df = pd.DataFrame(columns=field_names)
        for row in rows:
            df.loc[len(df.index)] = row
        return df

    # def display_table(self, table):
    #     df = self.table_to_df(table)
    #     print(table)
    #     pd.display(df)

    def table_to_csv(self, table):
        df = self.table_to_df(table)
        df.to_csv(f"{table}.csv", index=False)

    def insert_into_table(self, table, df):
        """
        TODO: modify function to be dynamic. take in table name to insert into as well
            as dataframe to add into the selected table. add data validation to make sure
            df is correctly formatted for table
        """
        cursor = self.connection.cursor()
        mysql_query = None
        if table == "ucs":
            # df columns: 'contributor_uuid, score'

            insert_ucs = "INSERT INTO `ucs` (`uuid`, `score`) VALUES (%s, %s)"

            def ucs_query(row):
                data_ucs = (row["contributor_uuid"], row["score"])
                print(data_ucs)
                cursor.execute(insert_ucs, data_ucs)
                return row

            mysql_query = ucs_query

            # cursor.execute('SELECT * from ucs')
        elif table == "task_scores":
            # df columns: 'quiz_task_uuid, contributor_uuid, score'
            task_scores = self.table_to_df("task_scores").iloc[:, [1, 2, 3]]
            merged = pd.merge(df, task_scores, how="inner")
            if len(merged) > 0:
                print("overlap, merged table:")
                # pd.display(merged)
                return

            insert_task_scores = "INSERT INTO task_scores (ts, quiz_task_uuid, user_uuid, task_score) VALUES (%s, %s, %s, %s)"

            def task_scores_query(row):
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                quiz_task_uuid = row["quiz_task_uuid"]
                contributor_uuid = row["contributor_uuid"]
                score = row["score"]
                data_task_scores = (ts, quiz_task_uuid, contributor_uuid, score)
                cursor.execute(insert_task_scores, data_task_scores)
                return row

            mysql_query = task_scores_query

            # cursor.execute('SELECT * from task_scores')
        elif table == "datahunt_tracker":
            # df columns: 'datahunt_id, num_rows_processed'

            insert_datahunt_tracker = "INSERT INTO datahunt_tracker (datahunt_id, num_rows_processed) VALUES (%s, %s)"

            def datahunt_tracker_query(row):
                datahunt_id = row["datahunt_id"]
                num_rows_processed = row["num_rows_processed"]
                data_datahunt_tracker = (datahunt_id, num_rows_processed)
                cursor.execute(insert_datahunt_tracker, data_datahunt_tracker)
                return row

            # cursor.execute('SELECT * from datahunt_tracker')

        # run the appropriate query on each row of the given dataframe
        df = df.apply(mysql_query, axis=1)
        self.connection.commit()
        # self.display_table(table)
        cursor.close()

    def clear_table(self, table):
        cursor = self.connection.cursor()
        if table == "ucs":
            truncate = "TRUNCATE TABLE `ucs`"
        elif table == "task_scores":
            truncate = "TRUNCATE TABLE `task_scores`"
        elif table == "datahunt_tracker":
            truncate = "TRUNCATE TABLE `datahunt_tracker`"
        cursor.execute(truncate)
        # self.display_table(table)
        self.connection.commit()
        cursor.close()

    def create_table(self, table):
        cursor = self.connection.cursor()
        if table == "ucs":
            create = (
                "CREATE TABLE `ucs` (`uuid` TINYTEXT, `score` DECIMAL(6,5) NOT NULL)"
            )
        elif table == "task_scores":
            create = "CREATE TABLE `task_scores` ( \
                                    `ts` TIMESTAMP, \
                                    `quiz_task_uuid` INT, \
                                    `user_uuid` TINYTEXT, \
                                    `task_score` DECIMAL(6,5) \
                                    )"
        elif table == "datahunt_tracker":
            create = "CREATE TABLE `datahunt_tracker` ( \
                                    `datahunt_id` TINYTEXT, \
                                    `num_rows_processed` INT \
                                    )"

        cursor.execute(create)
        # self.display_table(table)
        self.connection.commit()
        cursor.close()

    def remake_table(self, table):
        cursor = self.connection.cursor()
        if table == "ucs":
            drop = "DROP TABLE `ucs`"
            create = (
                "CREATE TABLE `ucs` (`uuid` TINYTEXT, `score` DECIMAL(6,5) NOT NULL)"
            )
        elif table == "task_scores":
            drop = "DROP TABLE `task_scores`"
            create = "CREATE TABLE `task_scores` ( \
                                    `ts` TIMESTAMP, \
                                    `quiz_task_uuid` TINYTEXT, \
                                    `user_uuid` TINYTEXT, \
                                    `task_score` DECIMAL(6,5) \
                                    )"
        elif table == "datahunt_tracker":
            drop = "DROP TABLE `datahunt_tracker`"
            create = "CREATE TABLE `datahunt_tracker` ( \
                                    `datahunt_id` TINYTEXT, \
                                    `num_rows_processed` INT \
                                    )"

        cursor.execute(drop)
        cursor.execute(create)
        # self.display_table(table)
        self.connection.commit()
        cursor.close()

    def remake_all_tables(self):
        self.remake_table("ucs")
        self.remake_table("task_scores")
        self.remake_table("datahunt_tracker")
        self.connection.commit()

    def post_results(self, data_dir, name):
        ucs = self.table_to_df("ucs")
        date = datetime.now().strftime("%Y%m%d-%H%M%S")
        ucs.to_csv(f"{data_dir}/{name}_{date}.csv")
