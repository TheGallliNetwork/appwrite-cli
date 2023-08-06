import rich_click as click
from appw import client
from appw.cli import questions
import inquirer as iq
from appw.cli._project import with_default_project
from appw.exceptions import BadRequest
from appw.utils import print_table, prompt_delete


@with_default_project
def select_keys(project=None):
    keys = client.list_api_keys(project["$id"])

    if not keys:
        click.echo(click.style(
            f"There are no keys under the project '{project['name']}'",
            fg="yellow"))
        exit(0)

    key = iq.prompt(questions.select_from_list(
        keys, message="Select API Key"
    ))

    return list(filter(lambda k: k["$id"] == key["id"], keys))[0]


@click.command()
@with_default_project
def list_keys(project=None):
    keys = client.list_api_keys(project["$id"])

    print_table(
        keys,
        title=f"API Keys under {project['name']}",
        keys=["name", "scopes", "accessedAt", "expire", "secret"],
        resolvers={
            "scopes": lambda x: ", ".join(x)
        })


@click.command()
@with_default_project
def create_key(project=None):
    config = iq.prompt(questions.create_keys)

    scopes = []
    scopes.extend(config["auth"])
    scopes.extend(config["database"])
    scopes.extend(config["function"])
    scopes.extend(config["storage"])

    try:
        key = client.create_api_key(project["$id"], config["name"], scopes)
        click.echo(click.style(config["name"], fg="green"))
        click.echo(key["secret"])
    except BadRequest as e:
        click.echo(click.style(e, fg="red"))


@click.command()
@with_default_project
def remove_key(project=None):
    project_id = project["$id"]

    prompt_delete("API Key", select_keys,
                  lambda k_id: client.remove_api_key(project_id, k_id))
