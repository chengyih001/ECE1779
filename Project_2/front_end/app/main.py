from ctypes import sizeof
from flask import render_template, url_for, request
from app import webapp, all_memcache_keys
from flask import json
import os, requests
import db_operations
import aws_operations
import base64, sys
import request_routing
import time

"'http://100.67.9.114:5001/'"
"'http://127.0.0.1:5001/'"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

AUTO_SCALER_LOCATION = 'http://127.0.0.1:5001/'
MANAGER_APP_LOCATION = 'http://127.0.0.1:5002/'


DEFAULT_CAPACITY = 1000
DEFAULT_POLICY = 'RR'

total_stat = {'no_items': 0,
              'total_size': 0,
              'no_request': 0,
              'miss_rate': 0,
              'hit_rate': 0
              }

s3_bucket = aws_operations.Bucket('ece1779-project2-bucket0', 'us-east-1')

def check_img_name(filename: str) -> bool:
    """
    Check if file is an acceptable image.

    >>> check_image("XXX.jpg")
    True
    >>> check_image("XXX.pdf")
    False
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@webapp.route('/')
def main():

    return render_template("main.html")


# URL endpoints

# Upload:
# relative URL = /api/upload
# enctype = multipart/form-data
# method = POST
# POST parameter: name = key, type = string
# POST parameter: name = file, type = file
@webapp.route('/api/upload', methods=['POST'])
def api_upload():
    """
    Save file to Local File System. Invalidate key in MemCache. If exists same filename, replace with new key. If exists same key, replace file.
    """

    if request.args:
        return json.dumps(
                        {
                            "error": {
                                        "code": 405,
                                        "message": "Appending parameters to URL unallowed!"
                                    },
                            "success": "false"
                        }
                    )

    key = request.form['key']
    file = request.files['file']

    if not key:
        return json.dumps(
                            {
                                "error": {
                                            "code": 400,
                                            "message": "Please enter a key!"
                                        },
                                "success": "false"
                            }
                        )

    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    node_count = len(running_ipv4_dict.keys())

    if file and check_img_name(file.filename):
        
        images = db_operations.display_keys()
        isDuplicatedKey = False

        for image in images:
            if key == image[0] and file.filename == image[1]:
                # return "Saved with same key file pair before! Nothing done."
                return json.dumps(
                                    {
                                        "success": "true"
                                    }
                                )

            # Repeated Key. Update file
            elif key == image[0] and file.filename != image[1]:
                # if os.path.exists(os.path.join(webapp.config['UPLOAD_FOLDER'], image[1])):
                #     os.remove(os.path.join(webapp.config['UPLOAD_FOLDER'], image[1]))
                # else:
                #     return json.dumps(
                #                         {
                #                             "error": {
                #                                         "code": 400,
                #                                         "message": "Unknown Error in api_upload 1"
                #                                     },
                #                             "success": "false"
                #                         }
                #                     )

                s3_bucket.delete_image(str(image[1]))

                db_operations.remove(str(image[0]))
                
                isDuplicatedKey = True
                break

        for image in images:
            # Repeated File. Update Key
            if key != image[0] and file.filename == image[1]:
                db_operations.remove(str(image[0]))
                loc = request_routing.request_route(node_count, str(image[0]))
                memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'
                rm_keys_list = requests.post(str(memcache_loc + 'invalidateKey'), params={'key': str(image[0])})

                for temp_key in rm_keys_list.json():
                    all_memcache_keys.remove(str(temp_key))
                
                # put_res = requests.post(str(MEMCACHE_LOCATION + 'invalidateKey'), params={'key': str(key)})
                
                if not isDuplicatedKey:
                    db_operations.put(str(key), str(file.filename))
                    # return "File duplicated. Updated Key."
                    return json.dumps(
                                        {
                                            "success": "true"
                                        }
                                    )
                                                        
        # file.save(os.path.join(webapp.config['UPLOAD_FOLDER'], file.filename))
        s3_bucket.put_image(file)

        # put_res = requests.post(str(MEMCACHE_LOCATION + 'invalidateKey'), params={'key': str(key)})


        def retry(url, payload):
            try:
                return requests.post(url, params=payload)
            except Exception:
                time.sleep(1)
                return retry(url, payload)

        



        loc = request_routing.request_route(node_count, str(key))
        memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'

        rm_keys_list = retry(str(memcache_loc) + 'invalidateKey', {'key': str(key)})

        for temp_key in rm_keys_list.json():
            all_memcache_keys.remove(str(temp_key))



        
        # if put_res.status_code != 200:
        #     return put_res

        db_operations.put(str(key), str(file.filename))
        
        if len(rm_keys_list.json()) == 0 or (len(rm_keys_list.json()) == 1 and rm_keys_list.json()[0] == str(key)) and not isDuplicatedKey:
            return json.dumps(
                                {
                                    "success": "true"
                                }
                            )

        elif len(rm_keys_list.json()) == 0 or (len(rm_keys_list.json()) == 1 and rm_keys_list.json()[0] == str(key)) and isDuplicatedKey:
            return json.dumps(
                                {
                                    "success": "true"
                                }
                            )
        else:
            # return "There is a problem in put operation!"
            return json.dumps(
                                {
                                  "error": {
                                                "code": 400,
                                                "message": "Unknown Error in api_upload 2"
                                            },
                                    "success": "false"
                                }
                            )

    else:
        return json.dumps(
                            {
                                "error": {
                                            "code": 400,
                                            "message": "File Error! Note that accepted filename extensions are only 'jpg', 'jpeg', 'png', 'gif'."
                                        },
                                "success": "false"
                            }
                        )


# Retrieve all keys
# relative URL = /api/list_keys
# method = POST
@webapp.route('/api/list_keys',methods=['POST'])
def api_list_keys():
    """
    Display all keys stored in database
    """
    if request.args:
        return json.dumps(
                        {
                            "error": {
                                        "code": 405,
                                        "message": "Appending parameters to URL unallowed!"
                                    },
                            "success": "false"
                        }
                    )

    result = db_operations.display_keys()
    res = []
    for row in result:
        key, value = row[0], row[1]
        res.append(str(key))
    
    
    return json.dumps(
                        {
                            "keys": res,
                            "success": "true"
                        }
                    )


# Retrieve an image associated with a key
# relative URL = /api/key/<key_value>
# method = POST
@webapp.route('/api/key/<key_value>',methods=['POST'])
def api_get_key_value(key_value):
    """
    Get data from MemCache Flask instance. If successful, read from Local File System and show context.
    If cache miss, read from Local File System and initiate "put".
    """

    if request.args:
        return json.dumps(
                        {
                            "error": {
                                        "code": 405,
                                        "message": "Appending parameters to URL unallowed!"
                                    },
                            "success": "false"
                        }
                    )

    key = key_value
    # value = db_operations.get(str(key))


    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    node_count = len(running_ipv4_dict.keys())
    loc = request_routing.request_route(node_count, str(key))


    def retry(url, payload):
        try:
            return requests.get(url, params=payload)
        except Exception:
            time.sleep(1)
            return retry(url, payload)


    memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'
    # get_res = requests.get(str(memcache_loc + 'get'), params={'get_key': str(key)})
    get_res = retry(str(memcache_loc + 'get'), {'get_key': str(key)})


    if get_res.status_code != 200:
        return get_res

    value = get_res.json()

    if value != "cache_miss":
        all_memcache_keys.remove(str(key))
        all_memcache_keys.append(str(key))
        return json.dumps(
                                {
                                    "success": "true",
                                    "content" : str(value)
                                }
                            )

    else:
        value = db_operations.get(str(key))
            
        if value == "Unknown Key!":
            return json.dumps(
                                {
                                    "success": "false",
                                    "error": {
                                        "code": 400,
                                        "message": "Unknown Key!"
                                        }
                                }
                            )

        else:
            image_data = s3_bucket.get_image(value)
            image_b64 = base64.b64encode(image_data).decode("utf8")
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            payload = json.dumps({"put_value": image_b64, 'put_key': str(key), 'filename': str(value)})

            all_memcache_keys.append(str(key))

            rm_keys_list = requests.post(str(memcache_loc + 'put'), data=payload, headers=headers)

            for temp_key in rm_keys_list.json():
                all_memcache_keys.remove(str(temp_key))


            return json.dumps(
                                {
                                    "success": "true",
                                    "content" : str(image_b64)
                                }
                            )
            # else:
            #     return json.dumps(
            #                         {
            #                             "success": "false",
            #                             "error": {
            #                                 "code": 500,
            #                                 "message": "Image is not in local file system!"
            #                                 }
            #                         }
            #                     )

        







@webapp.route('/get_keys')
def get_keys():
    return render_template("get_keys.html")

@webapp.route('/upload_photos')
def upload_photos():
    return render_template("upload_photos.html")

@webapp.route('/invalidate_keys')
def invalidate_keys():
    return render_template("invalidate_keys.html")

@webapp.route('/clear_memcache')
def clear_memcache():
    return render_template("clear_memcache.html")

# @webapp.route('/config_memcache')
# def config_memcache():
#     return render_template("config_memcache.html")

# @webapp.route('/get_memcache_stats')
# def get_memcache_stat():
#     return render_template("get_memcache_stats.html")

@webapp.route('/display_db_keys')
def display_db_keys():
    result = db_operations.display_keys()

    return render_template("display_db_keys.html", pairs=result, where='database')

    # return render_template("display_db_keys.html")

@webapp.route('/display_memcache_keys')
def display_memcache_key():
    return render_template("display_memcache_keys.html")


# @webapp.route('/add_to_DB',methods=['POST'])
# def add_to_DB():
#     """
#     MIMICKING DB!!! TESTING ONLY!!!!
#     """
#     key = request.form.get('add_to_DB_key')
#     file = request.form.get('add_to_DB_value')

