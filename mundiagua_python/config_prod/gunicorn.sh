#!/bin/bash

# This script is only for production purposes

NAME="mundiagua_py"                          # Name of the application
DJANGODIR=/root/mundiagua_saas          # Django project directory
VENVDIR=/root/.virtualenvs/mundiagua_py  	   # Virtual Ennvironment directory
USER=root                              # The user to run as
GROUP=root                             # The group to run as
NUM_WORKERS=1                          # How many worker processes
                                       # should Gunicorn spawn?
DJANGO_WSGI_MODULE=mundiagua_python.wsgi         # WSGI module name
# Which settings file should Django use?
DJANGO_SETTINGS_MODULE=mundiagua_python.settings_prod

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
source $VENVDIR/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
cd $DJANGODIR

# Start your Django Gunicorn
# Programs meant to be run under supervisor should
# not daemonize themselves (do not use --daemon)
exec $VENVDIR/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=0.0.0.0:8001 \
  --log-level=debug \
  --log-file=-