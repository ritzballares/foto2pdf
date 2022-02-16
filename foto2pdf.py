from werkzeug.utils import secure_filename
from helpers import SUPPORTED_EXTENSIONS
from glob import glob
from fpdf import FPDF
from PIL import Image
import os


class FotoToPdf:
    def __init__(self, images_path, pdf_path):
        """Initializes a FotoToPdf object.

        Parameters:
            images_path: a path to the images directory.
            pdf_path: a path to the pdf directory.
        """
        self.images_path = images_path
        self.pdf_path = pdf_path

    def convert(self, images):
        """ Converts the images passed to this function into a pdf.

        Parameters:
            images: a list of images uploaded by the user.
        """
        self.save_images(images)
        self.convert_images_to_pdf()

    def save_images(self, images):
        """Saves the images uploaded by the user into the images directory.

        Parameters:
            images: a list of images uploaded by the user.        
        """
        for image in images:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(self.images_path, image_filename))

    def convert_images_to_pdf(self):
        """Converts the images in the images directory into a PDF and stores it into the PDF directory."""
        image_filenames = []

        pdf = FPDF()
        pdf.oversized_images = 'DOWNSCALE'

        for extension in SUPPORTED_EXTENSIONS:
            # Get all filenames with the extension
            image_filenames.extend(glob(f'{self.images_path}/*{extension}'))

            for image in image_filenames:
                img = Image.open(f'{image}')
                img_width, img_height = img.size

                # Calculate new height to so the image does not go out of bounds
                # Divide the image height by its width and multiply the result with the pdf's max width
                new_height = (img_height / img_width) * pdf.epw

                pdf.add_page()
                pdf.image(img, 0, 0, pdf.epw, new_height)

            image_filenames.clear()

        pdf.output(f'{self.pdf_path}/foto2pdf.pdf')