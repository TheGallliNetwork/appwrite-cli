import click

from appw import client
from appw.cli import with_default_org, with_default_project
from appw.utils import set_default

Data = dict | list[dict | str]
Key = str


class Snapshot:
    def backup(self, **kwargs) -> Data:
        """Return the data to backup in the snapshot"""

    def restore(self, value: Data, **kwargs) -> None:
        """Restore the data by overriding the existing content"""

    def cleanup(self, value: Data) -> None:
        """Clean up the previous operation"""

    def migrate(self, value: Data, **kwargs) -> None:
        """Migrate the data"""


class OrgSnapshot(Snapshot):
    @with_default_org
    def backup(self, org=None, **kwargs) -> Data:
        return org

    def restore(self, value: Data, **kwargs):
        org = client.create_organization(value["name"], value.get("$id"))
        set_default("org", org)

        return org

    def cleanup(self, value: Data) -> None:
        if value and value.get("$id"):
            client.remove_organization(value.get("$id"))


class ProjectSnapshot(Snapshot):
    def __init__(self):
        self.created_project = None

    @with_default_project
    def backup(self, project=None, **kwargs) -> Data:
        return project

    @with_default_org
    def restore(self, value: Data, org=None, **kwargs):
        if value.get("$id"):
            try:
                project = client.get_project(value.get("$id"))

                if project.get("name") == value.get("name"):
                    click.echo(click.style(f"Project '{project['name']}'"
                                           f" already exists", dim=True))
                    return

                project = client.update_project_name(value.get("$id"),
                                                     value.get("name"))
                return set_default("project", project)
            except:
                pass

        project = client.create_project(org["$id"], value["name"],
                                        project_id=value.get("$id"))
        self.created_project = project

        set_default("project", project)

        return project

    def cleanup(self, value: Data) -> None:
        if value and value.get("$id"):
            client.remove_organization(value.get("$id"))


class ApiKeysSnapshot(Snapshot):
    @with_default_project
    def backup(self, project=None, **kwargs) -> Data:
        return client.list_api_keys(project["$id"])

    @with_default_project
    def restore(self, value: Data, project=None, **kwargs):
        existing = client.list_api_keys(project["$id"])

        if existing:
            for key in existing:
                client.remove_api_key(project["$id"], key["$id"])

        for key in value:
            client.create_api_key(project["$id"], key["name"], key["scopes"],
                                  expire=key.get("expire"))


class PlatformsSnapshot(Snapshot):
    @with_default_project
    def backup(self, project=None, **kwargs) -> Data:
        return client.list_platforms(project["$id"])

    @with_default_project
    def restore(self, value: Data, project=None, **kwargs):
        existing = client.list_platforms(project["$id"])

        if existing:
            for p in existing:
                client.remove_platform(project["$id"], p["$id"])

        for p in value:
            client.create_platform(project["$id"], name=p["name"],
                                   type=p["type"],
                                   key=p.get("hostname") or p.get("key"))


class StorageSnapshot(Snapshot):
    pass
