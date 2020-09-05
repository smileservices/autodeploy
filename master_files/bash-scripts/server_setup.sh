#!/bin/bash
USER={{user}}

apt-get update
apt-get -y upgrade
apt-get -y install build-essential libpq-dev python-dev
apt-get -y install nginx
apt-get -y install python3-virtualenv
apt-get -y install python3-pip
apt-get -y install git

# setup logs
mkdir /var/www/logs
touch /var/www/logs/nginx-access.log
touch /var/www/logs/nginx-error.log

# secure server
echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config
sed '/PasswordAuthentication yes/d' /etc/ssh/sshd_config -i
systemctl restart sshd

{% if new_ssh_port %}
echo "Port {{new_ssh_port}}" >> /etc/ssh/sshd_config
{% endif %}

{% if db=="postgres" %}
apt-get -y install build-essential libpq-dev python-dev
apt-get -y install postgresql postgresql-contrib
{% endif %}

ufw allow {% if new_ssh_port %}{{new_ssh_port}}{% else %}{{port}}{% endif %}
ufw allow http
ufw allow https
ufw --force enable
ufw --force reset

ssh-keyscan github.com >> ~/.ssh/known_hosts
ssh-keyscan bitbucket.com >> ~/.ssh/known_hosts

echo "server setup script ok" >> ~/server_setup.log
systemctl reboot