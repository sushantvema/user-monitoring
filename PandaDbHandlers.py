import pandas as pd
from datetime import datetime

from dbInterface import DbInterface


class PandasDbHandler(DbInterface):
    def __init__(self):
        #creates structure of df and defines vars
        self.ucs_df, self.task_scores_df, self.datahunt_tracker_df = self.remake_all_tables()

    def table_to_df(self, table):
        if table == "ucs":
            return self.ucs_df
        elif table == "task_scores":
            return self.task_scores_df
        elif table == "datahunt_tracker":
            return self.datahunt_tracker_df

    def display_table(self):
        print(self.ucs_df)
        pd.display(self.ucs_df)
        print(self.task_scores_df)
        pd.display(self.task_scores_df_df)
        print(self.datahunt_tracker_df_df)
        pd.display(self.datahunt_tracker_df_df)

    def table_to_csv(self, filename):
        self.df.to_csv(filename, index=False)

    def insert_into_table(self, table, df):
        """
        TODO: modify function to be dynamic. take in table name to insert into as well
            as dataframe to add into the selected table. add data validation to make sure
            df is correctly formatted for table
        """
        if table == "ucs":
            # df columns: 'contributor_uuid, score'
            self.ucs_df = self.ucs_df.append(df, ignore_index=True)
        elif table == "task_scores":
            # df columns: 'quiz_task_uuid, contributor_uuid, score'
            merged = pd.merge(self.task_scores_df, df, how="inner")
            if len(merged) > 0:
                print("overlap, merged table:")
                pd.display(merged)
                return
            self.task_scores_df = self.task_scores_df.append(df, ignore_index=True)
        elif table == "datahunt_tracker":
            # df columns: 'datahunt_id, num_rows_processed'
            self.datahunt_tracker_df = self.datahunt_tracker_df.append(df, ignore_index=True)

    def insert_ucs_scores(self, user_id, new_ucs, is_in_table):
        if is_in_table:
            self.ucs_df.loc[self.ucs_df['uuid'] == user_id, 'score'] = new_ucs
        else:
            self.ucs_df = self.ucs_df.append({'uuid': user_id, 'score': new_ucs}, ignore_index=True)

    def clear_table(self, table):
        self.remake_table(table)

    def create_table(self, table):
        pass

    def remake_table(self, table):
        if table == "ucs":
            self.ucs_df = pd.DataFrame(columns=['uuid', 'score'])
            return self.ucs_df
        elif table == "task_scores":
            self.task_scores_df = pd.DataFrame(columns=['ts', 'quiz_task_uuid', 'user_uuid', 'task_score'])
            return self.task_scores_df
        elif table == "datahunt_tracker":
            self.datahunt_tracker_df = pd.DataFrame(columns=['datahunt_id', 'num_rows_processed'])
            return self.datahunt_tracker_df

    def remake_all_tables(self):
        self.remake_table("ucs")
        self.remake_table("task_scores")
        self.remake_table("datahunt_tracker")
        # return is weird to appease the definition in init
        return self.ucs_df, self.task_scores_df, self.datahunt_tracker_df

    def post_results(self, data_dir, name):
        ucs = self.table_to_df()
        date = datetime.now().strftime("%Y%m%d-%H%M%S")
        ucs.to_csv(f"{data_dir}/{name}_{date}.csv")
