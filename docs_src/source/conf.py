# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import re
from parver import Version, ParseError

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = 'seeq-plot-digitizer'
copyright = '2022, Eric Parsonnet'
author = 'Eric Parsonnet'

version_scope = {'__builtins__': None}
with open("../../seeq/addons/plot_digitizer/_version.py", "r+") as f:
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

# The full version, including alpha/beta/rc tags
version = version_scope['__version__']
release = version_scope['__version__']

# -- General configuration ---------------------------------------------------
source_suffix = ['.rst', '.md']
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.githubpages',
    'sphinx.ext.viewcode',
    'myst_parser'
]
extensions.append('sphinx.ext.mathjax')

napoleon_google_docstring = False
napoleon_numpy_docstring = True

# Enable numref
numfig = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'sphinxdoc'
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', '_usecases', '_userguide']

html_favicon = '_static/seeq-favicon.ico'

html_logo = '_static/Seeq_logo_darkPurple_sm.png'
# html_logo = '_static/Seeq_logo_white_sm.png'

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/custom.css',
]

# This will completely replace the theme stylesheet
# html_style = 'css/yourtheme.css'

html_theme_options = {
    'style_external_links': True,
    'style_nav_header_background': '#e3e3e3',
}

# Enable References
myst_heading_anchors = 2

# Enable Latex style Figure referencing
myst_enable_extensions = ["colon_fence"]

# Remove View page source
html_show_sourcelink = False