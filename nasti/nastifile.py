import os
import re
import yaml

from nasti.mutation import Mutation
from nasti.globals import Global
import nasti.exceptions as exceptions


# This class is used to store the results of the find command
class UnmentionedFilesResult:
    def __init__(self):
        self.results = []
    
    def add(self, mutation, files):
        if len(files) == 0:
            return
        self.results.append(UnmentionedFilesResultItem(files, mutation))

    def get_report(self):
        if len(self.results) == 0:
            return ""
        report = ""
        report += "The following mutations match files not listed in the nastifile:\n"
        for result in self.results:
            report += result.get_report()
        return report

    def get_results(self):
        return self.results

# This class stores the individual results of a find operation
class UnmentionedFilesResultItem:
    def __init__(self, files, mutation):
        self.files = files
        self.mutation = mutation

    def get_report(self):
        report = ""
        report += f"\nMutation {self.mutation.name} matches but does not reference:\n"
        for file in self.files:
            report += f"    {file}"
        return report
    
    def get_files(self):
        return self.files

    def get_mutation(self):
        return self.mutation

class NastiFile:
    MUTATIONS_KEY="mutations"
    NAME_KEY="name"
    PROMPT_KEY="prompt"
    REPLACE_KEY="replace"
    FILES_KEY="files"
    HELP_KEY="help"
    VALIDATION_KEY="validation"
    GLOBALS_KEY="globals"

    globals = {}

    def __init__(self, opts={}):
        # Dependency injection
        self.os_dep = opts["os_dep"]
        self.open_dep = opts["open_dep"]

        if "print_dep" in opts:
            self.print_dep = opts["print_dep"]
        else:
            self.print_dep = print
        if "input_dep" in opts:
            self.input_dep = opts["input_dep"]
        else:
            self.input_dep = input

        self.__set_path(opts["path"])

    def load(self):
        self.__verify_exists()
        with self.open_dep(self.path, 'r') as file:
            try:
                self.config = yaml.load(file, Loader=yaml.SafeLoader)
            except yaml.YAMLError as e:
                raise exceptions.NastiFileInvalidYamlException(f"Error: Unable to load {self.path}.")

    def run(self):
        self.load()
        self.run_globals()
        self.run_mutations()


    def run_mutations(self):
        working_dir = self.get_dir()
        for mutation_config in self.config[self.MUTATIONS_KEY]:
            self.print_dep("")
            mutation_config["globals"] = self.globals
            mutation = Mutation(mutation_config, working_dir, os, open, self.input_dep, self.print_dep)
            mutation.run()

    def run_globals(self):
        if self.GLOBALS_KEY in self.config:
            for global_config in self.config[self.GLOBALS_KEY]:
                self.print_dep("")
                global_obj = Global(global_config, self.input_dep, self.print_dep)
                global_obj.populate()
                self.globals[global_obj.get_name()] = global_obj.get_value()
    
    def get_global(self, name):
        if name in self.globals:
            return self.globals[name]
        raise exceptions.NastiFileGlobalNotFoundException(f"Error: Global {name} not found.")

    # Get the abolute path of the directory containing the nasti file
    def get_dir(self):
        return self.os_dep.path.dirname(self.os_dep.path.abspath(self.path))
    
    # Validate the nastifile syntax
    def validate(self):
        for mutation in self.__mutations():
             mutation.validate()
    
    # Find files that are not mentioned in the nastifile
    def find_unmentioned_files(self):
        unmentioned_files = UnmentionedFilesResult()
        for mutation in self.__mutations():
            mutation_unmentioned_files = mutation.find_unmentioned_files(self.get_dir())
            unmentioned_files.add(mutation, mutation_unmentioned_files)
        return unmentioned_files

    # Get a list of mutation objects from the config
    # Does some validation on the config
    def __mutations(self):
        mutations = []
        self.load()
        # verify there are mutations
        if not self.MUTATIONS_KEY in self.config:
            raise exceptions.NastiFileNoMutationsException(f"Error: {self.path} does not contain any mutations.")
        working_dir = self.get_dir()
        for mutation_config in self.config[self.MUTATIONS_KEY]:
            # verify each mutation is valid
            # throws an exception if there is a problem
            self.__validate_mutation_config_keys(mutation_config)
            # create a mutation object and add it to the list
            mutation = Mutation(mutation_config, working_dir)
            mutations.append(mutation)
        return mutations

    def __validate_mutation_config_keys(self, mutation_config):
        valid_keys = [
            self.NAME_KEY, 
            self.PROMPT_KEY, 
            self.REPLACE_KEY, 
            self.FILES_KEY, 
            self.HELP_KEY, 
            self.VALIDATION_KEY,
        ]
        for key in mutation_config:
            if not key in valid_keys:
                raise exceptions.NastiFileUnknownKeysException(f"Error: Invalid key in mutation config: {key}")

    def __set_path(self, path):
        if not path:
            path = './nasti.yaml'
        self.path = f"{path}/nasti.yaml"


    def __verify_exists(self):
        # ensure that the file exists
        if not self.os_dep.path.isfile(self.path):
            raise exceptions.NastiFileUnableToOpenFileException(f"Error: {self.path} does not exist.")
