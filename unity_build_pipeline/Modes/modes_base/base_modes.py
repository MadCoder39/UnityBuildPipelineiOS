class BaseParser:
    _parser_name = ''

    @property
    def parser_name(self) -> str:
        if self._parser_name:
            return self._parser_name
        raise NotImplementedError(f"{self.__class__.__name__}: parser_name not set")

    def run(self, kwargs):
        raise NotImplementedError

class ParserNode(BaseParser):
    _children_name = ''
    _children_classes = []
    extra_parser_args = {}
    extra_subparser_args = {}

    def __init__(self):
        self._children_parsers = {cls._parser_name: cls() for cls in self._children_classes}


    def run(self, kwargs):
        mode_name = kwargs.get(self.children_name, None)
        if mode_name:
            target_parser = self._children_parsers.get(mode_name, None)
            if target_parser:
                target_parser.run(kwargs)

    @property
    def children_name(self):
        if self._children_name:
            return self._children_name
        raise NotImplementedError("submodes key name not set")


    def configure_arg_parser(self, parent_subparsers):
        parser = self.add_as_subparser(parent_subparsers)
        sub = self.make_sub(parser)
        self.configure_children(sub)
        return parser

    def add_as_subparser(self, parent_sub):
        return parent_sub.add_parser(**dict(
            name=self.parser_name,
            **self.get_extra_parser_args()
        ))

    def make_sub(self, parser):
        return parser.add_subparsers(**dict(
            dest=self._children_name,
            **self.get_extra_subparser_args()
        ))

    def configure_children(self, subparsers):
        for child in self._children_parsers.values():
            child.configure_arg_parser(subparsers)

    def get_extra_subparser_args(self):
        return self.extra_subparser_args

    def get_extra_parser_args(self):
        return self.extra_parser_args

class ParserEndpoint(BaseParser):
    def configure_arg_parser(self, parent_subparsers):
        return parent_subparsers.add_parser(self.parser_name)

    def run(self, kwargs):
        raise NotImplementedError