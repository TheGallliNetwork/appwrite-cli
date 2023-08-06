import rich_click as click
from appw import client
from appw.exceptions import UnauthenticatedError
from appw.cli._database import with_default_database, list_databases
from appw.cli._org import with_default_org
from appw.cli._project import with_default_project
from appw.cli._database import list_collections
from appw.cli._keys import list_keys
from appw.cli._platform import list_platforms
from appw.utils import print_dict


@click.command()
def show_account():
    try:
        account = client.get_account()
        print_dict(account, title="Current User")
    except UnauthenticatedError as e:
        click.echo(click.style(e, fg="red"))


@click.command()
@with_default_org
@with_default_project
@with_default_database
def show_context(org=None, project=None, database=None):
    context = {
        "organization": f'{org["name"]} [{org["$id"]}]' if org else "Not Set",
        "project": f'{project["name"]} [{project["$id"]}]' if project else "Not Set",
        "database": f'{database["name"]} [{database["$id"]}]' if database else "Not Set",
    }

    print_dict(context, title="Appwrite Context",
               keys=["organization", "project", "database"])


@click.command()
@with_default_org
@with_default_project
@with_default_database
@click.pass_context
def show_info(ctx, org=None, project=None, database=None):
    ctx.invoke(show_account)
    click.echo("\n")
    ctx.invoke(show_context)
    click.echo("\n")
    ctx.invoke(list_keys)
    click.echo("\n")
    ctx.invoke(list_platforms)
    click.echo("\n")
    ctx.invoke(list_databases)
    click.echo("\n")

    databases = client.list_databases(project["$id"])

    for db in databases:
        ctx.invoke(list_collections, db_id=db["$id"])
        click.echo("\n")
