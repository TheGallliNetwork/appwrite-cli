from rich import inspect

import client
import rich_click as click
import inquirer as iq
from cli import questions
from cli._org import with_default_org
from cli._project import with_default_project
from utils import (
    print_table, get_default, set_default, remove_default, prompt_delete
)
from exceptions import BadRequest, NoDefaultSet


@with_default_org
@with_default_project
def select_database(org=None, project=None):
    if not project:
        exit(0)

    databases = client.list_databases(project["$id"])

    if not databases:
        click.echo(click.style("There are no databases", fg="yellow"))
        exit(0)

    db = iq.prompt(
        questions.select_from_list(databases, message="Select a database"))

    return list(filter(lambda o: o["$id"] == db["id"], databases))[0]


def with_default_database(method):
    def _wrapper(*args, **kwargs):
        try:
            database = get_default("database")
        except NoDefaultSet:
            database = select_database()
            set_default("database", database)

        return method(*args, database=database, **kwargs)

    return _wrapper


@with_default_org
@with_default_project
@with_default_database
def select_collection(org=None, project=None, database=None, name=None):
    collections = client.list_collections(project["$id"], database["$id"])

    if name:
        filtered = list(filter(lambda x: x["name"] == name, collections))

        if not filtered:
            click.echo(
                click.style(f"Unable to find collection by name '{name}'",
                            fg="yellow"))
            return
        else:
            return filtered[0]

    if not collections:
        click.echo(click.style("There are no collections", fg="yellow"))
        return

    collection = iq.prompt(
        questions.select_from_list(collections, message="Select a collection"))

    return list(filter(lambda o: o["$id"] == collection["id"], collections))[0]


@click.command()
@click.option("--limit", default=None, type=int,
              help="Number of databases to load")
@click.option("--offset", default=None, type=int,
              help="The offset from which to load the databases")
@with_default_org
@with_default_project
def list_databases(org=None, project=None, limit=None, offset=None):
    databases = client.list_databases(project["$id"], limit=limit,
                                      offset=offset)

    print_table(
        databases,
        title="Databases under {}/{}".format(org["name"], project["name"])
    )


@click.command()
@with_default_org
@with_default_project
def create_database(org=None, project=None):
    config = iq.prompt(questions.create_database)

    try:
        client.create_database(project["$id"], **config)
        click.echo(click.style(
            "Database '{}' created".format(config["name"]),
            fg="green"))
        print_table(
            client.list_databases(project["$id"]),
            title="Databases under {}/{}".format(org["name"], project["name"])
        )
    except BadRequest as e:
        click.echo(click.style(e, fg="red"))


@click.command()
@with_default_project
def remove_database(project=None):
    project_id = project["$id"]

    prompt_delete("Database", select_database,
                  lambda db_id: client.remove_database(project_id, db_id),
                  lambda x: remove_default("database"))


@click.command()
def switch_database():
    database = select_database()

    set_default("database", database)
    click.echo(
        click.style(f"'{database['name']}' set as default database. ",
                    dim=True)
    )


@click.command()
@click.option("--db-id", default=None, type=str,
              help="Optional Database ID")
@click.option("--limit", default=None, type=int,
              help="Number of databases to load")
@click.option("--offset", default=None, type=int,
              help="The offset from which to load the databases")
@with_default_project
@with_default_database
def list_collections(project=None, database=None, limit=None, offset=None,
                     db_id=None):
    if db_id:
        database = client.get_database(project["$id"], db_id)

    collections = client.list_collections(project["$id"],
                                          db_id or database["$id"],
                                          limit=limit, offset=offset)
    print_table(
        collections,
        title=f"Collections under {database['name']}",
        keys=["$id", "documentSecurity", "enabled", "name"]
    )


@click.command()
@click.option("--name", "-n", help="Name of the collection")
@with_default_project
@with_default_database
def get_collection(project=None, database=None, name=None):
    _collection = select_collection(name=name)

    if not _collection:
        return

    collection = client.get_collection(project["$id"], database["$id"],
                                       _collection["$id"])

    print_table([collection])
    inspect(collection)

    click.echo(click.style("\nAttributes", underline=True, fg="blue"))
    print_table(
        collection["attributes"],
        keys=["key", "type", "size", "default", "array"]
    )

    click.echo(click.style("\nIndexes", underline=True, fg="blue"))
    print_table(
        collection["indexes"],
        keys=["key", "type", "attributes", "orders"],
        resolvers={
            "attributes": lambda x: ", ".join(x),
            "orders": lambda x: ", ".join(x)
        }
    )

    click.echo(click.style("\nPermissions", underline=True, fg="blue"))
    click.echo(", ".join(collection.get("$permissions", [])))

    print("\n")
