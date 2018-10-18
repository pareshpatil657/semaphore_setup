#! /bin/python
from __future__ import print_function
import json
import sys

def config():
    return {"repositories":[
        {
            "name": "playbooks",
            "git_url": "/tmp/repositories/semaphore/playbooks/.git",
            "ssh_key_name": "dummy_key"
        }
    ]}

def main():
    if len(sys.argv) < 2:
        print("usage: python script.py config.json")
        sys.exit(127)

    with open(sys.argv[1], "r") as c:
        v = json.loads(c.read())
        v.update(config())
        print(json.dumps(v, indent=2))

main()
