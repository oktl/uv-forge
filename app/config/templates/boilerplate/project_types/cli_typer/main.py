"""{{project_name}} — CLI application entry point."""

import typer

app = typer.Typer()


@app.command()
def hello():
    """Say hello."""
    typer.echo("Hello from {{project_name}}!")


if __name__ == "__main__":
    app()
