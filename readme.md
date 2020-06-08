# Autodeploy Django

Server configuration and app deployment for django applications

## What it does
This is an automation tool for setting up linux server for hosting your django app.
It works on Ubuntu20.04, should work with Ubuntu18.04 too and maybe on other Debian based servers, i didn't test.

## How to use
1. clone this repo
```angular2html
git clone https://github.com/smileservices/autodeploy
```
2. install the requirements
```angular2html
pip install -r requirements.txt
```
3. Spin up an Ubuntu20.04 or 18.04 VM at DigitalOcean or any other VM providers.
4. Create server config json file with your server configuration:
```angular2html
{
	"host": "127.0.0.1",                                             # server ip address
	"port": 2222,                                                    # server ssh port
	"new_ssh_port": 22,                                              # optional; changes the ssh port for security reasons
	"user": "vm",                                                    # user with sudo access
	"pass": "123",                                                   # user's password
	"ssh_key": "/home/youruser/.ssh/id_rsa.pub",                     # path to ssh public key on your localmachine 
	"db": "postgres"                                                 # only implemented postgresql support. leave like this
}
```
5. Run server setup script
```angular2html
python autodeploy server {path to server config file}
```
It will create the file server_setup.sh which will be uploaded to the server and executed and deploy.log file.
Be sure to provide a valid public key because the script will disable password authentication and will only allow for ssh key authentication
6. Create app config json file:
```angular2html
{
    "repo": "https://github.com/smileservices/serviceagencies",     # repository to clone from
    "name": "serviceagencies",                                      # name of the app
    "url": "www.myapp.com",                                         # url for the app
    "user": "serviceagencies",                                      # system user for the app (better leave it like app name)
    "user_pass": "somepass",                                        # system user pass
    "service_name": "serviceagencies",                              # system service name for the systemd process
    "debug": false,                                                 # debug flag
    "allowed_hosts": "*",                                           # allowed hosts
    "db_type": "postgres",                                          # db type. only postgres implemented so far
}
```
6. Deploy the app
```angular2html
python autodeploy app {server config path} {app config path}
```
It will create a folder which will contain all the app files for deployment on server. The files will be uploaded on the server and the script file will be executed for setting up the app.
What the deploy app script does:
 - creates system user for running the app
 - clones the app inside the user home directory
 - sets up virtualenv and installs the pip packages from the requirements file
 - sets up .env file with DEBUG, ALLOWED_HOSTS, DB, SECRET_KEY
 - install gunicorn and psycopg2
 - set up gunicorn file for delivering the app
 - set up nginx serving
 - set up systemd process
 - creates log directory at /var/www/logs/{app name}
 - run collectstatic and migrate commands
 - 
 
### Deployed Project structure:
If you start a project from scratch, use the project at [djangotemplatescripts](https://github.com/smileservices/djangotemplatescripts) to generate the required structure and bootstrap the new app. 
So far the structure of the apps that the script works with is fixed to this:
```angular2html
settings file:          app_root/{appname}/app/settings.py
manage file:            app_root/{appname}/manage.py
requirements file:      app_root/requirements.txt
```
