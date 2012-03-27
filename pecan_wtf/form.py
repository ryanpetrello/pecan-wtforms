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
        :param formdata:
            Used to pass data coming from the enduser, usually `request.POST`
            or equivalent.
        :param obj:
            If `formdata` is empty or not provided, this object is checked for
            attributes matching form field names, which will be used for field
            values.
        :param prefix:
            If provided, all fields will have their name prefixed with the
            value.
        :param csrf_enabled:
            Whether to use CSRF protection. If False, all CSRF behavior is
            suppressed.
        :param error_config:
            A dictionary containing configuration for displaying validation
            errors.  See ``pecan_wtf.with_form``.
        :param `**kwargs`:
            If `formdata` is empty or not provided and `obj` does not contain
            an attribute named the same as a field, form will assign the value
            of a matching keyword argument to the field, if one exists.
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
