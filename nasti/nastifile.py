import re
import yaml

from nasti.mutation import Mutation
import nasti.exceptions as exceptions

class UnmentionedFilesResultItem:
    def __init__(self, files, mutation):
        self.files = files
        self.mutation = mutation

    def print(self):
        print(f"\nMutation {self.mutation.name} matches but does not reference:")
        for file in self.files:
            print(f"    {file}")

class UnmentionedFilesResult:
    def __init__(self):
        self.results = []
    
    def add(self, mutation, files):
        self.results.append(UnmentionedFilesResultItem(files, mutation))

    def print(self):
        if len(self.results) == 0:
            return
        print("The following mutations match files not listed in the nastifile:")
        for result in self.results:
            result.print() 

class NastiFile:
    MUTATIONS_KEY="mutations"
    NAME_KEY="name"
    PROMPT_KEY="prompt"
    REPLACE_KEY="replace"
    FILES_KEY="files"
    HELP_KEY="help"
    VALIDATION_KEY="validation"

    def __init__(self, opts={}):
        # Dependency injection
        self.os_dep = opts["os_dep"]
        self.open_dep = opts["open_dep"]

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
        working_dir = self.get_dir()
        for mutation_config in self.config[self.MUTATIONS_KEY]:
            print()
            mutation = Mutation(mutation_config, working_dir)
            mutation.run()

    # Get the abolute path of the directory containing the nasti file
    def get_dir(self):
        return self.os_dep.path.dirname(self.os_dep.path.abspath(self.path))
    
    def validate(self):
        self.load()
        # verify there are mutations
        if not self.MUTATIONS_KEY in self.config:
            raise exceptions.NastiFileNoMutationsException(f"Error: {self.path} does not contain any mutations.")
        working_dir = self.get_dir()
        # verify each mutation is valid
        for mutation_config in self.config[self.MUTATIONS_KEY]:
            self.__validate_mutation_config_keys(mutation_config)
            mutation = Mutation(mutation_config, working_dir)
            mutation.validate()
    
    def find_unmentioned_files(self):
        self.load()
        unmentioned_files = UnmentionedFilesResult()
        # verify there are mutations
        if not self.MUTATIONS_KEY in self.config:
            raise exceptions.NastiFileNoMutationsException(f"Error: {self.path} does not contain any mutations.")
        working_dir = self.get_dir()
        # verify each mutation is valid
        for mutation_config in self.config[self.MUTATIONS_KEY]:
            mutation = Mutation(mutation_config, working_dir)
            mutation_unmentioned_files = mutation.find_unmentioned_files(working_dir)
            if len(mutation_unmentioned_files) > 0:
                unmentioned_files.add(mutation, mutation_unmentioned_files)
        return unmentioned_files


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
