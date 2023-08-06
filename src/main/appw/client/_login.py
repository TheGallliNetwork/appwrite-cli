import pickle

import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.exceptions import UnauthenticatedError
from appw.utils import APPWRITE_HEADERS, make_request


def login(email_id, password):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/account/sessions/email"
    body = {
        "email": email_id,
        "password": password,
    }

    response = requests.post(endpoint, data=body, headers=APPWRITE_HEADERS)

    if response.status_code != 201:
        raise UnauthenticatedError("[{}] {}".format(
            response.status_code,
            response.json().get("message")))

    with open(".session", "wb") as f:
        pickle.dump(response.cookies, f)


def get_account():
    endpoint = f"{APPWRITE_ENDPOINT}/v1/account"
    return make_request(requests.get, endpoint)
