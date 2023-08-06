import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


def list_api_keys(project_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}/keys"
    response = make_request(requests.get, endpoint)

    return response.get("keys", [])


def remove_api_key(project_id, key):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}/keys/{key}"

    return make_request(requests.delete, endpoint)


def create_api_key(project_id, name, scopes, expire=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}/keys"
    body = {
        "name": name,
        "scopes": scopes,
        "expire": expire or None
    }

    return make_request(requests.post, endpoint, body=body)
