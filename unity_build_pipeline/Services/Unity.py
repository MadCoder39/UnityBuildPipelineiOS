import glob
import os
import re
from unity_build_pipeline.Support.logger import color_print, YELLOW
from unity_build_pipeline.Support.fileutils import search_recursive
from unity_build_pipeline.Support.shell import run, question


class Unity:
    MAC_UNITY_APP = 'Unity.app'
    MAC_EXECUTABLE_RELATIVE_PATH = '/Contents/MacOS/Unity'
    MAC_EXECUTABLE_NAME = '/' + MAC_UNITY_APP
    MAC_PLAYBACK_ENGINES_PATH = '/PlaybackEngines'
    PROJECT_VERSION_PATH = '/ProjectSettings/ProjectVersion.txt'
    MAC_UNITY_SEARCH_DIRS = [
        '/Applications/Unity/Hub/Editor/', '/Applications/Unity'
    ]

    @staticmethod
    def get_available_executables():
        executables = []
        for x in Unity.MAC_UNITY_SEARCH_DIRS:
            results = search_recursive(x, Unity.MAC_UNITY_APP)
            for res in results:
                executables.append(Unity(res.split('/').pop(), res))
        return executables

    @staticmethod
    def detect_version(project_path):
        with open(project_path + Unity.PROJECT_VERSION_PATH, 'r') as f:
            version = re.match(re.compile(".*(\d\d\d\d\.\d+\.\d+[a-z]+\d+).*"), f.read()).group(1)
            color_print("Detected Unity version %s" % version)
            unity_exec = None
            for executable in Unity.get_available_executables():
                if version == executable.version:
                    color_print("Unity executable found in %s" % executable.path)
                    return executable
            if unity_exec is None:
                color_print("Couldn't find Unity executable for version %s" % version, YELLOW)
                path = question(
                    "Please, provide path to Unity %s executable" % version,
                    example="/Applications/Unity/2018.2.20f1",
                    check_answer=lambda p: os.path.exists(p + Unity.MAC_EXECUTABLE_RELATIVE_PATH),
                    incorrect_answer=lambda p: "Unity path %s is invalid" % p
                )
                if path.endswith("/Unity.app"):
                    path = path.replace("/Unity.app", "")
                unity_exec = Unity(version, path)
            return unity_exec

    def __init__(self, version, path):
        self.version = version
        self.path = path.rstrip('/')

    def is_build_type_supported(self, build_type):
        map = {
            'xcode': 'iossupport'
        }
        for path in glob.glob(self.path + Unity.MAC_PLAYBACK_ENGINES_PATH + '/*Support'):
            if map[build_type] in path.lower():
                return True
        return False

    def execute(self, pwd, args):
        exit_code = run(
            [self.path + Unity.MAC_EXECUTABLE_NAME + Unity.MAC_EXECUTABLE_RELATIVE_PATH, '-projectPath', pwd] + args,
            cwd=pwd
        )
        return exit_code == 0
