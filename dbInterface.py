from abc import ABC, abstractmethod

class DbInterface(ABC):

    @abstractmethod
    def table_to_df(self, table):
        pass

    @abstractmethod
    def table_to_csv(self, table):
        pass

    @abstractmethod
    def insert_into_table(self, table, df):
        pass

    #TODO: This should be merged into insert_into_table, but on time crunch
    @abstractmethod
    def insert_ucs_scores(self, user_id, new_ucs, is_in_table):
        pass

    @abstractmethod
    def clear_table(self, table):
        pass

    @abstractmethod
    def create_table(self, table):
        pass

    @abstractmethod
    def remake_table(self, table):
        pass

    @abstractmethod
    def remake_all_tables(self):
        pass

    @abstractmethod
    def post_results(self, data_dir, name):
        pass
