"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""
from appw import client

from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import data_from, set_env
from appw.exceptions import BadRequest
from appw.utils import set_default


@data_from("project.json")
@set_env("APPWRITE_PROJECT_ID", "$id")
@set_env("APPWRITE_PROJECT_NAME", "name")
def restore_project(data=None, env=None, **kwargs):
    old_org_id = env.get("APPWRITE_OLD_ORG_ID")
    org_id = env.get("APPWRITE_ORG_ID")

    if data.get("$id"):
        try:
            projects = client.list_projects(org_id)
            existing = list(
                filter(lambda x: x["name"] == data.get("name"), projects))

            if existing:
                log.dim(f"[SKIP] Project '{data['name']}' exists")
                set_default("project", existing[0])

                return existing[0]

            if old_org_id == org_id:
                project_by_id = client.get_project(data.get("$id"))

                if project_by_id:
                    log.success(
                        f"[CHANGE] Changing project name to {data['name']}")
                    project = client.update_project_name(
                        data.get("$id"), data.get("name")
                    )
                    set_default("project", project)

                    return project
        except:
            pass

    log.success(f"[CHANGE] Creating Project '{data.get('name')}'")

    try:
        project = client.create_project(org_id, data["name"],
                                        project_id=data.get("$id"))
    except BadRequest:
        log.warn(f"Project with id [{data.get('$id')}] already exists. This "
                 f"requires your new callback URL for Oauth to be registered "
                 f"in GCP IAM console.")
        project = client.create_project(org_id, data["name"])

    set_default("project", project)

    return project
