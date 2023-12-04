import json
from appw.cli import log


def write_snapshots(snapshot):
    _write_project_snapshots(snapshot.get("org", {}),
                             snapshot.get("project", {}))
    _write_keys_snapshots(snapshot.get("project", {}).get("keys", []))
    _write_providers_snapshots(
        snapshot.get("project", {}).get("providers", []))
    _write_platforms_snapshots(snapshot.get("platforms", []))
    _write_db_snapshots(snapshot.get("databases", []))
    _write_function_snapshots(snapshot.get("functions", []))
    _write_bucket_snapshots(snapshot.get("buckets", []))


def _write_project_snapshots(org, project):
    file_root = "snapshot-templates"

    with open(f"{file_root}/org.json", "w+") as f:
        log.info(
            f"✅ [Snapshot] Organization: {org.get('name')} [{org.get('$id')}]")
        json.dump(org, f, indent=4)

    with open(f"{file_root}/project.json", "w+") as f:
        log.info(
            f"✅ [Snapshot] Project: {project.get('name')} [{project.get('$id')}]")
        json.dump({
            "name": project.get("name"),
            "$id": project.get("$id"),
        }, f, indent=4)


def _write_keys_snapshots(keys):
    file_root = "snapshot-templates"

    _keys = []

    for key in keys:
        key["secret"] = "{" + key.get("name") + "}"
        _keys.append(key)

    with open(f"{file_root}/keys.json", "w+") as f:
        log.info("✅ [Snapshot] API Keys")
        json.dump(_keys, f, indent=4)


def _write_providers_snapshots(providers):
    file_root = "snapshot-templates"

    _providers = list(filter(lambda x: x["enabled"], providers))

    with open(f"{file_root}/providers.json", "w+") as f:
        log.info("✅ [Snapshot] Auth Providers")
        json.dump(_providers, f, indent=4)


def _write_platforms_snapshots(platforms):
    file_root = "snapshot-templates"

    with open(f"{file_root}/platforms.json", "w+") as f:
        log.info("✅ [Snapshot] Platforms")
        json.dump(platforms, f, indent=4)


def _write_db_snapshots(dbs):
    file_root = "snapshot-templates"

    for db_id in dbs:
        meta = dbs[db_id]
        db = meta.get("db")

        file_name = "{}/databases/{}.json".format(file_root, db.get("name"))
        with open(file_name, "w+") as f:
            log.info(f"✅ [Snapshot] Database: {db['name']} [{db['$id']}]")
            json.dump(db, f, indent=4)

        for c in meta.get("collections"):
            if not c.get("attributes", []):
                log.dim(
                    f"❌ [Snapshot] Collection: {c['name']} [{c['$id']}] "
                    f"[Skipping: No Attributes]",
                    indent=4)
                continue

            log.info(f"✅ [Snapshot] Collection: {c['name']} [{c['$id']}]",
                     indent=4)

            file_name = "{}/collections/{}.json".format(file_root,
                                                        c.get("name"))
            with open(file_name, "w+") as f:
                c["databaseId"] = "{DB_" + \
                                  db.get("name").replace(' ', '').upper() + \
                                  "_ID}"
                json.dump(c, f, indent=4)


def _write_function_snapshots(functions):
    file_root = "snapshot-templates/functions"

    for fn in functions:
        file_name = "{}/{}.json".format(file_root, fn.get("name"))

        for (index, _) in enumerate(fn["vars"]):
            fn["vars"][index]["value"] = "{" + fn["vars"][index]["key"] + "}"

        with open(file_name, "w+") as f:
            log.info(f"✅ [Snapshot] Function: {fn['name']} [{fn['$id']}]")
            json.dump(fn, f, indent=4)


def _write_bucket_snapshots(buckets):
    file_root = "snapshot-templates"

    with open(f"{file_root}/buckets.json", "w+") as f:
        log.info("✅ [Snapshot] Storage Buckets")
        json.dump(buckets, f, indent=4)