#     DB_testing[key] = file

#     response = webapp.response_class(
#         response=json.dumps("OK"),
#         status=200,
#         mimetype='application/json'
#     )

#     return response

@webapp.route('/get',methods=['POST'])
def get():
    """
    Get data from MemCache Flask instance. If successful, read from Local File System and show context.
    If cache miss, read from Local File System and initiate "put".
    """
    key = request.form.get('get_key')

    
    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    node_count = len(running_ipv4_dict.keys())
    loc = request_routing.request_route(node_count, str(key))


    def retry(url, payload):
        try:
            return requests.get(url, params=payload)
        except Exception:
            time.sleep(1)
            return retry(url, payload)


    memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'
    # get_res = requests.get(str(memcache_loc + 'get'), params={'get_key': str(key)})
    get_res = retry(str(memcache_loc + 'get'), {'get_key': str(key)})



    # memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'
    # get_res = requests.get(str(memcache_loc + 'get'), params={'get_key': str(key)})



    # get_res = requests.get(str(MEMCACHE_LOCATION + 'get'), params={'get_key': str(key)})
    
    if get_res.status_code != 200:
        return get_res

    value = get_res.json()
    
    if value != "cache_miss":
        all_memcache_keys.remove(str(key))
        all_memcache_keys.append(str(key))
        return render_template("image.html", user_image=("data:image/JPG;base64," + value), where='memcache')

    else:
        # Check DB to see if key exists. If yes, get value from local file sys and put key to memcach. If no, return "Unknown Key".
        # Syncronous? Asyncronous?

        value = db_operations.get(str(key))
        
        if value == "Unknown Key!":
            return "Unknown Get Key"

        else:
            # image_data = open(os.path.join(webapp.config['UPLOAD_FOLDER'], value),'rb').read()
            image_data = s3_bucket.get_image(value)
            image_b64 = base64.b64encode(image_data).decode("utf8")
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            payload = json.dumps({"put_value": image_b64, 'put_key': str(key), 'filename': str(value)})

            all_memcache_keys.append(str(key))

            rm_keys_list = requests.post(str(memcache_loc + 'put'), data=payload, headers=headers)
            print("rm_keys_list", rm_keys_list.json())
            
            for temp_key in rm_keys_list.json():
                all_memcache_keys.remove(str(temp_key))

            print("get ", all_memcache_keys)
            

            # return render_template("image.html", user_image=os.path.join(webapp.config['IMAGE_FOLDER'], value), where='database')
            return render_template("image.html", user_image=("data:image/JPG;base64," + image_b64), where='database')



