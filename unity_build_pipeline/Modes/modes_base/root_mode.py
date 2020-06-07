import argparse

from unity_build_pipeline.Modes.pipeline_modes.RapidMode import RapidEndpoint
from unity_build_pipeline.Modes.pipeline_modes.ExportMode import ExportEndpoint
from unity_build_pipeline.Modes.pipeline_modes.FastlaneMode import FastlaneEndpoint
from unity_build_pipeline.Modes.pipeline_modes.InitMode import InitEndpoint
from unity_build_pipeline.Modes.modes_base.base_modes import ParserNode
from unity_build_pipeline.Modes.pipeline_modes.RunMode import RunModeEndpoint


class Root(ParserNode):
    _parser_name = 'Pipeline'
    _children_name = 'pipeline_mode'
    extra_subparser_args = dict(required=True)
    _children_classes = [
        InitEndpoint,
        ExportEndpoint,
        FastlaneEndpoint,
        RunModeEndpoint,
        RapidEndpoint
    ]

    def __init__(self):
        super().__init__()
        self.parser = self.make_parser()

    def parse(self):
        return self.parser.parse_args().__dict__

    def make_parser(self):
        parser = argparse.ArgumentParser()
        sub = self.make_sub(parser)
        self.configure_children(sub)
        return parser
