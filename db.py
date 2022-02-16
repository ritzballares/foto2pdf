from dotenv import load_dotenv
import os
import mysql.connector


class Db:
    def __init__(self):
        """Initializes a Db object."""
        load_dotenv()
        self.connection = mysql.connector.connect(
            host = os.environ.get('host'),
            user = os.environ.get('user'),
            password = os.environ.get('password'),
            database = os.environ.get('db')
        )
        self.cursor = self.connection.cursor()

    def get_row_count(self):
        """Gets the number of rows in the users table."""
        self.cursor.execute('SELECT * FROM users')
        self.cursor.fetchall()

        num_rows = self.cursor.rowcount
        return num_rows

    def insert_record(self, images_path, pdf_path):
        """Inserts a record into the users table."""
        self.cursor.execute(f"INSERT INTO users(images_path, pdf_path) VALUES('{images_path}', '{pdf_path}')")

    def get_pdf_path_from_id(self, id):
        """Gets the path to the PDF directory with the associated id."""
        self.cursor.execute(f"SELECT pdf_path FROM users WHERE id='{id}'")
        
        pdf_path = self.cursor.fetchall()
        if len(pdf_path) == 0:
            return ''
        else:
            return pdf_path[0][0]

    def id_exists(self, id):
        """Checks if the id exists in the users table."""
        self.cursor.execute(f"SELECT * FROM users WHERE id='{id}'")
        record = self.cursor.fetchall()

        if len(record) == 0:
            return False
        else:
            return True

    def close(self):
        """Commits the changes made to the database and closes the connection."""
        self.connection.commit()
        self.connection.close()