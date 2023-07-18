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


@click.command()
@click.option("--limit", default=None, type=int,
              help="Number of databases to load")
@click.option("--search", default=None, type=str,
              help="Search term to filter results")
@with_default_org
@with_default_project
def list_functions(org=None, project=None, limit=None, search=None):
    functions = client.list_functions(project["$id"], limit=limit,
                                      search=search)

    print_table(
        functions,
        title="Functions under {}/{}".format(org["name"], project["name"]),
        keys=["$id", "name", "enabled", "runtime", "timeout", "vars"],
        resolvers={
            "vars": lambda x: ", ".join(list(map(lambda y: y["key"], x)))
        }
    )


@click.command()
@with_default_org
@with_default_project
def create_function(org=None, project=None):
    config = iq.prompt(questions.create_function)

    try:
        client.create_function(project["$id"], **config)
        click.echo(click.style(
            "Function '{}' created".format(config["name"]),
            fg="green"))
        list_functions()
    except BadRequest as e:
        click.echo(click.style(e, fg="red"))
