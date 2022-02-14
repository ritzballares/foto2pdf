from flask import Flask, request, jsonify, send_from_directory
from helpers import check_files
from pathlib import Path
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from fpdf import FPDF
from PIL import Image
from glob import glob
from markupsafe import escape
from model import FotoToPdf
import os
import mysql.connector


SUPPORTED_EXTENSIONS = {
    'jpg': True,
    'jpeg': True,
    'png': True
}
UPLOAD_FOLDER = 'static/client'

app = Flask(__name__)
load_dotenv()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = os.environ.get('host')
app.config['MYSQL_USER'] = os.environ.get('user')
app.config['MYSQL_PASSWORD'] = os.environ.get('password')
app.config['MYSQL_DB'] = os.environ.get('db')

mysql = MySQL(app)

@app.route('/convert', methods=['POST'])
def convert():
    if "images" not in request.files:
        msg = {'error': 'images part not found'}
        return jsonify(msg), 400

    files = request.files.getlist('images')

    images_are_valid = check_files(files)
    if not images_are_valid:
        msg = {'error': 'unsupported file type found'}
        return jsonify(msg), 400

    pdf = FotoToPdf()
    converted_successfully = pdf.convert(files, app.config['UPLOAD_FOLDER'])

    if not converted_successfully:
        return '', 500

    msg = {'success': 'true', 'id': f'{pdf.get_id()}'}
    return jsonify(msg), 200

@app.route('/convert/<id>', methods=['PUT'])
def update(id):
    id = escape(id)

    cursor = mysql.connection.cursor()
    id_exists = cursor.execute(f"SELECT * FROM users WHERE id='{id}'")

    if not id_exists:
        msg = {'error': 'id does not exist'}
        return jsonify(msg), 400

    if "images" not in request.files:
        msg = {'error': 'images part not found'}
        return jsonify(msg), 400

    files = request.files.getlist('images')

    # Check if file type is supported
    for file in files:
        filename_split = file.filename.split(".")
        extension = filename_split[-1]

        if extension not in SUPPORTED_EXTENSIONS:
            msg = {'error': f'unsupported file type - {extension}'}
            return jsonify(msg), 400

    cursor.execute(f"SELECT images_dir, pdf_dir FROM users WHERE id='{id}'")
    directories = cursor.fetchall()

    # Indexing twice gets the directories by itself (no parenthesis and commas)
    images_dir = directories[0][0]
    pdf_dir = directories[0][1]

    # Remove files inside images_dir
    images_files_dir = glob(os.path.join(images_dir, '*'))

    for image_file in images_files_dir:
        os.remove(image_file)

    # Remove pdf file inside pdf_dir
    pdf_file_dir = glob(os.path.join(pdf_dir, '*'))

    for pdf_file in pdf_file_dir:
        os.remove(pdf_file)

    for file in files:
        # Save uploaded images
        filename = secure_filename(file.filename)
        file.save(os.path.join(images_dir, filename))
    
    # Create PDF
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

    cursor.execute(f"UPDATE users SET modified=now() WHERE id='{id}'")
    mysql.connection.commit()
    cursor.close()
    msg = {'success': 'true', 'id': f'{id}'}
    return jsonify(msg), 200

@app.route('/download/<id>', methods=['GET'])
def download(id):
    id = escape(id)

    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT pdf_dir FROM users WHERE id='{id}'")
    pdf_dir = cursor.fetchall()
    cursor.close()

    if len(pdf_dir) == 0:
        msg = {'error': 'id does not exist'}
        return jsonify(msg), 400

    pdf_dir = pdf_dir[0][0] # Gets the pdf_directory by itself (no parenthesis and commas)
    return send_from_directory(pdf_dir, 'foto2pdf.pdf')