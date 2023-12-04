"""
Copyright (c) 2023, The Gallli Network
"""
from appw import client
from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import data_from


@data_from("platforms.json")
def restore_platforms(data=None, env=None):
    project_id = env["APPWRITE_PROJECT_ID"]

    log.dim("Syncing app platforms")

    existing = client.list_platforms(project_id)

    for platform in data:
        exists = list(filter(
            lambda x: x["$id"] == platform["$id"] or x["name"].lower() == platform["name"].lower(),
            existing
        ))

        if exists:
            log.dim(f"[SKIP] Platform '{platform['name']}' exists", indent=4)
            continue

        log.success(f"[SYNC] {platform['name']}", indent=4)
        client.create_platform(
            project_id,
            name=platform["name"],
            type=platform["type"],
            key=platform["key"],
        )
