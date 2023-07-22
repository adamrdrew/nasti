from nasti.grabbers import GrabberResolver
from nasti.nastifile import NastiFile

class Nasti:
    def __init__(self, source):
        self.source = source

    def run(self):
        # resolve our source input
        try:
            self.get_source()
            self.load_nasti_file()
        except:
            self.grabber.clean_up()
            raise

    def load_nasti_file(self):
        self.nasti_file = NastiFile(self.grabber.source_dir + '/nasti.yaml')
        self.nasti_file.load()

    # resolve our source input
    # ensure that there's a local directory with our source in it
    # if the soure is a git repo, clone it
    # if the source is a local directory, use it
    def get_source(self):
        resolver = GrabberResolver(self.source)
        self.grabber = resolver.resolve()
        self.grabber.grab()