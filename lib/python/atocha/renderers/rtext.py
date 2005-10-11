#!/usr/bin/env python
#
# $Id$
#

"""
Simple text-based form renderers.
"""

# stdlib imports.
import StringIO, codecs

# atocha imports.
from atocha.render import FormRenderer
from atocha.fields import ORI_VERTICAL, FileUploadField
from atocha.messages import msg_type


__all__ = ['TextFormRenderer', 'TextDisplayRenderer']


#-------------------------------------------------------------------------------
#
class TextRenderer(FormRenderer):
    """
    Base class for all renderers that will output to text.
    """    

    # Default encoding for output.
    default_encoding = None # Default: to unicode.

    # CSS classes.
    css_errors = u'formerror'
    css_table = u'formtable'
    css_label = u'formlabel'

    def __init__( self, *args, **kwds ):
        """
        Grab the encoding parameter on top of the basic form renderer
        construction parameters.
        """

        try:
            self.outenc = kwds['output_encoding']
            del kwds['output_encoding']
        except KeyError:
            self.outenc = self.default_encoding
        """Encoding for output strings produced by this renderer."""

        try:
            self.label_semicolon = kwds['labelsemi']
            del kwds['labelsemi']
        except KeyError:
            self.label_semicolon = False
        """Whether we automatically add a semicolon to the labels or not."""

        FormRenderer.__init__(self, *args, **kwds)


    def _create_buffer( self ):
        """
        Create the default file for output.
        """
        sio = StringIO.StringIO()
        if self.outenc is not None:
            Writer = codecs.getwriter(self.outenc)
            sio = Writer(sio)
        return sio

    def _get_label( self, field ):
        """
        Returns a printable label for the given field.
        """
        return (field.label and _(field.label)
                or unicode(field.name.capitalize()))

    def do_table( self, pairs=(), extra=None ):
        # Use side-effect for efficiency if requested.
        f = self.ofile or self._create_buffer()

        print >> f, u'<table class=%s>' % self.css_table
        for label, inputs in pairs:
            assert isinstance(label, unicode)
            assert isinstance(inputs, unicode)

            if self.label_semicolon:
                label += ':'
            print >> f, ((u'<tr><td class="%s">%s</td>\n'
                          u'    <td class="%s">%s</td></tr>') %
                         (self.css_label, label, self.css_input, inputs or u''))
        if extra:
            assert isinstance(extra, unicode)
            print >> f, extra
        print >> f, u'</table>'

        if self.ofile is None: return f.getvalue()

    def _geterror( self, errmsg ):
        if errmsg:
            assert isinstance(errmsg, unicode)
            return (u'<span class="%s">%s</span><br/>' %
                    (self.css_errors, errmsg))
        else:
            return u''



