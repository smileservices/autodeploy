#!/bin/bash
FILES_PATH=/home/{{superuser}}/{{app_name}}
APP_REPO={{app_repo}}
APP_USER={{app_user}}
APP_NAME={{app_name}}
APP_SERVICE_NAME={{systemd_service}}
APP_USER_PATH=/home/$APP_USER
APP_ROOT_PATH=$APP_USER_PATH/{{app_name}}
APP_MANAGE_PATH=$APP_ROOT_PATH/app
PYTHON_PATH=$APP_USER_PATH/venv/bin/python
PIP_PATH=$APP_USER_PATH/venv/bin/pip

# files paths
FILE_ENV=$FILES_PATH/{{env_file}}
FILE_GUNICORN=$FILES_PATH/{{gunicorn_start}}
FILE_NGINX=$FILES_PATH/{{nginx_conf}}
FILE_SYSTEMD=$FILES_PATH/{{systemd_service}}
# files destinations
FILE_ENV_DEST=$APP_ROOT_PATH/{{env_file}}
FILE_GUNICORN_DEST=$APP_USER_PATH/{{gunicorn_start}}
FILE_NGINX_DEST=/etc/nginx/sites-available/{{nginx_conf}}
FILE_SYSTEMD_DEST=/etc/systemd/system/{{systemd_service}}

rm /etc/nginx/sites-enabled/{{nginx_conf}}
rm $FILE_ENV_DEST
rm $FILE_GUNICORN_DEST
rm $FILE_NGINX_DEST
rm $FILE_SYSTEMD_DEST
rm -rf /var/www/logs/$APP_NAME
rm -rf $APP_ROOT_PATH
rm -rf APP_USER_PATH/venv
systemctl daemon-reload