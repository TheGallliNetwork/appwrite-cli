import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


def list_organizations():
    endpoint = f"{APPWRITE_ENDPOINT}/v1/teams"
    response = make_request(requests.get, endpoint)

    return response.get("teams", [])


def create_organization(name: str, team_id=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/teams"
    body = {
        "name": name,
        "teamId": team_id or "unique()"
    }

    return make_request(requests.post, endpoint, body=body)


def update_organization(name: str, team_id: str):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/teams/{team_id}"

    body = {
        "name": name
    }

    return make_request(requests.put, endpoint, body=body)


def remove_organization(org_id):
    endpoint = "{}/v1/teams/{}".format(APPWRITE_ENDPOINT, org_id)
    return make_request(requests.delete, endpoint)
