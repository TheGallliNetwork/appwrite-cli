"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""
from time import sleep

from appw import client
from appw.cli import log
from appw.cli.snapshots.utils.restore.utils import data_from_dir, set_env
from appw.exceptions import BadRequest


def _create_attributes(collection, attributes, database_id, project_id,
                       relationships=None):
    for attr in attributes:
        if attr["type"] == "relationship":
            if collection["$id"] not in relationships:
                relationships[collection["$id"]] = {
                    "collection": collection,
                    "relations": []
                }

            relationships[collection["$id"]]["relations"].append(attr)

            continue

        log.success(f"[CHANGE] Creating attribute '{attr['key']}'",
                    indent=4)
        client.create_attribute(
            project_id, database_id, collection["$id"], attr["type"],
            attr["key"], required=attr["required"], default=attr["default"],
            array=attr["array"], elements=attr.get("elements"),
            max=attr.get("max"), min=attr.get("min"),
            format=attr.get("format"), size=attr.get("size")
        )


def _delete_attributes(collection, attributes, database_id, project_id):
    for attr in attributes:
        log.error(f"[CHANGE] Deleting attribute '{attr['key']}'",
                  indent=4)
        client.remove_attribute(
            project_id, database_id, collection["$id"], attr["key"]
        )


def _create_indexes(collection, indexes, database_id, project_id):
    for attr in indexes:
        log.success(f"[CHANGE] Creating index '{attr['key']}'",
                    indent=4)
        client.create_index(
            project_id, database_id, collection["$id"],
            type=attr["type"],
            key=attr["key"],
            attributes=attr.get("attributes", []),
            orders=attr.get("orders", ["ASC"])
        )


def _delete_indexes(collection, indexes, database_id, project_id):
    for attr in indexes:
        log.error(f"[CHANGE] Deleting index '{attr['key']}'",
                  indent=4)
        client.remove_index(
            project_id, database_id, collection["$id"], attr["key"]
        )


@set_env("COLLECTION_{name}_ID", "$id", dynamic_key=True)
def _sync_collection(data, database_id, project_id, relationships=None, env=None):
    collections = client.list_collections(project_id, database_id)
    c_name = data["name"]
    c_id = data["$id"]

    existing = list(
        filter(lambda c: c["name"].lower() == c_name.lower(), collections)
    )

    if not existing:
        existing = list(filter(lambda c: c["$id"] == c_id, collections))

    if not existing:
        log.success(f"[CHANGE] Creating collection '{c_name}'")
        c = client.create_collection(
            project_id, database_id, c_name, c_id,
            permissions=data.get("$permissions", []),
            document_security=data.get("documentSecurity", False)
        )

        _create_attributes(
            c, data.get("attributes", []), database_id, project_id,
            relationships=relationships
        )

        # wait for some of the async ops to complete
        log.dim("....waiting")
        sleep(3)

        _create_indexes(
            c, data.get("indexes", []), database_id, project_id
        )

        return c

    existing = existing[0]
    existing_attrs = set(map(lambda x: x["key"], existing["attributes"]))
    snap_attrs = set(map(lambda x: x["key"], data["attributes"]))

    existing_indexes = set(map(lambda x: x["key"], existing["indexes"]))
    snap_indexes = set(map(lambda x: x["key"], data["indexes"]))

    _attributes_inserted_keys = snap_attrs - existing_attrs
    _attributes_deleted_keys = existing_attrs - snap_attrs

    _attributes_insert = list(filter(
        lambda x: x["key"] in _attributes_inserted_keys, data["attributes"]))
    _attributes_delete = list(filter(
        lambda x: x["key"] in _attributes_deleted_keys,
        existing["attributes"]))

    _indexes_inserted_keys = snap_indexes - existing_indexes
    _indexes_deleted_keys = existing_indexes - snap_indexes

    _indexes_insert = list(filter(
        lambda x: x["key"] in _indexes_inserted_keys, data["indexes"]))
    _indexes_delete = list(filter(
        lambda x: x["key"] in _indexes_deleted_keys, existing["indexes"]))

    log.success(f"[CHANGE] Syncing collection '{existing['name']}'")
    existing = client.update_collection(
        project_id, database_id,
        data.get("name", existing.get("name")),
        existing["$id"],
        permissions=data.get("$permissions", existing.get("$permissions")),
        document_security=data.get("documentSecurity",
                                   existing.get("documentSecurity")),
        enabled=data.get("enabled", existing.get("enabled")),
    )

    if not _attributes_insert and not _attributes_delete:
        log.dim("[SKIP] All attributes up to date", indent=4)

    if _attributes_insert:
        _create_attributes(
            existing, _attributes_insert, database_id, project_id,
            relationships=relationships
        )

    if _attributes_delete:
        _delete_attributes(
            existing, _attributes_delete, database_id, project_id
        )

    if not _indexes_insert and not _indexes_delete:
        log.dim("[SKIP] All indexes up to date", indent=4)

    if _indexes_insert:
        # wait for some of the async ops to complete
        log.dim("....waiting")
        sleep(3)

        _create_indexes(
            existing, _indexes_insert, database_id, project_id
        )

    if _indexes_delete:
        _delete_indexes(
            existing, _indexes_delete, database_id, project_id
        )

    return existing


def _sync_relationships(collection_id_map, project_id, relationships):
    for (c_id, relationship) in relationships.items():
        c = relationship["collection"]
        attrs = relationship["relations"]
        db_id = c["databaseId"]

        log.dim(f"[INFO] Syncing collection relationships [{c['name']}]")

        for rel in attrs:
            existing = None

            try:
                existing = client.get_attribute(project_id, db_id, c["$id"],
                                                rel["key"])
            except:
                pass

            if existing:
                log.dim(f"[SKIP] Relationship '{rel['key']}' exists", indent=4)
                continue

            log.success(f"[CHANGE] Creating relationship '{rel['key']}' "
                        f"[Two-way: {rel['twoWay']}, "
                        f"On Delete: {rel['onDelete']}]", indent=4)

            try:
                client.create_relationship(
                    project_id, db_id, c["$id"], rel["key"],
                    collection_id_map[rel["relatedCollection"]]["$id"],
                    rel["relationType"],
                    two_way=rel.get("twoWay"),
                    two_way_key=rel.get("twoWayKey"),
                    on_delete=rel.get("onDelete")
                )
                sleep(0.5)
            except BadRequest as e:
                if "[409]" in str(e):
                    pass
                else:
                    raise


@data_from_dir("collections")
def restore_collections(data=None, env=None, **kwargs):
    project_id = env.get("APPWRITE_PROJECT_ID")
    relationships = {}
    collection_id_map = {}

    for (c_id, c) in data.items():
        key = c["databaseId"].replace("{", "").replace("}", "")
        db_id = env.get(key)
        c["databaseId"] = db_id

        synced = _sync_collection(c, db_id, project_id,
                                  relationships=relationships,
                                  env=env)
        collection_id_map[c["$id"]] = {
            "$id": synced["$id"],
            "name": synced["name"]
        }

    if relationships:
        _sync_relationships(collection_id_map, project_id, relationships)
