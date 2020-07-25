import os
import chevron
import master_files
import utils
from jinja2 import Template
import secrets

'''
set up deployment files for the specific app
- gunicorn start
- nginx config file
- systemd for gunicorn process
'''

MASTER_FILES_PATH = os.path.join(
    os.path.dirname(master_files.__file__),
    'deployment-files'
)

MASTER_SCRIPT_FILES_PATH = os.path.join(
    os.path.dirname(master_files.__file__),
    'bash-scripts'
)


def make_server_setup_script(config, location_path):
    file_name = 'server_setup.sh'
    rendered = Template(
        open(os.path.join(MASTER_SCRIPT_FILES_PATH, 'server_setup.sh'))
            .read()
    ).render(config)
    with open(os.path.join(location_path, file_name), 'w') as script_file:
        script_file.write(rendered)
    return os.path.realpath(file_name), file_name


def make_app_deployment_files(app_config, server_config, location_path, files):
    config_dict = {
        'superuser': server_config['user'],
        'app_name': app_config['name'],
        'app_user': app_config['user'],
        'app_dir': app_config['name'],
        'app_service': app_config['service_name'],
        'app_url': app_config['url'],
        'app_repo': app_config['repo'],
        'db_type': app_config['db_type'],
        'db_pass': secrets.token_urlsafe(16)
    }

    if os.path.exists(location_path) and os.listdir(location_path):
        do_next = input(f'The path for deployment files already exists at {location_path}.\nExisting files: {os.listdir(location_path)}\n Overwrite (y) or use the existing ones (n)?')
        if do_next == 'n':
            return False
    os.chdir(location_path)
    config_dict['files'] = files

    with open(os.path.join(MASTER_FILES_PATH, "gunicorn_start.template"), "r") as f:
        rendered = chevron.render(f, config_dict)
        with open(files['gunicorn_start'], 'w') as gf:
            gf.write(rendered)

    with open(os.path.join(MASTER_FILES_PATH, "nginx_config.template"), "r") as f:
        rendered = chevron.render(f, config_dict)
        with open(f'{config_dict["app_name"]}', 'w') as nginxf:
            nginxf.write(rendered)

    with open(os.path.join(MASTER_FILES_PATH, "systemd.template"), "r") as f:
        rendered = chevron.render(f, config_dict)
        with open(files['systemd_service'], 'w') as systemdf:
            systemdf.write(rendered)

    with open(files['env_file_path'], 'w') as envfile:
        db_url = False
        if app_config["db_type"] == 'postgres':
            app_config['db'] = {
                'address': 'localhost',
                'port': '5432',
                'name': config_dict['app_user'],
                'username': config_dict['app_user'],
                'password': config_dict['db_pass'],
            }
            db_url = utils.get_postgresql_url(**app_config['db'])
        if app_config["db_type"] == 'sqlite':
            db_url = utils.get_sqlite_url(app_config['db']['path'])

        if not db_url:
            raise ValueError('DB config is empty!')

        envfile.write(f'SECRET_KEY={app_config["secret_key"]}\n')
        envfile.write(f'DEBUG={app_config["debug"]}\n')
        envfile.write(f'ALLOWED_HOSTS={app_config["allowed_hosts"]}\n')
        envfile.write(f'DB={db_url}')

    rendered_script_file = Template(
        open(os.path.join(MASTER_SCRIPT_FILES_PATH, files['user_install_app_script'])).read()).render({**config_dict, **files})

    rendered_cleanup_script = Template(
        open(os.path.join(MASTER_SCRIPT_FILES_PATH, files['cleanup_script'])).read()).render({**config_dict, **files})

    with open(files['user_install_app_script'], 'w') as script_file:
        script_file.write(rendered_script_file)

    with open(files['cleanup_script'], 'w') as script_file:
        script_file.write(rendered_cleanup_script)
