#!/usr/bin/env python
#
# $Id$
#
#  Atocha -- A web forms rendering and handling Python library.
#  Copyright (C) 2005  Martin Blais
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""
Time and Date Fields
"""

# stdlib imports
import re, datetime, locale
from types import NoneType

# atocha imports.
from atocha import AtochaInternalError
from atocha.field import Field, FieldError
from atocha.messages import msg_registry
from texts import StringField


__all__ = ['DateField', 'JSDateField',]


#-------------------------------------------------------------------------------
#
class DateField(StringField):
    """
    A string field that accepts strings that represent dates, in some specific
    formats.
    """
    types_data = (NoneType, datetime.date,)
    types_parse = (NoneType, unicode,)
    types_render = (unicode,)
    css_class = 'date'

    attributes_delete = ('strip', 'minlen', 'maxlen')


    __def_display_format = '%a, %d %B %Y' # or '%x'

    # Support ISO-8601 format.  
    __date_re1 = re.compile('(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)')

    # Support a natural format, like 11 Sep 2001, or Sep 11, 2001
    __date_re2 = re.compile('(?P<day>\d+)\s+(?P<nmonth>\w+)\s+(?P<year>\d+)')
    __date_re3 = re.compile('(?P<nmonth>\w+)\s+(?P<day>\d+)[\s,]+(?P<year>\d+)')

    # Pre-fetch lists of constants for month locale lookups.
    _mon_list = [getattr(locale, 'MON_%d' % x) for x in xrange(1, 13)]
    _abmon_list = [getattr(locale, 'ABMON_%d' % x) for x in xrange(1, 13)]

    def __init__( self, name, label=None, **attribs ):
        DateField.validate_attributes(attribs)

        attribs.setdefault('size', 20)
        attribs['strip'] = True
        StringField.__init__(self, name, label, **attribs)

    def parse_value( self, pvalue ):
        value = StringField.parse_value(self, pvalue)
        assert isinstance(value, unicode)
        
        # Indicate that this field has not been sent.
        if not value:
            return None

        # Check formats.
        for fre in self.__date_re1, self.__date_re2, self.__date_re3:
            mo = fre.match(value)
            if mo:
                break
        else:
            raise FieldError(msg_registry['date-invalid-format'] % value, value)

        year, day = map(int, mo.group('year', 'day'))
        try:
            month = int(mo.group('month'))
        except IndexError, e:
            # Get abbreviated and full month names.
            enc = locale.getpreferredencoding()
            abmons = [locale.nl_langinfo(x).decode(enc)
                      for x in self._abmon_list]
            mons = [locale.nl_langinfo(x).decode(enc)
                    for x in self._mon_list]

            nmonth = mo.group('nmonth')

            try:
                month = abmons.index(nmonth.capitalize()) + 1
            except ValueError, e:
                try:
                    month = mons.index(nmonth.capitalize()) + 1
                except ValueError, e:
                    raise FieldError(
                        msg_registry['date-invalid-month'] % nmonth, value)

        assert type(month) is int
            
        # Convert into date.
        try:
            dvalue = datetime.date(year, month, day)
        except ValueError, e:
            raise FieldError(msg_registry['date-invalid'] % value,
                             value)

        return dvalue

    def render_value( self, dvalue ):
        if dvalue is None:
            return u''

        # Convert the date object in a format suitable for rendering it.
        rvalue = dvalue.isoformat().decode('ascii')
        return rvalue

    def display_value( self, dvalue ):
        if dvalue is None:
            return u''
        return DateField._time_to_string(dvalue)

    def _time_to_string( date ):
        """
        Convert a date object to a unicode string.  We need this because
        strftime has calendar limitations on years before 1900.
        """
        if date.year < 1900:
            # Use simplistic format for old dates.
            return u'%d-%d-%d' % (date.year, date.month, date.day)
        else:
            # Note: what encoding does the time module return the format in?
            # i.e. We never use the default encoding in this library.
            return date.strftime(DateField.__def_display_format).decode(
                locale.getpreferredencoding())
    _time_to_string = staticmethod(_time_to_string)


#-------------------------------------------------------------------------------
#
class JSDateField(Field): # Is always required.
    """
    A fancy Javascript-based date field.

    This is an adaptation for this form handling library of a nice
    Javascript-based date input field found at http://www.jasonmoon.net/.  The
    conditions of utilisation of that code is that a notice should be present
    and kept intact somewhere in the comments.
    """
    types_data = (datetime.date,)
    types_parse = (NoneType, unicode,)
    types_render = (unicode,)
    css_class = 'jsdate'

    # Public data used for adding the script reference to the head.
    scripts = (('calendarDateInput.js',
               u"""Jason's Date Input Calendar- By Jason Moon
               http://www.jasonmoon.net/ Script featured on and available at
               http://www.dynamicdrive.com Keep this notice intact for use.
               """),)

    __date_re = re.compile('(\d\d\d\d)(\d\d)(\d\d)')

    __script_re = '^[a-zA-Z_]+$'

    def __init__( self, name, label=None, **attribs ):
        JSDateField.validate_attributes(attribs)

        # Note: there is a special constraint on the varname of the field due to
        # the Javascript code involved (see below).  This verification is
        # required for the JS calendar.
        assert re.match(JSDateField.__script_re, name)

        Field.__init__(self, name, label, attribs)

    def parse_value( self, pvalue ):
        if pvalue is None:
            # No value submitted... this is strange, since this field should
            # always send us a value, always, even without user edits. Raise a
            # strange user error.
            raise FieldError(msg_registry['date-invalid'] % u'')

        # Encode value into ascii.
        try:
            dvalue = pvalue.encode('ascii')
        except UnicodeEncodeError:
            # This should not happen if the value comes from the code.
            raise AtochaInternalError(
                "Error: internal error with input from JSDateField.")

        # Match the given string, it should always match.
        mo = JSDateField.__date_re.match(dvalue)
        if mo is None:
            raise AtochaInternalError(
                "Error: internal error with input from JSDateField.")

        # Convert into date.
        try:
            dvalue = datetime.date(*map(int, mo.groups()))
        except ValueError, e:
            raise FieldError(msg_registry['date-invalid'] % pvalue)

        return dvalue

    def render_value( self, dvalue ):
        if dvalue is None:
            return u''

        # Convert the date object in a format suitable for being accepted by the
        # Javascript code. Note: this may not work before 1900.
        rvalue = dvalue.strftime('%Y%m%d')
        return rvalue.decode('ascii')

    def display_value( self, dvalue ):
        assert dvalue is not None
        return DateField._time_to_string(dvalue)

