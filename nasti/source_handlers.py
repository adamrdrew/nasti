import os
import uuid
import nasti.exceptions as exceptions

# SourceHandlerResolver finds the correct source handler for the source input and returns it
# If no source is provided, it returns the help handler
class SourceHandlerResolver:
    HELP_KEY = "help"
    GIT_PREFIX = "git@"

    def __init__(self, source, help_text, os_dep=os, print_dep=print):
        self.os_dep = os_dep
        self.source = source
        self.print_dep = print_dep
        self.help_text = help_text

    def resolve(self):
        if not self.source or self.source.lower() == self.HELP_KEY:
            return HelpHandler(self.source, self.os_dep, self.print_dep, self.help_text)
        if self.source.startswith(self.GIT_PREFIX):
            return GitHandler(self.source, self.os_dep)
        return LocalDirectoryHandler(self.source, self.os_dep)

class GitHandler:
    source_dir = ""
    TMP_DIR = "/tmp/nasti/"
    def __init__(self, source, os_dep=os):
        self.source = source
        self.os_dep = os_dep

    def run(self):
        self.validate_git()
        self.__create_tmp_dir()
        self.clone_repo()

    def clean_up(self):
        self.os_dep.system('rm -rf ' + self.source_dir)
    
    def __command_exists(self, command):
        return self.os_dep.system("which " + command + " > /dev/null") == 0

    # I wouldn't normally make these methods public
    # but it aids in testing these methods
    def validate_git(self):
        if not self.__command_exists('git'):
            raise exceptions.GitHandlerGitMissingException("Error: git is not installed.")
    def clone_repo(self):
        if self.os_dep.system('git clone ' + self.source + ' ' + self.source_dir) != 0:
            raise exceptions.GitHandlerCloneException("Error: Unable to clone git repo.")

    def __create_tmp_dir(self):
        tmp_dir_path = self.TMP_DIR
        if not self.os_dep.path.isdir(tmp_dir_path):
            try:
                self.os_dep.mkdir(tmp_dir_path)
            except:
                raise exceptions.GitHandlerTmpDirCreationException("Error: Unable to create tmp directory.")
        random_dir = str(uuid.uuid4())
        self.source_dir = tmp_dir_path + random_dir
        try:
            self.os_dep.mkdir(self.source_dir)
        except:
            raise exceptions.GitHandlerTmpDirCreationException("Error: Unable to create tmp directory.")

class LocalDirectoryHandler:
    source_dir = ""
    def __init__(self, source, os_dep=os):
        self.source = source
        self.os_dep = os_dep
    
    def run(self):
        self.__validate_source_dir()
        self.source_dir = self.source

    def clean_up(self):
        pass

    def __validate_source_dir(self):
        if not self.os_dep.path.isdir(self.source):
            raise exceptions.LocalDirHandlerSourceNotDirException("Error: " + self.source + " is not a directory.")

class HelpHandler:
    source_dir = ""
    def __init__(self, source, os_dep=os, print_dep=print, help_text=""):
        self.source = source
        self.os_dep = os_dep
        self.print_dep = print_dep
        self.help_text = help_text

    def run(self):
        self.print_dep(self.help_text)

    def clean_up(self):
        pass

