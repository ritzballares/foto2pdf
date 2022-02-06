from flask import Flask, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
import os


SUPPORTED_EXTENSIONS = {
    'jpg': True,
    'jpeg': True,
    'png': True
}
UPLOAD_FOLDER = "static/client"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/convert", methods=["POST"])
def convert():
    if request.method == "POST":
        if "images" not in request.files:
            msg = {"error": "images part not found"}
            return jsonify(msg), 400

        files = request.files.getlist("images")

        # Check if file type is supported
        for file in files:
            filename_split = file.filename.split(".")
            extension = filename_split[-1]

            if extension not in SUPPORTED_EXTENSIONS:
                msg = {"error": f"unsupported file type - {extension}"}
                return jsonify(msg), 400

        user_id = uuid.uuid4()
        user_id = str(user_id)
        user_images_dir = os.path.join(app.config["UPLOAD_FOLDER"], user_id, "images")
        user_pdf_dir = os.path.join(app.config["UPLOAD_FOLDER"], user_id, "pdf")

        for file in files:
            # Create directory for specific client
            # In that directory, create /images and /pdf directory
            # /images will hold the client's images, and /pdf will hold the pdf
            try:
                Path(os.path.join(app.config["UPLOAD_FOLDER"], user_id)).mkdir(parents=True, exist_ok=True)
                Path(user_images_dir).mkdir(parents=True, exist_ok=True)
                Path(user_pdf_dir).mkdir(parents=True, exist_ok=True)
            except FileNotFoundError:
                return "", 500
            except FileExistsError:
                return "", 500

            # Save uploaded images
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], user_id, "images", filename))

        msg = {"success": "true", "id": f"{user_id}"}
        return jsonify(msg), 200