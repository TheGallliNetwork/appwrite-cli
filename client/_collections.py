import requests

from client.endpoint import APPWRITE_ENDPOINT
from utils import make_request


def list_collections(project_id, database_id, limit=None, offset=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/{database_id}/collections"
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

    return response.get("collections", [])


def get_collection(project_id, database_id, collection_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}"

    return make_request(requests.get, endpoint, project=project_id)


def create_attribute(project_id, database_id, collection_id, kind, key,
                     required=True, default=None, array=False, elements=None,
                     max=None, min=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/attributes/{kind}"
    body = {
        "databaseId": database_id,
        "collectionId": collection_id,
        "key": key,
        "required": required,
        "default": default,
        "array": array,
        "elements": elements,
        "max": max,
        "min": min
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)


def update_attribute(project_id, database_id, collection_id, kind, key,
                     required=True, default=None, array=False, elements=None,
                     max=None, min=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/" \
               f"{collection_id}/attributes/{kind}/{key}"
    body = {
        "databaseId": database_id,
        "collectionId": collection_id,
        "key": key,
        "required": required,
        "default": default,
        "array": array,
        "elements": elements,
        "max": max,
        "min": min
    }

    return make_request(requests.patch, endpoint, body=body,
                        project=project_id)


def remove_attribute(project_id, database_id, collection_id, key):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/" \
               f"{collection_id}/attributes/{key}"

    return make_request(requests.delete, endpoint, project=project_id)
