"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""

from appw import client
from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import set_env, data_from_dir


@set_env("DB_{name}_ID", "$id", dynamic_key=True)
def _sync_database(data=None, env=None, databases=None, project_id=None,
                   **kwargs):
    project_id = env.get("APPWRITE_PROJECT_ID")
    db_id = data.get("$id")
    db_name = data.get("name")

    db = list(
        filter(lambda d: d["name"].lower() == db_name.lower(), databases)
    )

    if not db:
        # find by id
        db = list(filter(lambda d: d["$id"] == db_id, databases))

    if db:
        log.dim(f"[SKIP] Database '{db_name}' exists")

        return db[0]

    log.success(f"[CHANGE] Creating database '{db_name}'")
    db = client.create_database(project_id, db_name, db_id)

    return db


@data_from_dir("databases")
def restore_databases(data=None, env=None, **kwargs):
    project_id = env.get("APPWRITE_PROJECT_ID")
    all_databases = client.list_databases(project_id)

    for (db_id, db) in data.items():
        _sync_database(data=db, env=env, databases=all_databases,
                       project_id=project_id)
