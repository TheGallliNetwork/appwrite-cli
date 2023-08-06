import rich_click as click
from appw import client
import inquirer as iq
from appw.cli import questions
from appw.utils import print_table, get_default, set_default, remove_default
from appw.exceptions import NoDefaultSet, BadRequest


def with_default_org(method):
    def _wrapper(*args, **kwargs):
        try:
            org = get_default('org')

            if not org:
                raise NoDefaultSet()
        except NoDefaultSet:
            org = select_organization()
            set_default("org", org)

        return method(*args, org=org, **kwargs)

    return _wrapper


def select_organization():
    organizations = client.list_organizations()

    if not organizations:
        click.echo(click.style("There are no organization", fg="yellow"))
        exit(0)

    org = iq.prompt(questions.select_from_list(
        organizations, message="Select Organization"
    ))

    return list(filter(lambda o: o["$id"] == org["id"], organizations))[0]


@click.command()
def list_orgs():
    organizations = client.list_organizations()
    print_table(organizations)


@click.command()
def create_org():
    config = iq.prompt(questions.create_organization)

    try:
        org = client.create_organization(
            config["name"], team_id=config.get("team_id")
        )
        click.echo(
            click.style(f"'{org['name']}' created successfully", fg="green"))

        set_default("org", org)
        remove_default("project")
        remove_default("database")

        click.echo(
            click.style(f"'{org['name']}' set as default org. "
                        f"To change the default run ./appwrite switch org",
                        dim=True)
        )
    except BadRequest as e:
        click.echo(click.style(e, fg="red"))


@click.command()
def remove_org():
    org = select_organization()

    confirm_delete = iq.prompt(
        questions.confirm_delete(
            "Organization",
            org["$id"],
            message=click.style(
                "This will remove all the projects and their data."
                " \nThis cannot be reversed. Continue?",
                fg="red")))

    if not confirm_delete["confirm"]:
        click.echo(click.style("[No] Discarded operation", dim=True))
    else:
        click.echo(
            click.style(f"[Yes] Deleting organization "
                        f"{org['name']} [{org['$id']}]"))
        try:
            client.remove_organization(org["$id"])
            remove_default("org")
            remove_default("project")
            remove_default("database")
            click.echo(
                click.style(
                    f"{org['name']} [{org['$id']}] deleted successfully",
                    fg="green"))
        except BadRequest as e:
            click.echo(click.style(e, fg="red"))


@click.command()
def switch_org():
    org = select_organization()

    set_default("org", org)
    remove_default("project")
    remove_default("database")
    click.echo(
        click.style(f"'{org['name']}' set as default org. ", dim=True)
    )
