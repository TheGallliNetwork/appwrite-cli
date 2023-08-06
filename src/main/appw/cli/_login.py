import rich_click as click
import inquirer as iq

from appw import client
from appw.cli import questions
from appw.exceptions import UnauthenticatedError


@click.command()
def login():
    config = iq.prompt(questions.login)

    try:
        client.login(**config)
        click.echo(click.style("Login successful", fg="green"))
    except UnauthenticatedError as e:
        click.echo(click.style(e, fg="red"))
