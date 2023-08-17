import nasti.exceptions as exceptions
import os

class Hooks:
    BEFORE_KEY = "before_script"
    AFTER_KEY = "after_script"
    AUTO_CLEANUP_KEY = "auto_cleanup"
    OS_DEP_KEY = "os_dep"

    before = False
    after = False
    auto_cleanup = False
    os_dep = os
    cleanup_command = "rm "

    def __init__(self, opts):
        if self.BEFORE_KEY in opts:
            self.before = opts[self.BEFORE_KEY]
        if self.AFTER_KEY in opts:
            self.after = opts[self.AFTER_KEY]
        if self.AUTO_CLEANUP_KEY in opts:
            self.auto_cleanup = opts[self.AUTO_CLEANUP_KEY]
        if self.OS_DEP_KEY in opts:
            self.os_dep = opts[self.OS_DEP_KEY]

    def __run_script(self, script):
        # Verify the script exists
        if not self.os_dep.path.exists(script):
            raise exceptions.HooksScriptNotFound()
        try:
            result = self.os_dep.system(f"sh {script} > /dev/null 2>&1")
        except Exception as e:
            raise exceptions.HooksScriptExecutionFailed(e)
        if result != 0:
            raise exceptions.HooksScriptExecutionFailed()

    def cleanup(self, script):
        if self.auto_cleanup == False:
            return
        try:
            result = self.os_dep.system(f"{self.cleanup_command} {script} > /dev/null 2>&1")
        except Exception as e:
            raise exceptions.HooksCleanupFailed(e)
        if result != 0:
            raise exceptions.HooksCleanupFailed()

    def __run_hook(self, hook):
        if hook == False:
            return hook
        self.__run_script(hook)
        self.cleanup(hook)
        return True

    def run_before(self):
        return self.__run_hook(self.before)

    def run_after(self):
        return self.__run_hook(self.after)