import os
import pickle

import click
from rich.style import Style

import inquirer as iq

from appw.cli import questions
from appw.exceptions import (
    BadRequest, NoDefaultSet
)

from rich.console import Console
from rich.table import Table

APPWRITE_HEADERS = {
    "x-appwrite-project": "console",
    "x-appwrite-response-format": "1.0.0",
    "sec-ch-ua":
        '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    "sec-ch-ua-platform": "macOS",
    "x-sdk-name": "Console",
}


def make_request(method, endpoint, body=None, project=None, files=None):
    try:
        with open(".session", "rb") as f:
            cookies = pickle.load(f)
    except:
        click.echo(
            click.style("Login to create a session by running", dim=True))
        click.echo(
            click.style("appw login", fg="green"))
        exit(0)

    headers = dict(**APPWRITE_HEADERS)

    if files:
        headers["Content-Transfer-Encoding"] = "application/gzip"

    if project:
        headers["x-appwrite-project"] = project
        headers["x-appwrite-mode"] = "admin"

    response = method(endpoint,
                      json=body if files is None else None,
                      data=body if files is not None else None,
                      files=files,
                      headers=headers,
                      cookies=cookies)

    if response.status_code == 401:
        click.echo(
            click.style("Login to create a session by running", dim=True))
        click.echo(
            click.style("appw login", fg="green"))
        exit(0)
        # raise UnauthenticatedError("[{}] {}".format(
        #     response.status_code,
        #     response.json().get("message")))
    elif response.status_code == 204:
        return {}
    elif response.status_code >= 400:
        raise BadRequest("[{}] {}".format(response.status_code,
                                          response.json().get("message")))
    else:
        return response.json()


def _value_of(key, value, resolver):
    _value = value

    if key in resolver:
        _value = resolver[key](value)

    return str(len(_value)) if isinstance(_value, list) else str(_value)


def print_table(data, title=None, keys=None, resolvers=None):
    console = Console()
    resolvers = resolvers or {}

    if not data:
        console.print(title, style=Style(color="blue", underline=True, bold=True))
        console.print("No data available", style="yellow")
        return

    item: dict = data[0]
    keys = keys or sorted(
        filter(
            lambda x: x != "$createdAt" and x != "$updatedAt" and not (
                isinstance(item[x], dict) or isinstance(item[x], list)),
            item.keys()))
    table = Table(title=title, title_justify="left",
                  title_style=Style(color="blue", underline=True, bold=True),
                  header_style="green")

    for key in keys:
        table.add_column(key, no_wrap=False)

    for d in data:
        row = (_value_of(key, d.get(key), resolvers) for key in keys)
        table.add_row(*row)

    console.print(table)


def prompt_delete(resource_name, select_from_list_method, remove_method,
                  on_remove_callback=None):
    resource = select_from_list_method()
    if "name" in resource:
        r_id = f"{resource['name']}"
    else:
        r_id = ""
    if "$id" in resource:
        r_id += f": {resource['$id']}"
    confirm_delete = iq.prompt(
        questions.confirm_delete(
            resource_name,
            resource["$id"],
            message=click.style(f"Remove {resource_name}: {r_id}",
                                fg="red")))
    if not confirm_delete["confirm"]:
        click.echo(click.style("[No] Discarded operation", dim=True))
    else:
        click.echo(click.style(f"[Yes] Deleting {resource_name}", fg="yellow"))

        try:
            remove_method(resource["$id"])

            if on_remove_callback:
                on_remove_callback(resource)

            click.echo(click.style(
                f"{resource_name} '{resource['name']}' deleted successfully",
                fg="green"))
        except BadRequest as e:
            click.echo(click.style(e, fg="red"))


def print_dict(item, title=None, keys=None):
    console = Console()

    if not item:
        console.print("No data available", style="yellow")

    keys = keys or sorted(
        filter(
            lambda x: x != "$createdAt" and x != "$updatedAt" and not (
                isinstance(item[x], dict) or isinstance(item[x], list)),
            item.keys()))

    if title:
        console.print(title,
                      style=Style(color="blue", underline=True, bold=True))

    table = Table(box=None, show_header=False)
    for i in range(2):
        justify = "left"
        style = None

        if i == 0:
            justify = "right"
            style = Style(bold=True, color="green")

        table.add_column(keys[i], justify=justify, style=style)

    for key in keys:
        table.add_row(str(key), str(item.get(key)))

    console.print(table)


def get_default(resource: str):
    try:
        with open(".{}".format(resource), "rb") as f:
            org = pickle.load(f)
        return org
    except:
        raise NoDefaultSet()


def set_default(resource: str, item):
    with open(".{}".format(resource), "wb") as f:
        pickle.dump(item, f)


def remove_default(resource: str):
    try:
        os.remove(".{}".format(resource))
    except OSError:
        pass
