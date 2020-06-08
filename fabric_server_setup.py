from fabric import Connection
from deployment_files import make_server_setup_script
import os

def setup_server(config):

    c = Connection(
        host=config['host'],
        user=config['user'],
        port=config['port'],
        connect_kwargs={
            'password': config['pass']
        }
    )

    setup_script_path, setup_script_name = make_server_setup_script(config, os.getcwd())
    remote_user_home = f'/home/{config["user"]}'
    c.run(f'mkdir {remote_user_home}/.ssh')
    remote_script_path = os.path.join(remote_user_home, setup_script_name)
    c.put(config['ssh_key'], f'{remote_user_home}/.ssh/authorized_keys')
    c.put(setup_script_path, remote_script_path)
    c.run(f'chmod +x {remote_script_path}')
    c.sudo(remote_script_path, password=config['pass'])
    c.close()

    if 'new_ssh_port' in config:
        config['port'] = config['new_ssh_port']
    return config


def validate_server(c: Connection):
    # todo
    pass