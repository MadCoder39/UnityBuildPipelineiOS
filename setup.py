import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="UnityBuildPipeline",
    version="0.0.4",
    author="MadCoder",
    author_email="madcoder39@gmail.com",
    description="Unity build pipeline for iOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MadCoder39/UnityBuildPipelineiOS",
    packages=setuptools.find_packages(),
    install_requires=required,
    scripts=['pipeline'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
)
