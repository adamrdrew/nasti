import click
import sys

from nasti.nastifile import NastiFile
from nasti.nasti import Nasti

@click.group()
def cli():
    """
    Welcome to NASTI!

    NASTI is free and open source software. Feel free to get weird with it!
    """
    pass

@click.command()
@click.argument("source", required=True)
@click.option("--git", "-g", help="Create a git repo in the new project. Default is True.", is_flag=True)
def process(source, git):
    try:
        nasti = Nasti(source, click.echo, git)
        nasti.run()
    except Exception as e:
        print(e)
        sys.exit(1)


@click.command()
@click.argument("path", required=False)
def validate(path):
    if not path:
        path = "."
    try:
        nasti_file = NastiFile(path)
        nasti_file.validate()
        click.echo("Nastifile is valid.")
    except Exception as e:
        print(e)
        sys.exit(1)

cli.add_command(process)
cli.add_command(validate)