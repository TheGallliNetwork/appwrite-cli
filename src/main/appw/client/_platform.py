import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


def list_platforms(project_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}/platforms"
    response = make_request(requests.get, endpoint)

    return response.get("platforms", [])


def create_platform(project_id, name=None, type=None, key=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}/platforms"
    _key = "hostname" if type == "web" else "key"

    body = {
        "name": name,
        "type": type,
        _key: key,
    }

    return make_request(requests.post, endpoint, body=body)


def remove_platform(project_id, platform_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/" \
               f"{project_id}/platforms/{platform_id}"
    return make_request(requests.delete, endpoint)
