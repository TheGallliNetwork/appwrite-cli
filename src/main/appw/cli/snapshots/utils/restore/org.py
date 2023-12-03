"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""
from appw import client
import inquirer as iq

from appw.cli import log, questions
from appw.cli.snapshots.utils.restore.utils import data_from, set_env
from appw.utils import set_default


@data_from("org.json")
@set_env("APPWRITE_ORG_ID", "$id")
@set_env("APPWRITE_ORG_NAME", "name")
def restore_org(data=None, env=None, **kwargs):
    env["APPWRITE_OLD_ORG_ID"] = data["$id"]
    orgs = client.list_organizations()

    existing = list(filter(lambda x: x["name"] == data.get("name"), orgs))

    if existing:
        log.dim(f"[SKIP] Organization '{data.get('name')}' exists")
        set_default("org", existing[0])

        return existing[0]

    if len(orgs) > 0:
        # there are already some orgs, should we re-use?
        options = [
            {"$id": "old", "name": "Select an existing organization"},
            {"$id": "new", "name": "Create a new organization"}
        ]
        action = iq.prompt(questions.select_from_list(
            options, message=f"Organization with name '{data['name']}' "
                             f"doesn't exist. What do you want to do?"
        ))

        if action["id"] == "old":
            org = iq.prompt(questions.select_from_list(
                orgs, message="Select Organization"
            ))

            org = list(filter(lambda o: o["$id"] == org["id"], orgs))[0]

            log.success(f"[CHANGE] Updating Organization name "
                        f"'{data.get('name')}'")

            org = client.update_organization(data["name"], org["$id"])
            set_default("org", org)

            return org

    log.success(f"[CHANGE] Creating Organization '{data.get('name')}'")

    org = client.create_organization(data.get("name"))
    set_default("org", org)

    return org
