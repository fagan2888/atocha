#!/usr/bin/env python

"""
Install script for the Atocha web forms library.
"""

__author__ = "Martin Blais <blais@furius.ca>"

import sys
from distutils.core import setup

def read_version():
    try:
        return open('VERSION', 'r').readline().strip()
    except IOError, e:
        raise SystemExit(
            "Error: you must run setup from the root directory (%s)" % str(e))

# Include all files without having to create MANIFEST.in
def add_all_files(fun):
    import os, os.path
    from os.path import abspath, dirname, join
    def f(self):
        for root, dirs, files in os.walk('.'):
            if '.hg' in dirs: dirs.remove('.hg')
            self.filelist.extend(join(root[2:], fn) for fn in files
                                 if not fn.endswith('.pyc'))
        return fun(self)
    return f
from distutils.command.sdist import sdist
sdist.add_defaults = add_all_files(sdist.add_defaults)


setup(name="atocha",
      version=read_version(),
      description=\
      "A web forms handling and rendering library.",
      long_description="""
Atocha is a Python library for rendering web forms and parsing submitted data.
It is framework-agnostic, generic, and it should be possible to use it even with
CGI scrips or to incorporate it in your favourite web application framework
""",
      license="GPL",
      author="Martin Blais",
      author_email="blais@furius.ca",
      url="http://furius.ca/atocha",
      download_url="http://github.com/blais/atocha",
      package_dir = {'': 'lib/python'},
      packages = ['atocha',
                  'atocha.fields',
                  'atocha.renderers',
                  'atocha.norms'],
     )
