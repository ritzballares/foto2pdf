from dotenv import load_dotenv
from pathlib import Path
from werkzeug.utils import secure_filename
from fpdf import FPDF
from glob import glob
from PIL import Image
import mysql.connector
import os


SUPPORTED_EXTENSIONS = {
    'jpg': True,
    'jpeg': True,
    'png': True
}


def check_files(files):
    """Checks if the uploaded files are valid.
    
    Parameters:
        files: file(s) uploaded by a user.

    Returns:
        True if files are valid, otherwise False.
    """
    for file in files:
        filename_split = file.filename.split(".")
        extension = filename_split[-1]

        if extension not in SUPPORTED_EXTENSIONS:
            return False

    return True

def connect_to_database():
    try:
        load_dotenv()

        connection = mysql.connector.connect(
            host = os.environ.get('host'),
            user = os.environ.get('user'),
            password = os.environ.get('password'),
            database = os.environ.get('db')
        )
    except mysql.connector.Error as err:
        print('Error:', err)
        raise

    return connection

def get_new_id(cursor):
    try:
        cursor.execute('SELECT * FROM users')
        cursor.fetchall()
    except mysql.connector.Error as err:
        print('Error:', err)
        raise

    num_rows = cursor.rowcount

    user_id = num_rows + 1
    user_id = str(user_id)

    return user_id

def get_images_dir(id, upload_folder):
    return os.path.join(upload_folder, id, 'images')

def get_pdf_dir(id, upload_folder):
    return os.path.join(upload_folder, id, 'pdf')

def create_directories(images_dir, pdf_dir):
    #Path(os.path.join(self.upload_folder, self.id)).mkdir(parents=True, exist_ok=True)
    Path(images_dir).mkdir(parents=True, exist_ok=True)
    Path(pdf_dir).mkdir(parents=True, exist_ok=True)

def insert_directories_into_database(cursor, images_dir, pdf_dir):
    cursor.execute(f"INSERT INTO users(images_dir, pdf_dir) VALUES('{images_dir}', '{pdf_dir}')")

def save_images(files, images_dir):
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(images_dir, filename))

def convert_images_to_pdf(images_dir, pdf_dir):
    image_filenames = []

    for extension in SUPPORTED_EXTENSIONS:
        image_filenames.extend(glob(f'{images_dir}/*{extension}'))

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

    pdf.output(f'{pdf_dir}/foto2pdf.pdf')

def get_pdf_dir_from_id(cursor, id):
    try:
        cursor.execute(f"SELECT pdf_dir FROM users WHERE id='{id}'")
    except mysql.connector.Error as err:
        print('Error:', err)
        raise

    pdf_dir = cursor.fetchall()
    return pdf_dir

def check_id_exists(cursor, id):
    try:
        cursor.execute(f"SELECT * FROM users WHERE id='{id}'")
    except mysql.connector.Error as err:
        print('Error:', err)
        raise

    row = cursor.fetchall()

    if len(row) == 0:
        return False

    return True

def get_directories(cursor, id):
    try:
        cursor.execute(f"SELECT images_dir, pdf_dir FROM users WHERE id='{id}'")
    except mysql.connector.Error as err:
        print('Error:', err)
        raise

    directories = cursor.fetchall()

    # Indexing twice gets the directories by itself (no parenthesis and commas)
    images_dir = directories[0][0]
    pdf_dir = directories[0][1]

    return images_dir, pdf_dir

def remove_existing_files(images_dir, pdf_dir):
    remove_existing_images(images_dir)
    remove_existing_pdf(pdf_dir)

def remove_existing_images(images_dir):
    images_files_dir = glob(os.path.join(images_dir, '*'))

    for image_file in images_files_dir:
        os.remove(image_file)

def remove_existing_pdf(pdf_dir):
    pdf_file_dir = glob(os.path.join(pdf_dir, '*'))

    for pdf_file in pdf_file_dir:
        os.remove(pdf_file)

def update_timestamp(cursor, id):
    try:
        cursor.execute(f"UPDATE users SET modified=now() WHERE id='{id}'")
    except mysql.connector.Error as err:
        print('Error:', err)
        raise