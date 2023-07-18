import requests

from client.endpoint import APPWRITE_ENDPOINT
from utils import make_request


def list_functions(project_id, limit=None, search=None):
    endpoint = "{}/v1/functions".format(APPWRITE_ENDPOINT)
    queries = []

    if limit:
        queries.append("limit({})".format(limit))

    if search:
        queries.append("search({})".format(search))

    if queries:
        endpoint = "{}?{}".format(
            endpoint,
            "&".join(list(map(lambda x: "queries[{}]={}".format(x, queries[x]),
                              range(len(queries))))))

    response = make_request(requests.get, endpoint, project=project_id)

    return response.get("functions", [])


def create_function(project_id, name, execute, functionId=None, **kwargs):
    pass
