import os
from os.path import join
from string import Template

import yaml

from unity_build_pipeline.Support.fileutils import remove, copy, makedirs, search_recursive
from unity_build_pipeline.Support.logger import color_print, YELLOW, GREEN
from .Unity import Unity


class Project:
    BUILD_TYPE_XCODE = 'xcode'

    XCODE_PROJECT_NAME = 'Unity-iPhone.xcodeproj'

    def __init__(self, path, load=True):
        self.path = path
        self.unity = None
        self.backups_enabled = True
        self.build = {}
        self.commands = {}
        self.username = ""
        self.bundleID = ""
        self.teamID = ""
        if load:
            self.load()

    @staticmethod
    def is_initialized(path):
        return os.path.exists(Project.get_pipeline_path(path))

    @staticmethod
    def get_pipeline_path(path):
        return Project.get_config_folder(path) + '/config.yml'

    @staticmethod
    def get_config_folder(path):
        return path + '/.unity_build_pipeline'

    def get_stubs_folder(self):
        return self.get_config_folder(self.path) + '/stubs'

    @staticmethod
    def factory(project_path, unity, xcode_project_path, use_backups, username, bundle_id, team_id):
        project = Project(project_path, load=False)
        project.unity = unity
        project.build = {
            Project.BUILD_TYPE_XCODE: {
                'path': xcode_project_path,
            }
        }
        project.backups_enabled = use_backups
        project.username = username
        project.bundleID = bundle_id
        project.teamID = team_id
        project.commands = {}
        return project

    def load(self):
        config = yaml.safe_load(
            open(Project.get_pipeline_path(self.path), 'r').read())
        self.unity = Unity(config['unity']['version'], config['unity']['path'])
        self.build = {
            Project.BUILD_TYPE_XCODE: config['xcode_build']
        }
        self.backups_enabled = config['backups']
        self.commands = config['commands']
        self.username = config['username']
        self.bundleID = config['bundleID']
        self.teamID = config['teamID']

    def save(self):
        if Project.is_initialized(self.path):
            config = yaml.safe_load(
                open(Project.get_pipeline_path(self.path), 'r').read())
        else:
            makedirs(self.get_config_folder(self.path))
            config = {}
        config.update({
            'unity': {
                'version': self.unity.version,
                'path': self.unity.path,
            },
            'backups': self.backups_enabled,
            'xcode_build': {
                'path': self.get_export_path(Project.BUILD_TYPE_XCODE, absolute=False),
            },
            'commands': self.commands,
            'username': self.username,
            'bundleID': self.bundleID,
            'teamID': self.teamID
        })
        open(Project.get_pipeline_path(self.path), 'w').write(
            yaml.dump(config, default_flow_style=False))

    def drop(self):
        config_folder = Project.get_pipeline_path(self.path)
        remove(config_folder)

    def backup(self, build_type, suffix=':backup'):
        if not self.backups_enabled:
            return
        backup_path = self.get_export_path(build_type) + suffix
        if os.path.exists(self.get_export_path(build_type)):
            copy(self.get_export_path(build_type), backup_path)
            color_print("Project has been backed up in %s" %
                        backup_path, GREEN)
            return backup_path

    def restore_from_backup(self, build_type, remove_backup=True, suffix=':backup'):
        if not self.backups_enabled:
            return
        export_path = self.get_export_path(build_type)
        backup_path = export_path + suffix
        if os.path.exists(backup_path):
            remove(export_path)
            copy(backup_path, export_path)
            if remove_backup:
                remove(backup_path)
            color_print("Project has been restored from backup", GREEN)

    def get_export_path(self, build_type=BUILD_TYPE_XCODE, absolute=True):
        rel_part = self.build[build_type]['path']
        if absolute:
            return join(self.path, rel_part)
        return rel_part
        # return (self.path + '/' if absolute else '') + self.build[build_type]['path']

    def is_exported_project_valid(self, build_type):
        return os.path.exists(self.get_export_path(build_type) + '/' + Project.XCODE_PROJECT_NAME)

    def detect_exported_project(self, build_type):
        if build_type == Project.BUILD_TYPE_XCODE:
            return search_recursive(self.path, Project.XCODE_PROJECT_NAME)

    def export(self, allow_debugging, is_development, is_append_build=False, build_type=BUILD_TYPE_XCODE):
        success = False
        try:
            if not self.unity.is_build_type_supported(build_type):
                raise Exception("%s build is not supported by %s version of Unity" % (
                    build_type, self.unity.version))
            color_print('Exporting %s project..' % build_type)
            export_path = self.get_export_path(build_type)
            log_file = export_path + '/export.log'
            command = self._generate_export_command(
                allow_debugging, is_development, build_type, is_append_build)
            if command:
                color_print(
                    "Please, be patient. You can follow log here %s\n" % log_file, YELLOW)
                success = self.unity.execute(
                    self.path,
                    ["-batchmode", "-quit", "-executeMethod",
                        command, "-logFile", log_file]
                )
                if success:
                    color_print(
                        "Project has been successfully exported!", GREEN)
                else:
                    raise Exception(
                        "Unity export failed! Check logs here: %s" % log_file)
        finally:
            self._cleanup(build_type)
        return success

    def _generate_export_command(self, allow_debugging, is_development, build_type, is_append_build=False):
        if build_type == Project.BUILD_TYPE_XCODE:
            color_print('Writing export tool file..')
            makedirs(self.path + '/Assets/Editor/')
            with open(self.get_config_folder(self.path) + '/stubs/Unity/IOSExportTool.cs.stub', 'r') as stub_file:
                stub = Template(stub_file.read())
                stub = stub.substitute(
                    allowDebugging=('true' if allow_debugging else 'false'),
                    isDevelopment=('true' if is_development else 'false'),
                    buildOptions=(
                        'BuildOptions.None' if not is_append_build else 'BuildOptions.AcceptExternalModificationsToPlayer'),
                    buildPath=self.get_export_path(Project.BUILD_TYPE_XCODE)
                )
                with open(self.path + '/Assets/Editor/IOSExportTool.cs', 'w') as export_tool_file:
                    export_tool_file.write(stub)
                    return 'IOSExportTool.ExportXcodeProject'
        raise Exception("Exporting %s project is not supported" % build_type)

    def _cleanup(self, build_type):
        if build_type == Project.BUILD_TYPE_XCODE:
            path = self.path + '/Assets/Editor/IOSExportTool.cs'
            remove(path)
