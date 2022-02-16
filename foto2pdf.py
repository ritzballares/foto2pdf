from werkzeug.utils import secure_filename
from helpers import SUPPORTED_EXTENSIONS
from glob import glob
from fpdf import FPDF
from PIL import Image
import os

class FotoToPdf:
    def __init__(self, images_path, pdf_path):
        self.images_path = images_path
        self.pdf_path = pdf_path

    def convert(self, images):
        self.save_images(images)
        self.convert_images_to_pdf()

    def save_images(self, images):
        for image in images:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(self.images_path, image_filename))

    def convert_images_to_pdf(self):
        image_filenames = []

        for extension in SUPPORTED_EXTENSIONS:
            image_filenames.extend(glob(f'{self.images_path}/*{extension}'))

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

            pdf.output(f'{self.pdf_path}/foto2pdf.pdf')