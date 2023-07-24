import click
import sys
import os

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
        nasti = Nasti({
            "source": source, 
            "print_func": click.echo, 
            "git_init": git, 
            "help_text": cli.get_help(click.Context(cli)),
            "os_dep": os,
            "open_dep": open,
            "input_dep": input
        })
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
        nasti_file = NastiFile({
            "path": path,
            "os_dep": os,
            "open_dep": open,
        })
        nasti_file.validate()
        click.echo("Nastifile is valid.")
    except Exception as e:
        print(e)
        sys.exit(1)

@click.command()
@click.argument("path", required=False)
def find(path):
    if not path:
        path = "."
    try:
        nasti_file = NastiFile({
            "path": path,
            "os_dep": os,
            "open_dep": open,
        })
        unmentioned_files = nasti_file.find_unmentioned_files()
        click.echo(unmentioned_files.get_report())
    except Exception as e:
        print(e)
        sys.exit(1)

cli.add_command(process)
cli.add_command(validate)
cli.add_command(find)