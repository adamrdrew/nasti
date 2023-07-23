import os
import re
from nasti.validation import Validation
import nasti.exceptions as exceptions


class Mutation:
    prompt = ""
    help = False
    validation = False
    replace = ""
    files = []
    path = ""

    HELP_KEY = "help"
    VALIDATION_KEY = "validation"
    NAME_KEY = "name"
    PROMPT_KEY = "prompt"
    REPLACE_KEY = "replace"
    FILES_KEY = "files"

    def __init__(self, mutation_config, path, os_dep=os, open_dep=open, input_dep=input, print_dep=print):
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
        if self.VALIDATION_KEY in mutation_config:
            try:
                self.validation = Validation(mutation_config[self.VALIDATION_KEY])
            except Exception as e:
                raise e(f"Error: Invalid vaidation config in mutation: {mutation_config} {e}")
        self.path = path

    def validate(self):
            self.__validate_files()

    def run(self):
        # Prompt the user for input
        if self.help:
            self.print_dep(self.help)
        user_input = self.__get_user_input()
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

    def __validate_files(self):
        # verify files isn't empty
        if len(self.files) == 0:
            raise exceptions.MutationEmptyFilesException(f"Error: mutation {self.name} does not contain any files.")
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

    def __get_file_full_path(self, file):
        return self.path + '/' + file