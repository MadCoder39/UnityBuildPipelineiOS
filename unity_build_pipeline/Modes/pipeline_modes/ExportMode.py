import os
import time
from os.path import exists, join

from unity_build_pipeline.Modes.modes_base.command import InitedCommand
from unity_build_pipeline.Modes.modes_base.base_modes import ParserEndpoint
from unity_build_pipeline.Services.Project import Project
from unity_build_pipeline.Services.Unity import Unity
from unity_build_pipeline.Support.fileutils import remove, copy, makedirs
from unity_build_pipeline.Support.logger import color_print, GREEN, YELLOW
import plistlib as plist

migrate_fields = [
    'CFBundleIdentifier',
    'CFBundleName',
    'CFBundleDisplayName'
]


def get_info_plist_path(root):
    return root + '/Info.plist'


class ExportMode(InitedCommand):
    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.export_params = {
            'allow_debugging': kwargs['allow_debugging'],
            'is_development': kwargs['dev'],
        }

    @staticmethod
    def configure_arg_parser(subparsers):
        parser = subparsers.add_parser('export', help='Export project')
        parser.add_argument('--allow-debugging', action='store_true', help='Export with AllowDebugging option')
        parser.add_argument('--dev', action='store_true', help='Export development project')
        return parser

    def run(self):
        project = Project(self.project_path)
        color_print("Exporting project", GREEN)
        detected_unity = Unity.detect_version(self.project_path)
        use_append_strategy = detected_unity.version == project.unity.version

        is_first_export = not os.path.exists(project.get_export_path(Project.BUILD_TYPE_XCODE))
        if is_first_export:
            color_print("No exported project detected. Performing clean export", YELLOW)
            return self._export(project, False)

        if not use_append_strategy:
            warning = "Detected Unity version difference was: {} now: {}" \
                .format(project.unity.version, detected_unity.version)
            color_print(warning, YELLOW)
            color_print("Using REPLACE strategy for project build")
        else:
            color_print("Using APPEND strategy for project build")
        self._export(project, use_append_strategy)

    def _get_meta_path(self, export_path):
        label = time.time()
        meta_files_path = join(export_path, f'_meta_{label}')
        return meta_files_path

    def _export(self, project, use_append_strategy):
        try:
            project.backup(build_type=Project.BUILD_TYPE_XCODE)
            export_path = project.get_export_path(Project.BUILD_TYPE_XCODE)
            meta_files_path = self._get_meta_path(export_path)

            self._backup_meta_files(export_path, meta_files_path)
            project.export(
                *self.export_params,
                build_type=Project.BUILD_TYPE_XCODE,
                is_append_build=use_append_strategy
            )
            if not use_append_strategy:
                self._migrate_plist(meta_files_path, export_path)
            remove(meta_files_path)
        except Exception as e:
            project.restore_from_backup(Project.BUILD_TYPE_XCODE)
            raise e

    def _backup_meta_files(self, src_root, dst_root):
        makedirs(dst_root)
        copy(src_root + '/Info.plist', dst_root)

    def _migrate_plist(self, src_root, dst_root):
        src_path = get_info_plist_path(src_root)
        dst_path = get_info_plist_path(dst_root)
        if not exists(src_root):
            return

        color_print("Settings migration..")

        src_plist = plist.load(open(src_path))
        dst_plist = plist.load(open(dst_path))

        self._replace_fields(src_plist, dst_plist, self._get_migrate_fields())
        plist.dump(dst_plist, open(dst_path, 'w'))

    def _replace_fields(self, plist_src, plist_dest, fields):
        for field_name in fields:
            plist_src[field_name] = plist_dest[field_name]

    def _get_migrate_fields(self):
        return migrate_fields

class ExportEndpoint(ParserEndpoint):
    _parser_name = 'export'
    extra_parser_args = dict()

    def run(self, kwargs):
        ExportMode(kwargs).start()

    def configure_arg_parser(self, parent_subparsers):
        parser = parent_subparsers.add_parser(
            name=self.parser_name, help='Export project')
        parser.add_argument('--allow-debugging', action='store_true', help='Export with AllowDebugging option')
        parser.add_argument('--dev', action='store_true', help='Export development project')
        return parser