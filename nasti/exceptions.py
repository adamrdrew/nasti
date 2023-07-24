class MutationRequiredKeysMissingException(Exception):
    pass

class MutationEmptyFilesException(Exception):
    pass

class MutationFileDoesNotExistException(Exception):
    pass

class MutationFileDoesNotContainReplacementStringException(Exception):
    pass

class MutationTooManyInputTriesException(Exception):
    pass

class MutationTextReplacementFailedException(Exception):
    pass

class MutationDefaultTemplateInvalidException(Exception):
    pass

class ValidationConfigMissingException(Exception):
    pass

class ValidationConfigInvalidException(Exception):
    pass

class ValidationUnknownKindException(Exception):
    pass

class GitHandlerGitMissingException(Exception):
    pass

class GitHandlerTmpDirCreationException(Exception):
    pass

class GitHandlerCloneException(Exception):
    pass

class LocalDirHandlerSourceNotDirException(Exception):
    pass

class NastiFileUnableToOpenFileException(Exception):
    pass

class NastiFileInvalidYamlException(Exception):
    pass

class NastiFileNoMutationsException(Exception):
    pass

class NastiFileUnknownKeysException(Exception):
    pass

class NastiFileGlobalNotFoundException(Exception):
    pass

class GlobalRequiredKeysMissingException(Exception):
    pass

class GlobalTooManyInputTriesException(Exception):
    pass