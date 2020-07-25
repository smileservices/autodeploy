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


def create_app_user(server_config, app_config):
    c = Connection(
        host=server_config['host'],
        user=server_config['user'],
        port=server_config['port'],
        connect_kwargs={
            'password': server_config['pass']
        }
    )
    enc_password = crypt.crypt(app_config["user_pass"], '22')
    try:
        c.sudo(f'deluser {app_config["user"]}', password=server_config["pass"])
        c.sudo(f'rm -rf /home/{app_config["user"]}', password=server_config["pass"])
        c.sudo(f'useradd -d /home/{app_config["user"]} -p {enc_password} -m {app_config["user"]}',
               password=server_config["pass"])
    except Exception as e:
        logger.error(e)


def put_files_on_server(server_config, app_config, files):
    c = Connection(
        host=server_config['host'],
        user=server_config['user'],
        port=server_config['port'],
        connect_kwargs={
            'password': server_config['pass']
        }
    )

    temp_app_folder = os.path.join(f"/home/{app_config['user']}/temp")
    install_script_path = os.path.join(
        temp_app_folder,
        files['user_install_app_script']
    )
    cleanup_script_path = os.path.join(
        temp_app_folder,
        files['cleanup_script']
    )
    try:
        c.run(f'mkdir {temp_app_folder}')
    except Exception as e:
        logger.debug(e.result.stderr)

    try:
        c.put(files['user_install_app_script_path'], temp_app_folder)
        c.put(files['cleanup_script_path'], temp_app_folder)
        c.put(files['env_file_path'], temp_app_folder)
        c.put(files['gunicorn_start_path'], temp_app_folder)
        c.put(files['nginx_conf_path'], temp_app_folder)
        c.put(files['systemd_service_path'], temp_app_folder)

        c.sudo(f'chmod +x {install_script_path}', password=server_config["pass"])
        c.sudo(f'chmod +x {cleanup_script_path}', password=server_config["pass"])
    except Exception as e:
        logger.error(e.result.stderr)
        logger.debug(f'Running cleanup script {cleanup_script_path}')
        c.sudo(f'{cleanup_script_path}', password=server_config["pass"])
        exit()


def restart_machine(c: Connection, server_config):
    c.sudo('systemctl restart nginx', password=server_config["pass"])


def execute_setup_script(server_config, app_config, files):
    c = Connection(
        host=server_config['host'],
        user=server_config['user'],
        port=server_config['port'],
        connect_kwargs={
            'password': server_config['pass']
        }
    )
    temp_app_folder = os.path.join(f"/home/{app_config['user']}/temp")
    install_script_path = os.path.join(
        temp_app_folder,
        files['user_install_app_script']
    )
    cleanup_script_path = os.path.join(
        temp_app_folder,
        files['cleanup_script']
    )
    try:
        logger.debug(f'Running install script {install_script_path}')
        c.sudo(install_script_path, password=server_config["pass"])
        restart_machine(c, server_config)
    except Exception as e:
        logger.error(e.result.stderr)
        logger.debug(f'Running cleanup script {cleanup_script_path}')
        c.sudo(f'{cleanup_script_path}', password=server_config["pass"])
        exit()


'''
Run the dev script
'''


def setup_scripts(server_config, app_config):
    logger.debug(
        f'Start the deployment script in {os.getcwd()}: app name is {app_config["name"]} and url {app_config["url"]}')
    # deploy app
    files_location = os.path.join(os.getcwd(), f"{app_config['name']}_files")

    files = {
        # paths
        'gunicorn_start_path': os.path.join(files_location, 'gunicorn_start'),
        'nginx_conf_path': os.path.join(files_location, f'{app_config["name"]}'),
        'systemd_service_path': os.path.join(files_location, f'{app_config["name"]}.service'),
        'env_file_path': os.path.join(files_location, '.env'),
        'user_install_app_script_path': os.path.join(files_location, 'user_install_app.sh'),
        'cleanup_script_path': os.path.join(files_location, 'cleanup_script.sh'),

        # file names
        'gunicorn_start': 'gunicorn_start',
        'nginx_conf': f'{app_config["name"]}',
        'systemd_service': f'{app_config["name"]}.service',
        'env_file': '.env',
        'user_install_app_script': 'user_install_app.sh',
        'cleanup_script': 'cleanup_script.sh'
    }

    try:
        os.makedirs(files_location)
    except FileExistsError:
        logger.debug(f'Folder {files_location} already exist.')
    make_app_deployment_files(app_config, server_config, files_location, files)
    return files
