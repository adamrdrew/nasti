import unittest
from nasti.globals import Global
import nasti.exceptions as exceptions

class TestGlobal(unittest.TestCase):
    def test_global_with_full_config(self):
        global_config = {
            "name": "test",
            "prompt": "test prompt",
            "help": "test help",
            "validation": {
                "regex": ".*"
            }
        }
        global_obj = Global(global_config, input_dep=input, print_dep=print)
        self.assertEqual(global_obj.name, "test")
    
    def test_global_with_required_config(self):
        global_config = {
            "name": "test",
            "prompt": "test prompt",
        }
        global_obj = Global(global_config, input_dep=input, print_dep=print)
        self.assertEqual(global_obj.name, "test")
    
    def test_global_with_missing_required_config(self):
        global_config = {
            "prompt": "test prompt",
        }
        with self.assertRaises(exceptions.GlobalRequiredKeysMissingException):
            Global(global_config, input_dep=input, print_dep=print)

    def test_global_with_misconfigured_validation(self):
        global_config = {
            "name": "test",
            "prompt": "test prompt",
            "validation": {
                "regex": ".*",
                "kind": "bogus"
            }
        }
        # Validations raise multiple exceptions
        # We only test for an exception here
        with self.assertRaises(Exception):
            Global(global_config, input_dep=input, print_dep=print)

    def test_global_with_too_many_tries(self):
        global_config = {
            "name": "test",
            "prompt": "test prompt",
            "validation": {
                "kind": "url"
            }
        }
        input_dep = func = lambda x: "bogus input"
        print_dep = func = lambda x: None
        global_obj = Global(global_config, input_dep=input_dep, print_dep=print_dep)
        with self.assertRaises(exceptions.GlobalTooManyInputTriesException):
            global_obj.populate()
    
    def test_global_with_validation(self):
        global_config = {
            "name": "test",
            "prompt": "test prompt",
            "validation": {
                "kind": "url"
            }
        }
        input_dep = func = lambda x: "http://www.google.com"
        print_dep = func = lambda x: None
        global_obj = Global(global_config, input_dep=input_dep, print_dep=print_dep)
        global_obj.populate()
        self.assertTrue(global_obj.validate())

    def test_global_with_validation_failure(self):
        global_config = {
            "name": "test",
            "prompt": "test prompt",
            "validation": {
                "kind": "url"
            }
        }
        input_dep = func = lambda x: "http://www.google.com"
        print_dep = func = lambda x: None
        global_obj = Global(global_config, input_dep=input_dep, print_dep=print_dep)
        global_obj.populate()
        global_obj.value = "bogus"
        self.assertFalse(global_obj.validate())