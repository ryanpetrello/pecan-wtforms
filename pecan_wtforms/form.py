import random
import urlparse
import warnings
from hashlib import md5

from pecan import abort
from wtforms.ext.csrf.form import SecureForm as WTFSecureForm
from wtforms.ext.csrf.fields import CSRFTokenField as WTFCSRFTokenField
from . import ValidationError
from .errors import ErrorMarkupWidget

__all__ = ['SecureForm', 'Form']

REASON_NO_REFERER = "Referer checking failed - no Referer."
REASON_BAD_REFERER = "Referer checking failed - %s does not match %s."
REASON_BAD_TOKEN = "CSRF token incorrect."
REASON_MISSING_TOKEN = "CSRF token missing."


def _get_new_csrf_value():
    return md5(str(random.getrandbits(128))).hexdigest()


def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.

    Theoretically, this is useful in avoiding timing attacks related to
    simple string equality checks.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0


class CSRFTokenField(WTFCSRFTokenField):
    """
    Behaves similarly to CSRFTokenField field, but throws an HTTP 403 exception
    on validation failure.
    """

    def validate(self, form, extra_validators=tuple()):
        valid = super(CSRFTokenField, self).validate(
            form,
            extra_validators=extra_validators
        )
        if valid is False:
            abort(403)
        return valid


class Form(WTFSecureForm):
    """
    Pecan-specific subclass of WTForms **Form** class.
    """
    csrf_token = CSRFTokenField()

    SECRET_KEY = '_pecan_wtform_auth_token'

    def __init__(self, formdata=None, obj=None, prefix='', csrf_context={},
                    error_cfg={}, **kwargs):
        """
        In addition to ``wtforms.ext.csrf.session.SecureForm``:

        :param error_cfg:
            A dictionary containing configuration for displaying validation
            errors.  See ``pecan_wtforms.with_form``.
        """

        # Warn the user if they don't choose a unique secret CSRF key
        if self.SECRET_KEY == Form.SECRET_KEY:
            warnings.warn(
                ('Using the default `SECRET_KEY` is a security risk.  To '
                 'prevent CSRF attacks, set a unique attribute value for '
                 '%s.SECRET_KEY') % self.__class__.__name__,
                RuntimeWarning
            )

        self.csrf_context = csrf_context
        super(Form, self).__init__(formdata, obj, prefix,
                                    csrf_context=self.csrf_context, **kwargs)

        if error_cfg.pop('auto_insert_errors', False) is True:
            self.setup_errors(error_cfg)

    def generate_csrf_token(self, _):
        return

    def validate_csrf_token(self, field):
        return

    def setup_errors(self, config):
        for f in self._fields.itervalues():
            f.widget = ErrorMarkupWidget(f.widget, **config)

    def process(self, formdata=None, obj=None, **kw):
        if formdata is None:
            if hasattr(self, '_validation_original_data'):
                formdata = self._validation_original_data
        super(Form, self).process(formdata, obj, **kw)


class SecureForm(Form):
    """
    A form that includes validation for a cookie-based CSRF token.
    """

    def same_origin(self, url1, url2):
        """
        Checks if two URLs are 'same-origin'
        """
        p1, p2 = urlparse.urlparse(url1), urlparse.urlparse(url2)
        return (p1.scheme, p1.hostname, p1.port) == \
                (p2.scheme, p2.hostname, p2.port)

    def generate_csrf_token(self, _):
        """
        Return the current authentication token, creating a cookie if it
        doesn't already exist.
        """
        key = self.SECRET_KEY
        request = self.csrf_context['request']
        response = self.csrf_context['response']

        if key in request.cookies:
            value = request.cookies[key]
        else:
            value = _get_new_csrf_value()

        # Always set the CSRF cookie to renew the expiry timer.
        self.set_cookie(
            response,
            key,
            value,
            max_age=60 * 60 * 24 * 7 * 52,  # one year
            secure=request.scheme == 'https'
        )
        return value

    def set_cookie(self, response, key, value, **kwargs):
        response.set_cookie(
            key,
            value,
            **kwargs
        )

    def validate_csrf_token(self, field):
        """
        Verify that the current authentication token matches the field data.
        """
        request = self.csrf_context['request']

        # For simplicity, don't require CSRF for unit tests.
        if request.environ.get('paste.testing'):
            return  # pragma: nocover

        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):

            referer = request.headers.get('Referer')

            # If there is no specified referer...
            if referer is None:
                raise ValidationError(field.gettext(
                    REASON_NO_REFERER
                ))

            #
            # If the hostname of the referer and the requested resource
            # don't match...
            #
            origin = 'http://%s/' % request.host
            if not self.same_origin(referer, origin):
                raise ValidationError(field.gettext(
                    REASON_BAD_REFERER % (referer, origin)
                ))

            #
            # If the CSRF token is missing from the form data...
            #
            if not field.data:
                raise ValidationError(field.gettext(REASON_MISSING_TOKEN))

            #
            # If the CSRF token in the session doesn't match the value
            # included in the request...
            #
            if not constant_time_compare(field.current_token, field.data):
                raise ValidationError(field.gettext(REASON_BAD_TOKEN))
