import os
from unity_build_pipeline.Services.Project import Project
from unity_build_pipeline.Support.logger import color_print, YELLOW, GREEN, RED
from unity_build_pipeline.Support.shell import question_yes_no


def init_project(project_path, kwargs):
    from ..pipeline_modes.InitMode import InitMode
    kwargs.update({'project_path': project_path})
    InitMode(kwargs).start()

class BaseCommand:
    op_name = None

    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.project_path = os.getcwd().rstrip('/')

    def start(self):
        self._log_running(self.get_operation_name())
        self.run()

    def get_operation_name(self):
        return self.op_name or self.__class__.__name__

    def _log_running(self, operation_name):
        color_print(f'### Running {operation_name} ###', GREEN)

    def run(self):
        pass


class InitedCommand(BaseCommand):
    def start(self):
        if not self.check_inited():
            color_print("Canceled: isn't initialized.", color=RED)
            return
        super().start()

    def check_inited(self):
        if not Project.is_initialized(self.project_path):
            if question_yes_no("Project is not initialized. Initialize it now?", color=YELLOW):
                init_project(self.project_path, self.kwargs)
            else:
                return False
        return True
