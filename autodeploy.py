from fabric_server_setup import setup_server
from fabric_deploy import setup_scripts, execute_setup_script, put_files_on_server, create_app_user
from utils import get_django_secret_key
import argparse
import json
import os

'''
# todo read configs from file
# todo run command like 
    djangodeploy server {server_conf}
    djangodeploy app {server_conf} {app_conf} 

the files should be in json format

server.json example
{
	"host": "127.0.0.1",
	"port": 2222,
	"new_ssh_port": 22, #optional
	"user": "vm",
	"pass": "123",
	"ssh_key": "/home/vladimir/.ssh/id_rsa.pub",
	"db": "postgres"
}

app.json example
{
    "repo": "https://github.com/smileservices/serviceagencies",
    "name": "serviceagencies",
    "url": "127.0.0.1",
    "user": "serviceagencies",
    "user_pass": "somepass",
    "service_name": "serviceagencies",
    "debug": false,
    "allowed_hosts": "*",
    "db_type": "postgres",
    "db": {
        "address": "localhost",
        "port": "5342",
        "username": "serviceagencies",
        "password": "123pasta",
        "name": "serviceagencies"
    }
}
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('type', help="server for server setup from scratch; app for app deployment")
    parser.add_argument('server', help="the json file with server configuration")
    parser.add_argument('--app', help="the json file with app configuration")
    parser.add_argument('--repo-key', help="private repository key file")
    args = parser.parse_args()

    #get config files
    server_config = json.load(open(os.path.realpath(args.server)))

    if args.type == 'server':
        server_config = setup_server(server_config)

    if args.app:
    # check if app config file was provided
    # deploy app
        app_config = json.load(open(os.path.realpath(args.app)))
        app_config['secret_key'] = get_django_secret_key()
        files = setup_scripts(server_config, app_config, repo_key=args.repo_key)
        do_next = input(f'Setup scripts have been prepared. Press y to upload them and execute or n to cancel?')
        if do_next == 'y':
            create_app_user(server_config, app_config)
            put_files_on_server(server_config, app_config, files)
            execute_setup_script(server_config, app_config, files)
        print('Finished...')