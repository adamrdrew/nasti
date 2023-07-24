import validators
import re
import nasti.exceptions as exceptions

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

    REGEX_KEY = "regex"
    KIND_KEY = "kind"

    def __init__(self, validation_config):
        try:
            self.__validate_config(validation_config)
        except Exception as e:
            raise e
        if self.REGEX_KEY in validation_config:
            self.regex = validation_config[self.REGEX_KEY]
        if self.KIND_KEY in validation_config:
            self.kind = validation_config[self.KIND_KEY]
    
    def validate(self, input):
        if self.regex:
            return self.__is_valid_regex(input)
        if self.kind:
            return self.__is_valid_kind(input)

    def __is_valid_regex(self, input):
        return bool(re.match(self.regex, input))
    
    def __is_valid_kind(self, input):
        return bool(self.kinds[self.kind](input))

    def __verify_known_kind(self, kind):
        if not kind in self.kinds:
            raise exceptions.ValidationUnknownKindException(f"Error: Unknown kind {kind}")

    def __validate_config(self, validation_config):
        if not "regex" in validation_config and not "kind" in validation_config: 
            raise exceptions.ValidationConfigMissingException(f"Error: Validation {validation_config} requires regex or kind")
        if "regex" in validation_config and "kind" in validation_config: 
            raise exceptions.ValidationConfigInvalidException(f"Error: Validation {validation_config} requires regex or kind, not both")
        if "kind" in validation_config:
            self.__verify_known_kind(validation_config["kind"])

