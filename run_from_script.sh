#!/bin/bash
PROJECT_ROOT=`dirname "$(readlink -f "$0")"`
CWD=$(pwd)
COMMAND=$1
SERVER_CONFIG=$2
APP_CONFIG=$3
if [ $COMMAND == 'server' ]
then
  echo "Will setup server from config file $SERVER_CONFIG in $CWD"
  $PROJECT_ROOT/venv/bin/python $PROJECT_ROOT/autodeploy.py $COMMAND $SERVER_CONFIG
else
  if [ $COMMAND == 'app' ]
  then
    echo "Will deploy app from app config file $APP_CONFIG to the server in $SERVER_CONFIG in $CWD"
    $PROJECT_ROOT/venv/bin/python $PROJECT_ROOT/autodeploy.py $COMMAND $SERVER_CONFIG --app $APP_CONFIG
  fi
fi
