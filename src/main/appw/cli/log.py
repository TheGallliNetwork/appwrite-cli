import rich_click as click


def info(msg: str, indent=0):
    click.echo(click.style(f"{(' '*indent).rjust(indent)}{msg}"))


def success(msg: str, indent=0):
    click.echo(click.style(f"{(' '*indent).rjust(indent)}{msg}", fg="green"))


def error(msg: str, indent=0):
    click.echo(click.style(f"{(' '*indent).rjust(indent)}{msg}", fg="red"))


def warn(msg: str, indent=0):
    click.echo(click.style(f"{(' '*indent).rjust(indent)}{msg}", fg="yellow"))


def dim(msg: str, indent=0):
    click.echo(click.style(f"{(' '*indent).rjust(indent)}{msg}", dim=True))
