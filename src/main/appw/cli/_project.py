import rich_click as click
from appw import client
import inquirer as iq
from appw.cli import questions
from appw.utils import (
    print_table, set_default, get_default, remove_default, prompt_delete
)
from appw.cli._org import with_default_org
from appw.exceptions import NoDefaultSet, BadRequest


@with_default_org
def select_project(org=None):
    projects = client.list_projects(org["$id"])

    if not projects:
        click.echo(click.style(f"There are no projects under {org['name']}",
                               fg="yellow"))
        exit(0)

    project = iq.prompt(
        questions.select_from_list(projects, message="Select a project"))

    return list(filter(lambda o: o["$id"] == project["id"], projects))[0]


def with_default_project(method):
    def _wrapper(*args, **kwargs):
        try:
            project = get_default("project")

            if not project:
                raise NoDefaultSet()
        except NoDefaultSet:
            project = select_project()
            set_default("project", project)

        return method(*args, project=project, **kwargs)

    return _wrapper


@click.command()
@with_default_org
def list_projects(org=None):
    print_table(
        client.list_projects(org["$id"]),
        title="Projects under {} organization".format(org["name"]),
        keys=["$id", "name", "keys", "platforms", "providers"],
        resolvers={
            "providers":
                lambda value: ", ".join(
                    list(
                        map(lambda p: p["name"],
                            filter(lambda x: x["enabled"], value)))),
            "platforms":
                lambda value: ", ".join(list(map(lambda x: x["type"], value)))
        })


@click.command()
@with_default_org
def create_project(org=None):
    config = iq.prompt(questions.create_project)

    try:
        client.create_project(org["$id"], **config)
        click.echo(click.style(
            "Project '{}' created".format(config["name"]),
            fg="green"))
        print_table(
            client.list_projects(org["$id"]),
            title="Projects under {}".format(org["name"]),
            keys=["$id", "name"]
        )
    except BadRequest as e:
        click.echo(click.style(e, fg="red"))


@click.command()
def remove_project():
    config = iq.prompt(questions.remove_project)
    prompt_delete("Project", select_project,
                  lambda p_id: client.remove_project(p_id, config["password"]),
                  on_remove_callback=lambda x: remove_default("project"))


@click.command()
def switch_project():
    project = select_project()

    set_default("project", project)
    remove_default("database")
    click.echo(
        click.style(f"'{project['name']}' set as default project. ", dim=True)
    )
