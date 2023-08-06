import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


def list_projects(org_id):
    endpoint = f'{APPWRITE_ENDPOINT}/v1/projects?' \
               f'queries[0]=equal("teamId",+["{org_id}"])&' \
               f'queries[1]=orderDesc("$createdAt")'

    response = make_request(requests.get, endpoint)
    return response.get("projects", [])


def get_project(project_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}?"

    return make_request(requests.get, endpoint)


def create_project(org_id, name, project_id=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects"
    body = {
        "projectId": project_id or "unique()",
        "name": name,
        "teamId": org_id,
        "region": "default"
    }

    return make_request(requests.post, endpoint, body=body)


def update_project_name(project_id, name):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}?"
    body = {
        "name": name
    }

    return make_request(requests.patch, endpoint, body=body)


def remove_project(project_id, password):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}"
    body = {
        "password": password
    }

    make_request(requests.delete, endpoint, body=body)
