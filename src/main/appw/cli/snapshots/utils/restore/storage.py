"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""

from appw import client
from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import set_env, data_from


@set_env("BUCKET_{name}_ID", "$id", dynamic_key=True)
def _sync_buckets(data=None, env=None, buckets=None, project_id=None, **kwargs):
    project_id = env.get("APPWRITE_PROJECT_ID")
    _id = data.get("$id")
    _name = data.get("name")

    _bucket = list(
        filter(lambda d: d["name"].lower() == _name.lower(), buckets)
    )

    if not _bucket:
        # find by id
        _bucket = list(filter(lambda d: d["$id"] == _id, buckets))

    if _bucket:
        log.dim(f"[SKIP] Storage Bucket '{_name}' exists")

        return _bucket[0]

    log.success(f"[CHANGE] Creating Storage Bucket '{_name}'")
    _bucket = client.create_bucket(
        project_id, _name,
        bucket_id=_id,
        permissions=data.get("permissions"),
        fileSecurity=data.get("fileSecurity"),
        maximumFileSize=data.get("maximumFileSize"),
        allowedFileExtensions=data.get("allowedFileExtensions", []),
        compression=data.get("compression"),
        encryption=data.get("encryption"),
        antivirus=data.get("antivirus"),
    )

    return _bucket


@data_from("buckets.json")
def restore_buckets(data=None, env=None, **kwargs):
    project_id = env.get("APPWRITE_PROJECT_ID")
    buckets = client.list_databases(project_id)

    for (_id, bucket) in data.items():
        _sync_buckets(data=bucket, env=env, buckets=buckets,
                       project_id=project_id)
