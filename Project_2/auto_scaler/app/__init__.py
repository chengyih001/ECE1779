from flask import Flask
import os

ROOT_FOLDER = '/Users/Joey/Google_Drive/Year_1_1/ECE1779/Project_2/manager_app/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

global memcache_ec2

memcache_ec2 = {
    'memcache0': None,
    'memcache1': None,
    'memcache2': None,
    'memcache3': None,
    'memcache4': None,
    'memcache5': None,
    'memcache6': None,
    'memcache7': None,
}




auto_scaler = Flask(__name__)
auto_scaler.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auto_scaler.config['IMAGE_FOLDER'] = IMAGE_FOLDER

auto_scaler.config['Max_Miss_Rate_threshold'] = 0.7
auto_scaler.config['Min_Miss_Rate_threshold'] = 0.3
auto_scaler.config['Ratio_by_which_to_expand_the_pool'] = 2.0
auto_scaler.config['Ratio_by_which_to_shrink_the_pool'] = 0.5
auto_scaler.config['mode'] = 0
# auto_scaler.config['mode'] = 1



from app import main
