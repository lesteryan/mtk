# -*- coding: utf-8 -*-
#!/bin/python3

import hashlib
import time
import sys
import requests

if len(sys.argv) < 2:
    print('please input env [dev, test, prod]')
    sys.exit(1)

env = 'prod'
# env = sys.argv[1]

if env == 'dev':
    ts = str(int(time.time()))
    key = 'ffdf34a2fb9c4a0bbf08362aa6d6c4ae'
    sha = '0A:20:BA:48:4D:8D:B9:66:DF:01:24:5D:57:64:1D:1D:9D:B9:53:52'
    pn = 'com.langgemap'
    an = '朗歌地图'.encode('utf-8')
    sig = hashlib.md5((key + pn + sha + str(ts)).encode()).hexdigest()

    url='http://dev-restapi.langgemap/navigate/terminal/config/acquire?scene=map_data&config=map_data_version.json'
elif env == 'test':
    ts = str(int(time.time()))
    key = '6dc68e9045284c98b9c25083cdbb26ef'
    sha = '0A:20:BA:48:4D:8D:B9:66:DF:01:24:5D:57:64:1D:1D:9D:B9:53:52'
    pn = 'com.langgemap'
    an = '朗歌地图'.encode('utf-8')
    sig = hashlib.md5((key + pn + sha + str(ts)).encode()).hexdigest()

    url='http://test-navigate-router.langge.tech/navigate/terminal/config/acquire?scene=map_data&config=map_data_version.json'
elif env == 'prod':
    ts = str(int(time.time()))
    key = '03ef3a411a3846d189cb6b1bf5d89e2a'
    sha = '0A:20:BA:48:4D:8D:B9:66:DF:01:24:5D:57:64:1D:1D:9D:B9:53:52'
    pn = 'com.langgemap'
    an = '朗歌地图'.encode('utf-8')
    sig = hashlib.md5((key + pn + sha + str(ts)).encode()).hexdigest()

    url='http://navigate.langgemap.com/navigate/terminal/config/acquire?scene=map_data&config=map_data_version.json'
else:
    print(f'invalid env {env}')
    sys.exit(1)

headers = {
    'ts': ts,
    'key': key,
    'sha': sha,
    'pn': pn,
    'sig': sig,
    'an': an,
    'sdv': '1',
    'sev': '1'
}

response = requests.get(url, headers=headers,timeout=5000)
sucess = False

if response.status_code == 200:
    data = response.json()
    if data['code'] == 0:
        print(data['data'])

        with open(file='map_data_version.json', mode='w',encoding='utf-8') as f:
            f.write(data['data'])
            sucess = True

if not sucess:
    print(f'get config failed, http code  {response.status_code}, response {response.content}')
    sys.exit(1)
