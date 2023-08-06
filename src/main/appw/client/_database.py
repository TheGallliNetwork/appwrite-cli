import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


def list_databases(project_id, limit=None, offset=None):
    endpoint = "{}/v1/databases".format(APPWRITE_ENDPOINT)
    queries = []

    if limit:
        queries.append("limit({})".format(limit))

    if offset:
        queries.append("offset({})".format(offset))

    if queries:
        endpoint = "{}?{}".format(
            endpoint,
            "&".join(list(map(lambda x: "queries[{}]={}".format(x, queries[x]),
                              range(len(queries))))))

    response = make_request(requests.get, endpoint, project=project_id)

    return response.get("databases", [])


def get_database(project_id, db_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/{db_id}"
    return make_request(requests.get, endpoint, project=project_id)


def create_database(project_id, name, database_id=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases"
    body = {
        "name": name,
        "databaseId": database_id or "unique()"
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)


def remove_database(project_id, db_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/{db_id}"

    make_request(requests.delete, endpoint, project=project_id)
