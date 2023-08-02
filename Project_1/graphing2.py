from logging import raiseExceptions
import requests
import os
import random
import time
import shutil
import mysql.connector
import math
import threading


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

request_20_80 = 0
request_50_50 = 0
request_80_20 = 0

def ratio_20_80():
    global request_20_80
    write_count = 8
    read_count = 2
    # print("Writing request_count {0}.".format(request_count))
    key_count = 0
    for filename in os.listdir(test_image_path):
        request_20_80 += 1
        if filename == '.DS_Store':
            continue

        f = os.path.join(test_image_path, filename)
        payload={'key': str(key_count)}
        files = [
            ('file',(filename,open(f,'rb'),'multipart/form-data'))
        ]
        headers = {}
        
        response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
        if response.json()['success'] != 'true':
            print(filename)
            
        write_count -= 1
        key_count += 1


        if write_count == 0:
            response = requests.request("POST", url_list_keys, headers={}, data={})
            if response.json()['success'] != 'true':
                raiseExceptions('Error in reading key list')
            key_list = response.json()['keys']
            while read_count != 0:
                request_20_80 += 1
                selected_key = random.choice(key_list)
                response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
                
                if response.json()['success'] != 'true':
                    raiseExceptions('Error in reading file')

                read_count -= 1
        
            write_count = 8
            read_count = 2
 

def ratio_50_50():
    global request_50_50
    write_count = 5
    read_count = 5
    key_count = 0
    # print("Writing request_count {0}.".format(request_count))
    for filename in os.listdir(test_image_path):
        request_50_50 += 1
        if filename == '.DS_Store':
            continue

        f = os.path.join(test_image_path, filename)
        payload={'key': str(key_count)}
        files = [
            ('file',(filename,open(f,'rb'),'multipart/form-data'))
        ]
        headers = {}
        
        response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
        if response.json()['success'] != 'true':
            print(filename)
            
        write_count -= 1
        key_count += 1



        if write_count == 0:
            response = requests.request("POST", url_list_keys, headers={}, data={})
            if response.json()['success'] != 'true':
                raiseExceptions('Error in reading key list')
            key_list = response.json()['keys']
            while read_count != 0:
                request_50_50 += 1
                selected_key = random.choice(key_list)
                response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
                
                if response.json()['success'] != 'true':
                    raiseExceptions('Error in reading file')

                read_count -= 1
        
            write_count = 5
            read_count = 5
 

def ratio_80_20():
    global request_80_20
    write_count = 2
    read_count = 8
    key_count = 0
    # print("Writing request_count {0}.".format(request_count))
    for filename in os.listdir(test_image_path):
        request_80_20 += 1
        if filename == '.DS_Store':
            continue

        f = os.path.join(test_image_path, filename)
        payload={'key': str(key_count)}
        files = [
            ('file',(filename,open(f,'rb'),'multipart/form-data'))
        ]
        headers = {}
        
        response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
        if response.json()['success'] != 'true':
            print(filename)
            
        write_count -= 1
        key_count += 1



        if write_count == 0:
            response = requests.request("POST", url_list_keys, headers={}, data={})
            if response.json()['success'] != 'true':
                raiseExceptions('Error in reading key list')
            key_list = response.json()['keys']
            while read_count != 0:
                request_80_20 += 1
                selected_key = random.choice(key_list)
                response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
                
                if response.json()['success'] != 'true':
                    raiseExceptions('Error in reading file')

                read_count -= 1
        
            write_count = 2
            read_count = 8
 

def time_keeper(xx):
    i = 1
    k = 5
    while i <= 20:
        time.sleep(k)

        ll = []
        if xx == 0:
            ll.append([i*k, request_20_80])
            print("20_80 time {0} requests {1}".format(i*k, request_20_80))
        elif xx == 1:
            ll.append([i*k, request_50_50])
            print("50_50 time {0} requests {1}".format(i*k, request_50_50))
        elif xx == 2:
            ll.append([i*k, request_80_20])
            print("80_20 time {0} requests {1}".format(i*k, request_80_20))

        i += 1
    
    return ll
        


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
    threading.Thread(target=time_keeper, args=(2,), daemon=True).start()
    res = ratio_80_20()