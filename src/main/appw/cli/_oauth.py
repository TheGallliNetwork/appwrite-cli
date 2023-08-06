import rich_click as click
from appw import client
from appw.cli import questions
import inquirer as iq

from appw.cli._org import with_default_org
from appw.cli._project import with_default_project
from appw.exceptions import BadRequest


@with_default_project
def select_provider(project=None):
    providers = filter(lambda x: x["enabled"], project.get("providers", []))

    if not providers:
        click.echo(click.style(
            f"There are no oauth providers configured for the "
            f"project '{project['name']}'",
            fg="yellow"))
        exit(0)

    provider = iq.prompt(questions.select_from_list(
        providers, message="Select Oauth Provider", id_attr="name"
    ))

    return list(filter(lambda k: k["name"] == provider["name"], providers))[0]


@click.command()
@with_default_org
@with_default_project
def create_oauth(org=None, project=None):
    config = iq.prompt(questions.create_provider)
    config["enabled"] = True

    try:
        client.create_or_update_oauth(project["$id"], **config)
        click.echo(click.style(f"{config['name']} configured successfully",
                               fg="green"))
    except BadRequest as e:
        click.echo(click.style(e, fg="red"))
