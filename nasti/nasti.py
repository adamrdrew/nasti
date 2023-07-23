import subprocess

from nasti.source_handlers import SourceHandlerResolver
from nasti.nastifile import NastiFile

class Nasti:
    
    def __init__(self, opts={}):
        # Dependency injection
        self.os_dep = opts["os_dep"]
        self.open_dep = opts["open_dep"]
        self.input_dep = opts["input_dep"]
        self.help_text = opts["help_text"]

        self.source = opts["source"]
        self.handler = None
        self.print_func = opts["print_func"]
        self.output_dir = ""
        self.git_init = opts["git_init"]

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
        self.os_dep.system(f"rm {self.output_dir}/nasti.yaml")
        # delete the git repo
        self.os_dep.system(f"rm -rf {self.output_dir}/.git")

    def __git_init(self):
        if self.git_init:
            with self.open_dep(self.os_dep.devnull, 'w') as devnull:
                return subprocess.run(f"cd {self.output_dir} && git init && git add -A && git commit -am 'Initial commit'", stdout=devnull, stderr=devnull, shell=True)


    def __create_output_dir(self):
        attemps = 0
        max_attempts = 3
        while True:
            self.output_dir = input("Enter an output directory name: ")
            try:
                # Attempt to create the directory
                self.os_dep.makedirs(self.output_dir)
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
        self.os_dep.system(f"rm -rf {self.output_dir}")

    def __copy_source_files(self):
        # Copy the files from the source to the output dir
        self.os_dep.system(f"cp -r {self.handler.source_dir}/* {self.output_dir}")

    def __load_nasti_file(self):
        if not self.handler:
            raise Exception("Error: No source handler found.")
        self.nasti_file = NastiFile({
            "path": self.output_dir,
            "os_dep": self.os_dep,
            "open_dep": self.open_dep,
        })
        self.nasti_file.load()

    def __get_source(self):
        resolver = SourceHandlerResolver(self.source, self.help_text, self.os_dep, self.print_func)
        self.handler = resolver.resolve()
        self.handler.run()

