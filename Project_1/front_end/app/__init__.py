from flask import Flask
import os

ROOT_FOLDER = '/home/ubuntu/ECE1779-Project/front_end/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

webapp = Flask(__name__)
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webapp.config['IMAGE_FOLDER'] = IMAGE_FOLDER

from app import main
