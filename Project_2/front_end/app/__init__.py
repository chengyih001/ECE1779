from flask import Flask
import os

ROOT_FOLDER = '/Users/Joey/Google_Drive/Year_1_1/ECE1779/Project_2/front_end/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

all_memcache_keys = []

webapp = Flask(__name__)
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webapp.config['IMAGE_FOLDER'] = IMAGE_FOLDER

from app import main
