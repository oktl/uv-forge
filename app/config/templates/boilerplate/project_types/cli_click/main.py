"""{{project_name}} — CLI application entry point."""

import click


@click.group()
def cli():
    """{{project_name}} command-line interface."""


@cli.command()
def hello():
    """Say hello."""
    click.echo("Hello from {{project_name}}!")


if __name__ == "__main__":
    cli()
