from wtforms.ext.csrf.session import SessionSecureForm
from .errors import ErrorMarkupWidget

__all__ = ['Form']


class Form(SessionSecureForm):
    """
    Pecan-specific subclass of WTForms **SessionSecureForm** class.
    """

    def __init__(self, formdata=None, obj=None, prefix='', csrf_enabled=True,
                    error_config={}, **kwargs):
        """
        In addition to ``wtforms.ext.csrf.session.SessionSecureForm``:

        :param csrf_enabled:
            Whether to use CSRF protection. If False, all CSRF behavior is
            suppressed.
        :param error_config:
            A dictionary containing configuration for displaying validation
            errors.  See ``pecan_wtforms.with_form``.
        """
        self.csrf_enabled = csrf_enabled

        self.SECRET_KEY = ""
        csrf_context = {}

        if self.csrf_enabled:
            pass  # TODO

        super(Form, self).__init__(formdata, obj, prefix,
                                    csrf_context=csrf_context, **kwargs)

        if error_config.pop('auto_insert_errors', False) is True:
            self.setup_errors(error_config)

    def generate_csrf_token(self, csrf_context=None):
        if self.csrf_enabled is False:
            return
        return super(Form, self).generate_csrf_token(csrf_context)

    def validate_csrf_token(self, field):
        if self.csrf_enabled is False:
            return
        super(Form, self).validate_csrf_token(field)

    def setup_errors(self, config):
        for f in self._fields.itervalues():
            f.widget = ErrorMarkupWidget(f.widget, **config)
