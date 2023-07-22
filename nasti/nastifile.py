import click
import os
import sys
import yaml

from nasti.mutation import Mutation

class NastiFile:
    def __init__(self, path):
        self.__set_path(path)

    def load(self):
        self.__verify_exists()
        try:
            with open(self.path, 'r') as file:
                self.config = yaml.safe_load(file)
        except:
            raise Exception(f"Error: Unable to load {self.path}.")

    # Get the abolute path of the directory containing the nasti file
    def get_dir(self):
        return os.path.dirname(os.path.abspath(self.path))
    
    def validate(self):
        self.load()
        # verify there are mutations
        if not "mutations" in self.config:
            raise Exception(f"Error: {self.path} does not contain any mutations.")
        working_dir = self.get_dir()
        # verify each mutation is valid
        for mutation_config in self.config["mutations"]:
            mutation = Mutation(mutation_config, working_dir)
            mutation.validate()
    
    def run(self):
        self.load()
        working_dir = self.get_dir()
        for mutation_config in self.config["mutations"]:
            print()
            mutation = Mutation(mutation_config, working_dir)
            mutation.run()

    def __set_path(self, path):
        if not path:
            path = 'nasti.yaml'
        self.path = path


    def __verify_exists(self):
        # ensure that the file exists
        if not os.path.isfile(self.path):
            raise Exception(f"Error: {self.path} does not exist.")
