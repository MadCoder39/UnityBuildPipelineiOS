from unity_build_pipeline.Support.logger import color_print, GREEN
from unity_build_pipeline.Support.shell import run
from unity_build_pipeline.Support.fileutils import replace_string_entries


class Fastlane:
    def __init__(self, project):
        self.project = project

    def execute(self, args):
        project_path = self.project.get_export_path('xcode')
        self.ensure_install(project_path)
        color_print("Starting fastlane..", GREEN)
        run(['bundle', 'exec', 'fastlane'] + args, cwd=project_path)

    def ensure_install(self, path):
        color_print("Updating fastlane..", GREEN)
        run(['rm', '-rf', path + '/fastlane'], path)
        run(['rm', '-f', path + '/Gemfile'], path)
        run(['cp', '-R', self.project.get_stubs_folder() +
             '/Fastlane/fastlane', path + '/fastlane'], path)

        replace_string_entries(path + '/fastlane/Fastfile',
                               "options[:username]", "'"+self.project.username+"'")

        replace_string_entries(path + '/fastlane/Fastfile',
                               "options[:teamid]", "'" + self.project.teamID + "'")

        replace_string_entries(path + '/fastlane/Fastfile',
                               "options[:appid]", "'" + self.project.bundleID + "'")

        replace_string_entries(path + '/fastlane/Appfile',
                               "username", self.project.username)

        replace_string_entries(path + '/fastlane/Appfile',
                               "appid", self.project.bundleID)

        replace_string_entries(path + '/fastlane/Appfile',
                               "teamid", self.project.teamID)

        run(['cp', '-R', self.project.get_stubs_folder() +
             '/Fastlane/Gemfile', path + '/Gemfile'], path)
        run(['bundle', 'update'], cwd=path, silent=True)
        pbx_project_path = path + '/Unity-iPhone.xcodeproj/project.pbxproj'

        content = open(pbx_project_path, 'r').read()
        if 'VERSIONING_SYSTEM = "apple-generic"' not in content:
            color_print("Patching versioning system..", GREEN)
            content = self.patch_pbx(content)
            open(pbx_project_path, 'w').write(content)

    def patch_pbx(self, content):
        pbx = content.split("\n")
        new_pbx = []
        for i, line in enumerate(pbx):
            new_pbx.append(line)
            if "COPY_PHASE_STRIP" in line:
                new_pbx.append('				CURRENT_PROJECT_VERSION = 0.1;')
            if "UNITY_SCRIPTING_BACKEND" in line:
                new_pbx.append('				VERSIONING_SYSTEM = "apple-generic";')
        return "\n".join(new_pbx)
