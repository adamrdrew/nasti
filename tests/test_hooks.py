import unittest
from nasti.hooks import Hooks
import nasti.exceptions as exceptions
import os

class TestHooks(unittest.TestCase):

    def test_null_hooks(self):
        hooks = Hooks({})
        self.assertEqual(hooks.before, False)
        self.assertEqual(hooks.after, False)
        self.assertEqual(hooks.auto_cleanup, False)
        self.assertEqual(hooks.run_before(), False)
        self.assertEqual(hooks.run_before(), False)
    
    def test_hooks_before_with_no_cleanup(self):
        script = "tests/hooks/success.sh"
        hooks = Hooks({
            "before_script": script,
        })
        self.assertEqual(hooks.before, script)
        self.assertEqual(hooks.after, False)
        self.assertEqual(hooks.auto_cleanup, False)
        self.assertEqual(hooks.run_before(), True)
    
    def test_hooks_after_with_no_cleanup(self):
        script = "tests/hooks/success.sh"
        hooks = Hooks({
            "after_script": script,
        })
        self.assertEqual(hooks.before, False)
        self.assertEqual(hooks.after, script)
        self.assertEqual(hooks.auto_cleanup, False)
        self.assertEqual(hooks.run_after(), True)
    
    def test_hooks_before_nonzero_exit(self):
        script = "tests/hooks/fail.sh"
        hooks = Hooks({
            "before_script": script,
        })
        self.assertEqual(hooks.before, script)
        self.assertEqual(hooks.after, False)
        self.assertEqual(hooks.auto_cleanup, False)
        with self.assertRaises(exceptions.HooksScriptExecutionFailed):
            hooks.run_before()
    
    def test_hooks_after_nonzero_exit(self):
        script = "tests/hooks/fail.sh"
        hooks = Hooks({
            "after_script": script,
        })
        self.assertEqual(hooks.before, False)
        self.assertEqual(hooks.after, script)
        self.assertEqual(hooks.auto_cleanup, False)
        with self.assertRaises(exceptions.HooksScriptExecutionFailed):
            hooks.run_after()

    def test_hooks_before_script_doesnt_exist(self):
        script = "tests/hooks/doesntexist.sh"
        hooks = Hooks({
            "before_script": script,
        })
        self.assertEqual(hooks.before, script)
        self.assertEqual(hooks.after, False)
        self.assertEqual(hooks.auto_cleanup, False)
        with self.assertRaises(exceptions.HooksScriptNotFound):
            hooks.run_before()
    
    def test_hooks_after_script_doesnt_exist(self):
        script = "tests/hooks/doesntexist.sh"
        hooks = Hooks({
            "after_script": script,
        })
        self.assertEqual(hooks.before, False)
        self.assertEqual(hooks.after, script)
        self.assertEqual(hooks.auto_cleanup, False)
        with self.assertRaises(exceptions.HooksScriptNotFound):
            hooks.run_after()
    
    def test_hooks_before_script_with_cleanup(self):
        # create a copy of the success script
        os.system("cp tests/hooks/success.sh tests/hooks/success_copy.sh")

        script = "tests/hooks/success_copy.sh"
        hooks = Hooks({
            "before_script": script,
            "auto_cleanup": True
        })
        self.assertEqual(hooks.before, script)
        self.assertEqual(hooks.after, False)
        self.assertEqual(hooks.auto_cleanup, True)
        self.assertEqual(hooks.run_before(), True)

        # verify the script was cleaned up
        self.assertEqual(os.path.exists(script), False)
    
    def test_hooks_after_script_with_cleanup(self):
        # create a copy of the success script
        os.system("cp tests/hooks/success.sh tests/hooks/success_copy.sh")

        script = "tests/hooks/success_copy.sh"
        hooks = Hooks({
            "after_script": script,
            "auto_cleanup": True
        })
        self.assertEqual(hooks.before, False)
        self.assertEqual(hooks.after, script)
        self.assertEqual(hooks.auto_cleanup, True)
        self.assertEqual(hooks.run_after(), True)

        # verify the script was cleaned up
        self.assertEqual(os.path.exists(script), False)
    
    def test_hooks_before_script_with_cleanup_failure(self):
        script = "popo.sh"
        hooks = Hooks({
            "before_script": script,
            "auto_cleanup": True
        })
        self.assertEqual(hooks.before, script)
        self.assertEqual(hooks.after, False)
        self.assertEqual(hooks.auto_cleanup, True)

        with self.assertRaises(exceptions.HooksCleanupFailed):
            hooks.cleanup(script)

    def test_hooks_script_execute_os_error(self):
        script = "tests/hooks/no_executable"
        hooks = Hooks({
            "before_script": script,
        })
        self.assertEqual(hooks.before, script)
        self.assertEqual(hooks.after, False)
        self.assertEqual(hooks.auto_cleanup, False)
        with self.assertRaises(exceptions.HooksScriptExecutionFailed):
            hooks.run_before()
