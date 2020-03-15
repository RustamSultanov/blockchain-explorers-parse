import time
import json
import threading
import requests
import os
import subprocess
import re

WEEK = 604800

BLOCK_EXPL_INFO = {
    "block_explorers" : [
     
    ]
} 



def search(d, key, default=None):
    """Return a value corresponding to the specified key in the (possibly
    nested) dictionary d. If there is no item with that key, return
    default.
    """
    stack = [iter(d.items())]
    while stack:
        for k, v in stack[-1]:
            if isinstance(v, dict):
                stack.append(iter(v.items()))
                break
            elif k == key:
                return v
        else:
            stack.pop()
    return default


def get_analytics():      
    while True:
        try:
            counter=-1
            with open('explorers.json', 'r') as file:
                block_expl_info = json.load(file)
            for key in block_expl_info.values():
                url = key['name']
                print(url)
                counter+=1
                try:
                    latest_block = BLOCK_EXPL_INFO['block_explorers']
                    analytics = latest_block[counter]['analytics']
                    find_cdn = f'whois {url}' +'''| grep "Name Server"'''
                    result = subprocess.run(find_cdn, shell=True, universal_newlines=True, stdout=subprocess.PIPE).stdout
                    print(result)
                    cdn = re.findall("cloudflare",result, re.IGNORECASE)
                    if cdn:
                            print('find cdn')
                            latest_block[counter]['cdn'] = 'CloudFlare'
                    else:
                            print("None")
                            latest_block[counter]['cdn'] = None
                    command = f'wget -x http://{url}'
                    os.system(command)
                    with open(f'{url}/index.html', 'r') as files:
                        html = files.read()
                    script_google = re.findall("GoogleAnalyticsObject",html)
                    script_piwik = re.findall("piwik",html)
                    if script_google:
                        print('find google-analytics')
                        analytics[0] = 'Google Analytics'      
                    else:
                        print("None")
                        analytics[0] = None
                    if script_piwik:
                        print('find analytics')
                        analytics[1] = 'Piwik'
                    else:
                        print("None")
                        analytics[1] = None
                except Exception as e:
                    print(e)    
            time.sleep(WEEK)
        except requests.ConnectionError:
            pass

def get_best_height(name,currency,url,best_height_key,num,timer):
    filepath = 'block_expl_info.json'
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 429:
                print('API limit!',url)
                time.sleep(timer)
                continue
            if r.status_code != 200:
                print('unknown code!',r.status_code,url)
                time.sleep(timer)
                continue
            block_info = r.json()
            latest_block = BLOCK_EXPL_INFO
            latest_block_list = latest_block['block_explorers']
            if type(block_info) == int:
                latest_block_list[num]["name"] = name
                latest_block_list[num]["currency"] = currency
                latest_block_list[num]["best_height"] = block_info
                time.sleep(timer)
                with open(filepath, 'w') as block_file:
                    json.dump(BLOCK_EXPL_INFO, block_file)
            else:
                best_height=search(block_info,best_height_key)                                      
                if best_height:
                    if type(best_height) == str:
                        best_height = int(best_height, 0)
                        latest_block_list[num]["name"] = name
                        latest_block_list[num]["currency"] = currency
                        latest_block_list[num]["best_height"] = best_height 
                        time.sleep(timer) 
                        with open(filepath, 'w') as block_file:
                            json.dump(BLOCK_EXPL_INFO, block_file)
                                                    
                    else:
                        latest_block_list[num]["name"] = name
                        latest_block_list[num]["currency"] = currency
                        latest_block_list[num]["best_height"] = best_height
                        time.sleep(timer)
                        with open(filepath, 'w') as block_file:
                            json.dump(BLOCK_EXPL_INFO, block_file)
                else:
                    latest_block_list[num]["name"] = name
                    latest_block_list[num]["currency"] = currency
                    latest_block_list[num]["best_height"] = None
                    time.sleep(timer)
                    with open(filepath, 'w') as block_file:
                        json.dump(BLOCK_EXPL_INFO, block_file)
                    continue
        except Exception as e:
            print(e)




def get_info():
    ''' This function get latest block from diffetent APIs and write in json file'''
    with open('explorers.json', 'r') as file:
        block_expl_info = json.load(file)
    BLOCK_EXPL_INFO['block_explorers'] = [{'analytics': [None,None]} for i in range(len(block_expl_info))]
    analytic_thread = threading.Thread(target=get_analytics)
    analytic_thread.start()
    print(analytic_thread) 
    counter_api=0
    for elem in block_expl_info:
        print(counter_api,elem)
        api = search(block_expl_info[elem],"api")
        name,currency,url,best_height_key,timer=search(block_expl_info[elem],"name"),search(block_expl_info[elem],"currency"),search(block_expl_info[elem],"url"),search(block_expl_info[elem],"best_height_key"),search(block_expl_info[elem],"api_limit")
        if api:
            my_thread = threading.Thread(target=get_best_height, args=(name,currency,url,best_height_key,counter_api,timer))
            counter_api+=1
            my_thread.start() 
            print(my_thread)
        else:
            latest_block = BLOCK_EXPL_INFO
            latest_block_list = latest_block['block_explorers']
            latest_block_list[counter_api]["name"] = name
            latest_block_list[counter_api]["currency"] = currency
            latest_block_list[counter_api]["best_height"] = best_height_key
            latest_block_list[counter_api]["api"] = None
            counter_api+=1



try:
    get_info()
except requests.ConnectionError:
    pass

    
