from cgi import escape

__all__ = ['ErrorMarkupWidget']


def default_formatter(v):
    """
    Formatter that escapes the error, wraps the error in a span with
    class ``error-message``
    """
    return '<span class="error-message">%s</span>\n' % escape(v, True)


class ErrorMarkupWidget(object):
    """"
    A custom widget that appends (or prepends) error markup to an existing
    widget's HTML output.
    """

    def __init__(self, widget, prepend_errors=True, class_='error',
                    formatter=default_formatter):
        self.widget = widget
        self.prepend_errors = prepend_errors
        self.class_ = class_
        self.formatter = formatter

    def __call__(self, field, **kwargs):
        if field.errors:
            c = kwargs.pop('class', '') or kwargs.pop('class_', '')
            kwargs['class'] = u'%s %s' % (self.class_, c) if c else self.class_
        value = self.widget(field, **kwargs)
        if field.errors:
            error_markup = self.format_errors(field.errors)
            if self.prepend_errors:
                value = error_markup + value
            else:
                value += error_markup
        return value

    def format_errors(self, errors):
        return ''.join([
            self.formatter(e) for e in errors
        ])
