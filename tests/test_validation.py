from nasti.validation import Validation
import unittest
import nasti.exceptions as exceptions

class TestValidation(unittest.TestCase):
    def test_valid_regex(self):
        validation = Validation({
            "regex": r'^[A-Za-z\s]+$',
        })
        assert validation.validate("Welcome To The Machine") == True

    def test_invalid_regex(self):
        validation = Validation({
            "regex": r'^[A-Za-z\s]+$',
        })
        assert validation.validate("867-5309") == False
    
    def test_missing_config(self):
        with self.assertRaises(exceptions.ValidationConfigMissingException):
            validation = Validation({
                "invalid": "invalid",
            })

    def test_invalid_config(self):
        with self.assertRaises(exceptions.ValidationConfigInvalidException):
            validation = Validation({
                "regex": r'^[A-Za-z\s]+$',
                "kind": "slug"
            })

    def test_valid_kind(self):
        validation = Validation({
            "kind": "slug",
        })
        assert validation.validate("coheed_and_cambria") == True
    
    def test_invalid_kind(self):
        validation = Validation({
            "kind": "slug",
        })
        assert validation.validate("Tonight, the south is on fire!") == False
    
    def test_unknown_kind(self):
        with self.assertRaises(exceptions.ValidationUnknownKindException):
            validation = Validation({
                "kind": "ire_works",
            })