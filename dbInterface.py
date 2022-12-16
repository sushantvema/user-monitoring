from abc import ABC, abstractmethod

class DbInterface(ABC):
    @abstractmethod
    def lambda_handler(self, event=None, context=None):
        pass

    @abstractmethod
    def table_to_df(self, table):
        pass

    @abstractmethod
    def table_to_csv(self, table):
        pass

    @abstractmethod
    def insert_into_table(self, table, df):
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
