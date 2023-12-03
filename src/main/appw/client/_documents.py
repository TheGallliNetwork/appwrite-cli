import click
import requests
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


def exception_handler(func):
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.echo("")
            click.secho(e, fg="red")
            click.echo("")
    return _wrapper


@exception_handler
def list_documents(project_id, database_id, collection_id, limit=None, offset=None, search=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/{database_id}/collections/{collection_id}/documents"
    queries = []

    if limit:
        queries.append("limit({})".format(limit))

    if offset:
        queries.append("offset({})".format(offset))
    if search:
        queries.append(Query.search(*search))
    if queries:
        endpoint = "{}?{}".format(
            endpoint,
            "&".join(list(map(lambda x: "queries[{}]={}".format(x, queries[x]),
                              range(len(queries))))))

    response = make_request(requests.get, endpoint, project=project_id)

    return response.get("documents", [])


def get_document(project_id, database_id, collection_id, document_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/documents/{document_id}"

    return make_request(requests.get, endpoint, project=project_id)


def create_document(project_id, database_id, collection_id, document_id=None,
                    permissions=None, data=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/{database_id}/collections/{collection_id}/documents"

    body = {
        "databaseId": database_id,
        "collectionId": collection_id,
        "documentId": document_id or ID.unique(),
        "permissions": permissions or [
            Permission.create(Role.any()),
        ],
        "data": data or {}
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)


def update_document(project_id, database_id, collection_id, document_id, data,
                    permissions=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/documents/{document_id}"

    body = {
        "databaseId": database_id,
        "collectionId": collection_id,
        "documentId": document_id,
        "permissions": permissions,
        "data": data or {}
    }

    return make_request(requests.put, endpoint, body=body, project=project_id)


def remove_document(project_id, database_id, collection_id, document_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/databases/" \
               f"{database_id}/collections/{collection_id}/documents/{document_id}"
    return make_request(requests.delete, endpoint, project=project_id)
