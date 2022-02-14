from flask import Flask, request, jsonify, send_from_directory
from markupsafe import escape
import mysql.connector
import helpers


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/client'

@app.route('/convert', methods=['POST'])
def convert():
    if "images" not in request.files:
        msg = {'error': 'images part not found'}
        return jsonify(msg), 400

    files = request.files.getlist('images')

    images_are_valid = helpers.check_files(files)
    if not images_are_valid:
        msg = {'error': 'unsupported file type found'}
        return jsonify(msg), 400

    try:
        connection = helpers.connect_to_database()
    except mysql.connector.Error:
        return '', 500

    cursor = connection.cursor()

    try:
        id = helpers.get_new_id(cursor)
    except mysql.connector.Error:
        return '', 500

    images_dir = helpers.get_images_dir(id, app.config['UPLOAD_FOLDER'])
    pdf_dir = helpers.get_pdf_dir(id, app.config['UPLOAD_FOLDER'])

    helpers.create_directories(images_dir, pdf_dir)

    try:
        helpers.insert_directories_into_database(cursor, images_dir, pdf_dir)
    except mysql.connector.Error:
        return '', 500

    helpers.save_images(files, images_dir)
    helpers.convert_images_to_pdf(images_dir, pdf_dir)

    connection.commit()
    connection.close()

    msg = {'success': 'true', 'id': f'{id}'}
    return jsonify(msg), 200

@app.route('/convert/<id>', methods=['PUT'])
def update(id):
    if "images" not in request.files:
        msg = {'error': 'images part not found'}
        return jsonify(msg), 400

    # Connect to database
    try:
        connection = helpers.connect_to_database()
    except mysql.connector.Error:
        return '', 500

    cursor = connection.cursor()

    # Check if id exists
    id = escape(id)

    try:
        id_exists = helpers.check_id_exists(cursor, id)
    except mysql.connector.Error:
        return '', 500

    if not id_exists:
        msg = {'error': 'id does not exist'}
        return jsonify(msg), 400

    # Get uploaded files
    files = request.files.getlist('images')

    # Check if the uploaded files are valid
    images_are_valid = helpers.check_files(files)
    if not images_are_valid:
        msg = {'error': 'unsupported file type found'}
        return jsonify(msg), 400

    # Get path for images and pdf
    try:
        images_dir, pdf_dir = helpers.get_directories(cursor, id)
    except mysql.connector.Error:
        return '', 500

    helpers.remove_existing_files(images_dir, pdf_dir)
    helpers.save_images(files, images_dir)
    helpers.convert_images_to_pdf(images_dir, pdf_dir)

    # Update timestamp in database
    try:
        helpers.update_timestamp(cursor, id)
    except mysql.connector.Error:
        return '', 500

    connection.commit()
    connection.close()

    msg = {'success': 'true', 'id': f'{id}'}
    return jsonify(msg), 200

@app.route('/download/<id>', methods=['GET'])
def download(id):
    id = escape(id)

    try:
        connection = helpers.connect_to_database()
    except mysql.connector.Error:
        return '', 500

    cursor = connection.cursor()

    try:
        pdf_dir = helpers.get_pdf_dir_from_id(cursor, id)
    except mysql.connector.Error:
        return '', 500

    connection.close()

    if len(pdf_dir) == 0:
        msg = {'error': 'id does not exist'}
        return jsonify(msg), 400

    # Get the pdf_directory by itself (no parenthesis and commas) by indexing twice
    pdf_dir = pdf_dir[0][0] 
    return send_from_directory(pdf_dir, 'foto2pdf.pdf')

if __name__ == '__main__':
    app.run()