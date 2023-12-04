import rich_click as click
from rich import inspect
from rich.progress import Progress

from appw import client
from appw.cli import log

from appw.cli._org import with_default_org
from appw.cli._project import with_default_project
from appw.cli.snapshots.utils.restore.collections import restore_collections
from appw.cli.snapshots.utils.restore.databases import restore_databases
from appw.cli.snapshots.utils.restore.functions import restore_functions
from appw.cli.snapshots.utils.restore.keys import restore_api_keys
from appw.cli.snapshots.utils.restore.org import restore_org
from appw.cli.snapshots.utils.restore.project import restore_project
from appw.cli.snapshots.utils.restore.providers import restore_auth_providers

from appw.cli.snapshots.utils.write import write_snapshots


@click.command()
@click.option("--dry-run", is_flag=True, default=False,
              help="Prints the snapshot to console without backing up to file")
@with_default_org
@with_default_project
def create_snapshot(dry_run, org=None, project=None):
    """
    Creates a snapshot of the project and everything under it.
    """
    with Progress() as progress:
        task = progress.add_task(f"Creating snapshot of {org['name']}",
                                 total=7)
        progress.console.print(
            f"Reading {org['name']} [org] & {project['name']} [project]"
        )
        snapshot = {
            "org": org,
            "project": project
        }
        progress.advance(task)

        # API Keys
        progress.console.print("Reading API Keys")
        snapshot["keys"] = client.list_api_keys(project["$id"])
        progress.advance(task)

        # platforms
        progress.console.print("Reading Web/Mobile app Platforms")
        snapshot["platforms"] = client.list_platforms(project["$id"])
        progress.advance(task)

        # providers
        progress.console.print("Reading Oauth Providers")
        snapshot["providers"] = list(filter(lambda x: x["enabled"],
                                            project.get("providers", [])))
        progress.advance(task)

        # databases
        progress.console.print("Reading Databases")
        databases = client.list_databases(project["$id"])
        dbs = {}

        for db in databases:
            progress.console.print(f"    Reading: {db['name']}")
            dbs[db["$id"]] = {
                "db": db,
                "collections": client.list_collections(project["$id"],
                                                       db["$id"])
            }

        snapshot["databases"] = dbs
        progress.advance(task)

        # functions
        progress.console.print("Reading Functions")
        functions = client.list_functions(project["$id"])
        snapshot["functions"] = functions

        progress.advance(task)

        # storage/buckets
        progress.console.print("Reading Storage Buckets")
        buckets = client.list_buckets(project["$id"])
        snapshot["buckets"] = buckets

        progress.advance(task)

        progress.stop()

        if dry_run:
            inspect(snapshot)
            return

        write_snapshots(snapshot)


def get_ip_address():
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    return ip


@click.command()
def restore_snapshot():
    """
    Restores an existing snapshot and syncs everything - names, schema and more
    """
    env = {
        "APPWRITE_FUNCTION_API_ENDPOINT": f"http://{get_ip_address()}/v1"
    }

    restore_org(env=env)
    restore_project(env=env)
    restore_api_keys(env=env)
    restore_auth_providers(env=env)

    restore_databases(env=env)
    restore_collections(env=env)

    restore_functions(env=env)

    print()
    log.dim("=" * 80)
    print()

    for (key, val) in env.items():
        print(f"{key}={val}")

    print()
    log.dim("=" * 80)
    log.success("Copy and paste the above environment variables "
                "into your .env.dev")
    print()


# @click.command()
# def migrate_snapshot():
#     pass
