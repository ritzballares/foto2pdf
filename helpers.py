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