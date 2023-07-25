import unittest
from nasti.mutation import Mutation
import nasti.exceptions as exceptions
import tests.mocks as mocks
import os
import yaml

class TestMutation(unittest.TestCase):
    # This tests that the files array is present but empty
    def test_empty_files(self):
        #open the yaml file
        with open("tests/nastifiles/mutation_empty_files/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_empty_files")
        with self.assertRaises(exceptions.MutationEmptyFilesException):
            mutation.validate()

    def test_unmentioned_files(self):
        #open the yaml file
        with open("tests/nastifiles/mutation_unmentioned_files/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_unmentioned_files")
        unmentioned_files = mutation.find_unmentioned_files("tests/nastifiles/mutation_unmentioned_files")
        assert unmentioned_files == ['files/nested/unmentioned', 'files/unmentioned']

    # this tests that the files array is not present
    def test_no_files(self):
        #open the yaml file
        with open("tests/nastifiles/mutation_no_files/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        with self.assertRaises(exceptions.MutationRequiredKeysMissingException):
            Mutation(mutation_config, "tests/nastifiles/mutation_no_files/")

    # this tests that the files array is present but the files are not on disk
    def test_files_dont_exist(self):
        #open the yaml file
        with open("tests/nastifiles/mutation_files_dont_exist/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_files_dont_exist", os, open)
        with self.assertRaises(exceptions.MutationFileDoesNotExistException):
            mutation.validate()
    
    def test_too_many_tries(self):
        input_dep = func = lambda x: "bogus input"
        print_dep = func = lambda x: None
        #open the yaml file
        with open("tests/nastifiles/valid/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_too_many_tries", os, open, input_dep, print_dep)
        with self.assertRaises(exceptions.MutationTooManyInputTriesException):
            mutation.run()
    
    def test_misconfigured_validation(self):
        #open the yaml file
        with open("tests/nastifiles/mutation_misconfigured_validation/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        # Validations raise multiple exceptions
        # We only test for an exception here
        # The validation tests cover all of the various kinds of failures
        with self.assertRaises(Exception):
            Mutation(mutation_config, "tests/nastifiles/mutation_misconfigured_validation")

    def test_mutation_with_missing_required_config(self):
        mutation_config = {
            "prompt": "test prompt",
        }
        with self.assertRaises(exceptions.MutationRequiredKeysMissingException):
            Mutation(mutation_config, "")

    def test_file_doesnt_contain_replacement_text(self):
        input_dep = func = lambda x: "bogus_slug"
        print_dep = func = lambda x: None
        #open the yaml file
        with open("tests/nastifiles/mutation_file_doesnt_contain_replacement_text/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_file_doesnt_contain_replacement_text", os, open, input_dep, print_dep)
        with self.assertRaises(exceptions.MutationFileDoesNotContainReplacementStringException):
            mutation.validate()
    
    def test_text_replacement_fails(self):
        input_dep = func = lambda x: "bogus_slug"
        print_dep = func = lambda x: None
        #open the yaml file
        with open("tests/nastifiles/mutation_text_replacement_fails/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_text_replacement_fails", os, mocks.mock_failed_open, input_dep, print_dep)
        with self.assertRaises(exceptions.MutationTextReplacementFailedException):
            mutation.run()

    def test_run(self):
        input_dep = func = lambda x: "bogus_slug"
        print_dep = func = lambda x: None
        #create the text file we'll use to replace stuff in
        with open("tests/nastifiles/mutation_run/test.txt", "w") as f:
            f.write("just replace_me please")
        #open the yaml file
        with open("tests/nastifiles/mutation_run/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_run", os, open, input_dep, print_dep)
        mutation.run()
        #open the file we replaced stuff in
        with open("tests/nastifiles/mutation_run/test.txt", "r") as f:
            file_contents = f.read()
        assert file_contents == "just bogus_slug please"
        #delete the file we replaced stuff in
        os.remove("tests/nastifiles/mutation_run/test.txt")

    def test_mutation_default_and_globals_simple(self):
        input_dep = func = lambda x: "bogus_slug"
        print_dep = func = lambda x: None
        #open the yaml file
        with open("tests/nastifiles/mutation_default_and_globals_simple/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation_config["globals"] = {config["globals"][0]["name"]: "Test App"}
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_default_and_globals_simple", os, open, input_dep, print_dep)
        default_value = mutation.render_default_template()
        assert default_value == "Test App"

    def test_mutation_default_and_globals_complex(self):
        input_dep = func = lambda x: "bogus_slug"
        print_dep = func = lambda x: None
        #open the yaml file
        with open("tests/nastifiles/mutation_default_and_globals_complex/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation_config["globals"] = {config["globals"][0]["name"]: "Test App"}
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_default_and_globals_complex", os, open, input_dep, print_dep)
        default_value = mutation.render_default_template()
        assert default_value == "test_app"

    def test_mutation_default_exception(self):
        input_dep = func = lambda x: "bogus_slug"
        print_dep = func = lambda x: None
        #open the yaml file
        with open("tests/nastifiles/mutation_default_exception/nasti.yaml", "r") as f:
            config = yaml.safe_load(f)
        mutation_config = config["mutations"][0]
        mutation_config["globals"] = {config["globals"][0]["name"]: "Test App"}
        mutation = Mutation(mutation_config, "tests/nastifiles/mutation_default_exception", os, open, input_dep, print_dep)
        with self.assertRaises(exceptions.MutationDefaultTemplateInvalidException):
            mutation.render_default_template()