import os
import re

class Mutation:
    prompt = ""
    help = ""
    validations = []
    replace = ""
    files = []
    path = ""

    def __init__(self, mutation_config, path):
        try:
            self.name       = mutation_config["name"]
            self.prompt     = mutation_config["prompt"]
            self.help       = mutation_config["help"]
            self.validations = mutation_config["validations"]
            self.replace    = mutation_config["replace"]
            self.files      = mutation_config["files"]
        except:
            raise Exception("Error: Invalid mutation config.")
        self.path = path

    def validate(self):
            self.__validate_files()
            self.__validate_validations()

    def __validate_validations(self):
            # verify the validations are valid
            if not isinstance(self.validations, list):
                raise Exception(f"Error: mutation {self.name} validations must be a list.")
            for validation in self.validations:
                # verify the validation is valid regex
                try:
                    re.compile(validation)
                except:
                    raise Exception(f"Error: mutation {self.name} validation {validation} is not valid regex.")

    def __validate_files(self):
        # verify files isn't empty
        if len(self.files) == 0:
            raise Exception(f"Error: mutation {self.name} does not contain any files.")
        for file in self.files:
            # verify file exists
            file_with_path = self.__get_file_full_path(file)
            if not os.path.isfile(file_with_path):
                raise Exception(f"Error: mutation: {self.name} file: {file} at: {file_with_path} does not exist.")
            # verify the file contains the text to be replaced
            with open(file_with_path, 'r') as f:
                # search for at least one instance of the text to be replaced
                if not re.search(self.replace, f.read()):
                    raise Exception(f"Error: mutation {self.name} file: {file} at: {file_with_path} does not contain {self.replace} ")
    
    def __get_file_full_path(self, file):
        return self.path + '/' + file