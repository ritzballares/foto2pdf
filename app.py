from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from fpdf import FPDF
from PIL import Image
from glob import glob
import os


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
    if request.method == 'POST':
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

        cursor = mysql.connection.cursor()
        num_rows = cursor.execute('SELECT * FROM users')
        user_id = num_rows + 1
        user_id = str(user_id)
        user_images_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id, 'images')
        user_pdf_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id, 'pdf')

        for file in files:
            # Create directory for specific client
            # In that directory, create /images and /pdf directory
            # /images will hold the client's images, and /pdf will hold the pdf
            try:
                Path(os.path.join(app.config['UPLOAD_FOLDER'], user_id)).mkdir(parents=True, exist_ok=True)
                Path(user_images_dir).mkdir(parents=True, exist_ok=True)
                Path(user_pdf_dir).mkdir(parents=True, exist_ok=True)
            except FileNotFoundError:
                return '', 500
            except FileExistsError:
                return '', 500

            # Save uploaded images
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_images_dir, filename))

        cursor.execute(f"INSERT INTO users(images_dir, pdf_dir) VALUES('{user_images_dir}', '{user_pdf_dir}')")
        
        # Create PDF
        image_filenames = []

        for extension in SUPPORTED_EXTENSIONS:
            image_filenames.extend(glob(f'{user_images_dir}/*{extension}'))

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

        pdf.output(f'{user_pdf_dir}/foto2pdf.pdf')

        mysql.connection.commit()
        cursor.close()

        msg = {'success': 'true', 'id': f'{user_id}'}
        return jsonify(msg), 200

@app.route('/download/<id>', methods=['GET'])
def download(id):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT pdf_dir FROM users where id='{id}'")
    pdf_dir = cursor.fetchall()
    cursor.close()

    if len(pdf_dir) == 0:
        msg = {'error': 'file not found'}
        return jsonify(msg), 404

    pdf_dir = pdf_dir[0][0] # Gets the pdf_directory by itself (no parenthesis and commas)
    return send_from_directory(pdf_dir, 'foto2pdf.pdf')