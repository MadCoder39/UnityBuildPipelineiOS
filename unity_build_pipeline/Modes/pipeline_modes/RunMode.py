import os

import yaml

from unity_build_pipeline.Modes.modes_base.command import InitedCommand
from unity_build_pipeline.Modes.modes_base.base_modes import ParserEndpoint
from unity_build_pipeline.Services.Project import Project
from unity_build_pipeline.Support.logger import color_print, RED
from unity_build_pipeline.Support.shell import run


class RunMode(InitedCommand):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.command = kwargs['command']
        self.options = kwargs['options']

    def run(self):
        project = Project(self.project_path)

        if self.command in ['list', 'ls']:
            print(yaml.dump(project.commands, default_flow_style=False))
            return

        if self.command not in project.commands:
            color_print("Command %s is not defined for this project" % self.command, RED)

        cmd = project.commands[self.command]
        if isinstance(cmd, str):
            shell_cmd = self._format(project, cmd)
            cwd = os.getcwd()
            run(shell_cmd.split(" "), cwd)
        else:
            commands = [cmd['command']] if isinstance(cmd['command'], str) else cmd['command']
            for command in commands:
                shell_cmd = self._format(project, command)
                cwd = self._format(project, cmd['cwd']) if 'cwd' in cmd else os.getcwd()
                run(shell_cmd.split(" "), os.path.abspath(os.path.expanduser(cwd)))

    def _format(self, project, string):
        vars = {
            'cwd': os.getcwd(),
            'unity_version': project.unity.version,
            'unity_path': project.unity.path,
            'project_path': project.path,
            'xcode_build_path': project.get_export_path(Project.BUILD_TYPE_XCODE, absolute=False),
            'xcode_build_path_absolute': project.get_export_path(Project.BUILD_TYPE_XCODE, absolute=True)
        }
        try:
            return string.format(*tuple(self.options), **vars)
        except IndexError as e:
            color_print("Cannot format \"%s\" string from command. Missing some options" % string, RED)
            exit(0)

class RunModeEndpoint(ParserEndpoint):
    _parser_name = 'run'

    def run(self, kwargs):
        RunMode(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Run command')
        parser.add_argument('command', help='command to execute')
        parser.add_argument('options', nargs='*')
        return parser
