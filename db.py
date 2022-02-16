import os
import mysql.connector
from dotenv import load_dotenv

class Db:
    def __init__(self):
        load_dotenv()
        self.connection = mysql.connector.connect(
            host = os.environ.get('host'),
            user = os.environ.get('user'),
            password = os.environ.get('password'),
            database = os.environ.get('db')
        )
        self.cursor = self.connection.cursor()

    def get_row_count(self):
        self.cursor.execute('SELECT * FROM users')
        self.cursor.fetchall()

        num_rows = self.cursor.rowcount
        return num_rows

    def insert_record(self, images_dir, pdf_dir):
        self.cursor.execute(f"INSERT INTO users(images_dir, pdf_dir) VALUES('{images_dir}', '{pdf_dir}')")

    def get_pdf_dir_from_id(self, id):
        self.cursor.execute(f"SELECT pdf_dir FROM users WHERE id='{id}'")
        
        pdf_dir = self.cursor.fetchall()
        if len(pdf_dir) == 0:
            return ''
        else:
            return pdf_dir[0][0]

    def id_exists(self, id):
        self.cursor.execute(f"SELECT * FROM users WHERE id='{id}'")
        record = self.cursor.fetchall()

        if len(record) == 0:
            return False
        else:
            return True

    def close(self):
        self.connection.commit()
        self.connection.close()