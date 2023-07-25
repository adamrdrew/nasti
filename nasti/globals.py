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

    def __init__(self, opts: dict, input_dep, print_dep):
        # Dependency injection
        self.input_dep = input_dep
        self.print_dep = print_dep
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
        tries = 0
        max_tries = 3
        while True:
            if self.help:
                self.print_dep(self.help)
            self.value = self.input_dep(f"{self.prompt}: ")
            if self.validate():
                break
            tries += 1
            if tries >= max_tries:
                raise exceptions.GlobalTooManyInputTriesException(f"Error: Too many tries for global {self.name}")

    def get_value(self):
        return self.value
    
    def get_name(self):
        return self.name
