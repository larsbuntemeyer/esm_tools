#!/usr/bin/env python
#
# esm_tools documentation build configuration file, created by
# sphinx-quickstart on Fri Jun  9 13:47:02 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))




# PG: Here, we grab the main yaml for each model stated in configs, and get a metadata chapter:
import yaml
config_blacklist = ["batch_system", "machines", "vcs", "esm_master", "esm_runscripts", "general_yaml"]
configs = [f for f in os.listdir(os.path.abspath("../configs")) if f not in config_blacklist]
components = {}
for component in ["../configs/components/"+c for c in os.listdir("../configs/components")]:
    d = yaml.load(component, Loader=yaml.FullLoader)
    comp_name = component.split("/")[-1].replace(".yaml", "")
    components[comp_name] = d
configs = []
for comp in components:
    if os.path.exists("../configs/components/"+comp+"/"+comp+".yaml"):
        configs.append(comp)
with open("Supported_Models.rst", "w") as rst:
    rst.write("================\n")
    rst.write("Supported Models\n")
    rst.write("================\n")
configs.sort()
for config in configs:
    with open(os.path.join("../configs/components/", config, config+".yaml")) as f:
        d = yaml.load(f, Loader=yaml.FullLoader)
        metadata = d.get("metadata")
        with open("metadata/"+config+".csv", "w") as table:
            if metadata:
                for key in metadata:
                    if key=="Publications":
                        if type(metadata[key]) is list:
                            public_string = key + '; "\n'
                            for publication in metadata[key]:
                                public_string = public_string + "`{0}`_\n\n".format(publication.replace('"', '""'))
                            table.write(public_string+'"\n')
                        else:
                            table.write("%s; `%s`_\n" % (key, metadata[key]))
                    else:
                        table.write("%s; %s\n" % (key, metadata[key]))
        with open("Supported_Models.rst", "a") as rst:
            rst.write("%s\n" % config.upper())
            rst.write("-"*len(config) + "\n")
            rst.write(".. csv-table::\n")
            rst.write("   :file: %s\n" % ("metadata/"+config+".csv"))
            rst.write("   :delim: ;\n")
            rst.write("   :widths: 20, 80\n")
            rst.write("   :stub-columns: 1\n\n")

# -- Unified API of subpackages ----------------------------------------

# TODO: If this could come directly from github, that'd be nice...

import subprocess
import shutil
import sphinx.ext.apidoc

esm_tools_modules = [
 "esm_archiving",
 "esm_calendar",
 "esm_database",
 "esm_environment",
 "esm_master",
 "esm_parser",
 "esm_profile",
 "esm_rcfile",
 "esm_runscripts",
 "esm_tools",
 "esm_version_checker",
]
esm_tools_modules.remove("esm_tools")
# Creating a docs/.docstrings.yml file allows you to control the compilation of
# the docstrings. Fill this file with ``docstrings: 0`` if you want to avoid
# docstring's compilation, or ``docstrings: 1`` if you want to compile the
# docstrings. If the file does not exists it always compiles the docstrings.
if os.path.isfile(".docstrings.yml"):
    with open(".docstrings.yml") as docstrings_yaml:
         docstrings_dict = yaml.load(docstrings_yaml, Loader=yaml.FullLoader)
    if docstrings_dict.get('docstrings')==0:
        esm_tools_modules = []

# Ensure the API folder exists:
try:
 os.makedirs("api")
except FileExistsError:
 shutil.rmtree("api")
 os.makedirs("api")
try:
 os.makedirs("tmp_clone")
except FileExistsError:
 shutil.rmtree("tmp_clone")
 os.makedirs("tmp_clone")

ESM_TOOLS_PROJECT_ADDRESS = "https://github.com/esm-tools/"

mods_to_skip = []

branches = {}
if os.path.isfile(".api_branches.yml"):
    with open(".api_branches.yml") as branch_yaml:
        branches = yaml.load(branch_yaml, Loader=yaml.FullLoader)

with open("API.rst", "w") as rst:
 rst.write("============================\n")
 rst.write("ESM Tools Code Documentation\n")
 rst.write("============================\n")
 rst.write(".. toctree::\n")
 rst.write("   :glob:\n\n")
 rst.write("   api/*")

 for esm_mod in sorted(esm_tools_modules):
     branch = branches.get(esm_mod, "")
     if branch:
         branch = "-b "+branch+" "
     # Clone:
     subprocess.call(
         "git clone "
         + branch
         + ESM_TOOLS_PROJECT_ADDRESS
         + esm_mod
         + " tmp_clone/"
         + esm_mod,
         shell=True,
     )
     # Run apidoc. Need the name twice to go into the actual part where the code is
     sphinx.ext.apidoc.main(
         [
             "--no-toc",
             "--module-first",
             "--output-dir",
             "api",
             "tmp_clone/" + esm_mod + "/" + esm_mod,
         ]
     )
     # rst.write(esm_mod+"\n")
     # rst.write("-"*len(esm_mod)+"\n")
     # rst.write("\n")
     # rst.write()
     # Skip a few hings for testing:
     if esm_mod in mods_to_skip:
         continue

     # Ensure that importing works correctly when running apidoc
     subprocess.check_call(
         [
             sys.executable,
             "-m",
             "pip",
             "install",
             "--no-warn-script-location",
             # "--user",
             "tmp_clone/" + esm_mod,
         ]
     )
     # sys.path.append(os.path.abspath("tmp_clone/" + esm_mod))
shutil.rmtree("tmp_clone")


# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
# MA: for some reason sphinxcontrib.napoleon does not work on ollie so
# the working module sphinx.ext.napoleon is used when compiled from ollie.
if os.getcwd().split('/')[2]=="ollie":
    extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode',
        'sphinx.ext.autosectionlabel', 'sphinx.ext.napoleon', 'sphinx_copybutton', 'sphinx_tabs.tabs' 'sphinx.ext.graphviz']
else:
    extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode',
        'sphinx.ext.autosectionlabel', 'sphinxcontrib.napoleon', 'sphinx_copybutton', 'sphinx_tabs.tabs', 'sphinx.ext.graphviz']

napoleon_custom_sections = ["User Information", "Programmer Information"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'ESM Tools'
copyright = "2020, Dirk Barbi"
author = "Dirk Barbi, Nadine Wieters, Paul Gierz, Fatemeh Chegini, Miguel Andrés-Martínez"
version = "4.0"
# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
#version = esm_tools.__version__
# The full version, including alpha/beta/rc tags.
#release = esm_tools.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "style_nav_header_background": "white",
    "logo_only": True,
    "prev_next_buttons_location": "both",
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_logo = "_static/ESM-TOOLS_LOGO_RGB_72dpi.jpg"

# Add custom css (to disable the horizontal scrolling in tables).
def setup(app):
    app.add_stylesheet('custom.css')

# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'esm_toolsdoc'


# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'esm_tools.tex',
     'ESM Tools r4 UserManual',
     'Dirk Barbi, Nadine Wieters, Paul Gierz, \\\\Fatemeh Chegini, Miguel Andrés-Martínez',
     'manual'),
]


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'esm_tools',
     'ESM Tools Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'esm_tools',
     'ESM Tools Documentation',
     author,
     'esm_tools',
     'One line description of project.',
     'Miscellaneous'),
]


# -- Options for labelling ---------------------------------------------

# This allows referencing different sections of the document by using
# :ref:`rst_file_name:title of the section` avoiding problems with
# duplicated sections across different rst files.
autosectionlabel_prefix_document = True



