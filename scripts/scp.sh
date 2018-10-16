#!/bin/sh

scp -r /home/paresh/home/paresh/Repos/semaphore_setup/ semaphore_centos:/tmp/repositories/
ssh semaphore_centos 'cp -r /tmp/repositories/.git  /tmp/repositories/semaphore_setup'
ssh semaphore_centos 'python /tmp/repositories/devops_idea_semaphore/semaphore_api_call/main.py --username admin --password password --host http://0.0.0.0:3000 --project-file /tmp/repositories/devops_idea_semaphore/semaphore_config/import_config.json'



