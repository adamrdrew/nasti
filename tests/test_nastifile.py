import unittest
from nasti.nastifile import NastiFile, UnmentionedFilesResult, UnmentionedFilesResultItem
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
    
    def test_unmentioned_files_found(self):
        nasti_file = NastiFile({
            "path": "tests/nastifiles/mutation_unmentioned_files",
            "os_dep": os,
            "open_dep": open,
        })
        unmentioned_files = nasti_file.find_unmentioned_files()
        # assert on array length
        assert isinstance(unmentioned_files, UnmentionedFilesResult)
        report = unmentioned_files.get_report()
        assert isinstance(report, str)
        assert len(report) != 0
        assert len(unmentioned_files.get_results()) == 1
        assert len(unmentioned_files.get_results()[0].files) == 2
        result = unmentioned_files.get_results()[0]
        assert isinstance(result, UnmentionedFilesResultItem)
        assert result.get_mutation().name == "example_mutation"
        assert "files/unmentioned" in result.get_files()
        assert "files/nested/unmentioned" in result.get_files()

    def test_unmentioned_files_not_found(self):
        nasti_file = NastiFile({
            "path": "tests/nastifiles/valid",
            "os_dep": os,
            "open_dep": open,
        })
        unmentioned_files = nasti_file.find_unmentioned_files()
        assert len(unmentioned_files.get_results()) == 0
        assert len(unmentioned_files.get_report()) == 0
    
    def test_globals(self):
        input_dep = func = lambda x: "test_global_value"
        print_dep = func = lambda x: None
        nasti_file = NastiFile({
            "path": "tests/nastifiles/nastifile_globals",
            "os_dep": os,
            "open_dep": open,
            "input_dep": input_dep,
            "print_dep": print_dep
        })
        nasti_file.load()
        nasti_file.run()
        global_obj = nasti_file.get_global("app_name")
        assert global_obj  == "test_global_value"
    
    def test_default(self):
        input_dep = func = lambda x: "input_from_user"
        print_dep = func = lambda x: None
        nasti_file = NastiFile({
            "path": "tests/nastifiles/nastifile_default",
            "os_dep": os,
            "open_dep": open,
            "input_dep": input_dep,
            "print_dep": print_dep
        })
        nasti_file.load()
        nasti_file.run()

