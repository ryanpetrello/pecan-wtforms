from cgi import escape

__all__ = ['ErrorMarkupWidget']


def default_formatter(v):
    """
    Formatter that escapes the error, wraps the error in a span with
    class ``error-message``, and adds a ``<br>``
    """
    return '<span class="error-message">%s</span><br />\n' % escape(v, True)


class ErrorMarkupWidget(object):
    """"
    A custom widget that appends (or prepends) error markup to an existing
    widget's HTML output.
    """

    def __init__(self, widget, prepend_errors=True,
                    error_formatter=default_formatter):
        self.widget = widget
        self.prepend_errors = prepend_errors
        self.error_formatter = error_formatter

    def __call__(self, field, **kw):
        value = self.widget(field, **kw)
        if field.errors:
            error_markup = self.format_errors(field.errors)
            if self.prepend_errors:
                value = error_markup + value
            else:
                value += error_markup
        return value

    def format_errors(self, errors):
        return ''.join([
            self.error_formatter(e) for e in errors
        ])
