import time

from unity_build_pipeline.Modes.modes_base.base_modes import ParserEndpoint, ParserNode
from unity_build_pipeline.Modes.modes_base.command import InitedCommand, BaseCommand
from unity_build_pipeline.Modes.pipeline_modes.InitMode import InitMode
from unity_build_pipeline.Modes.pipeline_modes.ExportMode import ExportMode
from unity_build_pipeline.Modes.pipeline_modes.FastlaneMode import FastlaneMode
from unity_build_pipeline.Support.logger import color_print, WHITE

class RapidCommand(BaseCommand):
    def run(self):
        kwargs = self.kwargs
        start_time = time.time()
        
        InitMode(kwargs).start()
        ExportMode(kwargs).start()
        FastlaneMode(kwargs).start()

        elapsed_min = str(round((time.time() - start_time)/60))
        color_print("Pipeline just saved you " + elapsed_min + " min", WHITE)

class RapidEndpoint(ParserEndpoint):
    _parser_name = 'runall'

    def run(self, kwargs):
        RapidCommand(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Run All Commands')
        parser.add_argument('-f', '--force', action='store_true')
        parser.add_argument('options', nargs='*', help='fastlane options')
        parser.add_argument('--allow-debugging', action='store_true',
                            help='Export with AllowDebugging option')
        parser.add_argument('--dev', action='store_true',
                            help='Export development project')
        return parser

