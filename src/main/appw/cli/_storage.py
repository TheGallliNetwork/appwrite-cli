from appw import client
import rich_click as click
from appw.cli._org import with_default_org
from appw.cli._project import with_default_project
from appw.utils import (
    print_table
)


@click.command()
@click.option("--limit", default=None, type=int,
              help="Number of storage buckets to load")
@click.option("--offset", default=None, type=int,
              help="The offset from which to load the storage buckets")
@with_default_org
@with_default_project
def list_buckets(org=None, project=None, limit=None, offset=None):
    databases = client.list_buckets(project["$id"], limit=limit,
                                      offset=offset)

    print_table(
        databases,
        title="Buckets under {}/{}".format(org["name"], project["name"])
    )
