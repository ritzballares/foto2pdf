from flask import Flask, request, jsonify, send_from_directory
from markupsafe import escape
from db import Db
from foto2pdf import FotoToPdf
from helpers import check_files, get_images_path, get_pdf_path, create_directories


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/client'

@app.route('/convert', methods=['POST'])
def convert():
    if 'images' not in request.files:
        msg = {'error': 'images part not found'}
        return jsonify(msg), 400

    images = request.files.getlist('images')
    images_are_valid = check_files(images)
    if not images_are_valid:
        msg = {'error': 'unsupported file type found'}
        return jsonify(msg), 400

    db = Db()

    user_id = str(db.get_row_count() + 1)
    images_path = get_images_path(user_id, app.config['UPLOAD_FOLDER'])
    pdf_path = get_pdf_path(user_id, app.config['UPLOAD_FOLDER'])
    
    create_directories(images_path, pdf_path)
    db.insert_record(images_path, pdf_path)

    pdf = FotoToPdf(images_path, pdf_path)
    pdf.convert(images)

    db.close()

    msg = {'success': 'true', 'id': f'{user_id}'}
    return jsonify(msg), 200

@app.route('/download/<id>', methods=['GET'])
def download(id):
    id = escape(id)

    db = Db()

    pdf_path = db.get_pdf_path_from_id(id)
    if pdf_path == '':
        msg = {'error': 'id does not exist'}
        return jsonify(msg), 400

    db.close()

    return send_from_directory(pdf_path, 'foto2pdf.pdf')

if __name__ == '__main__':
    app.run()