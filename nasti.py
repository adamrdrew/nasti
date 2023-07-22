import click
import sys
import os
import uuid
import yaml

class GitGrabber:
    source_dir = ""
    def __init__(self, source):
        self.source = source

    def grab(self):
        click.echo("Getting from git: " + self.source)
        self.__validate_git()
        self.__create_tmp_dir()
        self.__clone_repo()

    def clean_up(self):
        os.system('rm -rf ' + self.source_dir)
    
    def __command_exists(self, command):
        return os.system("which " + command + " > /dev/null") == 0

    def __validate_git(self):
        if not self.__command_exists('git'):
            click.echo("Error: git is not installed.")
            sys.exit(1)

    def __create_tmp_dir(self):
        tmp_dir_path = '/tmp/nasti/'
        if not os.path.isdir(tmp_dir_path):
            try:
                os.mkdir(tmp_dir_path)
            except:
                click.echo("Error: Unable to create tmp directory.")
                sys.exit(1)
        random_dir = str(uuid.uuid4())
        self.source_dir = tmp_dir_path + random_dir
        try:
            os.mkdir(self.source_dir)
        except:
            click.echo("Error: Unable to create source directory.")
            sys.exit(1)

    def __clone_repo(self):
        retval = os.system('git clone ' + self.source + ' ' + self.source_dir)
        if retval != 0:
            click.echo("Error: Unable to clone repo.")
            sys.exit(1)

class LocalDirectoryGrabber:
    source_dir = ""
    def __init__(self, source):
        self.source = source
    
    def grab(self):
        click.echo("Getting from local directory: " + self.source)
        self.__validate_source_dir()
        self.source_dir = self.source

    def clean_up(self):
        pass

    def __validate_source_dir(self):
        if not os.path.isdir(self.source):
            click.echo("Error: " + self.source + " is not a directory.")
            sys.exit(1)

class NullGrabber:
    source_dir = ""
    def __init__(self, source):
        self.source = source

    def grab(self):
        click.echo(click.get_current_context().get_help())
        sys.exit(0)

    def clean_up(self):
        pass

class GrabberResolver:
    def __init__(self, source):
        self.source = source

    def resolve(self):
        if not self.source or self.source.lower() == 'help':
            return NullGrabber(self.source)
        if self.source.startswith('git@'):
            return GitGrabber(self.source)
        return LocalDirectoryGrabber(self.source)

class NastiFile:
    def __init__(self, path):
        self.path = path

    def load(self):
        self.__verify_exists()
        try:
            self.config = yaml.load(open(self.path))
        except:
            click.echo("Error: " + self.path + " is not valid YAML.")
            sys.exit(1)
    
    def __verify_exists(self):
        # ensure that the file exists
        if not os.path.isfile(self.path):
            click.echo("Error: " + self.path + " does not exist.")
            sys.exit(1)


class Nasti:
    def __init__(self, source):
        self.source = source

    def run(self):
        # resolve our source input
        try:
            self.get_source()
            self.load_nasti_file()
        except:
            self.grabber.clean_up()
            raise

    def load_nasti_file(self):
        self.nasti_file = NastiFile(self.grabber.source_dir + '/nasti.yml')
        self.nasti_file.load()

    # resolve our source input
    # ensure that there's a local directory with our source in it
    # if the soure is a git repo, clone it
    # if the source is a local directory, use it
    def get_source(self):
        resolver = GrabberResolver(self.source)
        self.grabber = resolver.resolve()
        self.grabber.grab()

@click.command()
@click.argument("source", required=False)
def greeting(source):
    """
    Welcome to NASTI!

    NASTI is free and open source software. Feel free to get weird with it!
    """

    nasti = Nasti(source)
    nasti.run()

if __name__ == "__main__":
    greeting()
