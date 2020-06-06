from unity_build_pipeline.Modes.modes_base.base_modes import ParserEndpoint, ParserNode
from unity_build_pipeline.Modes.modes_base.command import InitedCommand, BaseCommand
from unity_build_pipeline.Modes.pipeline_modes.InitMode import InitMode


class CommandA(InitedCommand):  # inited: like base but checks if project is inited
    def run(self):
        print(*self.kwargs)


class CommandB(BaseCommand):
    def run(self):
        print("test", self.kwargs.get("testArgs", {}))


class CommandAB(BaseCommand):
    def run(self):
        kwargs = self.kwargs
        CommandA(kwargs).start()
        CommandB(kwargs).start()


class AEndpoint(ParserEndpoint):  # endpoint is a "leaf" of command parsing
    _parser_name = 'A'

    def run(self, kwargs):
        CommandA(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Run A command')
        return parser


class BEndpoint(ParserEndpoint):
    _parser_name = 'B'

    def run(self, kwargs):
        CommandB(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Run B command')
        parser.add_argument('honkyArgs', nargs='*',
                            help='args to be flowed to B command')
        return parser


class ABEndpoint(ParserEndpoint):
    _parser_name = 'AB'

    def run(self, kwargs):
        InitMode(kwargs).start()
        CommandAB(kwargs).start()
        # CommandA(kwargs).start()
        # CommandB(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Run both A and B commands')
        parser.add_argument('honkyArgs', nargs='*',
                            help='args to be flowed to B command')
        return parser


class NestedExampleNode(ParserNode):  # node is a
    _parser_name = 'neEx2'
    # required for a node, shouldn't be repeated in children. Can be any string
    _children_name = 'nested_example_modes2'
    # list of nodes/endpoints accessed from this node
    _children_classes = [AEndpoint, BEndpoint, ABEndpoint]
    extra_parser_args = dict(help="Nested example command node")
    # ˆ additional kwargs for parent's subparsers.add_parser()
    # See https://docs.python.org/3/library/argparse.html#sub-commands

    def run(self, kwargs):
        print("/-- Nested step run --/")  # additional stuff
        super().run(kwargs)  # node's super() delegates job to children if they're called


class ExampleNode(ParserNode):
    _parser_name = 'neEx'
    _children_name = 'nested_example_modes'
    _children_classes = [NestedExampleNode, BEndpoint]
    extra_subparser_args = dict(required=True)
    extra_parser_args = dict(help="Root-node for examples")

# exampleNode is added to Root class'' _children_classes
# Root is ParserNode too but a bit trickier (to be actually "root")
