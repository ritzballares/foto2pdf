from pathlib import Path
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


def get_images_path(id, upload_folder):
    """Creates a path to the images directory and returns it.

    Parameters:
        id: the user's id.
        upload_folder: the path to the upload folder.

    Returns:
        A path to the images directory.
    """
    return os.path.join(upload_folder, id, 'images')


def get_pdf_path(id, upload_folder):
    """Creates a path to the pdf directory and returns it.

    Parameters:
        id: the user's id.
        upload_folder: the path to the upload folder.

    Returns:
        A path to the pdf directory.
    """
    return os.path.join(upload_folder, id, 'pdf')


def create_directories(images_path, pdf_path):
    """Creates directories for images and pdf to be stored in.

    Parameters:
        images_path: the path to the image directory.
        pdf_path: the path to the pdf directory.
    """
    Path(images_path).mkdir(parents=True, exist_ok=True)
    Path(pdf_path).mkdir(parents=True, exist_ok=True)