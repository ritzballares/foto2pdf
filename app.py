from flask import Flask, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from dotenv import load_dotenv
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], user_id, 'images', filename))


        cursor.execute(f"INSERT INTO users(images_dir, pdf_dir) VALUES('{user_images_dir}', '{user_pdf_dir}')")
        mysql.connection.commit()
        cursor.close()

        msg = {'success': 'true', 'id': f'{user_id}'}
        return jsonify(msg), 200