import unittest
from nasti.source_handlers import SourceHandlerResolver, GitHandler, LocalDirectoryHandler, HelpHandler
import tests.mocks as mocks
import nasti.exceptions as exceptions

class TestSourceHandlerResolver(unittest.TestCase):
    def test_resolve_dir_handler(self):
        mock_os = mocks.MockOs()
        resolver = SourceHandlerResolver("this_charming_man", "there is a light that never goes out", mock_os, mocks.mock_print)
        handler = resolver.resolve()
        assert isinstance(handler, LocalDirectoryHandler)

    def test_resolve_git_handler(self):
        mock_os = mocks.MockOs()
        resolver = SourceHandlerResolver("git@test.com/test/test.git", "help text", mock_os, mocks.mock_print)
        handler = resolver.resolve()
        assert isinstance(handler, GitHandler)
    
    def test_resolve_help_handler(self):
        mock_os = mocks.MockOs()
        resolver = SourceHandlerResolver(None, "We all go up in flames, going out in style", mock_os, mocks.mock_print)
        handler = resolver.resolve()
        assert isinstance(handler, HelpHandler)

class TestGitHandler(unittest.TestCase):
    def test_run(self):
        handler = GitHandler("git@test.com/test/test.git", mocks.MockOs())
        handler.run()
    
    def test_run_no_git(self):
        handler = GitHandler("git@test.com/test/test.git", mocks.MockOs({"system": 1}))
        with self.assertRaises(exceptions.GitHandlerGitMissingException):
            handler.validate_git()
    
    def test_run_create_tmp_dir_fails(self):
        handler = GitHandler(
            "git@test.ci/test/test.git", 
            mocks.MockOs({
                "mkdir": False, 
                "isdir": False
            })
        )
        with self.assertRaises(exceptions.GitHandlerTmpDirCreationException):
            handler.run()
    
    def test_run_clone_fails(self):
        handler = GitHandler(
            "git@test.com/test/test.git",
            mocks.MockOs({
                "system": 1
            })
        )
        with self.assertRaises(exceptions.GitHandlerCloneException):
            handler.clone_repo()

class TestLocalDirectoryHandler(unittest.TestCase):
    def test_run(self):
        handler = LocalDirectoryHandler("tests/mocks/test_dir", mocks.MockOs())
        handler.run()
    
    def test_run_no_dir(self):
        handler = LocalDirectoryHandler("tests/mocks/this_dir_does_not_exist", mocks.MockOs(
            {"isdir": False}
        ))
        with self.assertRaises(exceptions.LocalDirHandlerSourceNotDirException):
            handler.run()

# There is no test for HelpHandler because it is just a byzantine print statement.