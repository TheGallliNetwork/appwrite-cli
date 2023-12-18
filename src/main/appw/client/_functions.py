import requests
import tarfile

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request


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


def get_function(project_id, f_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{f_id}"
    return make_request(requests.get, endpoint, project=project_id)


def create_function(project_id, name, execute, enabled=True, function_id=None,
                    runtime="python-3.10", events=None, schedule=None,
                    timeout=None, commands=None, entrypoint=None, logging=False,
                    **kwargs):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions"

    if not commands:
        if "python" in runtime:
            commands = "pip install -r requirements.txt"
        elif "node" in runtime:
            commands = "npm install"

    if not execute:
        execute = []
    elif execute and not isinstance(execute, list):
        execute = [execute]

    body = {
        "name": name,
        "functionId": function_id or "unique()",
        "execute": execute,
        "enabled": enabled,
        "logging": logging,
        "runtime": runtime,
        "events": events or [],
        "schedule": schedule or "",
        "timeout": timeout or 15,
        "commands": commands or "",
        "entrypoint": entrypoint or "",
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)


def update_function(project_id, function_id, name, execute, enabled=True,
                    runtime="python-3.10", events=None, schedule=None,
                    timeout=None, commands=None, entrypoint=None, logging=False,
                    **kwargs):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{function_id}"
    if not commands:
        if "python" in runtime:
            commands = "pip install -r requirements.txt"
        elif "node" in runtime:
            commands = "npm install"

    if not execute:
        execute = []
    elif execute and not isinstance(execute, list):
        execute = [execute]

    body = {
        "name": name,
        "functionId": function_id,
        "execute": execute,
        "enabled": enabled,
        "logging": logging,
        "runtime": runtime,
        "events": events or [],
        "schedule": schedule or "",
        "timeout": timeout or 15,
        "commands": commands or "",
        "entrypoint": entrypoint or "",
    }

    return make_request(requests.put, endpoint, body=body, project=project_id)


def remove_function(project_id, f_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{f_id}"

    make_request(requests.delete, endpoint, project=project_id)


def list_deployments(project_id, function_id, limit=None, search=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{function_id}/deployments"
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

    return response.get("deployments", [])


def create_deployment(project_id, function_id, entrypoint, code_path,
                      activate=True):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{function_id}/deployments"
    fname = code_path.split('/')[-1]
    tar = None

    # with tempfile.TemporaryFile(suffix='.tar.gz', mode="wb") as f:
    try:
        tar = tarfile.open(f"{fname}.tar.gz", mode='w:gz')
        tar.add(code_path, arcname=fname)
        tar.close()

        tar = open(f"{fname}.tar.gz", mode="rb")

        files = {
            "code": (f"{fname}.tar.gz", tar, 'application/octet-stream')
        }

        body = {
            "entrypoint": entrypoint,
            "activate": 'true' if activate else 'false',
            "code": None,
        }

        make_request(
            requests.post, endpoint, body=body, project=project_id, files=files
        )
    except Exception as e:
        print(e)
        if tar:
            tar.close()


def list_function_variables(project_id, function_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{function_id}/variables"

    response = make_request(requests.get, endpoint, project=project_id)

    return response.get("variables", [])


def create_function_variable(project_id, function_id, key, value=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{function_id}/variables"

    body = {
        "functionId": function_id,
        "key": key,
        "value": value
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)


def update_function_variable(project_id, function_id, variable_id, key,
                             value=None):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{function_id}/" \
               f"variables/{variable_id}"
    body = {
        "functionId": function_id,
        "variableId": variable_id,
        "key": key,
        "value": value
    }

    return make_request(requests.put, endpoint, body=body, project=project_id)


def remove_function_variable(project_id, function_id, variable_id):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/functions/{function_id}/" \
               f"variables/{variable_id}"

    return make_request(requests.delete, endpoint, project=project_id)
