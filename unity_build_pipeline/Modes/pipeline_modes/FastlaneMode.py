from unity_build_pipeline.Modes.modes_base.command import InitedCommand
from unity_build_pipeline.Modes.modes_base.base_modes import ParserEndpoint
from unity_build_pipeline.Services.Fastlane import Fastlane
from unity_build_pipeline.Services.Project import Project


class FastlaneMode(InitedCommand):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.options = kwargs.get('options', list())

    def run(self):
        project = Project(self.project_path)
        fastlane = Fastlane(project)
        fastlane.execute(self.options)


class FastlaneEndpoint(ParserEndpoint):
    _parser_name = 'fastlane'

    def run(self, kwargs):
        FastlaneMode(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Make project')
        parser.add_argument('options', nargs='*', help='fastlane options')
        return parser
