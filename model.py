from pathlib import Path
from werkzeug.utils import secure_filename
from helpers import SUPPORTED_EXTENSIONS
from dotenv import load_dotenv
from fpdf import FPDF
from PIL import Image
from glob import glob
import mysql.connector
import os

UPLOAD_FOLDER = '/static/client'
class FotoToPdf:
    def __init__(self):
        self.id = 0
        self.images_dir = ''
        self.pdf_dir = ''
        self.upload_folder = ''

    def convert(self, files, upload_folder):
        connection = self.connect_to_database()
        cursor = connection.cursor()

        self.id = self.create_new_id(cursor)
        self.upload_folder = upload_folder
        self.images_dir = self.get_images_dir()
        self.pdf_dir = self.get_pdf_dir()

        self.create_directories()
        self.insert_directories_into_database(cursor)

        self.save_images(files)
        
        self.convert_images_to_pdf()

        connection.commit()
        connection.close()

        return True

    def connect_to_database(self):
        load_dotenv()

        connection = mysql.connector.connect(
            host = os.environ.get('host'),
            user = os.environ.get('user'),
            password = os.environ.get('password'),
            database = os.environ.get('db')
        )

        return connection

    def create_new_id(self, cursor):
        cursor.execute('SELECT * FROM users')
        cursor.fetchall()
        num_rows = cursor.rowcount

        user_id = num_rows + 1
        user_id = str(user_id)

        return user_id

    def get_images_dir(self):
        return os.path.join(self.upload_folder, self.id, 'images')

    def get_pdf_dir(self):
        return os.path.join(self.upload_folder, self.id, 'pdf')

    def create_directories(self):
        Path(os.path.join(self.upload_folder, self.id)).mkdir(parents=True, exist_ok=True)
        Path(self.images_dir).mkdir(parents=True, exist_ok=True)
        Path(self.pdf_dir).mkdir(parents=True, exist_ok=True)

    def insert_directories_into_database(self, cursor):
        cursor.execute(f"INSERT INTO users(images_dir, pdf_dir) VALUES('{self.images_dir}', '{self.pdf_dir}')")

    def save_images(self, files):
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(self.images_dir, filename))

    def convert_images_to_pdf(self):
        image_filenames = []

        for extension in SUPPORTED_EXTENSIONS:
            image_filenames.extend(glob(f'{self.images_dir}/*{extension}'))

        pdf = FPDF()
        pdf.oversized_images = 'DOWNSCALE'

        for image in image_filenames:
            img = Image.open(f'{image}')
            img_width, img_height = img.size

            # Calculate new height to so the image does not go out of bounds
            # Divide the image height by its width and multiply the result with the pdf's max width
            new_height = (img_height / img_width) * pdf.epw

            pdf.add_page()
            pdf.image(img, 0, 0, pdf.epw, new_height)

        pdf.output(f'{self.pdf_dir}/foto2pdf.pdf')

    def get_pdf(self):
        pass

    def get_id(self):
        return self.id