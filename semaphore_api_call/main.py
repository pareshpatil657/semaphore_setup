'''
Semaphore module to setup ansible playbooks.
'''
import json
import logging
import argparse

import requests

try:
    import urlparse as up
except ImportError:
    import urllib.parse as up


class Semaphore(object):

    '''
        Semaphore class which takes username, password, host and filename
        to setup a project by calling Seamphore API
    '''

    def __init__(self, username=None, password=None, host=None, filename=None):

        help_string = "Check 'python main.py --help'"

        if not username:
            raise Exception("Please pass semaphore username. %s" % help_string)

        if not password:
            raise Exception("Please pass semaphore password. %s" % help_string)

        if not host:
            raise Exception("Please pass semaphore host. %s" % help_string)

        if not filename:
            raise Exception("Please pass semaphore filename. %s" % help_string)

        if not host.startswith("http"):
            raise Exception("Host name should start with http/https")

        self.username = username
        self.password = password
        self.host = host

        with open(filename) as _file:
            self.project_data = json.load(_file)

        self.keys = {}
        self.repos = {}
        self.inventory = {}
        self.templates = {}
        self.cookie = None
        self.project = None

    def get_complete_url(self, url_name):
        '''
            Get a complete url.
        '''
        return up.urljoin(self.host, "api/"+url_name)

    def login(self):
        '''
            Login to semaphore
        '''
        res = requests.post(
            self.get_complete_url("auth/login"),
            json={"auth":self.username, "password":self.password}
        )
        self.cookie = res.cookies

    def delete_project(self, project_id):
        '''
            Delete a project.
        '''
        requests.delete(
            self.get_complete_url("project/{}".format(project_id)),
            cookies=self.cookie
        )

    def get_entity(self, entity):
        '''
            Get an entity.
        '''
        res = requests.get(
            self.get_complete_url(
                "project/{}/{}".format(self.project.get("id"), entity)),
            cookies=self.cookie
        )
        return res.json()

    def lookup_entity(self, name, key_name='name', entity=None):
        '''
            Search for entity.
        '''
        found_entity = None
        for _, each in enumerate(self.get_entity(entity=entity)):
            if each.get(key_name) == name:
                found_entity = each

        return found_entity

    def create_entity(self, entity=None, data=None):
        '''
            Create an entity like template,key,inventory.
        '''
        req = requests.post(
            self.get_complete_url(
                "project/{}/{}".format(self.project.get("id"), entity)
            ),
            json=data,
            cookies=self.cookie
        )

        if req.status_code not in [200, 201, 204]:
            raise Exception(
                "Error while creating {}. Status code is {}".format(
                    entity, req.status_code
                )
            )

    def get_projects(self):
        '''
            Get all the projects.
        '''
        req = requests.get(
            self.get_complete_url("projects"), cookies=self.cookie)
        return req.json()

    def create_project(self):
        '''
            Create project
        '''
        data = {
            "name":self.project_data.get("project_name"), "alert":True
        }

        req = requests.post(
            self.get_complete_url("projects"), json=data, cookies=self.cookie)

        return req.json()

    def check_project(self):
        '''
            Populate project
        '''

        for _, each in enumerate(self.get_projects()):
            if each.get("name") == self.project_data.get("project_name"):
                logging.info("Deleting project...")
                self.delete_project(each.get("id"))
                break

        logging.info("Creating project...")
        return self.create_project()

    def check_keys(self):
        '''
            Populate keys
        '''

        for _, new_keys in enumerate(self.project_data.get("ssh_keys")):

            name = new_keys.get("name").strip()

            if name in self.keys.keys():
                raise Exception(
                    "Multiple ssh keys with name '{}' found!".format(
                        new_keys.get("name")
                    )
                )

            new_keys["project_id"] = self.project.get("id")
            self.create_entity(entity="keys", data=new_keys)
            self.keys[name] = self.lookup_entity(
                new_keys.get("name"), entity="keys")


    def check_repositories(self):
        '''
            Populate repositories
        '''

        for _, new_repo in enumerate(self.project_data.get("repositories")):

            name = new_repo.get("name").strip()

            if name in self.repos.keys():
                raise Exception(
                    "Multiple repos with name '{}' found!".format(
                        new_repo.get("name")
                    )
                )

            new_repo["project_id"] = self.project.get("id")

            new_repo["ssh_key_id"] = self.keys.get(
                new_repo.get("ssh_key_name")
            ).get("id")

            self.create_entity(entity="repositories", data=new_repo)
            self.repos[name] = self.lookup_entity(
                new_repo.get("name"), entity="repositories")

    def check_inventories(self):
        '''
            Populate inventories
        '''

        for _, new_inventory in enumerate(self.project_data.get("inventory")):

            name = new_inventory.get("name").strip()

            if name in self.inventory.keys():
                raise Exception(
                    "Multiple inventory with name '{}' found!".format(
                        new_inventory.get("name")
                    )
                )

            new_inventory["project_id"] = self.project.get("id")
            new_inventory["ssh_key_id"] = self.keys.get(new_inventory.get("ssh_key_name")).get("id")
            self.create_entity(entity="inventory", data=new_inventory)
            self.inventory[name] = self.lookup_entity(new_inventory.get("name"), entity="inventory")

    def check_templates(self):
        '''
            Populate templates
        '''
        for _, new_template in enumerate(self.project_data.get("templates")):

            name = new_template.get("alias").strip()

            if name in self.templates.keys():
                raise Exception(
                    "Multiple task templates with name '{}' found!".format(
                        new_template.get("alias")
                    )
                )

            new_template["project_id"] = self.project.get("id")
            new_template["ssh_key_id"] = self.keys.get(
                new_template.get("ssh_key_name")
            ).get("id")

            new_template["inventory_id"] = self.inventory.get(
                new_template.get("inventory_name")
            ).get("id")

            new_template["repository_id"] = self.repos.get(
                new_template.get("repository_name")
            ).get("id")

            self.create_entity(entity="templates", data=new_template)
            self.templates[name] = self.lookup_entity(
                new_template.get("alias"), entity="templates", key_name="alias"
            )

    def start(self):
        ''' Start Populating '''
        self.project = self.check_project()
        self.check_keys()
        self.check_repositories()
        self.check_inventories()
        self.check_templates()

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Call semaphore api to import playbooks")
    PARSER.add_argument("--username", type=str, dest="username")
    PARSER.add_argument("--password", type=str, dest="password")
    PARSER.add_argument("--host", type=str, dest="host")
    PARSER.add_argument("--project-file", type=str, dest="file_name")
    ARGS = PARSER.parse_args()

    LOGGER = logging.getLogger()
    LOGGER.setLevel(logging.DEBUG)

    S = Semaphore(
        username=ARGS.username,
        password=ARGS.password,
        host=ARGS.host,
        filename=ARGS.file_name
    )

    S.login()
    S.start()