import validators
import re

class Validation:
    regex = False
    kind = False

    kinds = {
        "domain":       validators.domain,
        "email":        validators.email,
        "ip_address":   validators.ip_address,
        "slug":         validators.slug,
        "url":          validators.url,
        "uuid":         validators.uuid,
    }

    def __init__(self, validation_config):
        try:
            self.__validate_config(validation_config)
        except Exception as e:
            raise e
        if "regex" in validation_config:
            self.regex = validation_config["regex"]
        if "kind" in validation_config:
            self.kind = validation_config["kind"]
    
    def validate(self, input):
        if self.regex:
            return self.__is_valid_regex(input)
        if self.kind:
            return self.__is_valid_kind(input)
        return False

    def __is_valid_regex(self, input):
        return re.match(self.regex, input)
    
    def __is_valid_kind(self, input):
        return self.kinds[self.kind](input)

    def __validate_config(self, validation_config):
        if not "regex" in validation_config and not "kind" in validation_config: 
            raise Exception(f"Error: Validation {validation_config} requires regex or kind")
        if "regex" in validation_config and "kind" in validation_config: 
            raise Exception(f"Error: Validation {validation_config} requires regex or kind, not both")

