#!/usr/bin/env python
#
# $Id$
#

"""
CGI forwarder script for query.
"""

# stdlib imports
import sys, cgi, cgitb; cgitb.enable()
sys.path.append('..')
from demo import handler_reset

handler_reset()
