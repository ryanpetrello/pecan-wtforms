__version__ = 0.1

from pecan import request
from pecan.middleware.recursive import ForwardRequestException

__all__ = ['with_form']


def with_form(formcls, key='form', error_handler=None):
    """
    Used to wrap a controller with form creation for GET | HEAD and form
    validation for anything else (e.g., POST | PUT | DELETE ).

    For an HTTP GET or HEAD request, the form is instantiated and
    injected into the request object at ``request.pecan['form']`` and in
    the template namespace at ``form`` (unless the key is otherwise specified).

    For an HTTP POST, PUT, or DELETE (non-idempotent) request, the form is
    instantiated and validated.  Errors from validation (if any) are accessible
    at ``request.pecan['form'].errors``.

    :param formcls: A subclass of ``wtforms.form.Form``
    :param key: The key used to inject the form in the template namespace
    :param error_handler: A URI path to a controller used to display errors
    """
    def deco(f):

        def wrapped(*args, **kwargs):
            form = request.environ.pop('pecan.validation_form', None) or \
                   formcls(request.POST)

            if key not in request.pecan:
                request.pecan[key] = form

            if request.method not in ('GET', 'HEAD') and \
                not form.validate() and error_handler is not None:
                location = error_handler
                if callable(location):
                    location = location()
                request.environ['REQUEST_METHOD'] = 'GET'
                request.environ['pecan.validation_redirected'] = True
                request.environ['pecan.validation_form'] = form
                raise ForwardRequestException(location)

            ns = f(*args, **kwargs)
            if type(ns) is dict and key not in ns:
                ns[key] = form
            return ns

        return wrapped

    return deco
