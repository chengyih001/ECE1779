from logging import raiseExceptions
import requests
import os
import random
import time
import shutil
import mysql.connector
import math
import threading
import boto3


url = '54.167.141.103'

url_upload = "http://" + url + ":5000/api/upload"
url_list_keys = "http://" + url + ":5000/api/list_keys"
url_get_image = "http://" + url + ":5000/api/key/"

test_image_path = "/Users/Joey/Desktop/screenshot_images"

ACCESS_KEY = 'AKIAYXTIZC27HZD67VO7'
SECRET_KEY = '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'

RDS_USERNAME = 'Joey'
RDS_PASSWORD = 'joey0101'
HOST_ENDPOINT = 'ece1779-project2-db0.c5m47mkaqikn.us-east-1.rds.amazonaws.com'


class Bucket(object):
    def __init__(self, name, region):
        self.name = name
        self.region = region
        self.conn = boto3.client('s3', 
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY, 
                        region_name=region
                    )

        if region != 'us-east-1':
            location = {'LocationConstraint': region}
            self.conn.create_bucket(Bucket=name, CreateBucketConfiguration=location)
        else:
            self.conn.create_bucket(Bucket=name)

    def put_image(self, file):
        self.conn.put_object(Bucket=self.name, Body = file, Key=file.filename)

    def get_image(self, filename):
        object = self.conn.get_object(Bucket=self.name, Key=filename)
        return object['Body'].read()
    
    def delete_image(self, filename):
        object = self.conn.delete_object(Bucket=self.name, Key=filename)

class RDS(object):
    def __init__(self, name, instance_class, region, storage):
        self.name = name
        self.region = region
        self.storage = storage
        self.instance_class = instance_class
        self.conn = boto3.client('rds',
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY, 
                        region_name=region
                    )

        repeat_db = False
        list_db = self.conn.describe_db_instances()['DBInstances']
        for db in list_db:
            if db['DBInstanceIdentifier'] == name:
                repeat_db = True
                break
        
        if not repeat_db:
            self.conn.create_db_instance(
                AllocatedStorage=storage,
                DBInstanceClass=instance_class,
                DBInstanceIdentifier=name,
                Engine='MySQL',
                MasterUsername=RDS_USERNAME,
                MasterUserPassword=RDS_PASSWORD,
            )
    
    def start_instance(self):
        self.conn.start_db_instance(DBInstanceIdentifier=self.name)

    def stop_instance(self):
        self.conn.stop_db_instance(DBInstanceIdentifier=self.name)

    def delete_instance(self):
        self.conn.delete_db_instance(
            DBInstanceIdentifier=self.name,
            SkipFinalSnapshot=True,
        )

def get_ec2_ip4_addresses(region='us-east-1') -> list:
    conn = boto3.resource('ec2',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY, 
                    region_name=region
                )
    
    memcache_dict = {}

    for instance in conn.instances.all():
        if (instance.state['Name'] == 'running' and 'memcache' in instance.tags[0]['Value']):
            memcache_dict[instance.tags[0]['Value']] = instance.public_ip_address

            # print(
            #     "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
            #     instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
            #     )
            # )
    return memcache_dict





def rw_ratio_50_50():
    global request_50_50
    request_50_50 = 0
    write_count = 5
    read_count = 5
    key_count = 0
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









# def ratio_20_80():
#     global request_20_80
#     write_count = 8
#     read_count = 2
#     # print("Writing request_count {0}.".format(request_count))
#     key_count = 0
#     for filename in os.listdir(test_image_path):
#         request_20_80 += 1
#         if filename == '.DS_Store':
#             continue

#         f = os.path.join(test_image_path, filename)
#         payload={'key': str(key_count)}
#         files = [
#             ('file',(filename,open(f,'rb'),'multipart/form-data'))
#         ]
#         headers = {}
        
#         response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
#         if response.json()['success'] != 'true':
#             print(filename)
            
#         write_count -= 1
#         key_count += 1


