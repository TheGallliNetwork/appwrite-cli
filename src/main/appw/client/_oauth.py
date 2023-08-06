from typing import Literal

import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request

Provider = Literal["google", "amazon", "facebook", "yahoo", "microsoft"]


def create_or_update_oauth(project_id: str, provider: Provider, enabled: bool,
                           app_id: str, secret: str):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/projects/{project_id}/oauth2"
    body = {
        "provider": provider,
        "enabled": enabled,
        "appId": app_id,
        "secret": secret,
    }

    return make_request(requests.patch, endpoint, body=body)
