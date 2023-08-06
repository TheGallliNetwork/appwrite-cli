import requests
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


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


def create_collection(project_id, database_id, name, collection_id=None,
                      permissions=None, document_security=False):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/{database_id}/collections"

    body = {
        "databaseId": database_id,
        "collectionId": collection_id or ID.unique(),
        "name": name,
        "permissions": permissions or [
            Permission.read(Role.users()),
        ],
        "documentSecurity": document_security
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)


def update_collection(project_id, database_id, name, collection_id,
                      permissions=None, document_security=False, enabled=True):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}"

    body = {
        "databaseId": database_id,
        "collectionId": collection_id or ID.unique(),
        "name": name,
        "permissions": permissions or [
            Permission.read(Role.users()),
        ],
        "documentSecurity": document_security,
        "enabled": enabled
    }

    return make_request(requests.put, endpoint, body=body, project=project_id)


def remove_collection(project_id, database_id, collection_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}"

    return make_request(requests.delete, endpoint, project=project_id)


def list_attributes(project_id, database_id, collection_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/attributes"

    response = make_request(requests.get, endpoint, project=project_id)

    return response.get("attributes", [])


def get_attribute(project_id, database_id, collection_id, key):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/attributes/{key}"

    response = make_request(requests.get, endpoint, project=project_id)

    return response.get("attributes", [])


def create_attribute(project_id, database_id, collection_id, kind, key,
                     required=True, default=None, array=False, elements=None,
                     max=None, min=None, format=None, size=None):
    if kind == "double":
        kind = "float"

    if format == "enum" and elements is not None:
        kind = "enum"

    if format == "email":
        kind = "email"

    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/attributes/{kind}"
    body = {
        "databaseId": database_id,
        "collectionId": collection_id,
        "key": key,
        "required": required,
        "default": default,
        "array": array,
    }

    if size is not None:
        body["size"] = size

    if elements is not None:  # enum
        body["elements"] = elements

    if max is not None:  # numbers
        body["max"] = max

    if min is not None:  # numbers
        body["min"] = min

    if format is not None:  # datetime
        body["format"] = format

    return make_request(requests.post, endpoint, body=body, project=project_id)


def create_relationship(project_id, database_id, collection_id, key,
                        related_collection_id, relation_type, two_way=False,
                        two_way_key=None, on_delete=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/" \
               f"attributes/relationship"
    body = {
        "databaseId": database_id,
        "collectionId": collection_id,
        "key": key,
        "relatedCollectionId": related_collection_id,
        "type": relation_type,
        "twoWay": two_way,
        "onDelete": on_delete or "setNull"
    }

    if two_way:
        body["twoWayKey"] = two_way_key

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


def create_index(project_id, database_id, collection_id, key, type, attributes,
                 orders=None, **kwargs):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/indexes"

    body = {
        "databaseId": database_id,
        "collectionId": collection_id,
        "key": key,
        "type": type,
        "attributes": attributes,
        "orders": orders or ["ASC"]
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)


def remove_index(project_id, database_id, collection_id, key):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/" \
               f"{collection_id}/indexes/{key}"

    return make_request(requests.delete, endpoint, project=project_id)
