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


@app.route('/return_ips')
def return_ips():

    ## auth

    if access_pass:
        submitted_pass = request.args.get('pass')
        
        if access_pass != submitted_pass:
            return Response('Forbidden', status=403)

    ##

    data = open_data()
    ips = []

    for user_key in data['users'].keys():
        user = data['users'][user_key]

        if user['enabled']:
            
            for ip_obj in user['ips']:
                ips.append(ip_obj['ip'] + '/32') # added subnet mask in cidr notation

    output = { "data": { "ipRange": ips } }

    return Response(json.dumps(output), mimetype='application/json')

@app.route('/new_user')
def new_user():

    ## auth

    if access_pass:
        submitted_pass = request.args.get('pass')
        
        if access_pass != submitted_pass:
            return Response('Forbidden', status=403)

    ##

    username = request.args.get('username')
    password = request.args.get('userpass')

    # 'username': {'userpass': <>, 'enabled': True, 'ips': []}

    user_obj = {'userpass': password, 'enabled': True, 'ips': []}

    data = open_data()
    data['users'][username] = user_obj
    write_data(data)

    return Response('OK')

@app.route('/new_ip')
def new_ip():
    new_ip = request.args.get('ip')

    username = request.args.get('username')
    password = request.args.get('userpass')

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