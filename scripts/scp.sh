#!/bin/sh

ssh  semaphore_centos 'mkdir -p /tmp/semaphore_setup'
scp -r /home/paresh/Repos/tsocial/semaphore_setup/ semaphore_centos:/tmp/semaphore_setup/
ssh semaphore_centos 'cp -r /tmp/semaphore_setup/semaphore_setup/.git  /tmp/semaphore_setup/semaphore_setup.git'
ssh semaphore_centos 'python /tmp/semaphore_setup/semaphore_setup/semaphore_api_call/main.py --username admin --password password --host http://0.0.0.0:3000 --project-file /tmp/semaphore_setup/semaphore_setup/semaphore_config/import_config.json'



