#!../venv/bin/python
from app import UPLOAD_FOLDER, auto_scaler
import aws_operations
import threading, time
import math
import requests

FRONTEND_LOCATION = 'http://127.0.0.1:5000/'
MANAGER_APP_LOCATION = 'http://127.0.0.1:5002/'


def update_auto_scaler():
    while True:
        if auto_scaler.config['mode'] == 0:
            running_ipv4_dict = aws_operations.get_ec2_ip4_addresses(region='us-east-1')

            metric_dict = {}
            curr_node_count = len(running_ipv4_dict.keys())

            for i in range(curr_node_count):
                metric_dict[str(i)] = aws_operations.get_cloudwatch_stats(instance_id=i)

            miss_rate = []

            for _, metric in metric_dict.items():
                if len(metric['no_request']['Datapoints']) != 0:
                    total_request = metric['no_request']['Datapoints'][0]['Sum']
                    total_miss = metric['miss_rate']['Datapoints'][0]['Sum']
                    miss_rate.append(total_miss/total_request if total_request != 0 else 0)
                # total_hit += metric['hit_rate']['Datapoints'][0]['Average']

    # auto_scaler.config['Max_Miss_Rate_threshold'] = 0.7
    # auto_scaler.config['Min_Miss_Rate_threshold'] = 0.3
    # auto_scaler.config['Ratio_by_which_to_expand_the_pool'] = 2.0
    # auto_scaler.config['Ratio_by_which_to_shrink_the_pool'] = 0.5
            

            ratio = sum(miss_rate) / len(miss_rate) if len(miss_rate) != 0 else 0
            print(miss_rate, ratio)

            if ratio > float(auto_scaler.config['Max_Miss_Rate_threshold']) and len(miss_rate) != 0:
                new_node_count = math.ceil(float(auto_scaler.config['Ratio_by_which_to_expand_the_pool']) * curr_node_count)
                
                if new_node_count > 8:
                    new_node_count = 8
                
                if new_node_count != curr_node_count:
                    print("Scale UP")
                    print(curr_node_count, new_node_count)


                    all_keys = requests.post(str(FRONTEND_LOCATION + 'retrieve_all_keys'))

                    aws_operations.start_memcache_ec2(curr_node_count, new_node_count-1)

                    requests.post(str(MANAGER_APP_LOCATION + 'configure_memcache_external'), params={'size': new_node_count})

                    requests.post(str(MANAGER_APP_LOCATION + 'rebalance_keys'), params={'keys': all_keys.json(), 'size': new_node_count})

            elif ratio < float(auto_scaler.config['Min_Miss_Rate_threshold']) and len(miss_rate) != 0:
                new_node_count = math.ceil(float(auto_scaler.config['Ratio_by_which_to_shrink_the_pool']) * curr_node_count)
                
                if new_node_count < 1:
                    new_node_count = 1

                if new_node_count != curr_node_count:
                    print("Scale DOWN")
                    print(curr_node_count, new_node_count)
                    

                    all_keys = requests.post(str(FRONTEND_LOCATION + 'retrieve_all_keys'))
                    
                    aws_operations.stop_memcache_ec2(new_node_count, curr_node_count-1)

                    requests.post(str(MANAGER_APP_LOCATION + 'rebalance_keys'), params={'keys': all_keys.json(), 'size': new_node_count})



    
        time.sleep(60)



if __name__ == '__main__':
    # print(aws_operations.start_memcache_ec2(0, 0))
    threading.Thread(target=update_auto_scaler, daemon=True).start()
    auto_scaler.run('0.0.0.0', 5001, debug=False)