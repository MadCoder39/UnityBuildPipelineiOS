import os
import time
import re

from unity_build_pipeline.Modes.modes_base.command import BaseCommand
from unity_build_pipeline.Modes.modes_base.base_modes import ParserEndpoint
from unity_build_pipeline.Services.Project import Project
from unity_build_pipeline.Services.Unity import Unity
from unity_build_pipeline.Support.config import pipeline_source_path
from unity_build_pipeline.Support.fileutils import copy, search_recursive
from unity_build_pipeline.Support.logger import color_print, RED, YELLOW, GREEN
from unity_build_pipeline.Support.shell import question_yes_no, quiz, question
from unity_build_pipeline.Support.shell import run

pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"


def remove_prefix(string: str, prefix, count=1):
    if string.startswith(prefix):
        string = string.replace(prefix, '', count)
    return string


class InitMode(BaseCommand):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.forced = kwargs.get('force', False)

    def run(self):
        if not self._check_all():
            return

        unity = Unity.detect_version(self.project_path)
        xcode_project_path = self._detect_xcode_project_path()
        if not unity or not xcode_project_path:
            return color_print("Project cannot be initialized", RED)

        use_backups = question_yes_no("Enable exported project backups?")

        ptrn = re.compile(pattern)
        username = question(
            "Please, provide your appleID (email) for further usage by fastlane",
            example="kek@gmail.com",
            check_answer=lambda p: re.match(ptrn, p),
            incorrect_answer=lambda p: "Email p %s is invalid" % p
        )

        bundleID = question(
            "Please, provide your app bundle id for further usage by fastlane",
            example="com.default.test"
        )

        teamID = question(
            "Please, provide your apple team id for further usage by fastlane",
            example="7NS7GL82HF"
        )

        project = Project.factory(
            self.project_path, unity, xcode_project_path, use_backups, username, bundleID, teamID)
        project.save()
        try:
            self._copy_stubs(project)
            color_print("Project successfully initialized!")
        except Exception as e:
            project.drop()
            color_print("Project initialization fail", RED)
            raise e

    def _check_all(self):
        if not self._check_project_folder():
            color_print("Project path %s is not exist or not writable" %
                        self.project_path, RED)
            return False
        if not self._check_if_unity_project():
            color_print("No Unity project detected in %s" %
                        self.project_path, RED)
            return False
        if Project.is_initialized(self.project_path):
            if not self.forced:
                color_print(
                    "Project already initialized. Use --force flag to reinitialize", RED)
                return False
            else:
                color_print(
                    "Project already initialized, but you've used --force flag!", YELLOW)
                project = Project(self.project_path)
                file_name = f":backup_before_init_{time.time()}"
                project.backup(Project.BUILD_TYPE_XCODE, file_name)
        return True

    def _check_project_folder(self):
        is_dir = os.path.isdir(self.project_path)
        accessable = os.access(self.project_path, os.W_OK)
        return is_dir and accessable

    def _check_if_unity_project(self):
        unity_path = self.project_path + Unity.PROJECT_VERSION_PATH
        return os.path.exists(unity_path)

    def _copy_stubs(self, project):
        old_config_path = pipeline_source_path
        new_config_path = project.get_config_folder(self.project_path)
        copy(old_config_path + '/stubs',
             new_config_path + '/stubs')

    def _detect_xcode_project_path(self):
        color_print("Searching for previous Xcode project...", GREEN)
        results = search_recursive(
            self.project_path, Project.XCODE_PROJECT_NAME)

        if not self.forced and len(results) > 0:
            if len(results) > 1:
                directory = quiz(
                    "Found multiple Xcode projects, which project to use?", results)
            else:
                directory = results.pop()
        else:
            directory = question(
                "Please, provide target ios project directory in project root",
                default_answer="Builds/IOS"
            ).strip()

        directory = remove_prefix(directory, self.project_path).lstrip('/')
        return directory


class InitEndpoint(ParserEndpoint):
    _parser_name = 'init'

    def run(self, kwargs):
        InitMode(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Initialize project')
        parser.add_argument('-f', '--force', action='store_true')
        return parser
