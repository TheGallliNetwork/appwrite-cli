import os
from appw import client
import rich_click as click
import inquirer as iq
from appw.cli import questions
from appw.cli._org import with_default_org
from appw.cli._project import with_default_project
from appw.utils import (
    print_table, print_dict, get_default, prompt_delete
)
from appw.exceptions import NoDefaultSet


@with_default_org
@with_default_project
def select_function(org=None, project=None):
    if not project:
        exit(0)

    functions = client.list_functions(project["$id"])

    if not functions:
        click.echo(click.style("There are no functions", fg="yellow"))
        exit(0)

    d = iq.prompt(
        questions.select_from_list(functions, message="Select a function"))

    return list(filter(lambda o: o["$id"] == d["id"], functions))[0]


def with_default_function(method):
    def _wrapper(*args, **kwargs):
        try:
            function = get_default("function")
        except NoDefaultSet:
            function = select_function()

        return method(*args, function=function, **kwargs)

    return _wrapper


@click.command()
@click.option("--limit", default=None, type=int,
              help="Number of functions to load")
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
    function = client.create_function(project.get("$id"), **config)

    print_dict(function)


@click.command()
@with_default_project
def remove_function(project=None):
    project_id = project["$id"]

    prompt_delete("Function", select_function,
                  lambda f_id: client.remove_function(project_id, f_id))


@click.command()
@click.option("--limit", default=None, type=int,
              help="Number of functions to load")
@click.option("--search", default=None, type=str,
              help="Search term to filter results")
@click.option("--function-id", default=None, type=str,
              help="Function ID")
@with_default_org
@with_default_project
def list_deployments(org=None, project=None, function_id=None, limit=None,
                     search=None):
    if not function_id:
        function = select_function()
        function_id = function.get("$id")

    deployments = client.list_deployments(
        project.get("$id"), function_id, limit=limit, search=search
    )

    print_table(
        deployments,
        title="Deployments",
        keys=["$id", "buildId", "activate", "entrypoint", "size", "status"],
    )


@click.command()
@with_default_org
@with_default_project
@with_default_function
def create_deployment(org=None, project=None, function=None):
    try:
        available = [item for item in os.listdir('functions') if
                     os.path.isdir(os.path.join('functions', item))]
    except FileNotFoundError:
        click.echo(click.style(
            "Couldn't find the `functions/` directory "
            "in the current directory", fg="yellow"))

        return

    fname = function.get("name")
    function_dir = list(filter(lambda x: x == fname, available))

    if not function_dir:
        click.echo(click.style(
            f"Couldn't find the `functions/{fname}` directory. "
            "Forgot to implement the function?", fg="yellow"))

        return

    root_dir = f"functions/{fname}"
    index_files = [f for f in os.listdir(root_dir) if
                   "index" in f or "main" in f]

    if not index_files:
        first_level_dirs = [f for f in os.listdir(root_dir) if
                            not f.startswith(".") and os.path.isdir(
                                os.path.join(root_dir, f))]

        for f_dir in first_level_dirs:
            index_files.extend(
                [f"{f_dir}/{f}" for f in os.listdir(f"{root_dir}/{f_dir}") if
                 "index" in f or "main" in f])

    if not index_files:
        click.echo(click.style(
            f"Couldn't find entry point file in `functions/{fname}` directory.",
            fg="yellow"))

        return
    elif len(index_files) == 1:
        index_files = index_files[0]
    else:
        d = iq.prompt(
            questions.select_from_list(
                map(lambda x: {"$id": x, "name": x}, index_files),
                message="Select entry point file"
            )
        )
        index_files = d.get("$id")

    client.create_deployment(
        project.get('$id'), function.get('$id'), index_files,
        code_path=f"functions/{fname}"
    )
