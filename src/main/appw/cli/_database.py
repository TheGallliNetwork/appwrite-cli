import functools

from rich import inspect

from appw import client
import rich_click as click
import inquirer as iq
from appw.cli import questions
from appw.cli._org import with_default_org
from appw.cli._project import with_default_project
from appw.utils import (
    print_table, get_default, set_default, remove_default, prompt_delete
)
from appw.exceptions import BadRequest, NoDefaultSet


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
@click.option("--debug", "-d", default=False, type=bool, is_flag=True,
              help="Print debug information")
@with_default_project
@with_default_database
def get_collection(project=None, database=None, name=None, debug=False):
    _collection = select_collection(name=name)

    if not _collection:
        return

    collection = client.get_collection(project["$id"], database["$id"],
                                       _collection["$id"])

    print_table([collection])

    if debug:
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


@click.command()
@click.option("--db-id", default=None, type=str,
              help="Optional Database ID")
@click.option("--collection-id", default=None, type=str,
              help="Optional Collection ID")
@click.option("--limit", default=None, type=int,
              help="Number of databases to load")
@click.option("--offset", default=None, type=int,
              help="The offset from which to load the databases")
@click.option("--columns", default=None, type=str, multiple=True,
              help="Columns to show")
@click.option("--search", default=None, nargs=2, type=str,
              help="Search full text indexed attributes")
@with_default_project
@with_default_database
def list_documents(project=None, database=None, limit=None, offset=None,
                   db_id=None, collection_id=None, columns=None, search=None):
    project_id = project["$id"]
    if db_id:
        database = client.get_database(project_id, db_id)

    if not collection_id:
        collection = select_collection()
    else:
        collection = client.get_collection(project_id,
                                           db_id or database["$id"],
                                           collection_id)

    documents = client.list_documents(project["$id"],
                                      db_id or database["$id"],
                                      collection["$id"],
                                      limit=limit,
                                      offset=offset,
                                      search=search
                                      )
    if documents is not None:
        print_table(
            documents,
            title=f"Documents under {database['name']} - {collection['name']}",
            keys=columns
            # keys=["$id", "name"]
        )


@click.command()
@click.option("--collection-id", default=None, type=str,
              help="Optional Collection ID")
@click.option("--db-id", default=None, type=str,
              help="Optional Database ID")
@click.option("--collection-id", default=None, type=str,
              help="Optional Collection ID")
@click.option("--doc-id", default=None, type=str,
              help="Optional Document ID")
@click.option("--search", default=None, nargs=2, type=str,
              help="Search full text indexed attributes")
@click.option("--truncate", default=False, is_flag=True,
              help="Delete all documents from the collection")
@with_default_project
@with_default_database
def remove_documents(project=None, database=None,
                     db_id=None, collection_id=None, doc_id=None,
                     search=None, truncate=False):
    project_id = project["$id"]
    if db_id:
        database = client.get_database(project_id, db_id)
    if not collection_id:
        collection = select_collection()
    else:
        try:
            collection = client.get_collection(project_id, db_id or database["$id"], collection_id)
        except BadRequest as e:
            click.secho(f"{e} '{collection_id}'", fg="red")
            return

    if not doc_id:
        documents = client.list_documents(project["$id"],
                                          db_id or database["$id"],
                                          collection["$id"],
                                          search=search
                                          )
    else:
        try:
            document = client.get_document(project_id, db_id or database["$id"], collection["$id"], doc_id)
        except BadRequest as e:
            click.secho(f"{e} '{doc_id}'", fg="red")
            return
        documents = [document]
    if documents:
        if not truncate:
            selected_documents = iq.prompt(
                questions.select_multiple_from_list(documents,
                                                    message="Select a document")
            )
            selected_documents = [d for d in documents if d["$id"] in selected_documents["id"]]
            _p = functools.partial(client.remove_document,
                                   project_id=project_id,
                                   database_id=db_id or database["$id"],
                                   collection_id=collection["$id"])
            for doc in selected_documents:
                prompt_delete("Document", lambda: doc,
                              lambda doc_id: _p(document_id=doc_id))
        else:
            confirm = iq.prompt(
                [
                    iq.Confirm(
                        "confirm",
                        default=False,
                        message=f"Are you sure you want to remove all "
                                f" documents [{len(documents)}] from "
                                f"{collection['$id']}"
                    )
                ]
            )
            if confirm["confirm"]:
                for doc in documents:
                    if "name" in doc:
                        r_id = f"{doc['name']}"
                    else:
                        r_id = ""
                    if "$id" in doc:
                        r_id += f": {doc['$id']}"
                    click.secho(f"[Yes] Deleting {r_id}")
                    client.remove_document(
                        project_id=project_id,
                        database_id=db_id or database["$id"],
                        collection_id=collection["$id"],
                        document_id=doc["$id"]
                    )
            else:
                click.secho("[No] Discarded operation", dim=True)
    else:
        click.secho("Unable to find documents with given 'id' or "
                    "'search criteria'", fg="yellow")


