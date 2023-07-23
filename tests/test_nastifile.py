import unittest
from nasti.nastifile import NastiFile
import tests.mocks as mocks
import os 
import nasti.exceptions as exceptions

class TestNastiFile(unittest.TestCase):
    def test_unable_to_open_file(self):
        nasti = NastiFile({
            "path": "tests/mocks/ddsfdsfdsfsdf",
            "os_dep": os,
            "open_dep": open,
        })
        with self.assertRaises(exceptions.NastiFileUnableToOpenFileException):
            nasti.load()

    def test_load_valid_yaml(self):
        nasti_file = NastiFile({
            "path": "tests/nastifiles/valid",
            "os_dep": os,
            "open_dep": open,
        })
        nasti_file.load()
        assert nasti_file.config["mutations"][0]["name"] == "example_mutation"

    def test_load_invalid_yaml(self):
        nasti_file = NastiFile({
            "path": "tests/nastifiles/bad_yaml",
            "os_dep": os,
            "open_dep": open,
        })
        with self.assertRaises(exceptions.NastiFileInvalidYamlException):
            nasti_file.load()
    
    def test_validate_no_mutations(self):
        nasti_file = NastiFile({
            "path": "tests/nastifiles/no_mutations",
            "os_dep": os,
            "open_dep": open,
        })
        nasti_file.load()
        with self.assertRaises(exceptions.NastiFileNoMutationsException):
            nasti_file.validate()
    
    def test_validate_mutations_unknown_keys(self):
        nasti_file = NastiFile({
            "path": "tests/nastifiles/mutation_unknown_keys",
            "os_dep": os,
            "open_dep": open,
        })
        nasti_file.load()
        with self.assertRaises(exceptions.NastiFileUnknownKeysException):
            nasti_file.validate()