#-------------------------------------------------------------------------------
#
class TextFormRenderer(TextRenderer):
    """
    Form renderer that outputs HTML text directly.

    See FormRenderer class for full details.
    """

    # CSS classes.
    css_input = u'forminput'
    css_required = u'formreq'
    css_vertical = u'formminitable'

    _emptyin = u'<input name="%s" type="%s" value="%s" class="%s" />'
    _in = u'<input name="%s" type="%s" value="%s" class="%s">%s</input>'
    
    def do_render( self, fields, action, submit ):
        form = self._form
        try:
            # File object that gets set as a side-effect.
            self.ofile = f = self._create_buffer()

            # (Side-effect will add to the file.)
            self.do_render_container(action)

            # (Side-effect will add to the file.)
            self.do_render_table(fields)

            # Render submit buttons.
            self.do_render_submit(submit)

            # Close the form (the container rendering only outputs the header.
            print >> f, u'</form>'
        finally:
            self.ofile = None

        return f.getvalue()


    def do_render_container( self, action ):
        # Use side-effect for efficiency if requested.
        f = self.ofile or self._create_buffer()
        form = self._form

        if action is None:
            raise RuntimeError('Error: You must specify a non-null action '
                               'for rendering this form.')

        # Other options.
        opts = [('id', form.name),
                ('name', form.name),
                ('action', form.action),
                ('method', form.method),]
        if form.accept_charset is not None:
            opts.append(('accept-charset', form.accept_charset))
        if form.enctype is not None:
            opts.append(('enctype', form.enctype))

        print >> f, (u'<form %s>' % ' '.join(['%s="%s"' % x for x in opts]))

        if self.ofile is None: return f.getvalue()


    def do_render_table( self, fields ):
        # Use side-effect for efficiency if requested.
        f = self.ofile or self._create_buffer()

        hidden, visible = [], []
        for field in fields:
            rendered = self._render_field(field)
            if field.ishidden():
                hidden.append(rendered)
            else:
                label = self._get_label(field)
                if field.isrequired():
                    label += u'<span class="%s">*</a>' % self.css_required
                visible.append( (label, rendered) )
            
        self.do_table(visible, '\n'.join(hidden))

        if self.ofile is None: return f.getvalue()

    def do_render_submit( self, submit ):
        # Use side-effect for efficiency if requested.
        f = self.ofile or self._create_buffer()

        if isinstance(submit, msg_type):
            print >> f, (u'<input type="submit" value="%s" />' %
                         _(submit))
        else:
            assert isinstance(submit, (list, tuple))
            for value, name in submit:
                print >> f, \
                      (u'<input type="submit" name="%s" value="%s" />' %
                       (name, _(value)))

        if self.ofile is None: return f.getvalue()


    #---------------------------------------------------------------------------

    def renderHidden( self, field, rvalue ):
        inputs = []

        if isinstance(rvalue, unicode):
            inputs.append(u'<input name="%s" type="hidden" value="%s" />' %
                          (field.name, rvalue))
        elif isinstance(rvalue, list):
            for rval in rvalue:
                inputs.append(u'<input name="%s" type="hidden" value="%s" />' %
                              (field.name, rval))
        else:
            raise RuntimeError("Error: unexpected type '%s' for rendering." %
                               type(rvalue))

        return '\n'.join(inputs)


    def _input( self, htmltype, field, value, checked=False, label=None ):
        """
        Render an html input.
        """
        if checked:
            checkstr = u'checked="1"'
        else:
            checkstr = u''

        fargs = (field.name,
                 htmltype,
                 value or u'',
                 field.css_class,
                 checkstr)
        
        if label is not None:
            o = ((u'<input name="%s" type="%s" value="%s" '
                  u'class="%s" %s>%s</input>') % (fargs + (label,)))
        else:
            o = (u'<input name="%s" type="%s" value="%s" class="%s" %s/>' %
                 fargs)
        return o
            
    def _single( self, htmltype, field, value, errmsg,
                 checked=False, label=None ):
        """
        Render a single field.
        """
        return self._geterror(errmsg) + \
               self._input(htmltype, field, value, checked, label)

    def _orient( self, field, inputs ):
        """
        Place the given list of inputs in a small vertical table if necessary.
        """
        if field.orient is ORI_VERTICAL:
            s = StringIO.StringIO()
            s.write(u'<table class="%s">\n' % self.css_vertical)
            for i in inputs:
                s.write(u'<tr><td>%s</td></td>\n' % i)
            s.write(u'</table>\n')
            return s.getvalue()
        else:
            return u'\n'.join(inputs)
        
    def renderStringField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)

    def renderTextAreaField( self, field, rvalue, errmsg, required ):
        s = self._geterror(errmsg)
        rowstr = field.rows and u' rows="%d"' % field.rows or u''
        colstr = field.cols and u' cols="%d"' % field.cols or u''
        return (self._geterror(errmsg) +
                u'<textarea name="%s" %s %s class="%s">%s</textarea>' %
                (field.name, rowstr, colstr, field.css_class, rvalue or ''))

        return self._single('text', field, rvalue, errmsg)

    def renderPasswordField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)

    def renderDateField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)

    def renderEmailField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)

    def renderURLField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)

    def renderIntField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)

    def renderFloatField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)

    def renderBoolField( self, field, rvalue, errmsg, required ):
        # The render type calls for any value and for the rvalue to determine
        # whether this will get checked or not.
        return self._single('checkbox', field, u'1', errmsg, rvalue)

    def renderRadioField( self, field, rvalue, errmsg, required ):
        assert rvalue is not None
        inputs = []
        for vname, label in field.values:
            checked = bool(vname == rvalue)
            inputs.append(
                self._input('radio', field, vname, checked, _(label)))
        output = self._orient(field, inputs)
        return self._geterror(errmsg) + output

    def _renderMenu( self, field, rvalue, errmsg, required,
                     multiple=None, size=None ):
        "Render a SELECT menu. 'rvalue' is expected to be a list of values."

        selopts = []
        if size is not None and size > 1:
            selopts.append('size="%d"' % field.size)
        if multiple:
            selopts.append('multiple="1"')

        lines = []
        lines.append(
            u'<select name="%s" %s class="%s">' %
            (field.name, ' '.join(selopts), field.css_class))
        for vname, label in field.values:
            selstr = u''
            if vname in rvalue:
                selstr = u'selected="selected"'
            lines.append(u'<option value="%s" %s>%s</option>' %
                         (vname, selstr, _(label)))
        lines.append(u'</select>')
        return self._geterror(errmsg) + u'\n'.join(lines)

    def renderMenuField( self, field, rvalue, errmsg, required ):
        return self._renderMenu(field, [rvalue], errmsg, required)

    def renderCheckboxesField( self, field, rvalue, errmsg, required ):
        inputs = []
        for vname, label in field.values:
            checked = vname in rvalue
            inputs.append(self._input('checkbox', field, vname, checked, _(label)))
        output = self._orient(field, inputs)
        return self._geterror(errmsg) + output

    def renderListboxField( self, field, rvalue, errmsg, required ):
        assert rvalue is not None
        if not isinstance(rvalue, list):
            rvalue = [rvalue] # May be a str if not multiple.
        return self._renderMenu(field, rvalue, errmsg, required,
                                field.multiple, field.size)

    def renderFileUploadField( self, field, rvalue, errmsg, required ):
        return self._single('file', field, rvalue, errmsg)

    def renderJSDateField( self, field, rvalue, errmsg, required ):
        return self._single('text', field, rvalue, errmsg)




