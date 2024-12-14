"""
Author: Taylor B. tayjaybabee@gmail.com
Date: 2024-12-13 19:56:40
LastEditors: Taylor B. tayjaybabee@gmail.com
LastEditTime: 2024-12-13 19:57:24
FilePath: docs/conf.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../nepyc'))


project = 'nePyc'
copyright = '2024, Inspyre Softworks'
author = 'Inspyre Softworks'
release = '1.0.0-dev+6'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage',
    'sphinx_rtd_theme',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'autoclasstoc',
]

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_default_options = {
    'members': True,
    'special-members': False,
    'undoc-members': True,
    'inherited-members': True,
    'exclude-members': '__weakref__',
    'private-members': True,

}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_private_members = True
napoleon_include_init_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_param = False
napoleon_preprocess_types = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
