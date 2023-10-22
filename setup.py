# coding: utf-8
import re
from parver import Version, ParseError
import setuptools

# Use the following command from a terminal window to generate the whl with source code
# python setup.py bdist_wheel


namespace = 'seeq.*'

with open("README.md", "r") as fh:
    long_description = fh.read()

version_scope = {'__builtins__': None}
with open("seeq/addons/plot_digitizer/_version.py", "r+") as f:
    version_file = f.read()
    version_line = re.search(r"__version__ = (.*)", version_file)
    if version_line is None:
        raise ValueError(f"Invalid version. Expected __version__ = 'xx.xx.xx', but got \n{version_file}")
    version = version_line.group(1).replace(" ", "").strip('\n').strip("'").strip('"')
    print(f"version: {version}")
    try:
        Version.parse(version)
        exec(version_line.group(0), version_scope)
    except ParseError as e:
        print(str(e))
        raise

setup_args = dict(
    name='seeq-plot-digitizer',
    version=version_scope['__version__'],
    author="Eric Parsonnet",
    author_email="e.parsonnet@berkeley.edu",
    license='Apache License 2.0',
    platforms=["Linux", "Windows"],
    description="Plot digitization in Seeq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seeq12/seeq-plot-digitizer",
    packages=setuptools.find_namespace_packages(include=[namespace]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'bokeh>=3.3.0',
        'imageio>=2.19.3',
        'numpy>=1.26.1',
        'pandas>=2.1.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

setuptools.setup(**setup_args)