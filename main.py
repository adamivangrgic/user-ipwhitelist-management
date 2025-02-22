from flask import Flask, request, Response
import requests
import os, os.path, time
import json

app = Flask(__name__)

access_pass = os.environ.get('ACCESS_PASS')
persistent_storage = os.environ.get('PERSISTENT_STORAGE', 'data')

data_file_path = os.path.join(persistent_storage, 'data.json')


def open_data():
    if not os.path.isfile(data_file_path):
        write_data({'users': {}})

    with open(data_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def write_data(data):
    with open(data_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_newest_ip(ips):

    current_time = time.time()
    threshold = 7 * 24 * 60 * 60  # 7 days in seconds

    valid_ips = [ip for ip in ips if current_time - ip['time'] < threshold]
    
    if valid_ips:
        # Return the IP with the newest timestamp
        newest_ip = max(valid_ips, key=lambda x: x['time'])
        return newest_ip['ip']
    return None


@app.route('/return_ips', methods=['GET', 'POST'])
def return_ips():

    ## auth

    if access_pass:
        submitted_pass = request.values.get('pass')
        
        if access_pass != submitted_pass:
            return Response('Forbidden', status=403)

    ##

    data = open_data()
    client_ips = {}

    for user_key in data['users'].keys():
        user = data['users'][user_key]

        if user['enabled']:
            ip = get_newest_ip(user['ips'])

            if ip:
                client_ips[user_key] = ip + '/32'

    output = { "data": { "ipRange": client_ips } }

    return Response(json.dumps(output), mimetype='application/json')

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():

    ## auth

    if access_pass:
        submitted_pass = request.values.get('pass')
        
        if access_pass != submitted_pass:
            return Response('Forbidden', status=403)

    ##

    username = request.values.get('username')
    password = request.values.get('userpass')

    # 'username': {'userpass': <>, 'enabled': True, 'ips': []}

    user_obj = {'userpass': password, 'enabled': True, 'ips': []}

    data = open_data()
    data['users'][username] = user_obj
    write_data(data)

    return Response('OK')

@app.route('/new_ip', methods=['GET', 'POST'])
def new_ip():
    new_ip = request.values.get('ip')

    username = request.values.get('username')
    password = request.values.get('userpass')

    ## auth

    try:
        access_pass = open_data()['users'][username]['userpass']

        if access_pass != password:
            raise KeyError()
    except:
        return Response('Forbidden', status=403)

    ##

    # {'ip': <>, 'time': <>}

    ip_obj = {'ip': new_ip, 'time': time.time()}

    data = open_data()
    data['users'][username]['ips'].append(ip_obj)
    write_data(data)

    return Response('OK')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