@webapp.route('/put',methods=['POST'])
def put():
    """
    Save file to Local File System. Invalidate key in MemCache. If exists same filename, replace with new key. If exists same key, replace file.
    """
    key = request.form.get('put_key')
    file = request.files['put_file']

    if not key:
        return "Please enter a key!"

    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    node_count = len(running_ipv4_dict.keys())

    if file and check_img_name(file.filename):
        
        images = db_operations.display_keys()
        isDuplicatedKey = False

        for image in images:
            if key == image[0] and file.filename == image[1]:
                return "Saved with same key file pair before! Nothing done."

            # Repeated Key. Update file
            elif key == image[0] and file.filename != image[1]:
                # if os.path.exists(os.path.join(webapp.config['UPLOAD_FOLDER'], image[1])):
                #     os.remove(os.path.join(webapp.config['UPLOAD_FOLDER'], image[1]))
                # else:
                #     return "The file does not exist"

                s3_bucket.delete_image(str(image[1]))

                db_operations.remove(str(image[0]))
                
                isDuplicatedKey = True
                break

        for image in images:
            # Repeated File. Update Key
            if key != image[0] and file.filename == image[1]:
                db_operations.remove(str(image[0]))
                loc = request_routing.request_route(node_count, str(image[0]))
                memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'
                rm_keys_list = requests.post(str(memcache_loc + 'invalidateKey'), params={'key': str(image[0])})

                for temp_key in rm_keys_list.json():
                    all_memcache_keys.remove(str(temp_key))

                if not isDuplicatedKey:
                    db_operations.put(str(key), str(file.filename))
                    return "File duplicated. Updated Key."
                
        #file.save(os.path.join(webapp.config['UPLOAD_FOLDER'], file.filename))
        s3_bucket.put_image(file)

        # loc = request_routing.request_route(node_count, str(key))
        # memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'

        # rm_keys_list = requests.post(str(memcache_loc + 'invalidateKey'), params={'key': str(key)})



        def retry(url, payload):
            try:
                return requests.post(url, params=payload)
            except Exception:
                time.sleep(1)
                return retry(url, payload)

        
        loc = request_routing.request_route(node_count, str(key))
        memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'

        rm_keys_list = retry(str(memcache_loc) + 'invalidateKey', {'key': str(key)})






        for temp_key in rm_keys_list.json():
            all_memcache_keys.remove(str(temp_key))

        db_operations.put(str(key), str(file.filename))

        print(all_memcache_keys)

        if len(rm_keys_list.json()) == 0 or (len(rm_keys_list.json()) == 1 and rm_keys_list.json()[0] == str(key)) and not isDuplicatedKey:
            return "OK"
        elif len(rm_keys_list.json()) == 0 or (len(rm_keys_list.json()) == 1 and rm_keys_list.json()[0] == str(key)) and isDuplicatedKey:
            return "Key duplicated. Updated file."
        else:
            return "There is a problem in put operation!"
            # return put_res.json()

    else:
        return "Filename Error"

