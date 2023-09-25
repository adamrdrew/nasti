import click
import sys
import os

from nasti.nastifile import NastiFile
from nasti.nasti import Nasti
import rich
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

def remove_silent_opt_outer_quotes(s):
    if len(s) < 2:  # If the string length is less than 2, just return the original string
        return s
    if (s[0] == "'" and s[-1] == "'") or (s[0] == '"' and s[-1] == '"'):
        return s[1:-1]
    return s

def parse_silent_opts(silent_str):
    silent_dict = {}
    pairs = silent_str.split(',')

    for pair in pairs:
        if '=' not in pair:
            raise ValueError(f"{pair}. Expected format: key=value.")

        key, value = pair.split('=')

        if not key or not value:
            raise ValueError(f"{pair}. Neither key nor value can be empty.")

        silent_dict[key] = remove_silent_opt_outer_quotes(value)

    return silent_dict

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
@click.option("--silent", "-s", help="Silent mode with key=value pairs separated by commas.")
def process(source, git, defaults, dest_dir, silent):
    # Convert silent string to a dictionary
    silent_mode = False
    silent_opts = {}
    if silent:
        try:
            silent_opts = parse_silent_opts(silent)
            if len(silent_opts) == 0:
                raise ValueError("Silent mode key/value pairs cannot be empty.")
            silent_mode = True
        except ValueError as e:
            rich.print("[red]:stop_sign:[bold] Error processing silent mode key/value pairs[/bold][red]")
            rich.print(e)
            return

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
            "input_dep": session.prompt,
            "accept_defaults": defaults,
            "output_dir": dest_dir,
            "silent_mode": silent_mode,
            "silent_opts": silent_opts,
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
    rich.print("[blue]Searching for files that match mutations but aren't mentioned in Nastifile...[/blue]")
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
        rich.print(unmentioned_files.get_report())
    except Exception as e:
        rich.print(e)

cli.add_command(process)
cli.add_command(validate)
cli.add_command(find)