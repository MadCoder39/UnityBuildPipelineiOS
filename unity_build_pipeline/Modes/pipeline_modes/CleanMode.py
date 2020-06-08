import time

from unity_build_pipeline.Modes.modes_base.base_modes import ParserEndpoint
from unity_build_pipeline.Modes.modes_base.command import InitedCommand
from unity_build_pipeline.Services.Project import Project
from unity_build_pipeline.Support.logger import color_print, WHITE
from unity_build_pipeline.Support.shell import run
from unity_build_pipeline.Support.fileutils import get_parent_dir

class CleanCommand(InitedCommand):
    def run(self):
        kwargs = self.kwargs
        project = Project(self.project_path)
        builds_path = get_parent_dir(project.get_export_path())
        pip_path = project.get_config_folder(self.project_path)
        run(['rm', '-rf', builds_path])
        run(['rm', '-rf', pip_path])
        color_print("Pipeline files and Builds were removed", WHITE)

class CleanEndpoint(ParserEndpoint):
    _parser_name = 'clean'

    def run(self, kwargs):
        CleanCommand(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Clean project from pipeline files and builds')
        return parser

