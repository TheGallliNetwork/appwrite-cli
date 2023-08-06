import rich_click as click
from appw import client
from appw.cli import questions
import inquirer as iq
from appw.cli._project import with_default_project
from appw.exceptions import BadRequest
from appw.utils import print_table, prompt_delete


@with_default_project
def select_platform(project=None):
    platforms = client.list_platforms(project["$id"])

    if not platforms:
        click.echo(click.style(f"There are no platforms under "
                               f"{project['name']}", fg="yellow"))
        exit(0)

    platform = iq.prompt(
        questions.select_from_list(platforms, message="Select a platform"))

    return list(filter(lambda o: o["$id"] == platform["id"], platforms))[0]


@click.command()
@with_default_project
def list_platforms(project=None):
    """View all the registered mobile/web apps"""
    keys = client.list_platforms(project["$id"])

    print_table(
        keys,
        title=f"Registered Apps under {project['name']}",
        keys=["$id", "type", "name", "key", "hostname"]
    )


@click.command()
@with_default_project
def create_platform(project=None):
    """Register your mobile/web app"""
    config = iq.prompt(questions.create_platform)

    try:
        client.create_platform(project["$id"], **config)
        click.echo(
            click.style(f"'{config['name']}' platform added", fg="green"))
    except BadRequest as e:
        click.echo(click.style(e, fg="red"))


@click.command()
@with_default_project
def remove_platform(project=None):
    """Remove app platform"""
    project_id = project["$id"]

    prompt_delete("App Platform", select_platform,
                  lambda p_id: client.remove_platform(project_id, p_id))
