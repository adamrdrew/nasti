import os
import re
from nasti.validation import Validation
 
class Mutation:
    prompt = ""
    help = False
    validation = False
    replace = ""
    files = []
    path = ""

    def __init__(self, mutation_config, path):
        # Required fields
        try:
            self.name        = mutation_config["name"]
            self.prompt      = mutation_config["prompt"]
            self.replace     = mutation_config["replace"]
            self.files       = mutation_config["files"]
        except Exception as e:
            raise Exception(f"Error: Invalid mutation config: {mutation_config} required field missing missing {e}")
        # Optional fields
        if "help" in mutation_config:
            self.help        = mutation_config["help"]
        if "validation" in mutation_config:
            try:
                self.validation = Validation(mutation_config["validation"])
            except Exception as e:
                raise Exception(f"Error: Invalid vaidation config in mutation: {mutation_config} {e}")
        self.path = path

    def validate(self):
            self.__validate_files()

    def run(self):
        # Prompt the user for input
        if self.help:
            print(self.help)
        user_input = self.__get_user_input()
        self.__replace_text_in_files(user_input)

    def __get_user_input(self):
        user_input = input(f"{self.prompt}> ")
        tries = 0
        max_tries = 3
        while True:
            tries += 1
            if tries > max_tries:
                raise Exception(f"Error: Too many invalid inputs.")
            if self.__is_input_valid(user_input):
                break
            print(f"Invalid input.")
            user_input = input(f"{self.prompt}> ")
        return user_input

    def __replace_text_in_files(self, user_input):
        # Replace the text in the files
        for file in self.files:
            file_with_path = self.__get_file_full_path(file)
            with open(file_with_path, 'r') as f:
                file_text = f.read()
            file_text = file_text.replace(self.replace, user_input)
            with open(file_with_path, 'w') as f:
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