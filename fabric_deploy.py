import os
import crypt
import logging
from fabric import Connection
from deployment_files import make_app_deployment_files
from fabric_server_setup import validate_server

logging.basicConfig(
    filename='deploy.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)

logger = logging.getLogger('DeployScript')


def create_app_user(c: Connection, server_config, app_config):
    enc_password = crypt.crypt(app_config["user_pass"], '22')
    c.sudo(f'useradd -d /home/{app_config["user"]} -p {enc_password} -m {app_config["user"]}', password=server_config["pass"])


def set_up_app(c: Connection, server_config, app_config):

    temp_app_folder = app_config['name']
    install_script_path = os.path.join(
        temp_app_folder,
        app_config['files']['user_install_app_script']
    )

    c.run(f'mkdir {temp_app_folder}')
    c.put(app_config['files']['user_install_app_script_path'], temp_app_folder)
    c.put(app_config['files']['env_file_path'], temp_app_folder)
    c.put(app_config['files']['gunicorn_start_path'], temp_app_folder)
    c.put(app_config['files']['nginx_conf_path'], temp_app_folder)
    c.put(app_config['files']['systemd_service_path'], temp_app_folder)

    c.sudo(f'chmod +x {install_script_path}', password=server_config["pass"])
    c.sudo(install_script_path, password=server_config["pass"])


'''
Run the dev script
'''

def run_deployment(server_config, app_config):

    logger.debug(f'Start the deployment script in {os.getcwd()}: app name is {app_config["name"]} and url {app_config["url"]}')

    c = Connection(
        host=server_config['host'],
        user=server_config['user'],
        port=server_config['port'],
        connect_kwargs={
            'password': server_config['pass']
        }
    )

    # deploy app
    deploy_files_location = os.path.join(os.getcwd(), f"{app_config['name']}_files")
    os.makedirs(deploy_files_location)
    app_config['files'] = make_app_deployment_files(app_config, server_config, deploy_files_location)
    validate_server(c)
    create_app_user(c, server_config, app_config)
    set_up_app(c, server_config, app_config)