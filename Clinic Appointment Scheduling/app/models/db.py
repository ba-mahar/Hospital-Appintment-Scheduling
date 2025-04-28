import pyodbc
from flask import current_app

class DB:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(
                driver=current_app.config['SQL_SERVER_DRIVER'],
                server=current_app.config['SQL_SERVER'],
                database=current_app.config['SQL_DATABASE'],
                uid=current_app.config['SQL_USERNAME'],
                pwd=current_app.config['SQL_PASSWORD']
            )
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return False

    def execute_query(self, query, params=None, fetch=False):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if fetch:
                columns = [column[0] for column in self.cursor.description]
                results = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
                return results
            else:
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Query execution error: {str(e)}")
            self.connection.rollback()
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

db = DB()