"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""
from appw import client
from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import data_from


@data_from("providers.json")
def restore_auth_providers(data=None, env=None):
    project_id = env["APPWRITE_PROJECT_ID"]

    log.dim("Syncing auth providers")

    for provider in data:
        log.success(f"[SYNC] {provider['name']}", indent=4)
        client.create_or_update_oauth(
            project_id,
            provider=provider["name"].lower(),
            enabled=provider.get("enabled"), app_id=provider.get("appId"),
            secret=provider.get("secret"))
