import requests

from client.endpoint import APPWRITE_ENDPOINT
from utils import make_request


def list_organizations():
    endpoint = "{}/v1/teams".format(APPWRITE_ENDPOINT)
    response = make_request(requests.get, endpoint)

    return response.get("teams", [])


def create_organization(name: str, team_id=None):
    endpoint = "{}/v1/teams".format(APPWRITE_ENDPOINT)
    body = {
        "name": name,
        "teamId": team_id or "unique()"
    }

    return make_request(requests.post, endpoint, body=body)


def remove_organization(org_id):
    endpoint = "{}/v1/teams/{}".format(APPWRITE_ENDPOINT, org_id)
    return make_request(requests.delete, endpoint)
