from logging import raiseExceptions
import requests
import os
import random
import time
import shutil
import mysql.connector
import math



# url_upload = "http://127.0.0.1:5000/api/upload"
# url_list_keys = "http://127.0.0.1:5000/api/list_keys"
# url_get_image = "http://127.0.0.1:5000/api/key/"

# test_image_path = "/Users/Joey/Desktop/screenshot_images"

# ROOT_FOLDER = '/Users/Joey/Google_Drive/Year_1_1/ECE1779/Project_1/front_end/app'
# IMAGE_FOLDER = os.path.join('static', 'image')
# UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

url_upload = "http://54.211.145.130:5000/api/upload"
url_list_keys = "http://54.211.145.130:5000/api/list_keys"
url_get_image = "http://54.211.145.130:5000/api/key/"

test_image_path = "/home/ubuntu/ECE1779-Project/screenshot_images"

ROOT_FOLDER = '/home/ubuntu/ECE1779-Project/front_end/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

def ratio_20_80(i):

    t0= time.time()


    request_count = i if i != 0 else 1
    read_count = math.floor(request_count * 0.2) if request_count > 1 else 0
    write_count = math.floor(request_count * 0.8) if request_count > 1 else 1

    # print("Writing request_count {0}.".format(request_count))
    for filename in os.listdir(test_image_path):
        if filename == '.DS_Store':
            continue

        f = os.path.join(test_image_path, filename)
        payload={'key': str(write_count)}
        files = [
            ('file',(filename,open(f,'rb'),'multipart/form-data'))
        ]
        headers = {}
        
        response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
        if response.json()['success'] != 'true':
            print(filename)
            
        write_count -= 1
        if write_count == 0:
            break
    
    response = requests.request("POST", url_list_keys, headers={}, data={})
    if response.json()['success'] != 'true':
        raiseExceptions('Error in reading key list')
    key_list = response.json()['keys']

    while read_count != 0:
        selected_key = random.choice(key_list)
        response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
        
        if response.json()['success'] != 'true':
            raiseExceptions('Error in reading file')

        read_count -= 1
    
    t1 = time.time()
    
    return [request_count, t1 - t0] # CPU seconds elapsed (floating point)
 

def ratio_50_50(i):

    t0= time.time()


    request_count = i if i != 0 else 1
    read_count = math.floor(request_count * 0.5) if request_count > 1 else 0
    write_count = math.floor(request_count * 0.5) if request_count > 1 else 1

    # print("Writing request_count {0}.".format(request_count))
    for filename in os.listdir(test_image_path):
        if filename == '.DS_Store':
            continue

        f = os.path.join(test_image_path, filename)
        payload={'key': str(write_count)}
        files = [
            ('file',(filename,open(f,'rb'),'multipart/form-data'))
        ]
        headers = {}
        
        response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
        if response.json()['success'] != 'true':
            print(filename)
            
        write_count -= 1
        if write_count == 0:
            break
    
    response = requests.request("POST", url_list_keys, headers={}, data={})
    if response.json()['success'] != 'true':
        raiseExceptions('Error in reading key list')
    key_list = response.json()['keys']

    while read_count != 0:
        selected_key = random.choice(key_list)
        response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
        
        if response.json()['success'] != 'true':
            raiseExceptions('Error in reading file')

        read_count -= 1
    
    t1 = time.time()
    
    return [request_count, t1 - t0] # CPU seconds elapsed (floating point)
 

def ratio_80_20(i):

    t0= time.time()


    request_count = i if i != 0 else 1
    read_count = math.floor(request_count * 0.8) if request_count > 1 else 0
    write_count = math.floor(request_count * 0.2) if request_count > 1 else 1

    # print("Writing request_count {0}.".format(request_count))
    for filename in os.listdir(test_image_path):
        if filename == '.DS_Store':
            continue

        f = os.path.join(test_image_path, filename)
        payload={'key': str(write_count)}
        files = [
            ('file',(filename,open(f,'rb'),'multipart/form-data'))
        ]
        headers = {}
        
        response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
        if response.json()['success'] != 'true':
            print(filename)
            
        write_count -= 1
        if write_count == 0:
            break
    
    response = requests.request("POST", url_list_keys, headers={}, data={})
    if response.json()['success'] != 'true':
        raiseExceptions('Error in reading key list')
    key_list = response.json()['keys']

    while read_count != 0:
        selected_key = random.choice(key_list)
        response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
        
        if response.json()['success'] != 'true':
            raiseExceptions('Error in reading file')

        read_count -= 1
    
    t1 = time.time()
    
    return [request_count, t1 - t0] # CPU seconds elapsed (floating point)
 


DUMMY_USER = 0

def db_connect():

    config = {
        'user': 'root',
        'password': 'ece1779pass',
        'host': '127.0.0.1',
        'database': 'image_db'
    }

    try:
        c = mysql.connector.connect(**config)
        return c
    except:
        print("Error when connecting!")
        exit(1)

def initialize_images():
    connect = db_connect()
    cursor = connect.cursor()

    query = ("SELECT COUNT(*) from image")
    cursor.execute(query)
    result = cursor.fetchall()

    if result[0][0] != 0:
        query = ("DELETE FROM image")
        cursor.execute(query)
        connect.commit()
    
    # return print("Successfully cleaned {0} entries in table `image`.".format(result[0][0]))



if __name__ == "__main__":

    ll = []
    for i in range(0, 501, 100):
        r_count = i if i != 0 else 1
        
        res = ratio_20_80(r_count)
        ll.append(res)

        shutil.rmtree(UPLOAD_FOLDER)
        os.mkdir(UPLOAD_FOLDER)

        initialize_images()
    # shutil.rmtree(UPLOAD_FOLDER)
    # os.mkdir(UPLOAD_FOLDER)

    # initialize_images()
    # res = ratio_20_80(500)
    # ll.append(res)
    print("No CACHE 20_80 r_w:")
    print(ll)

    ll2 = []
    for j in range(0, 501, 100):
        r_count2 = j if j != 0 else 1
        
        res2 = ratio_50_50(r_count2)
        ll2.append(res2)

        shutil.rmtree(UPLOAD_FOLDER)
        os.mkdir(UPLOAD_FOLDER)

        initialize_images()
    # shutil.rmtree(UPLOAD_FOLDER)
    # os.mkdir(UPLOAD_FOLDER)

    # initialize_images()
    # res2 = ratio_50_50(500)
    # ll2.append(res2)
    print("No CACHE 50_50 r_w: ")
    print(ll2)

    ll3 = []
    for k in range(0, 501, 100):
        r_count3 = k if k != 0 else 1
        
        res3 = ratio_80_20(r_count3)
        ll3.append(res3)

        shutil.rmtree(UPLOAD_FOLDER)
        os.mkdir(UPLOAD_FOLDER)

        initialize_images()
    # shutil.rmtree(UPLOAD_FOLDER)
    # os.mkdir(UPLOAD_FOLDER)

    # initialize_images()
    # res3 = ratio_80_20(500)
    # ll3.append(res3)
    print("No CACHE 80_20 r_w: ")
    print(ll3)