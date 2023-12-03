"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""
import jsondiff as jd
from jsondiff import diff

from appw import client

from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import data_from


def create_api_key(project_id, key, env):
    _key = client.create_api_key(
        project_id, key["name"], key["scopes"],
        expire=key.get("expire"))
    env[_key.get("name")] = _key.get("secret")


def regenerate_key(project_id, existing, key, env):
    client.remove_api_key(project_id, existing["$id"])
    create_api_key(project_id, key, env)


@data_from('keys.json')
def restore_api_keys(data=None, env=None, **kwargs):
    project_id = env["APPWRITE_PROJECT_ID"]
    existing_keys = client.list_api_keys(project_id)

    log.dim("Syncing API keys")

    for key in data:
        existing = list(
            filter(lambda x: x["name"] == key["name"], existing_keys))

        if existing:
            _diff = diff(existing[0], key, syntax="explicit")

            if jd.update in _diff:
                _diff[jd.update].pop("secret", None)
                _diff[jd.update].pop("$updatedAt", None)
                _diff[jd.update].pop("$createdAt", None)
                _diff[jd.update].pop("accessedAt", None)
                _diff[jd.update].pop("$id", None)

                if _diff[jd.update]:
                    log.success(f"[CHANGE] Regenerating key [{key['name']}]",
                                indent=4)
                    regenerate_key(project_id, existing[0], key, env)
                else:
                    _diff.pop(jd.update, None)

            if _diff:
                log.success(f"[CHANGE] Regenerating key [{key['name']}]",
                            indent=4)
                regenerate_key(project_id, existing[0], key, env)
            else:
                env[existing[0].get("name")] = existing[0].get("secret")
        else:
            log.success(f"[CHANGE] Creating key [{key['name']}]",
                        indent=4)
            create_api_key(project_id, key, env)
