git clone https://github.com/adamivangrgic/user-ipwhitelist-management.git

cd user-ipwhitelist-management

docker build -t user-ipwhitelist-management .

docker run --name user-ipwhitelist-management -dp 9201:5000 user-ipwhitelist-management


enviroment variables

ACCESS_PASS = secure_access_password

PERSISTENT_STORAGE = /data by default


ip list endpoint:   http://127.0.0.1:5000/return_ips  ?pass=<env:ACCESS_PASS> ; pass not required if not in env variables

new ip endpoint:    http://127.0.0.1:5000/new_ip  ?ip=<newIP>&username=<user>&userpass=<password>

new user endpoint:  http://127.0.0.1:5000/new_user  ?pass=<env:ACCESS_PASS>&username=<user>&userpass=<password>
