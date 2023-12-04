"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""
from appw import client
from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import data_from_dir
import dotenv


def _create_function(data, project_id, env):
    log.success(f"[CHANGE] Creating function {data['name']} [{data['$id']}]")
    func = client.create_function(
        project_id, data["name"], data["execute"], data["enabled"],
        runtime=data["runtime"], events=data["events"],
        schedule=data["schedule"], timeout=data["timeout"]
    )

    # Create env variables for the function

    for var in data["vars"]:
        if env.get(var["key"]):
            log.success(f"[CHANGE] Creating env variable [{var['key']}]",
                        indent=4)
        else:
            log.warn(f"[CHANGE] Creating env variable [{var['key']}] "
                     f"(Cannot resolve value, you need to set this yourself)",
                     indent=4)
        client.create_function_variable(project_id, func["$id"], var["key"],
                                        env.get(var["key"], ""))

    # Create a new deployment
    log.success("[CHANGE] Deploying function code", indent=4)

    # TODO: We don't have non-hard-coded solution atm
    entry_point = "src/index.py" if "python" in data[
        "runtime"] else "src/index.js"
    client.create_deployment(project_id, func["$id"], entry_point,
                             f"functions/{func['name']}")


def _update_function(data, existing, project_id, env):
    new_execute = set(data["execute"])
    old_execute = set(existing["execute"])
    added_perm = new_execute - old_execute
    removed_perm = old_execute - new_execute

    if added_perm or removed_perm or data["name"] != existing["name"] or data[
            "runtime"] != existing["runtime"] or data[
                "enabled"] != existing["enabled"]:
        log.success(f"[CHANGE] Updating function '{data['name']}'", indent=4)

        client.update_function(project_id, existing["$id"], data["name"],
                               data["execute"], data["enabled"],
                               data["runtime"], events=data["events"],
                               schedule=data["schedule"],
                               timeout=data["timeout"])
    else:
        log.dim(f"[SKIP] Syncing function '{data['name']}'", indent=4)

    log.success("Updating Environment variables", indent=4)

    for var in existing["vars"]:
        log.dim(f"[CHANGE] Removing '{var['key']}'", indent=8)
        client.remove_function_variable(project_id, existing["$id"],
                                        var["$id"])

    for var in data["vars"]:
        if env.get(var["key"]):
            log.success(f"[CHANGE] Creating '{var['key']}'", indent=8)
        else:
            log.warn(f"[CHANGE] Creating '{var['key']}' "
                     f"(Cannot resolve value, you need to set this yourself)",
                     indent=8)
        client.create_function_variable(project_id, existing["$id"],
                                        var["key"], env.get(var["key"], ""))

    log.success("Deploying function code", indent=4)
    # TODO: We don't have non-hard-coded solution atm
    entry_point = "src/index.py" if "python" in data[
        "runtime"] else "src/index.js"
    client.create_deployment(project_id, existing["$id"], entry_point,
                             f"functions/{data['name']}")


@data_from_dir("functions")
def restore_functions(data=None, env=None, **kwargs):
    project_id = env.get("APPWRITE_PROJECT_ID")
    all_functions = client.list_functions(project_id)

    global_env = {
        **dotenv.dotenv_values(".env"),
        **dotenv.dotenv_values(".env.dev"),
        **env
    }

    for (id, func) in data.items():
        existing = list(
            filter(
                lambda x: x["$id"] == func["$id"] or x["name"].lower() == func[
                    "name"].lower(),
                all_functions
            )
        )

        try:
            if existing:
                _update_function(func, existing[0], project_id, global_env)

            else:
                _create_function(func, project_id, global_env)
        except Exception as e:
            log.error(
                f"Failed '{func['name']}' - {str(e)}")
