from nasti.validation import Validation
import nasti.exceptions as exceptions

class Global:
    NAME_KEY = "name"
    PROMPT_KEY = "prompt"
    HELP_KEY = "help"
    VALIDATION_KEY = "validation"

    name = None
    prompt = None
    value = None
    help = None
    validation = None

    def __init__(self, opts: dict, input_dep, print_dep, silent_mode=False, silent_opts={}):
        # Dependency injection
        self.input_dep = input_dep
        self.print_dep = print_dep
        self. silent_mode = silent_mode
        self.silent_opts = silent_opts
        # Required fields
        try:
            self.name        = opts[self.NAME_KEY]
            self.prompt      = opts[self.PROMPT_KEY]
        except Exception as e:
            raise exceptions.GlobalRequiredKeysMissingException(f"Error: Invalid global config: {opts} required field missing: {e}")
        # Optional fields
        if self.HELP_KEY in opts:
            self.help        = opts[self.HELP_KEY]
        if self.VALIDATION_KEY in opts:
            try:
                self.validation = Validation(opts[self.VALIDATION_KEY])
            except Exception as e:
                raise e(f"Error: Invalid vaidation config in global: {opts} {e}")
    
    def validate(self):
        if self.validation:
            return self.validation.validate(self.value)
        return True

    def populate(self):
        if self.silent_mode:
            self.__populate_silent()
            return
        tries = 0
        max_tries = 3
        while True:
            self.print_dep(f"{self.prompt}")
            if self.help:
                self.print_dep(self.help)
            self.value = self.input_dep("> ")
            if self.validate():
                break
            tries += 1
            if tries >= max_tries:
                raise exceptions.GlobalTooManyInputTriesException(f"Error: Too many tries for global {self.name}")

    def __populate_silent(self):
        if self.name not in self.silent_opts:
            raise exceptions.GlobalSilentModeException(f"Error: Silent mode enabled but no value found for global {self.name}")
        self.value = self.silent_opts[self.name]
        if self.validate():
            return
        raise exceptions.GlobalSilentModeException(f"Error: Silent mode enabled but value {self.value} for global {self.name} failed validation")            

    def get_value(self):
        return self.value
    
    def get_name(self):
        return self.name
