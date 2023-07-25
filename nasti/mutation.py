import os
import re
from nasti.validation import Validation
import nasti.exceptions as exceptions
from jinja2 import Template

class Mutation:
    prompt = ""
    help = False
    validation = False
    replace = ""
    files = []
    path = ""
    default = False
    globals = {}

    HELP_KEY = "help"
    VALIDATION_KEY = "validation"
    NAME_KEY = "name"
    PROMPT_KEY = "prompt"
    REPLACE_KEY = "replace"
    FILES_KEY = "files"
    DEFAULT_KEY = "default"
    GLOBALS_KEY = "globals"

    def __init__(self, mutation_config: dict, path, os_dep=os, open_dep=open, input_dep=input, print_dep=print):
        # Dependency injection
        self.os_dep = os_dep
        self.open_dep = open_dep
        self.input_dep = input_dep
        self.print_dep = print_dep
        # Required fields
        try:
            self.name        = mutation_config[self.NAME_KEY]
            self.prompt      = mutation_config[self.PROMPT_KEY]
            self.replace     = mutation_config[self.REPLACE_KEY]
            self.files       = mutation_config[self.FILES_KEY]
        except Exception as e:
            raise exceptions.MutationRequiredKeysMissingException(f"Error: Invalid mutation config: {mutation_config} required field missing missing {e}")
        # Optional fields
        if self.HELP_KEY in mutation_config:
            self.help        = mutation_config[self.HELP_KEY]
        if self.GLOBALS_KEY in mutation_config:
            self.globals     = mutation_config[self.GLOBALS_KEY]
        if self.DEFAULT_KEY in mutation_config:
            self.default     = mutation_config[self.DEFAULT_KEY]
        if self.VALIDATION_KEY in mutation_config:
            try:
                self.validation = Validation(mutation_config[self.VALIDATION_KEY])
            except Exception as e:
                raise e(f"Error: Invalid vaidation config in mutation: {mutation_config} {e}")
        self.path = path

    # Recursively find all files in the directory that contain the text to be replaced
    # and are not mentioned in the mutation
    # Returns a list of file paths relative to the working directory
    def find_unmentioned_files(self, root_dir):
        if not root_dir:
            root_dir = self.path
        unmentioned_files = []
        # list all files in the directory
        files_in_dir = self.os_dep.listdir(root_dir)
        # for each file in the directory
        for file_in_dir in files_in_dir:
            # skip the nastifile
            if file_in_dir == 'nasti.yaml':
                continue
            # if the file starts with a dot skip it
            if file_in_dir.startswith('.'):
                continue
            # The file path is relative to the working directory
            # so we need to construct fill file path
            file_full_path = root_dir + '/' + file_in_dir

            # if the file is a directory recurse
            if self.os_dep.path.isdir(file_full_path):
                unmentioned_files += self.find_unmentioned_files(file_full_path)
                continue
            
            # Determine if the file is in the mutation file list and if it is we'll skip it
            # this code is kind of hard to read so I'll explain it
            # We split the full file path by the working directory path
            # this gives us a list with elements: the working directory, the relative path to the file
            file_path_split = file_full_path.split(self.path)
            # remove the working directory from the list because we don't need it
            # as files in a mutation are relative to the working directory
            file_path_split.pop(0)
            # now we have a list with one element: the relative path to the file
            # we get the first element and remove the leading slash
            relative_file_path = file_path_split[0].lstrip('/')
            # the end result of all this is that a path like this:
            # /home/user/projects/nasti/nasti.yaml
            # with a working directory of:
            # /home/user/projects/nasti
            # becomes this:
            # nasti.yaml
            # which is the same format as the files in the mutation file list
            # so we can just check if the file is in the list and if it is we skip it
            if relative_file_path in self.files:
                continue

            # look into the file and see if the text to be replaced is there
            with self.open_dep(file_full_path, 'r') as f:
                if re.search(self.replace, f.read()):
                    # if the text to be replaced is there add it to the list
                    unmentioned_files.append(relative_file_path)
        return unmentioned_files

    # Validate the nastifile syntax
    # Raises exceptions if there are any problems
    def validate(self):
        # verify files isn't empty
        if len(self.files) == 0:
            raise exceptions.MutationEmptyFilesException(f"Error: mutation {self.name} does not contain any files.")
        # If there's a default template verify it renders
        if self.default:
            self.render_default_template()
        for file in self.files:
            # verify file exists
            file_with_path = self.__get_file_full_path(file)
            if not self.os_dep.path.isfile(file_with_path):
                raise exceptions.MutationFileDoesNotExistException(f"Error: mutation: {self.name} file: {file} at: {file_with_path} does not exist.")
            # verify the file contains the text to be replaced
            with self.open_dep(file_with_path, 'r') as f:
                # search for at least one instance of the text to be replaced
                if not re.search(self.replace, f.read()):
                    raise exceptions.MutationFileDoesNotContainReplacementStringException(f"Error: mutation {self.name} file: {file} at: {file_with_path} does not contain {self.replace} ")

    def render_default_template(self):
        default_value = ""
        if not self.default:
            return
        try:
            template = Template(self.default)
            default_value = template.render(**self.globals)
        except Exception as e:
            raise exceptions.MutationDefaultTemplateInvalidException(f"Error: Unable to render default template: {e}")
        return default_value
        

    def run(self):
        # Prompt the user for input
        if self.help:
            self.print_dep(self.help)
        # If there is a default value, print it
        if self.default:
            default = self.render_default_template()
            self.print_dep(f"Enter for Default: {default}")
        user_input = self.__get_user_input()
        if user_input == "":
            user_input = self.render_default_template()
        try:
            self.__replace_text_in_files(user_input)
        except Exception as e:
            raise exceptions.MutationTextReplacementFailedException(f"Error: Unable to replace text in files: {e}")

    def __get_user_input(self):
        tries = 0
        max_tries = 3
        user_input = ""
        while True:
            user_input = self.input_dep(f"{self.prompt}> ")
            tries += 1
            if tries > max_tries:
                raise exceptions.MutationTooManyInputTriesException(f"Error: Too many invalid inputs.")
            if self.__is_input_valid(user_input):
                break
            self.print_dep(f"Invalid input.")
        return user_input

    def __replace_text_in_files(self, user_input):
        # Replace the text in the files
        for file in self.files:
            file_with_path = self.__get_file_full_path(file)
            with self.open_dep(file_with_path, 'r') as f:
                file_text = f.read()
            file_text = file_text.replace(self.replace, user_input)
            with self.open_dep(file_with_path, 'w') as f:
                f.write(file_text)
    
    def __is_input_valid(self, input):
        # If there is no validation, the input is valid
        if not self.validation:
            return True
        # Validate the input by testing it against the validations
        return self.validation.validate(input)

    def __get_file_full_path(self, file):
        return self.path + '/' + file