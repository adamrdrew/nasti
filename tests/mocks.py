class MockPath:
    def __init__(self, opts):
        self.exists_ret = opts["exists"] if "exists" in opts else True
        self.join_ret = opts["join"] if "join" in opts else True
        self.isfile_ret = opts["isfile"] if "isfile" in opts else True
        self.isdir_ret = opts["isdir"] if "isdir" in opts else True
    def join(self, path1, path2):
        return self.join_ret
    def isfile(self, path):
        return self.isfile_ret
    def isdir(self, path):
        return self.isdir_ret
    def exists(self, path):
        return self.exists_ret

class MockOs:
    
    def __init__(self, opts={}):
        self.mkdir_ret = opts["mkdir"] if "mkdir" in opts else True
        self.system_ret = opts["system"] if "system" in opts else 0
        self.devnull_ret = opts["devnull"] if "devnull" in opts else True
        self.path = MockPath(opts)
        pass

    def mkdir(self, path):
        if not self.mkdir_ret:
            raise OSError("Error: Directory creation failed.")
        return self.mkdir_ret
    
    def system(self, command):
        return self.system_ret

    def devnull(self):
        return self.devnull_ret


def mock_print(text):
    pass

def mock_open(path, mode):
    pass

def mock_input(text):
    pass

def mock_failed_open(path, mode):
    raise OSError("Error: Unable to open file.")