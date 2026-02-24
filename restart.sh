#!/usr/bin/env bash

systemctl stop gunicorn
supervisorctl stop all

pkill -f 'manage.py rqworker' || true
pkill -f 'rqworker' || true

systemctl start gunicorn
supervisorctl start all