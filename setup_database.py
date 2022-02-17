from dotenv import load_dotenv
import os
import mysql.connector


try:
    load_dotenv()

    print('Connecting to server...')
    connection = mysql.connector.connect(
        host = os.environ.get('host'),
        user = os.environ.get('user'),
        password = os.environ.get('password')
    )

    db = os.environ.get('db')

    cursor = connection.cursor()

    print('Creating database...')
    cursor.execute(f"CREATE DATABASE {db}")

    print('Creating table...')
    cursor.execute(f"USE {db}")
    cursor.execute("CREATE TABLE users(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, images_path VARCHAR(30), pdf_path VARCHAR(30), created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

    connection.commit()
    connection.close()

    print('Database setup successful.')
except mysql.connector.Error as err:
    print(f'An error occurred while setting up database: {err}')