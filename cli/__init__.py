from ._login import login
from ._org import (
    with_default_org, list_orgs, create_org, switch_org, remove_org
)
from ._project import (
    with_default_project, list_projects, create_project, remove_project,
    switch_project
)
from ._database import (
    with_default_database, list_databases, create_database, remove_database,
    list_collections, get_collection, switch_database
)
from ._functions import(
    list_functions, create_function, remove_function,
    list_deployments, create_deployment
)
from ._keys import list_keys, create_key, remove_key
from ._platform import list_platforms, create_platform, remove_platform
from ._snapshot import create_snapshot, restore_snapshot, migrate_snapshot
from ._info import show_info, show_account
from ._oauth import create_oauth
from cli import questions
