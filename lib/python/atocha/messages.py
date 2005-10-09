#!/usr/bin/env python
#
# $Id$
#

"""
Message strings for form library.

We group here all the human readable strings that are used in the form library,
so that there is a single place for i18n and for changing them.  The strings are
meant to be translated at the time of rendering only.



FIXME: not sure about the following... how about the type checking then?  N_()
returns a str, not a unicode...

  Any active translation will be carried out by the renderer code only, all
  other strings are meant to be identifiers that get translated later.


, and we don't perform the translation ourselves, except in the renderer, where
a translator object is clearly passed or assumed to have been set at a global
builtin (as _() and N_(), which is standard naming for gettext applications).
"""


# stdlib imports.
import __builtin__


__all__ = ['msg_registry']


# Set default values for translators, if not already set in builtin.  We will
# expect those translation functions to be available globally via the
# __builtin__ dictionary, which is a bit of a kludge, but makes writing i18n
# programs so much easier.  We will also expect these functions to change
# possibly everytime a request is made, as a result of setup for a specific user
# session.
#
# If they're not set, we will set them to noop functions here, so that at least
# we can run the tests outside the environment and so that this library still
# works even if the app is not i18n'ed.
if not hasattr(__builtin__, '_'):
    __builtin__._ = lambda x: unicode(x)
if not hasattr(__builtin__, 'N_'):
    __builtin__.N_ = lambda x: x

# The type of the messages returned by N_().  This is used to check the type of
# the user displayable strings when they're given to our library.  At that point
# they have not yet become translated, so they may be unicode or str.
msg_type = str


class TranslatorDict(dict):
    """
    A dictionary class that automatically translates on access.
    """
    def __getitem__( self, key ):
        """
        Automatically translate the key.
        """
        return _(dict.__getitem__(self, key))

    def get_notrans( self, key ):
        return dict.__getitem__(self, key)
    
# Message registry: the single place where we store all forms of human-readable
# strings that you may want to customize for your application.
msg_registry = TranslatorDict({
    # String that goes on the submit button by default.
    'submit-button': N_('Submit'),
  
    # Some error message strings that can be returned by the parse routine.
    'error-invalid-encoding':
        N_('Browser error: Invalid chars in expected encoding.'),

    # Error when a value is missing.
    'error-required-value': N_('Missing value required.'),

    # Generic UI message for errors.
    'generic-ui-message': N_("Please fix errors below."),

    # Generic error message for a value that has a parse error.
    'generic-value-error': N_("Invalid value."),

    #
    # Field-specific error messages.
    #
    
    'text-invalid-chars': N_("Invalid characters in string."),
    'text-minlen': N_("String too short."),
    'text-maxlen': N_("String too long."),

    'email-invalid': N_("Invalid email address."),
    'email-error-local': N_("Please specify a full email address."),

    'numerical-invalid': N_("Invalid number."),
    'numerical-minval': N_("Value too small.  Minimum value is '%s'."),
    'numerical-maxval': N_("Value too large.  Maximum value is '%s'."),

    'one-choice-required': N_("Please select at least one of the choices."),

    'date-invalid-format':
    N_("Invalid format for date: '%s'. Use YYYY-MM-DD format."),
    'date-invalid': N_("Invalid date: '%s'."),

    })