#         if write_count == 0:
#             response = requests.request("POST", url_list_keys, headers={}, data={})
#             if response.json()['success'] != 'true':
#                 raiseExceptions('Error in reading key list')
#             key_list = response.json()['keys']
#             while read_count != 0:
#                 request_20_80 += 1
#                 selected_key = random.choice(key_list)
#                 response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
                
#                 if response.json()['success'] != 'true':
#                     raiseExceptions('Error in reading file')

#                 read_count -= 1
        
#             write_count = 8
#             read_count = 2
 

# def ratio_50_50():
#     global request_50_50
#     write_count = 5
#     read_count = 5
#     key_count = 0
#     # print("Writing request_count {0}.".format(request_count))
#     for filename in os.listdir(test_image_path):
#         request_50_50 += 1
#         if filename == '.DS_Store':
#             continue

#         f = os.path.join(test_image_path, filename)
#         payload={'key': str(key_count)}
#         files = [
#             ('file',(filename,open(f,'rb'),'multipart/form-data'))
#         ]
#         headers = {}
        
#         response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
#         if response.json()['success'] != 'true':
#             print(filename)
            
#         write_count -= 1
#         key_count += 1



#         if write_count == 0:
#             response = requests.request("POST", url_list_keys, headers={}, data={})
#             if response.json()['success'] != 'true':
#                 raiseExceptions('Error in reading key list')
#             key_list = response.json()['keys']
#             while read_count != 0:
#                 request_50_50 += 1
#                 selected_key = random.choice(key_list)
#                 response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
                
#                 if response.json()['success'] != 'true':
#                     raiseExceptions('Error in reading file')

#                 read_count -= 1
        
#             write_count = 5
#             read_count = 5
 

# def ratio_80_20():
#     global request_80_20
#     write_count = 2
#     read_count = 8
#     key_count = 0
#     # print("Writing request_count {0}.".format(request_count))
#     for filename in os.listdir(test_image_path):
#         request_80_20 += 1
#         if filename == '.DS_Store':
#             continue

#         f = os.path.join(test_image_path, filename)
#         payload={'key': str(key_count)}
#         files = [
#             ('file',(filename,open(f,'rb'),'multipart/form-data'))
#         ]
#         headers = {}
        
#         response = requests.request("POST", url_upload, headers=headers, data=payload, files=files)
        
#         if response.json()['success'] != 'true':
#             print(filename)
            
#         write_count -= 1
#         key_count += 1



#         if write_count == 0:
#             response = requests.request("POST", url_list_keys, headers={}, data={})
#             if response.json()['success'] != 'true':
#                 raiseExceptions('Error in reading key list')
#             key_list = response.json()['keys']
#             while read_count != 0:
#                 request_80_20 += 1
#                 selected_key = random.choice(key_list)
#                 response = requests.request("POST", url_get_image + selected_key, headers={}, data={}, files={})
                
#                 if response.json()['success'] != 'true':
#                     raiseExceptions('Error in reading file')

#                 read_count -= 1
        
#             write_count = 2
#             read_count = 8
 

def time_keeper(xx):
    i = 1
    k = 5
    while True:
        time.sleep(k)

        ll = []
        ll.append([i*k, request_50_50])
        print("50_50 time {0} requests {1}".format(i*k, request_50_50))
        # if xx == 0:
        #     ll.append([i*k, request_20_80])
        #     print("20_80 time {0} requests {1}".format(i*k, request_20_80))
        # elif xx == 1:
        #     ll.append([i*k, request_50_50])
        #     print("50_50 time {0} requests {1}".format(i*k, request_50_50))
        # elif xx == 2:
        #     ll.append([i*k, request_80_20])
        #     print("80_20 time {0} requests {1}".format(i*k, request_80_20))

        i += 1
    
    # return ll
        


DUMMY_USER = 0

def db_connect():

    config = {
        'user': 'Joey',
        'password': 'joey0101',
        'host': HOST_ENDPOINT,
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
    res = rw_ratio_50_50()