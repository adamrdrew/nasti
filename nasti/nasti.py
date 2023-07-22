import os

from nasti.source_handlers import SourceHandlerResolver
from nasti.nastifile import NastiFile

class Nasti:
    def __init__(self, source, print_func=print, git_init=True):
        self.source = source
        self.handler = None
        self.print_func = print_func
        self.output_dir = ""
        self.git_init = git_init

    def run(self):
        try:
            self.__get_source()
            self.__create_output_dir()
            self.__copy_source_files()
            self.__load_nasti_file()
            self.nasti_file.validate()
            self.nasti_file.run()
            self.__clean_up()
            self.__git_init()
        except Exception as e:
            self.handler.clean_up()
            self.__delete_output_dir()
            raise e

    def __clean_up(self):
        #delete the nastifile
        os.system(f"rm {self.output_dir}/nasti.yaml")
        # delete the git repo
        os.system(f"rm -rf {self.output_dir}/.git")

    def __git_init(self):
        if self.git_init:
            os.system(f"cd {self.output_dir} && git init && git add . && git commit -am 'Initial commit'")


    def __create_output_dir(self):
        attemps = 0
        max_attempts = 3
        while True:
            self.output_dir = input("Enter an output directory name: ")
            try:
                # Attempt to create the directory
                os.makedirs(self.output_dir)
                self.print_func(f"Directory '{self.output_dir}' created successfully.")
                break
            except OSError as e:
                # Handle error if directory creation fails
                self.print_func(f"Error: {e}")
                self.print_func("Please check the directory name and try again.")
                attemps += 1
                if attemps >= max_attempts:
                    raise Exception("Error: Something really weird is up. ")

    def __delete_output_dir(self):
        os.system(f"rm -rf {self.output_dir}")

    def __copy_source_files(self):
        # Copy the files from the source to the output dir
        os.system(f"cp -r {self.handler.source_dir}/* {self.output_dir}")

    def __load_nasti_file(self):
        if not self.handler:
            raise Exception("Error: No source handler found.")
        self.nasti_file = NastiFile(self.output_dir)
        self.nasti_file.load()

    def __get_source(self):
        resolver = SourceHandlerResolver(self.source)
        self.handler = resolver.resolve()
        self.handler.run()

