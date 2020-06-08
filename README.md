# Github Project URL:
[https://github.com/MadCoder39/UnityBuildPipelineiOS]("https://github.com/MadCoder39/UnityBuildPipelineiOS")

# PyPI Project URL: 
[https://pypi.org/project/UnityBuildPipeline/](https://pypi.org/project/UnityBuildPipeline/)

# Description
A command-line application that will help you building Unity builds for iOS.
Drink coffee, relax, and let this little yet mighty app do everything for you. 

# Requirements
1. Python 3.x Installation can be checked by command "python3 --version"
2. YAML `pip3 install pyyaml`
3. Ruby & Bundler. Ruby is pre-installed on Macs by default. Bundler can be installed using `gem install bundler` command
4. Fastlane. It's recommended to install it using homebrew, but doesn't really matter. Instructions here: [https://docs.fastlane.tools/](https://docs.fastlane.tools/)


# Setup/Update
```
pip3 install --upgrade UnityBuildPipeline
```
# Uninstall
```
pip3 uninstall UnityBuildPipeline
```

## Runall command 
This command is taking care of everything, while you can sit back and enjoy your ☕ 
It has lots of arguments because it combines all other commands. Most of them are optional. 

Best way to use it is `pipeline runall beta`, where 'beta' is passed to fastlane command.
One command to run them all...
```
pipeline runall -h
usage: pipeline runall [-h] [-f] [--allow-debugging] [--dev] [options [options ...]]

positional arguments:
  options            fastlane options

optional arguments:
  -h, --help         show this help message and exit
  -f, --force
  --allow-debugging  Export with AllowDebugging option
  --dev              Export development project
```

## Init command 
Command is required in order to prepare the Unity project to be used by UnityBuildPipeline

```
pipeline init -h
usage: pipeline init [-h] [-f]

optional arguments:
  -h, --help    show this help message and exit
  -f, --force
```

## Clean command
Clears the project folder from pipeline's output folders and files
```
pipeline clean -h
usage: pipeline clean [-h]

optional arguments:
  -h, --help  show this help message and exit
```

## Export command
Command is doing the exporting procedure (from Unity to Xcode)
```
pipeline export -h
usage: pipeline export [-h] [--allow-debugging] [--dev]

optional arguments:
  -h, --help         show this help message and exit
  --allow-debugging  Export with AllowDebugging option
  --dev              Export development project
```

#### Replace Strategy
1. Project back-up
2. Exporting new project with BuildOptions.None
3. Migrating the config file from the back-up to the new project
4. Copying Fastlane pipeline from the back-up to the new project

#### Append Strategy
1. Project back-up
2. Exporting project with BuildOptions.AcceptExternalModificationsToPlayer

## Fastlane command
Command launches fastlane
```
pipeline fastlane -h
usage: pipeline fastlane [-h] [options [options ...]]

positional arguments:
  options     fastlane options
```
Here `options` will be added to the end of launch command
For example: `pipeline fastlane x y z` will launch `fastlane x y z` in Xcode project

## Run command
Command for running user-made custom commands. It's needed if you have some very specific needs for your project. In most of cases you won't need to use it.

After the project initialization, file `.unity_build_pipeline/config.yml` is being created in the root folder. 
There is `commands: {}` section, where custom commands could be added


For example: 
```yaml
commands:
  my-cool-command: "echo 1"
  my-second-cool-command: "open https://google.com"
```
There are 2 commands defined in this example. Running `pipeline run my-cool-command` will output 1 in console. `pipeline run my-cool-command` will open Google main page. 

It's also possible to define more useful commands:
```yaml
commands:
  run-fastlane-with-kek:
    command: fastlane kek {0}
    cwd: '{xcode_build_path_absolute}'
```
This is a command for launching fastlane. 
Launching `pipeline run run-fastlane-with-kek build` will execute `fastlane kek build`
As we can see, command `run` can accept additional arguments.
There are 2 types of arguments:
 1) arguments, that can be added via console. Instead of markers `{0}`, `{1}`, `{2}` etc, the corresponding parameters from the console will be passed.
 2) Named arguments. This is a hard-coded list of arguments
 ```python
{
     'cwd': os.getcwd(), # absolute path to current directory
     'unity_version': project.unity.version, # Current unity version in project
     'unity_path': project.unity.path, # path to unity
     'project_path': project.path, # path to project
     'xcode_build_path': project.get_export_path(Project.BUILD_TYPE_XCODE, absolute=False), # relative path to xcode build
     'xcode_build_path_absolute': project.get_export_path(Project.BUILD_TYPE_XCODE, absolute=True) # absolute path to xcode build
 }
```
 
# Recommendations
1) Running such command will help avoiding retyping your credentials every time
`fastlane fastlane-credentials add --username <your email>`
2) Also this command will help to avoid retyping `export FASTLANE_USER=<your appleID>`
3) In case during archive build Xcode throws error such as: "Please provide an auth token with USYM_UPLOAD_AUTH_TOKEN environment variable". It happens when using Unity Services in your game. Try using this command `export USYM_UPLOAD_AUTH_TOKEN="whatever"`
4) First build requires some configuration, after that things will be automated given that the recommendations are followed.

Good luck :)


# License
MIT