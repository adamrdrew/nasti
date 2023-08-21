import nasti.exceptions as exceptions
import os

class Hooks:
    BEFORE_KEY = "before_script"
    AFTER_KEY = "after_script"
    AUTO_CLEANUP_KEY = "auto_cleanup"
    OS_DEP_KEY = "os_dep"
    WORKING_DIR_KEY = "working_dir"

    before = False
    after = False
    auto_cleanup = False
    os_dep = os
    cleanup_command = "rm "

    def __init__(self, opts):
        self.working_dir = os.getcwd()
        if self.BEFORE_KEY in opts:
            self.before = opts[self.BEFORE_KEY]
        if self.AFTER_KEY in opts:
            self.after = opts[self.AFTER_KEY]
        if self.AUTO_CLEANUP_KEY in opts:
            self.auto_cleanup = opts[self.AUTO_CLEANUP_KEY]
        if self.OS_DEP_KEY in opts:
            self.os_dep = opts[self.OS_DEP_KEY]
        if self.WORKING_DIR_KEY in opts:
            self.working_dir = opts[self.WORKING_DIR_KEY]

    def __run_script(self, script):
        # Verify the script exists
        full_path_for_script = self.os_dep.path.join(self.working_dir, script)
        if not self.os_dep.path.exists(full_path_for_script):
            raise exceptions.HooksScriptNotFound(f"Hooks script not found: {full_path_for_script}")
        try:
            result = self.os_dep.system(f"sh {full_path_for_script} > /dev/null 2>&1")
        except Exception as e:
            raise exceptions.HooksScriptExecutionFailed(f"Hooks script failed: {e}")
        if result != 0:
            raise exceptions.HooksScriptExecutionFailed("Hooks script failed.")

    def cleanup(self, script):
        if self.auto_cleanup == False:
            return
        try:
            full_path_for_script = self.os_dep.path.join(self.working_dir, script)
            result = self.os_dep.system(f"{self.cleanup_command} {full_path_for_script} > /dev/null 2>&1")
        except Exception as e:
            raise exceptions.HooksCleanupFailed(f"Hooks cleanup failed: {e}")
        if result != 0:
            raise exceptions.HooksCleanupFailed("Hooks cleanup failed.")

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