@webapp.route('/invalidateKey',methods=['POST'])
def invalidateKey():
    """
    Drop specific key if key-value in memcache. If not, ignore this request.
    """
    key = request.form.get('invalidate_key')

    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    node_count = len(running_ipv4_dict.keys())
    loc = request_routing.request_route(node_count, str(key))
    memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'

    rm_keys_list = requests.post(str(memcache_loc + 'invalidateKey'), params={'key': str(key)})

    for temp_key in rm_keys_list.json():
        all_memcache_keys.remove(str(temp_key))

    print("invalidateKey ", all_memcache_keys)
    
    
    # if invalKey_res.status_code != 200:
    #     return invalKey_res
    
    return "Successfully invalidated key {0}".format(str(key)) if len(rm_keys_list.json()) != 0 else "Key not in memcache"
    # return invalKey_res.json()




    
@webapp.route('/clear',methods=['POST'])
def clear():
    """
    Drop all keys in memcache.
    """

    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    node_count = len(running_ipv4_dict.keys())
    # loc = request_routing.request_route(node_count, str(key))
    # memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'

    for node in running_ipv4_dict.values():
        memcache_loc = 'http://' + str(node) + ':5001/'
        clear_res = requests.post(str(memcache_loc + 'clear'))
        
        if clear_res.status_code != 200:
            return clear_res
    
    all_memcache_keys.clear()

    print("clear ", all_memcache_keys)


    return "Successfully cleared all keys"

@webapp.route('/display_memcache_keys',methods=['POST'])
def display_memcache_keys():
    """
    Display all keys stored in MemCache
    """

    instance_id = request.form.get('instance_id')

    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()

    memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(instance_id)]) + ':5001/'

    result = requests.get(str(memcache_loc + 'display_keys'))

    res = []
    for i in range(len(result.json())):
        res.append(result.json()[i])

    return render_template("display_keys_2.html", pairs=res, where='memcache')


    # return result.json()[1][0]


@webapp.route('/retrieve_all_keys',methods=['POST'])
def retrieve_all_keys():
    # running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    
    # keys = []

    # for memcache, ipv4 in running_ipv4_dict.items():
    #     temp_keys = requests.get(str('http://' + ipv4 + ':5001/' + 'get_all_keys'))
    #     for i in range(len(temp_keys.json())):
    #         print(temp_keys.json())
    #         keys.append(temp_keys.json()[i][0])

    # return json.dumps(keys)
    
    print("retrieve_all_keys ", all_memcache_keys)

    return json.dumps(all_memcache_keys)
        



