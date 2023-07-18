import json
import os
from datetime import datetime

import rich_click as click
from rich import inspect
from rich.progress import Progress, SpinnerColumn, TextColumn

import client

from cli._org import with_default_org
from cli._project import with_default_project

from cli.snapshots.utils.write import write_snapshots


@click.command()
@click.option("--dry-run", is_flag=True, default=False,
              help="Prints the snapshot to console without backing up to file")
@with_default_org
@with_default_project
def create_snapshot(dry_run, org=None, project=None):
    """Creates a snapshot of the project and everything under it.
    [yellow]NOTE: This doesn't backup the data from the database, just the
    schema
    """
    with Progress() as progress:
        task = progress.add_task(f"Creating snapshot of {org['name']}",
                                 total=5)
        progress.console.print(
            f"Reading {org['name']} \[org] & {project['name']} \[project]"
        )
        snapshot = {
            "org": org,
            "project": project
        }
        progress.advance(task)

        progress.console.print("Reading API Keys")
        snapshot["keys"] = client.list_api_keys(project["$id"])
        progress.advance(task)

        progress.console.print("Reading Web/Mobile app Platforms")
        snapshot["platforms"] = client.list_platforms(project["$id"])
        progress.advance(task)

        progress.console.print("Reading Oauth Providers")
        snapshot["providers"] = list(filter(lambda x: x["enabled"],
                                            project.get("providers", [])))
        progress.advance(task)

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
        progress.stop()

        if dry_run:
            inspect(snapshot)
            return

        write_snapshots(snapshot)




@click.command()
def restore_snapshot():
    pass


@click.command()
def migrate_snapshot():
    pass
