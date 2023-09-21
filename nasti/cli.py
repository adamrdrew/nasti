import click
import sys
import os

from nasti.nastifile import NastiFile
from nasti.nasti import Nasti
import rich
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

@click.group()
def cli():
    """
    Welcome to NASTI!

    NASTI is free and open source software. Feel free to get weird with it!
    """
    pass

@click.command()
@click.argument("source", required=True)
@click.argument("dest_dir", required=False)
@click.option("--git", "-g", help="Create a git repo in the new project. Default is True.", is_flag=True, default=True )
@click.option("--defaults", "-d", help="Accept all defaults. Default is False", is_flag=True, default=False )
def process(source, git):
    try:
        history = InMemoryHistory()
        session = PromptSession(history=history)
        nasti = Nasti({
            "source": source, 
            "print_dep": rich.print, 
            "git_init": git, 
            "help_text": cli.get_help(click.Context(cli)),
            "os_dep": os,
            "open_dep": open,
            "input_dep": session.prompt
        })
        nasti.run()
    except Exception as e:
        print(f"    Error: {e}")
    except KeyboardInterrupt:
        # Check if the output directory exists
        if nasti.output_dir:
            rich.print("")
            rich.print("[red]:stop_sign:[bold] Keyboard interrupt detected.[/bold][red]")
            rich.print("[gray][italic]   Deleting output directory...[/italic][/gray]")
            nasti.delete_output_dir()
            rich.print("[gray][italic]   Exiting.[gray][italic]")

@click.command()
@click.argument("path", required=False)
def validate(path):
    if not path:
        path = "."
    try:
        nasti_file = NastiFile({
            "print_dep": rich.print,
            "path": path,
            "os_dep": os,
            "open_dep": open,
        })
        nasti_file.load()
        nasti_file.validate_mutations()
        rich.print("[green]:heavy_check_mark: Nastifile is valid.[/green]")
    except Exception as e:
        rich.print("[red]:x: Nastifile is invalid.[/red]")
        rich.print(e)

@click.command()
@click.argument("path", required=False)
def find(path):
    if not path:
        path = "."
    try:
        nasti_file = NastiFile({
            "print_dep": rich.print,
            "path": path,
            "os_dep": os,
            "open_dep": open,
        })
        unmentioned_files = nasti_file.find_unmentioned_files()
        click.echo(unmentioned_files.get_report())
    except Exception as e:
        print(e)

cli.add_command(process)
cli.add_command(validate)
cli.add_command(find)