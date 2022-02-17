# foto2pdf
foto2pdf is an API that converts JPG, JPEG, and PNG images into a PDF.

## Setup
1. Install dependencies `pip install -r requirements.txt`
2. Install MySQL `brew install mysql` and run `mysql_secure_installation`
3. Enter your credentials in the __.env__ file. You only need to enter the values for __host__, __user__, and __password__. You do not have to modify __db__ unless if you want to use another database name.
4. Run `python3 setup_database.py`. This will create a database and a table to store the data necessary for this project.

## Run
1. In the root directory of the project, cd into the app directory `cd app`
2. Run the server `flask run`

## Endpoints
### /convert
- Method: POST
- __images__ must be included in the request body. _images_ would be the parameter name, and its values would include the actual images. Remember to set Content-Type to multipart/form-data

### /download/:id
- Method: GET
- This returns the PDF file associated with _id_.

## Examples
`curl -F "images=@photo.jpg" http://127.0.0.1:5000/convert`

If successful, you will get the response:
```
{
    "id": "<some_id>", 
    "success": "true"
}
```

`curl http://127.0.0.1:5000/download/1 --output foto2pdf.pdf`

This request attempts to download the PDF associated with the id 1. If successful, you will receive a PDF file.