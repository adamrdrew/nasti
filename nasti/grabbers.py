import os
import sys
import uuid

class GitGrabber:
    source_dir = ""
    def __init__(self, source):
        self.source = source

    def grab(self):
        self.__validate_git()
        self.__create_tmp_dir()
        self.__clone_repo()

    def clean_up(self):
        os.system('rm -rf ' + self.source_dir)
    
    def __command_exists(self, command):
        return os.system("which " + command + " > /dev/null") == 0

    def __validate_git(self):
        if not self.__command_exists('git'):
            raise Exception("Error: git is not installed.")

    def __create_tmp_dir(self):
        tmp_dir_path = '/tmp/nasti/'
        if not os.path.isdir(tmp_dir_path):
            try:
                os.mkdir(tmp_dir_path)
            except:
                raise Exception("Error: Unable to create tmp directory.")
        random_dir = str(uuid.uuid4())
        self.source_dir = tmp_dir_path + random_dir
        try:
            os.mkdir(self.source_dir)
        except:
            raise Exception("Error: Unable to create tmp directory.")

    def __clone_repo(self):
        retval = os.system('git clone ' + self.source + ' ' + self.source_dir)
        if retval != 0:
            raise Exception("Error: Unable to clone git repo.")

class LocalDirectoryGrabber:
    source_dir = ""
    def __init__(self, source):
        self.source = source
    
    def grab(self):
        self.__validate_source_dir()
        self.source_dir = self.source

    def clean_up(self):
        pass

    def __validate_source_dir(self):
        if not os.path.isdir(self.source):
            raise Exception("Error: " + self.source + " is not a directory.")

class NullGrabber:
    source_dir = ""
    def __init__(self, source):
        self.source = source

    def grab(self):
        click.echo(click.get_current_context().get_help())

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