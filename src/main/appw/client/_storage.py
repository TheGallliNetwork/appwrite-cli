import requests

from appw.client.endpoint import APPWRITE_ENDPOINT
from appw.utils import make_request

def list_buckets(project_id, limit=None, offset=None):
    endpoint = "{}/v1/storage/buckets".format(APPWRITE_ENDPOINT)
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

    return response.get("buckets", [])


def create_bucket(project_id, name, bucket_id=None, permissions=None,
                  file_security=False, maximum_file_size=None,
                  allowed_file_extensions=None, compression=None,
                  encryption=False, antivirus=False):
    endpoint = f"{APPWRITE_ENDPOINT}/v1/storage/buckets"
    body = {
        "name": name,
        "bucketId": bucket_id or "unique()",
        "permissions": permissions,
        "fileSecurity": file_security,
        "maximumFileSize": maximum_file_size,
        "allowedFileExtensions": allowed_file_extensions or [],
        "compression": compression,
        "encryption": encryption,
        "antivirus": antivirus,
    }

    return make_request(requests.post, endpoint, body=body, project=project_id)
