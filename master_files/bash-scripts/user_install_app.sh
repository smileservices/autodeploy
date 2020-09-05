#!/bin/bash
FILES_PATH=/home/{{app_user}}/temp
APP_REPO={{app_repo}}
APP_USER={{app_user}}
APP_NAME={{app_name}}
APP_SERVICE_NAME={{systemd_service}}
APP_USER_PATH=/home/$APP_USER
APP_ROOT_PATH=$APP_USER_PATH/{{app_name}}
APP_MANAGE_PATH=$APP_ROOT_PATH/app
PYTHON_PATH=$APP_USER_PATH/venv/bin/python3
PIP_PATH=$APP_USER_PATH/venv/bin/pip3

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

cd $APP_USER_PATH

{% if repo_key_path %}
eval "$(ssh-agent -s)"
ssh-add $APP_USER_PATH/.ssh/id_rsa
{% endif %}

git clone $APP_REPO $APP_ROOT_PATH
chown $APP_USER:$APP_USER $APP_ROOT_PATH -R
echo "=========== done =========="

echo "set up venv"
su -c "virtualenv venv --python=$(which python3)" -m $APP_USER
echo "=========== done =========="

cd $APP_ROOT_PATH
echo "install pip from requirements.txt"
su -c "$PIP_PATH install -r requirements.txt" -m $APP_USER
su -c "$PIP_PATH install gunicorn" -m $APP_USER
echo "=========== done =========="

chmod +x $FILE_GUNICORN
cp $FILE_ENV $FILE_ENV_DEST
cp $FILE_GUNICORN $FILE_GUNICORN_DEST
cp $FILE_NGINX $FILE_NGINX_DEST
cp $FILE_SYSTEMD $FILE_SYSTEMD_DEST

{% if db_type == "postgres" %}
su - postgres <<-'EOF'
        createuser {{app_user}}
        createdb {{app_user}} --owner {{app_user}}
        psql -c "ALTER USER {{app_user}} WITH PASSWORD '{{db_pass}}'"
EOF
su -c "$PIP_PATH install psycopg2" -m $APP_USER
{% endif %}


cd $APP_MANAGE_PATH
echo "doing django commands"
su -c "$PYTHON_PATH manage.py migrate" -m $APP_USER
su -c "$PYTHON_PATH manage.py collectstatic" -m $APP_USER
echo "=========== all done =========="

mkdir /var/www/logs/$APP_NAME
touch /var/www/logs/$APP_NAME/error.log
touch /var/www/logs/$APP_NAME/access.log
ln -s /etc/nginx/sites-available/{{nginx_conf}} /etc/nginx/sites-enabled/{{nginx_conf}}

echo "start and enabling $APP_NAME service..."
systemctl daemon-reload
systemctl enable $APP_SERVICE_NAME
systemctl start $APP_SERVICE_NAME
echo "Testing nginx configuration file..."
nginx -t

# add ssl certificate
# sudo certbot --nginx -d {{app_url}}