#-------------------------------------------------------------------------------
#
class TextDisplayRenderer(TextRenderer):
    """
    Display renderer in normal text. This renderer is meant to display parsed
    values as a read-only table, and not as an editable form.
    """

    # CSS classes.
    css_input = u'formdisplay'

    def do_render( self, fields, action, submit ):
        form = self._form
        try:
            # File object that gets set as a side-effect.
            self.ofile = f = self._create_buffer()
            
            # (Side-effect will add to the file.)
            self.do_render_table(fields)

            # Close the form (the container rendering only outputs the header.
            print >> f, '</form>'
        finally:
            self.ofile = None

        return f.getvalue()

    def do_render_container( self, action ):
        return ''

    def do_render_table( self, fields ):
        # Use side-effect for efficiency if requested.
        f = self.ofile or self._create_buffer()

        visible = []
        for field in fields:
            # Don't display hidden fields.
            if field.ishidden():
                continue

            # Never display a file upload. Don't even try.
            if isinstance(field, FileUploadField):
                continue
            
            rendered = self._display_field(field)
            visible.append( (self._get_label(field), rendered) )
            
        self.do_table(visible)

        if self.ofile is None: return f.getvalue()

    def do_render_submit( self, submit ):
        return ''

    #---------------------------------------------------------------------------

    def renderHidden( self, field, rvalue ):
        return ''

    def _simple( self, field, value, errmsg, required ):
        """
        Render a simple field with the given parameters.
        """
        return (self._geterror(errmsg) + value)

    renderStringField = _simple

    def renderTextAreaField( self, field, value, errmsg, required ):
        return (self._geterror(errmsg) + u'<pre>%s</pre>' % value)

    renderPasswordField = _simple
    renderDateField = _simple
    renderEmailField = _simple
    renderURLField = _simple
    renderIntField = _simple
    renderFloatField = _simple
    renderBoolField = _simple
    renderRadioField = _simple
    renderMenuField = _simple
    renderCheckboxesField = _simple
    renderListboxField = _simple

    def renderFileUploadField( self, field, value, errmsg, required ):
        # Never display a file upload. Don't even try.
        return u''

    renderJSDateField = _simple
