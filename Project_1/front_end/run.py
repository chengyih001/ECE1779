#!../venv/bin/python
from app import UPLOAD_FOLDER, webapp
import shutil
import os
import db_operations

if __name__ == '__main__':
    shutil.rmtree(UPLOAD_FOLDER)
    os.mkdir(UPLOAD_FOLDER)
    db_operations.initialize_images()
    webapp.run('0.0.0.0', 5000, debug=True)